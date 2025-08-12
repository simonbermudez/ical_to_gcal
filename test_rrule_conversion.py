#!/usr/bin/env python3
"""
Test just the RRULE conversion without full sync
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import requests
from icalendar import Calendar
import pytz

def test_rrule_conversion():
    # Fetch a few events and test RRULE conversion
    ics_url = "YOUR_ICS_URL_HERE"
    
    r = requests.get(ics_url, timeout=30)
    r.raise_for_status()
    
    cal = Calendar.from_ical(r.content)
    
    tested = 0
    for component in cal.walk():
        if component.name == "VEVENT" and tested < 5:
            rrule = component.get("rrule")
            if rrule:
                tested += 1
                summary = component.get('summary', 'No Title')
                uid = str(component.get('uid', ''))[:30] + "..."
                
                print(f"\n--- Event {tested}: {summary} ---")
                print(f"UID: {uid}")
                print(f"RRULE type: {type(rrule)}")
                
                # Test conversion methods
                try:
                    if hasattr(rrule, 'to_ical'):
                        rrule_bytes = rrule.to_ical()
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
                
                # Manual method
                try:
                    parts = []
                    for k, v in rrule.items():
                        key = k.upper()
                        if isinstance(v, (list, tuple)):
                            v_str = ",".join(str(x) for x in v)
                        elif hasattr(v, 'dt'):
                            dt = v.dt
                            if dt.tzinfo:
                                dt_utc = dt.astimezone(pytz.UTC)
                                v_str = dt_utc.strftime('%Y%m%dT%H%M%SZ')
                            else:
                                v_str = dt.strftime('%Y%m%dT%H%M%S')
                        elif hasattr(v, 'strftime'):
                            v_str = v.strftime('%Y%m%d')
                        else:
                            v_str = str(v)
                        parts.append(f"{key}={v_str}")
                    
                    manual_rrule = f"RRULE:{';'.join(parts)}"
                    print(f"✓ Manual method: {manual_rrule}")
                except Exception as e:
                    print(f"✗ Manual method failed: {e}")

if __name__ == "__main__":
    test_rrule_conversion()
