#!/usr/bin/env python3
"""
Test script to verify the Google Analytics data fetching and persistence functionality
"""

import sys
import os
import logging
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/Users/alex/Projects/Analytics/backend/.env')

from app.config.settings import settings
from app.services.google_analytics import GoogleAnalyticsService
from app.services.data_persistence import DataPersistenceService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_configuration():
    """Test configuration settings"""
    print("=== Testing Configuration ===")
    print(f"Environment: {settings.environment}")
    print(f"Property ID: {settings.google_analytics_property_id}")
    print(f"Credentials: {settings.google_application_credentials}")
    print(f"Database URL: {settings.database_url}")
    print()

def test_google_analytics_connection():
    """Test Google Analytics API connection"""
    print("=== Testing Google Analytics Connection ===")
    try:
        ga_service = GoogleAnalyticsService()
        property_info = ga_service.get_property_info()
        
        print(f"Connection Status: {property_info['status']}")
        if property_info['status'] == 'connected':
            print(f"Property ID: {property_info['property_id']}")
            print(f"Last Data Date: {property_info.get('last_data_date', 'N/A')}")
            print(f"Records Available: {property_info.get('records_available', 0)}")
        else:
            print(f"Error: {property_info.get('error', 'Unknown error')}")
        
        return property_info['status'] == 'connected'
        
    except Exception as e:
        print(f"❌ Google Analytics connection failed: {str(e)}")
        return False
    
    print()

def test_database_connection():
    """Test database connection and table creation"""
    print("=== Testing Database Connection ===")
    try:
        data_service = DataPersistenceService()
        summary = data_service.get_stored_data_summary()
        
        print(f"✅ Database connection successful")
        print(f"Total Records: {summary.get('total_records', 0)}")
        print(f"Date Range: {summary.get('date_range', 'No data')}")
        print(f"Properties: {summary.get('properties', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False
    
    print()

def test_data_fetch_and_store():
    """Test the complete data fetch and store workflow"""
    print("=== Testing Data Fetch and Store ===")
    try:
        data_service = DataPersistenceService()
        
        # Fetch data for the last 3 days (small test)
        print("Fetching data for the last 3 days...")
        result = data_service.fetch_and_store_recent_data(days_back=3)
        
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Records Processed: {result.get('records_processed', 0)}")
        print(f"New Records: {result.get('new_records', 0)}")
        print(f"Updated Records: {result.get('updated_records', 0)}")
        
        if 'date_range' in result:
            print(f"Date Range: {result['date_range']['start']} to {result['date_range']['end']}")
        
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"❌ Data fetch and store failed: {str(e)}")
        return False
    
    print()

def main():
    """Run all tests"""
    print("🚀 Starting Analytics Data Service Tests")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 50)
    print()
    
    # Test configuration
    test_configuration()
    
    # Test database connection
    db_ok = test_database_connection()
    if not db_ok:
        print("❌ Database tests failed. Cannot continue.")
        sys.exit(1)
    
    # Test Google Analytics connection
    ga_ok = test_google_analytics_connection()
    if not ga_ok:
        print("❌ Google Analytics connection failed.")
        print("Please check your credentials and property ID in the .env file")
        sys.exit(1)
    
    # Test complete workflow
    workflow_ok = test_data_fetch_and_store()
    if not workflow_ok:
        print("❌ Complete workflow test failed.")
        sys.exit(1)
    
    print("✅ All tests passed successfully!")
    print()
    print("🎉 Your analytics data service is ready to use!")
    print()
    print("Next steps:")
    print("1. Run the FastAPI server: uvicorn app.main:app --reload")
    print("2. Open http://localhost:8000/docs to see the API documentation")
    print("3. Use POST /fetch-data to manually fetch analytics data")
    print("4. Use GET /data-summary to view stored data")

if __name__ == "__main__":
    main()