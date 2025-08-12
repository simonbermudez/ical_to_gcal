#!/usr/bin/env python3
"""
Quick test of sync with future-only flag using cached data
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from icalendar import Calendar
from sync import is_future_event

def count_events():
    if not os.path.exists('debug.ics'):
        print("debug.ics not found")
        return
    
    with open('debug.ics', 'rb') as f:
        cal = Calendar.from_ical(f.read())
    
    total = 0
    future = 0
    
    for component in cal.walk():
        if component.name == "VEVENT":
            total += 1
            if is_future_event(component):
                future += 1
    
    print(f"Total events in ICS file: {total}")
    print(f"Future events (including recurring with future occurrences): {future}")
    print(f"Past events that would be skipped: {total - future}")
    print(f"Performance improvement: {((total - future) / total * 100):.1f}% fewer API calls")

if __name__ == "__main__":
    count_events()
