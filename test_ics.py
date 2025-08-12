#!/usr/bin/env python3
"""
Test script to check if the ICS URL is accessible and parseable
"""
import requests
from icalendar import Calendar

def test_ics_fetch():
    ics_url = "YOUR_ICS_URL_HERE"
    
    print("Testing ICS URL accessibility...")
    try:
        r = requests.get(ics_url, timeout=30)
        r.raise_for_status()
        print(f"✓ ICS URL accessible, got {len(r.content)} bytes")
        
        # Try to parse the calendar
        cal = Calendar.from_ical(r.content)
        print("✓ ICS file parsed successfully")
        
        # Count events
        event_count = 0
        for component in cal.walk():
            if component.name == "VEVENT":
                event_count += 1
                print(f"Event: {component.get('summary', 'No Title')}")
                if event_count >= 3:  # Just show first 3
                    break
        
        print(f"✓ Found {event_count}+ events in the ICS file")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_ics_fetch()
