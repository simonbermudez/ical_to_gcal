#!/usr/bin/env python3
"""
Clear all events that were synced from ICS (identified by icsUid property).
This preserves any manually added events in the calendar.
"""
import argparse
import os
from sync import get_service, get_all_synced_google_events, gcal_delete_event

def clear_ics_synced_events(service, calendar_id, dry_run=False):
    """Delete all events that have the icsUid extended property."""
    print(f"Fetching all ICS-synced events from calendar: {calendar_id}")
    
    synced_events = get_all_synced_google_events(service, calendar_id)
    
    print(f"Found {len(synced_events)} ICS-synced events")
    
    if dry_run:
        print("\nDRY RUN - Would delete the following events:")
        for event in synced_events:
            summary = event.get('summary', 'No title')
            event_id = event.get('id')
            print(f"  - {summary} (ID: {event_id})")
    else:
        print("\nDeleting ICS-synced events...")
        for i, event in enumerate(synced_events, 1):
            summary = event.get('summary', 'No title')
            event_id = event.get('id')
            try:
                gcal_delete_event(service, calendar_id, event_id)
                print(f"  [{i}/{len(synced_events)}] Deleted: {summary}")
            except Exception as e:
                print(f"  [{i}/{len(synced_events)}] Failed to delete {summary}: {e}")
    
    print(f"\n{'Would delete' if dry_run else 'Deleted'} {len(synced_events)} events")
    print("You can now run a fresh sync to repopulate the calendar.")

def main():
    parser = argparse.ArgumentParser(description="Clear all ICS-synced events from Google Calendar")
    parser.add_argument("--calendar-id", required=True, help="Target Google Calendar ID")
    parser.add_argument("--credentials", default="credentials.json", help="OAuth credentials file")
    parser.add_argument("--token", default="token.json", help="OAuth token file")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be deleted")
    
    args = parser.parse_args()
    
    # Override with environment variables if present
    creds_path = os.environ.get("CREDENTIALS_PATH", args.credentials)
    token_path = os.environ.get("TOKEN_PATH", args.token)
    
    service = get_service(token_path=token_path, creds_path=creds_path)
    clear_ics_synced_events(service, args.calendar_id, args.dry_run)

if __name__ == "__main__":
    main()