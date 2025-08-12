#!/usr/bin/env python3
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_service_device_flow(token_path="token.json", creds_path="credentials.json"):
    """Alternative OAuth flow using device flow instead of local server."""
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Will refresh on use
            pass
        else:
            # Use device flow instead of local server
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            
            # Start the device flow
            device_flow = flow.run_console()
            creds = device_flow
            
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds, cache_discovery=False)

if __name__ == "__main__":
    # Test the device flow
    service = get_service_device_flow()
    print("Authentication successful!")
