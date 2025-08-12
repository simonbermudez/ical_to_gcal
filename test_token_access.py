#!/usr/bin/env python3
"""
Test script to verify token.json access in Docker
"""
import os
import json

def test_token_access():
    print("Testing token.json access...")
    
    # Check environment variables
    creds_path = os.environ.get('CREDENTIALS_PATH', 'credentials.json')
    token_path = os.environ.get('TOKEN_PATH', 'token.json')
    
    print(f"CREDENTIALS_PATH: {creds_path}")
    print(f"TOKEN_PATH: {token_path}")
    
    # Check if files exist
    print(f"\nFile existence checks:")
    print(f"credentials.json exists: {os.path.exists(creds_path)}")
    print(f"token.json exists: {os.path.exists(token_path)}")
    
    # Try to read token.json
    if os.path.exists(token_path):
        try:
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            print(f"✓ Successfully read token.json")
            print(f"Token keys: {list(token_data.keys())}")
        except Exception as e:
            print(f"✗ Failed to read token.json: {e}")
    
    # Try to read credentials.json
    if os.path.exists(creds_path):
        try:
            with open(creds_path, 'r') as f:
                creds_data = json.load(f)
            print(f"✓ Successfully read credentials.json")
            if 'installed' in creds_data:
                print(f"Credentials type: installed")
            elif 'web' in creds_data:
                print(f"Credentials type: web")
        except Exception as e:
            print(f"✗ Failed to read credentials.json: {e}")

if __name__ == "__main__":
    test_token_access()
