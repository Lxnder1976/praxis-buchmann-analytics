#!/usr/bin/env python3
"""
Test script for all Google APIs (Analytics, Search Console, Google Ads)
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

from app.services.unified_data import UnifiedDataService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    print("🚀 Testing All Google APIs")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    try:
        # Initialize unified service
        print("📊 Initializing Unified Data Service...")
        unified_service = UnifiedDataService()
        print("✅ Service initialized successfully")
        print()
        
        # Test all connections
        print("🔌 Testing API Connections...")
        connections = unified_service.test_all_connections()
        
        for service_name, status in connections.items():
            print(f"\n📈 {service_name.replace('_', ' ').title()}:")
            print(f"   Status: {status.get('status', 'unknown')}")
            if status.get('error'):
                print(f"   Error: {status.get('error')}")
            else:
                for key, value in status.items():
                    if key not in ['status', 'error']:
                        print(f"   {key}: {value}")
        
        print()
        print("=" * 50)
        
        # Check which services are working
        working_services = [
            name for name, status in connections.items() 
            if status.get('status') == 'connected'
        ]
        
        if not working_services:
            print("❌ No services are properly configured.")
            print("Please check your .env configuration and API credentials.")
            return
        
        print(f"✅ Working services: {', '.join(working_services)}")
        print()
        
        # Get current data summary
        print("📊 Current Data Summary:")
        summary = unified_service.get_unified_summary()
        
        for service_name, data in summary.items():
            if service_name != 'total_records' and isinstance(data, dict):
                print(f"\n📈 {service_name.replace('_', ' ').title()}:")
                for key, value in data.items():
                    print(f"   {key}: {value}")
        
        print(f"\n📊 Total Records: {summary.get('total_records', 0)}")
        print()
        
        # Option to fetch new data
        if working_services:
            print("🔄 Fetching new data from working services...")
            result = unified_service.fetch_and_store_all_data(days_back=3)
            
            print(f"\n📊 Fetch Results:")
            print(f"Overall Status: {result['overall_status']}")
            print(f"Total Records Processed: {result['total_records_processed']}")
            
            for service_name, data in result.items():
                if service_name not in ['overall_status', 'total_records_processed'] and isinstance(data, dict):
                    print(f"\n📈 {service_name.replace('_', ' ').title()}:")
                    print(f"   Status: {data.get('status', 'unknown')}")
                    print(f"   Message: {data.get('message', 'No message')}")
                    if 'records_fetched' in data:
                        print(f"   Records Fetched: {data.get('records_fetched', 0)}")
                        print(f"   Records Stored: {data.get('records_stored', 0)}")
        
        print()
        print("🎉 Multi-API test complete!")
        
        if len(working_services) == 3:
            print("✅ All services working perfectly!")
        elif len(working_services) > 0:
            print(f"⚠️  Partial success: {len(working_services)}/3 services working")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()