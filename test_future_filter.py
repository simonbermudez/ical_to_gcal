#!/usr/bin/env python3
"""
Test the future-only filtering functionality
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from icalendar import Calendar
from sync import is_future_event
from datetime import datetime
import pytz

def test_future_filtering():
    print("Testing future event filtering (including recurring events)...")
    
    if not os.path.exists('debug.ics'):
        print("debug.ics not found")
        return
    
    with open('debug.ics', 'rb') as f:
        cal = Calendar.from_ical(f.read())
    
    now = datetime.now(pytz.UTC)
    print(f"Current time (UTC): {now}")
    print()
    
    total_events = 0
    future_events = 0
    past_events = 0
    recurring_events = 0
    
    for component in cal.walk():
        if component.name == "VEVENT":
            total_events += 1
            
            summary = component.get('summary', 'No Title')
            dtstart = component.get('dtstart')
            rrule = component.get('rrule')
            
            if dtstart:
                is_future = is_future_event(component)
                is_recurring = rrule is not None
                
                if is_recurring:
                    recurring_events += 1
                
                if is_future:
                    future_events += 1
                    status = "FUTURE"
                else:
                    past_events += 1
                    status = "PAST"
                
                recurring_info = " (RECURRING)" if is_recurring else ""
                print(f"[{status}] {summary}{recurring_info}")
                print(f"  Start: {dtstart.dt}")
                
                if is_recurring:
                    print(f"  RRULE: {rrule.to_ical().decode('utf-8') if hasattr(rrule, 'to_ical') else 'Unknown'}")
                
                print()
                
                if total_events >= 15:  # Show more events to catch recurring ones
                    break
    
    print(f"Summary:")
    print(f"Total events examined: {total_events}")
    print(f"Recurring events: {recurring_events}")
    print(f"Future events (including recurring with future occurrences): {future_events}")
    print(f"Past events (non-recurring or recurring with no future occurrences): {past_events}")

if __name__ == "__main__":
    test_future_filtering()
