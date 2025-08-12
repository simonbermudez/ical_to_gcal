#!/usr/bin/env python3
"""
Test RRULE conversion using the cached debug.ics file
"""
from icalendar import Calendar
import pytz
import os

def test_rrule_from_file():
    if not os.path.exists('debug.ics'):
        print("debug.ics not found. Run rrule_debug.py first.")
        return
    
    print("Testing RRULE conversion from cached debug.ics...")
    
    with open('debug.ics', 'rb') as f:
        cal = Calendar.from_ical(f.read())
    
    tested = 0
    for component in cal.walk():
        if component.name == "VEVENT" and tested < 3:
            rrule = component.get("rrule")
            if rrule:
                tested += 1
                summary = component.get('summary', 'No Title')
                uid = str(component.get('uid', ''))[:30] + "..."
                
                print(f"\n--- Event {tested}: {summary} ---")
                print(f"UID: {uid}")
                print(f"RRULE type: {type(rrule)}")
                print(f"RRULE attrs: {[attr for attr in dir(rrule) if not attr.startswith('_')]}")
                
                # Test to_ical method
                try:
                    if hasattr(rrule, 'to_ical'):
                        rrule_bytes = rrule.to_ical()
                        print(f"to_ical() raw: {rrule_bytes} (type: {type(rrule_bytes)})")
                        
                        if isinstance(rrule_bytes, bytes):
                            rrule_string = rrule_bytes.decode('utf-8')
                        else:
                            rrule_string = str(rrule_bytes)
                        
                        if not rrule_string.startswith('RRULE:'):
                            rrule_string = f"RRULE:{rrule_string}"
                        
                        print(f"✓ to_ical() method: {rrule_string}")
                    else:
                        print("✗ No to_ical() method")
                except Exception as e:
                    print(f"✗ to_ical() failed: {e}")
                
                # Test items method
                try:
                    if hasattr(rrule, 'items'):
                        print("RRULE items():")
                        for k, v in rrule.items():
                            print(f"  {k}: {v} (type: {type(v)})")
                    else:
                        print("✗ No items() method")
                except Exception as e:
                    print(f"✗ items() failed: {e}")

if __name__ == "__main__":
    test_rrule_from_file()
