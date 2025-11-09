#!/usr/bin/env python3
"""
Test Enhanced Analytics APIs
This script tests the extended Google Analytics API with traffic sources,
page analytics, and Search Console keyword data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.unified_data import UnifiedDataService
from app.services.google_analytics import GoogleAnalyticsService
from app.services.google_search_console import GoogleSearchConsoleService
from datetime import datetime, timedelta
import json

def test_enhanced_google_analytics():
    """Test enhanced Google Analytics with traffic sources"""
    print("🔍 Testing Enhanced Google Analytics...")
    
    try:
        ga_service = GoogleAnalyticsService()
        
        # Test enhanced metrics (basic + traffic sources)
        print("\n1. Testing Enhanced Metrics (with Traffic Sources):")
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        enhanced_data = ga_service.fetch_enhanced_metrics(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        print(f"   ✅ Fetched {len(enhanced_data)} records with traffic sources")
        
        # Show sample with traffic sources
        if enhanced_data:
            sample = enhanced_data[0]
            print(f"   📊 Sample data for {sample['date']}:")
            print(f"      Sessions: {sample['sessions']}")
            print(f"      Organic Sessions: {sample.get('organic_sessions', 0)}")
            print(f"      Direct Sessions: {sample.get('direct_sessions', 0)}")
            print(f"      Referral Sessions: {sample.get('referral_sessions', 0)}")
            print(f"      Social Sessions: {sample.get('social_sessions', 0)}")
        
        # Test page analytics
        print("\n2. Testing Page Analytics:")
        page_data = ga_service.fetch_page_analytics(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            limit=10
        )
        
        print(f"   ✅ Fetched {len(page_data)} page records")
        
        if page_data:
            print("   📄 Top pages:")
            for i, page in enumerate(page_data[:5]):
                print(f"      {i+1}. {page['page_path']} - {page['page_views']} views")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_search_console_keywords():
    """Test Search Console keyword data"""
    print("\n🔍 Testing Search Console Keywords...")
    
    try:
        gsc_service = GoogleSearchConsoleService()
        
        # Test top queries
        print("\n1. Testing Top Queries:")
        end_date = datetime.now().date() - timedelta(days=3)  # Account for delay
        start_date = end_date - timedelta(days=7)
        
        query_data = gsc_service.fetch_top_queries(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            limit=20
        )
        
        print(f"   ✅ Fetched {len(query_data)} query records")
        
        if query_data:
            print("   🔎 Top search queries:")
            for i, query in enumerate(query_data[:10]):
                print(f"      {i+1}. '{query['query']}' - {query['clicks']} clicks, {query['impressions']} imp.")
        
        # Test top pages
        print("\n2. Testing Top Search Pages:")
        page_data = gsc_service.fetch_top_pages(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            limit=10
        )
        
        print(f"   ✅ Fetched {len(page_data)} page records from search console")
        
        if page_data:
            print("   📄 Top performing pages in search:")
            for i, page in enumerate(page_data[:5]):
                print(f"      {i+1}. {page['page']} - {page['clicks']} clicks")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_enhanced_data_collection():
    """Test the enhanced unified data collection"""
    print("\n🚀 Testing Enhanced Data Collection...")
    
    try:
        service = UnifiedDataService()
        
        # Run enhanced data collection
        results = service.fetch_and_store_enhanced_data(days_back=7)
        
        print(f"   📊 Overall Status: {results['overall_status']}")
        print(f"   📈 Total Records Processed: {results['total_records_processed']}")
        
        # Show results for each service
        services = ['google_analytics', 'page_analytics', 'search_console', 'search_queries', 'search_pages', 'google_ads']
        
        for service_name in services:
            if service_name in results:
                service_result = results[service_name]
                status = service_result.get('status', 'unknown')
                fetched = service_result.get('records_fetched', 0)
                stored = service_result.get('records_stored', 0)
                message = service_result.get('message', 'No message')
                
                status_emoji = "✅" if status == 'success' else "⚠️" if status == 'warning' else "❌"
                print(f"   {status_emoji} {service_name}: {fetched} fetched, {stored} stored - {message}")
        
        return results['overall_status'] in ['success', 'partial_success']
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def analyze_enhanced_data():
    """Analyze the enhanced data collected"""
    print("\n📊 Analyzing Enhanced Data...")
    
    try:
        import sqlite3
        conn = sqlite3.connect('/Users/alex/Projects/Analytics/backend/analytics.db')
        
        # Check traffic sources
        print("\n1. Traffic Sources Analysis:")
        traffic_sources = conn.execute("""
            SELECT 
                SUM(organic_sessions) as organic,
                SUM(direct_sessions) as direct,
                SUM(referral_sessions) as referral,
                SUM(social_sessions) as social
            FROM analytics_data 
            WHERE date >= date('now', '-7 days')
        """).fetchone()
        
        organic, direct, referral, social = traffic_sources
        total_sourced = organic + direct + referral + social
        
        if total_sourced > 0:
            print(f"   ✅ Traffic Sources Working!")
            print(f"      Organic: {organic} sessions")
            print(f"      Direct: {direct} sessions")
            print(f"      Referral: {referral} sessions")
            print(f"      Social: {social} sessions")
        else:
            print(f"   ⚠️ Traffic Sources still showing zeros - checking channel mapping...")
        
        # Check page analytics
        print("\n2. Page Analytics Analysis:")
        page_count = conn.execute("SELECT COUNT(*) FROM page_analytics_data").fetchone()[0]
        
        if page_count > 0:
            print(f"   ✅ Page Analytics Working! {page_count} page records")
            
            top_pages = conn.execute("""
                SELECT page_path, page_views, sessions, users 
                FROM page_analytics_data 
                ORDER BY page_views DESC 
                LIMIT 5
            """).fetchall()
            
            print("   📄 Top Pages:")
            for page_path, views, sessions, users in top_pages:
                print(f"      {page_path}: {views} views, {sessions} sessions")
        else:
            print("   ❌ No page analytics data found")
        
        # Check search queries
        print("\n3. Search Queries Analysis:")
        query_count = conn.execute("SELECT COUNT(*) FROM search_query_data").fetchone()[0]
        
        if query_count > 0:
            print(f"   ✅ Search Queries Working! {query_count} query records")
            
            top_queries = conn.execute("""
                SELECT query, clicks, impressions, ctr, position 
                FROM search_query_data 
                ORDER BY clicks DESC 
                LIMIT 5
            """).fetchall()
            
            print("   🔎 Top Search Queries:")
            for query, clicks, impressions, ctr, position in top_queries:
                print(f"      '{query}': {clicks} clicks, {impressions} imp., pos {position:.1f}")
        else:
            print("   ❌ No search query data found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error analyzing data: {str(e)}")
        return False

def main():
    print("🎯 ENHANCED ANALYTICS API TESTING")
    print("=" * 50)
    
    # Test individual components
    ga_success = test_enhanced_google_analytics()
    gsc_success = test_search_console_keywords()
    
    # Test unified collection
    unified_success = test_enhanced_data_collection()
    
    # Analyze results
    analysis_success = analyze_enhanced_data()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TESTING SUMMARY:")
    print(f"   Enhanced Google Analytics: {'✅' if ga_success else '❌'}")
    print(f"   Search Console Keywords: {'✅' if gsc_success else '❌'}")
    print(f"   Enhanced Data Collection: {'✅' if unified_success else '❌'}")
    print(f"   Data Analysis: {'✅' if analysis_success else '❌'}")
    
    overall_success = ga_success and gsc_success and unified_success
    print(f"\n🎯 Overall Status: {'SUCCESS' if overall_success else 'NEEDS WORK'}")
    
    if overall_success:
        print("\n✨ Enhanced APIs are working! You now have:")
        print("   • Traffic source data (organic, direct, referral, social)")
        print("   • Page-level analytics")
        print("   • Search keyword data")
        print("   • Landing page performance from search")
    else:
        print("\n🔧 Some enhancements need debugging. Check the errors above.")
    
    return overall_success

if __name__ == "__main__":
    main()