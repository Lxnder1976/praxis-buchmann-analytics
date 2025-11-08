#!/usr/bin/env python3
"""
Setup OAuth2 credentials for Google Analytics
"""

import os
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import pickle
import json

def setup_oauth_credentials():
    print("🔑 Setting up OAuth2 credentials for Google Analytics")
    print("=" * 50)
    
    # OAuth2 setup - we need to create a OAuth2 credentials file
    # This is easier than dealing with service account permissions
    
    print("We need to set up OAuth2 authentication instead of Service Account.")
    print("")
    print("📋 Next steps:")
    print("1. Go to Google Cloud Console")
    print("2. Navigate to 'APIs & Services' > 'Credentials'")
    print("3. Click 'CREATE CREDENTIALS' > 'OAuth client ID'")
    print("4. Application type: 'Desktop application'")
    print("5. Name: 'Analytics Dashboard'")
    print("6. Download the JSON file")
    print("7. Rename it to 'oauth_credentials.json' and place it in the backend folder")
    print("")
    print("After that, run this script again to authenticate.")
    
    credentials_path = "/Users/alex/Projects/Analytics/backend/oauth_credentials.json"
    if os.path.exists(credentials_path):
        print("✅ OAuth credentials file found!")
        return True
    else:
        print(f"❌ OAuth credentials file not found: {credentials_path}")
        return False

if __name__ == "__main__":
    setup_oauth_credentials()