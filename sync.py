#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
import os
import sys
from datetime import datetime
from urllib.parse import urlparse

import pytz
import requests
from dateutil import tz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from icalendar import Calendar, Event

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_service(token_path="token.json", creds_path="credentials.json"):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Will refresh on use
            pass
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds, cache_discovery=False)

def fetch_ics(ics_url: str) -> bytes:
    r = requests.get(ics_url, timeout=30)
    r.raise_for_status()
    return r.content

def parse_ics(data: bytes):
    cal = Calendar.from_ical(data)
    for component in cal.walk():
        if component.name == "VEVENT":
            yield component

def _to_rfc3339(dt_obj):
    """
    Return a dict ready for Google Calendar:
    - If date-only (all-day): {"date": "YYYY-MM-DD"}
    - Else: {"dateTime": "...", "timeZone": "..."}
    """
    # All-day if it's a date (no time)
    if isinstance(dt_obj.dt, datetime):
        dt_val = dt_obj.dt
        if dt_val.tzinfo is None:
            # Treat naive as UTC (safer) or local? Prefer UTC.
            dt_val = dt_val.replace(tzinfo=pytz.UTC)
        # Use the zone name if present
        tzinfo = dt_val.tzinfo
        tzname = getattr(tzinfo, "zone", None) or "UTC"
        return {
            "dateTime": dt_val.isoformat(),
            "timeZone": tzname,
        }
    else:
        # date-only
        return {"date": dt_obj.dt.isoformat()}

def event_to_gcal_payload(e: Event):
    summary = str(e.get("summary", "")) if e.get("summary") else ""
    description = str(e.get("description", "")) if e.get("description") else ""
    location = str(e.get("location", "")) if e.get("location") else ""
    status = str(e.get("status", "")).upper() if e.get("status") else ""
    uid = str(e.get("uid", "")).strip()

    # Start/End
    dtstart = e.get("dtstart")
    dtend = e.get("dtend")
    if not dtstart:
        raise ValueError("VEVENT missing DTSTART")

    # Some ICS omit DTEND for all-day; for all-day, Google expects end = next day
    start = _to_rfc3339(dtstart)
    if dtend:
        end = _to_rfc3339(dtend)
    else:
        # derive end for all-day
        if "date" in start:
            from datetime import date, timedelta
            d = datetime.fromisoformat(start["date"]).date()
            end = {"date": (d + timedelta(days=1)).isoformat()}
        else:
            # assume 1 hour duration if timed and no end
            from datetime import timedelta
            dt = datetime.fromisoformat(start["dateTime"])
            end_dt = dt + timedelta(hours=1)
            end = {
                "dateTime": end_dt.isoformat(),
                "timeZone": start.get("timeZone", "UTC"),
            }

    # Recurrence (use icalendar's to_ical method)
    recurrence = []
    rrule = e.get("rrule")
    if rrule:
        try:
            # Use the icalendar library's built-in conversion
            rrule_bytes = rrule.to_ical()
            if isinstance(rrule_bytes, bytes):
                rrule_string = rrule_bytes.decode('utf-8')
            else:
                rrule_string = str(rrule_bytes)
            
            # Ensure it starts with RRULE:
            if not rrule_string.startswith('RRULE:'):
                rrule_string = f"RRULE:{rrule_string}"
            
            recurrence = [rrule_string]
            print(f"[debug] RRULE: {rrule_string}")
                
        except Exception as ex:
            print(f"[warning] Failed to convert RRULE, skipping recurrence: {ex}")
            recurrence = []

    attendees = []
    if e.get("attendee"):
        # May be a list of vCalAddress or str
        raw = e.get("attendee")
        if not isinstance(raw, list):
            raw = [raw]
        for a in raw:
            email = None
            try:
                # vCalAddress like MAILTO:john@x.com
                s = str(a)
                if s.upper().startswith("MAILTO:"):
                    email = s.split(":", 1)[1]
                else:
                    email = s
            except Exception:
                pass
            if email:
                attendees.append({"email": email})

    payload = {
        "summary": summary,
        "description": description,
        "location": location,
        "start": start,
        "end": end,
        "recurrence": recurrence if recurrence else None,
        "attendees": attendees if attendees else None,
        "extendedProperties": {
            "private": {"icsUid": uid}
        }
    }
    # Remove None fields
    return {k: v for k, v in payload.items() if v not in (None, "", [])}, status, uid

def gcal_find_by_ics_uid(service, calendar_id, ics_uid):
    # Use privateExtendedProperty filter
    return service.events().list(
        calendarId=calendar_id,
        privateExtendedProperty=f"icsUid={ics_uid}",
        maxResults=2,
        singleEvents=False
    ).execute()

def gcal_upsert_event(service, calendar_id, payload, existing_event_id=None):
    if existing_event_id:
        return service.events().update(
            calendarId=calendar_id,
            eventId=existing_event_id,
            body=payload
        ).execute()
    else:
        return service.events().insert(
            calendarId=calendar_id,
            body=payload
        ).execute()

def gcal_delete_event(service, calendar_id, event_id):
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

def load_feed_uids(events):
    uids = set()
    for e in events:
        uid = str(e.get("uid", "")).strip()
        if uid:
            uids.add(uid)
    return uids

def get_all_synced_google_events(service, calendar_id):
    """Fetch all events that originated from this ICS (identified by extendedProperties.private.icsUid)."""
    items = []
    page_token = None
    while True:
        # Get all events, then filter client-side for those with icsUid
        # The privateExtendedProperty filter requires a key=value format
        resp = service.events().list(
            calendarId=calendar_id,
            pageToken=page_token,
            maxResults=2500,
            showDeleted=False,
            singleEvents=False
        ).execute()
        
        # Filter events that have the icsUid extended property
        events = resp.get("items", [])
        for event in events:
            ext_props = event.get("extendedProperties", {})
            private_props = ext_props.get("private", {})
            if "icsUid" in private_props:
                items.append(event)
        
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return items

def is_future_event(event):
    """Check if an event starts in the future or has future recurring occurrences."""
    try:
        dtstart = event.get("dtstart")
        if not dtstart:
            return False
        
        now = datetime.now(pytz.UTC)
        
        # Handle different datetime formats for the start time
        event_start = None
        if hasattr(dtstart.dt, 'tzinfo'):
            # datetime with timezone
            event_start = dtstart.dt
            if event_start.tzinfo is None:
                # Treat naive datetime as UTC
                event_start = event_start.replace(tzinfo=pytz.UTC)
        else:
            # date only (all-day event)
            from datetime import date
            if isinstance(dtstart.dt, date):
                # Convert date to datetime at start of day UTC
                event_start = datetime.combine(dtstart.dt, datetime.min.time()).replace(tzinfo=pytz.UTC)
        
        if not event_start:
            return True  # If we can't parse, include it to be safe
        
        # Check if the event has a recurrence rule
        rrule = event.get("rrule")
        if rrule:
            # For recurring events, check if they have future occurrences
            try:
                # Check if there's an UNTIL date
                until_date = None
                if hasattr(rrule, 'items'):
                    for k, v in rrule.items():
                        if k.upper() == 'UNTIL' and v:
                            # v is typically a list
                            until_value = v[0] if isinstance(v, list) else v
                            if hasattr(until_value, 'tzinfo'):
                                until_date = until_value
                                if until_date.tzinfo is None:
                                    until_date = until_date.replace(tzinfo=pytz.UTC)
                            elif hasattr(until_value, 'dt'):
                                until_date = until_value.dt
                                if until_date.tzinfo is None:
                                    until_date = until_date.replace(tzinfo=pytz.UTC)
                            break
                
                # If there's an UNTIL date, check if it's in the future
                if until_date:
                    return until_date > now
                else:
                    # No UNTIL date means the recurrence continues indefinitely
                    # Always include these recurring events
                    return True
                    
            except Exception:
                # If we can't parse the recurrence rule, include the event
                return True
        else:
            # Non-recurring event - just check the start time
            return event_start > now
        
    except Exception:
        # If we can't determine the date, include the event to be safe
        return True

def main():
    parser = argparse.ArgumentParser(description="Sync an ICS public feed into a Google Calendar.")
    parser.add_argument("--ics-url", required=True, help="Public ICS feed URL")
    parser.add_argument("--calendar-id", required=True, help="Target Google Calendar ID (e.g., primary or you@domain.com)")
    parser.add_argument("--credentials", default="credentials.json", help="Google OAuth client secrets file")
    parser.add_argument("--token", default="token.json", help="Cached OAuth token file")
    parser.add_argument("--prune-missing", action="store_true", help="Delete Google events (with icsUid) not present in the current feed")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing to Google")
    parser.add_argument("--future-only", action="store_true", help="Only sync events that start in the future (skip past events)")
    args = parser.parse_args()

    service = get_service(token_path=args.token, creds_path=args.credentials)

    # Fetch and parse ICS
    ics_bytes = fetch_ics(args.ics_url)
    ics_events = list(parse_ics(ics_bytes))
    feed_uids = load_feed_uids(ics_events)

    # For pruning, prefetch currently synced Google events
    existing_synced = {e.get("extendedProperties", {}).get("private", {}).get("icsUid"): e
                       for e in get_all_synced_google_events(service, args.calendar_id)}

    created = 0
    updated = 0
    deleted = 0
    skipped = 0

    for ev in ics_events:
        try:
            payload, status, uid = event_to_gcal_payload(ev)
        except Exception as ex:
            print(f"[skip] malformed event: {ex}", file=sys.stderr)
            skipped += 1
            continue

        if not uid:
            print("[skip] event without UID")
            skipped += 1
            continue

        # Skip past events if --future-only flag is set
        if args.future_only and not is_future_event(ev):
            summary = ev.get("summary", "No Title")
            print(f"[skip] past event: {summary} ({uid})")
            skipped += 1
            continue

        # Look up existing
        lookup = gcal_find_by_ics_uid(service, args.calendar_id, uid)
        items = lookup.get("items", [])
        existing = items[0] if items else None
        existing_id = existing.get("id") if existing else None

        if status == "CANCELLED":
            if existing_id:
                print(f"[delete] {uid} (cancelled in ICS)")
                if not args.dry_run:
                    gcal_delete_event(service, args.calendar_id, existing_id)
                deleted += 1
            else:
                print(f"[skip] {uid} cancelled but not present in Google")
            continue

        # Upsert with robust error handling and retry logic
        try:
            if existing_id:
                print(f"[update] {uid} -> {existing_id}")
                if not args.dry_run:
                    gcal_upsert_event(service, args.calendar_id, payload, existing_event_id=existing_id)
                updated += 1
            else:
                print(f"[create] {uid}")
                if not args.dry_run:
                    gcal_upsert_event(service, args.calendar_id, payload, existing_event_id=None)
                created += 1
        except Exception as ex:
            error_msg = str(ex).lower()
            operation = 'update' if existing_id else 'create'
            
            # If it's a recurrence-related error, try without recurrence
            if "recurrence" in error_msg or "rrule" in error_msg:
                print(f"[error] {operation} failed due to recurrence rule: {ex}")
                if "recurrence" in payload and payload["recurrence"]:
                    print(f"[retry] Retrying {uid} without recurrence")
                    payload_no_recur = payload.copy()
                    payload_no_recur.pop("recurrence", None)
                    try:
                        if existing_id:
                            gcal_upsert_event(service, args.calendar_id, payload_no_recur, existing_event_id=existing_id)
                            updated += 1
                        else:
                            gcal_upsert_event(service, args.calendar_id, payload_no_recur, existing_event_id=None)
                            created += 1
                        print(f"[success] {operation.capitalize()}d {uid} without recurrence")
                        continue
                    except Exception as ex2:
                        print(f"[error] Still failed to {operation} {uid}: {ex2}")
                        skipped += 1
                        continue
                else:
                    print(f"[error] Recurrence error but no recurrence in payload: {ex}")
                    skipped += 1
                    continue
            else:
                print(f"[error] Failed to {operation} {uid}: {ex}")
                skipped += 1

    # Prune events that exist in Google but not in current ICS feed
    if args.prune_missing:
        for uid, g_event in existing_synced.items():
            if uid and uid not in feed_uids:
                ev_id = g_event["id"]
                print(f"[prune-delete] {uid} -> {ev_id} (missing from feed)")
                if not args.dry_run:
                    gcal_delete_event(service, args.calendar_id, ev_id)
                deleted += 1

    print(f"Done. created={created}, updated={updated}, deleted={deleted}, skipped={skipped}")

if __name__ == "__main__":
    main()