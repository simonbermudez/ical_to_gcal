#!/usr/bin/env python3
"""
Debug script to understand RRULE structure from ICS and create proper conversion
"""
import requests
from icalendar import Calendar
import sys

def debug_rrules():
    ics_url = "YOUR_ICS_URL_HERE"
    
    print("Fetching and analyzing RRULE data...")
    try:
        r = requests.get(ics_url, timeout=30)
        r.raise_for_status()
        print(f"Downloaded {len(r.content)} bytes")
        
        # Save raw ICS for inspection
        with open('debug.ics', 'wb') as f:
            f.write(r.content)
        print("Saved raw ICS to debug.ics")
        
        cal = Calendar.from_ical(r.content)
        
        events_with_rrule = 0
        total_events = 0
        
        for component in cal.walk():
            if component.name == "VEVENT":
                total_events += 1
                summary = component.get('summary', 'No Title')
                uid = str(component.get('uid', 'No UID'))
                rrule = component.get('rrule')
                
                if rrule:
                    events_with_rrule += 1
                    print(f"\n--- Event {events_with_rrule} ---")
                    print(f"Summary: {summary}")
                    print(f"UID: {uid[:50]}...")
                    print(f"RRULE type: {type(rrule)}")
                    print(f"RRULE dir: {[attr for attr in dir(rrule) if not attr.startswith('_')]}")
                    
                    # Try to understand the structure
                    if hasattr(rrule, 'items'):
                        print("RRULE items:")
                        for k, v in rrule.items():
                            print(f"  {k}: {v} (type: {type(v)})")
                    
                    # Try different ways to get string representation
                    print(f"RRULE str: {str(rrule)}")
                    print(f"RRULE repr: {repr(rrule)}")
                    
                    # Try to convert to string manually
                    try:
                        parts = []
                        for k, v in rrule.items():
                            if isinstance(v, list):
                                v_str = ','.join(str(x) for x in v)
                            else:
                                v_str = str(v)
                            parts.append(f"{k}={v_str}")
                        manual_rrule = f"RRULE:{';'.join(parts)}"
                        print(f"Manual conversion: {manual_rrule}")
                    except Exception as e:
                        print(f"Manual conversion failed: {e}")
                    
                    if events_with_rrule >= 3:  # Limit output
                        break
        
        print(f"\nSummary: {total_events} total events, {events_with_rrule} with RRULE")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rrules()
