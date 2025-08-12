#!/usr/bin/env python3
import requests

def simple_test():
    print("Testing ICS URL access...")
    url = "YOUR_ICS_URL_HERE"
    
    try:
        r = requests.get(url, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Content length: {len(r.content)}")
        
        # Look for RRULE in first part of content
        content_str = r.content.decode('utf-8')
        rrule_count = content_str.count('RRULE:')
        print(f"RRULE count: {rrule_count}")
        
        if rrule_count > 0:
            # Find first RRULE
            start = content_str.find('RRULE:')
            if start != -1:
                end = content_str.find('\n', start)
                if end != -1:
                    first_rrule = content_str[start:end].strip()
                    print(f"First RRULE: {first_rrule}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simple_test()
