#!/usr/bin/env python3
"""
List all available Google Calendars to help find the correct calendar ID.
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_service(token_path="token.json", creds_path="credentials.json"):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Will refresh on use
            pass
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds, cache_discovery=False)

def list_calendars():
    service = get_service()
    
    print("Available Google Calendars:")
    print("=" * 50)
    
    try:
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        if not calendars:
            print("No calendars found.")
            return
        
        for calendar in calendars:
            calendar_id = calendar['id']
            summary = calendar.get('summary', 'No Title')
            access_role = calendar.get('accessRole', 'unknown')
            primary = calendar.get('primary', False)
            
            print(f"Calendar ID: {calendar_id}")
            print(f"Title: {summary}")
            print(f"Access Role: {access_role}")
            print(f"Primary: {'Yes' if primary else 'No'}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error listing calendars: {e}")

if __name__ == "__main__":
    list_calendars()
