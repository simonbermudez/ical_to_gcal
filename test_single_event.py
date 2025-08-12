#!/usr/bin/env python3
"""
Test creating a single event with recurrence in Google Calendar
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from icalendar import Calendar
from sync import get_service, event_to_gcal_payload, gcal_upsert_event

def test_single_recurring_event():
    print("Testing single recurring event creation...")
    
    # Use the cached debug.ics file
    if not os.path.exists('debug.ics'):
        print("debug.ics not found. Run the sync script first to download it.")
        return
    
    with open('debug.ics', 'rb') as f:
        cal = Calendar.from_ical(f.read())
    
    # Find first event with RRULE
    test_event = None
    for component in cal.walk():
        if component.name == "VEVENT":
            rrule = component.get("rrule")
            if rrule:
                test_event = component
                break
    
    if not test_event:
        print("No recurring events found")
        return
    
    print(f"Found test event: {test_event.get('summary', 'No Title')}")
    
    try:
        # Convert to Google Calendar payload
        payload, status, uid = event_to_gcal_payload(test_event)
        print(f"Payload created successfully")
        print(f"Recurrence: {payload.get('recurrence', 'None')}")
        
        # Get Google Calendar service
        calendar_id = "YOUR_CALENDAR_ID_HERE"
        service = get_service()
        
        # Try to create the event (dry run - we'll catch the error)
        print("Attempting to create event...")
        try:
            result = gcal_upsert_event(service, calendar_id, payload, existing_event_id=None)
            print(f"✓ Success! Created event: {result.get('id', 'Unknown ID')}")
        except Exception as e:
            print(f"✗ Creation failed: {e}")
            
            # If recurrence error, try without recurrence
            if "recurrence" in str(e).lower():
                print("Trying without recurrence...")
                payload_no_recur = payload.copy()
                payload_no_recur.pop('recurrence', None)
                try:
                    result = gcal_upsert_event(service, calendar_id, payload_no_recur, existing_event_id=None)
                    print(f"✓ Success without recurrence! Created event: {result.get('id', 'Unknown ID')}")
                except Exception as e2:
                    print(f"✗ Still failed: {e2}")
        
    except Exception as e:
        print(f"Error processing event: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_recurring_event()
