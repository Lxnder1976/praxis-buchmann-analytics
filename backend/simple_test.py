#!/usr/bin/env python3
"""
Simple test script to verify Google Analytics API connection
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account
from datetime import datetime, timedelta
import json

def test_google_analytics():
    print("🚀 Testing Google Analytics API Connection")
    print("=" * 50)
    
    # Configuration
    PROPERTY_ID = "503566620"
    CREDENTIALS_PATH = "/Users/alex/Projects/Analytics/backend/credentials.json"
    
    print(f"Property ID: {PROPERTY_ID}")
    print(f"Credentials: {CREDENTIALS_PATH}")
    
    # Check if credentials file exists
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"❌ Credentials file not found: {CREDENTIALS_PATH}")
        return False
    
    print("✅ Credentials file found")
    
    try:
        # Initialize client
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        client = BetaAnalyticsDataClient(credentials=credentials)
        print("✅ Google Analytics client initialized")
        
        # Test API call - get data for yesterday
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.strftime('%Y-%m-%d')
        end_date = yesterday.strftime('%Y-%m-%d')
        
        print(f"📊 Fetching data for {start_date}")
        
        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="date")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="screenPageViews")
            ]
        )
        
        response = client.run_report(request=request)
        
        print(f"✅ API call successful!")
        print(f"📈 Rows returned: {len(response.rows)}")
        
        if response.rows:
            row = response.rows[0]
            print(f"📅 Date: {row.dimension_values[0].value}")
            print(f"👥 Sessions: {row.metric_values[0].value}")
            print(f"👤 Users: {row.metric_values[1].value}")
            print(f"📄 Page Views: {row.metric_values[2].value}")
        else:
            print("⚠️  No data returned (this might be normal for recent dates)")
        
        print("\n🎉 Google Analytics API is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nPossible solutions:")
        print("1. Check if the service account email is added to Google Analytics")
        print("2. Verify the Property ID is correct")
        print("3. Ensure the Google Analytics Data API is enabled")
        return False

if __name__ == "__main__":
    success = test_google_analytics()
    if success:
        print("\n✅ Ready to proceed with the full application!")
    else:
        print("\n❌ Please fix the issues above before continuing.")
        sys.exit(1)