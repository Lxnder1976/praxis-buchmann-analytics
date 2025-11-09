#!/usr/bin/env python3
"""
Google Ads API Test Script

This script tests the Google Ads API integration.
Run this after setting up your Google Ads configuration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.google_ads import GoogleAdsService
from app.config.settings import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_ads_service():
    """Test Google Ads service functionality"""
    print("🧪 Testing Google Ads Service")
    print("=" * 40)
    
    # Initialize service
    print("📱 Initializing Google Ads service...")
    service = GoogleAdsService()
    
    # Test account info
    print("\n1️⃣ Testing account connection...")
    account_info = service.get_account_info()
    print(f"Account Status: {account_info.get('status')}")
    
    if account_info.get('status') == 'not_configured':
        print("⚠️ Google Ads not configured. Please run setup_google_ads.py first.")
        print("\nConfiguration needed:")
        print(f"- GOOGLE_ADS_CUSTOMER_ID: {settings.google_ads_customer_id}")
        print(f"- GOOGLE_ADS_CONFIG_PATH: {settings.google_ads_config_path}")
        return False
    elif account_info.get('status') == 'error':
        print(f"❌ Error: {account_info.get('error')}")
        print("\nCommon issues:")
        print("- Developer token not approved or invalid")
        print("- Service account doesn't have access to Google Ads account")
        print("- Customer ID is incorrect")
        print("- Network connectivity issues")
        return False
    else:
        print("✅ Account connection successful!")
        if 'customer_id' in account_info:
            print(f"   Customer ID: {account_info['customer_id']}")
    
    # Test data fetching
    print("\n2️⃣ Testing data fetching...")
    try:
        data = service.fetch_data_for_date_range(days_back=7)
        print(f"📊 Fetched {len(data)} campaign records for last 7 days")
        
        if data:
            # Show sample data
            sample = data[0]
            print(f"   Sample record:")
            print(f"   - Campaign: {sample.get('campaign_name', 'N/A')}")
            print(f"   - Date: {sample.get('date', 'N/A')}")
            print(f"   - Impressions: {sample.get('impressions', 0)}")
            print(f"   - Clicks: {sample.get('clicks', 0)}")
            print(f"   - Cost: ${sample.get('cost_micros', 0) / 1000000:.2f}")
        else:
            print("   ⚠️ No campaign data found (this might be normal for new accounts)")
        
    except Exception as e:
        print(f"❌ Data fetching failed: {str(e)}")
        return False
    
    # Test account performance
    print("\n3️⃣ Testing account performance summary...")
    try:
        from datetime import datetime, timedelta
        end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        performance = service.fetch_account_performance(start_date, end_date)
        print(f"📈 Account performance status: {performance.get('status')}")
        
        if performance.get('status') == 'connected' and 'summary' in performance:
            summary = performance['summary']
            print(f"   Total Impressions: {summary.get('total_impressions', 0):,}")
            print(f"   Total Clicks: {summary.get('total_clicks', 0):,}")
            print(f"   Total Cost: ${summary.get('total_cost', 0):.2f}")
            print(f"   Average CTR: {summary.get('average_ctr', 0):.2f}%")
            print(f"   Average CPC: ${summary.get('average_cpc', 0):.2f}")
        
    except Exception as e:
        print(f"❌ Performance summary failed: {str(e)}")
        return False
    
    print("\n✅ Google Ads service test completed successfully!")
    return True

def show_configuration():
    """Show current configuration"""
    print("\n📋 Current Google Ads Configuration:")
    print("-" * 30)
    print(f"Customer ID: {settings.google_ads_customer_id or 'Not set'}")
    print(f"Config Path: {settings.google_ads_config_path or 'Not set'}")
    print(f"Service Account: {settings.google_application_credentials or 'Not set'}")
    
    # Check if files exist
    if settings.google_ads_config_path:
        import os
        if os.path.exists(settings.google_ads_config_path):
            print("✅ Google Ads config file exists")
        else:
            print("❌ Google Ads config file not found")
    
    if settings.google_application_credentials:
        import os
        if os.path.exists(settings.google_application_credentials):
            print("✅ Service account credentials exist")
        else:
            print("❌ Service account credentials not found")

def main():
    """Main test function"""
    print("🚀 Google Ads API Integration Test")
    print("=" * 50)
    
    show_configuration()
    
    if not settings.google_ads_customer_id or not settings.google_ads_config_path:
        print("\n⚠️ Google Ads not configured!")
        print("Run: python setup_google_ads.py")
        return
    
    success = test_google_ads_service()
    
    if success:
        print("\n🎉 All tests passed! Google Ads API is ready to use.")
    else:
        print("\n❌ Tests failed. Please check configuration and try again.")

if __name__ == "__main__":
    main()