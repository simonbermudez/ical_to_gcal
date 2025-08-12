#!/usr/bin/env python3
"""
Test script to examine RRULE data from the ICS file
"""
import requests
from icalendar import Calendar

def examine_rrules():
    ics_url = "YOUR_ICS_URL_HERE"
    
    print("Examining RRULE data from ICS file...")
    try:
        r = requests.get(ics_url, timeout=30)
        r.raise_for_status()
        
        cal = Calendar.from_ical(r.content)
        
        event_count = 0
        rrule_count = 0
        
        for component in cal.walk():
            if component.name == "VEVENT":
                event_count += 1
                summary = component.get('summary', 'No Title')
                uid = component.get('uid', 'No UID')
                rrule = component.get('rrule')
                
                if rrule:
                    rrule_count += 1
                    print(f"\nEvent: {summary}")
                    print(f"UID: {uid}")
                    print(f"RRULE type: {type(rrule)}")
                    print(f"RRULE content: {rrule}")
                    print(f"RRULE items: {list(rrule.items()) if hasattr(rrule, 'items') else 'N/A'}")
                    
                    if rrule_count >= 3:  # Show first 3 recurring events
                        break
        
        print(f"\nSummary: {event_count} total events, {rrule_count} with recurrence rules")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    examine_rrules()
