from app.services.google_analytics import GoogleAnalyticsService
from app.services.google_search_console import GoogleSearchConsoleService
from app.services.google_ads import GoogleAdsService
from app.models.database import (
    AnalyticsData, SearchConsoleData, GoogleAdsData, 
    get_db_session, create_db_engine, create_tables
)
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class UnifiedDataService:
    """Service for fetching data from all Google APIs and persisting to database"""
    
    def __init__(self):
        self.ga_service = GoogleAnalyticsService()
        self.gsc_service = GoogleSearchConsoleService()
        self.ads_service = GoogleAdsService()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables for all services"""
        try:
            engine = create_db_engine()
            create_tables(engine)
            logger.info("All database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def fetch_and_store_all_data(self, days_back: int = 7) -> Dict:
        """
        Fetch data from all APIs and store in database
        
        Args:
            days_back: Number of days to fetch data for
            
        Returns:
            Summary of the operation for all services
        """
        results = {
            'google_analytics': {'status': 'skipped', 'message': 'Not attempted'},
            'search_console': {'status': 'skipped', 'message': 'Not attempted'},
            'google_ads': {'status': 'skipped', 'message': 'Not attempted'},
            'overall_status': 'unknown',
            'total_records_processed': 0
        }
        
        # Fetch Google Analytics Data
        try:
            logger.info("Fetching Google Analytics data...")
            ga_data = self.ga_service.fetch_data_for_date_range(days_back)
            ga_stored = self._store_analytics_data(ga_data)
            
            results['google_analytics'] = {
                'status': 'success',
                'records_fetched': len(ga_data),
                'records_stored': ga_stored,
                'message': f'Successfully processed {len(ga_data)} GA records'
            }
        except Exception as e:
            logger.error(f"Google Analytics fetch failed: {str(e)}")
            results['google_analytics'] = {
                'status': 'error',
                'message': str(e),
                'records_fetched': 0,
                'records_stored': 0
            }
        
        # Fetch Search Console Data
        try:
            logger.info("Fetching Google Search Console data...")
            gsc_data = self.gsc_service.fetch_data_for_date_range(days_back)
            gsc_stored = self._store_search_console_data(gsc_data)
            
            results['search_console'] = {
                'status': 'success',
                'records_fetched': len(gsc_data),
                'records_stored': gsc_stored,
                'message': f'Successfully processed {len(gsc_data)} GSC records'
            }
        except Exception as e:
            logger.error(f"Search Console fetch failed: {str(e)}")
            results['search_console'] = {
                'status': 'error',
                'message': str(e),
                'records_fetched': 0,
                'records_stored': 0
            }
        
        # Fetch Google Ads Data
        try:
            logger.info("Fetching Google Ads data...")
            ads_data = self.ads_service.fetch_data_for_date_range(days_back)
            ads_stored = self._store_google_ads_data(ads_data)
            
            results['google_ads'] = {
                'status': 'success' if ads_data else 'warning',
                'records_fetched': len(ads_data),
                'records_stored': ads_stored,
                'message': f'Successfully processed {len(ads_data)} Ads records' if ads_data else 'Google Ads not configured'
            }
        except Exception as e:
            logger.error(f"Google Ads fetch failed: {str(e)}")
            results['google_ads'] = {
                'status': 'error',
                'message': str(e),
                'records_fetched': 0,
                'records_stored': 0
            }
        
        # Calculate overall status
        success_count = sum(1 for service in results.values() 
                          if isinstance(service, dict) and service.get('status') == 'success')
        total_services = 3
        
        if success_count == total_services:
            results['overall_status'] = 'success'
        elif success_count > 0:
            results['overall_status'] = 'partial_success'
        else:
            results['overall_status'] = 'failed'
        
        # Calculate total records
        total_records = sum(
            service.get('records_processed', service.get('records_fetched', 0))
            for service in results.values()
            if isinstance(service, dict) and 'records_fetched' in service
        )
        results['total_records_processed'] = total_records
        
        logger.info(f"Data fetch complete. Status: {results['overall_status']}, Total records: {total_records}")
        return results
    
    def _store_analytics_data(self, analytics_data: List[Dict]) -> int:
        """Store Google Analytics data in database"""
        if not analytics_data:
            return 0
        
        session = get_db_session()
        stored_count = 0
        
        try:
            for record in analytics_data:
                existing = session.query(AnalyticsData).filter(
                    AnalyticsData.property_id == record['property_id'],
                    AnalyticsData.date == record['date']
                ).first()
                
                if existing:
                    for key, value in record.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    new_record = AnalyticsData(**record)
                    session.add(new_record)
                    stored_count += 1
            
            session.commit()
            return stored_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing analytics data: {str(e)}")
            raise
        finally:
            session.close()
    
    def _store_search_console_data(self, gsc_data: List[Dict]) -> int:
        """Store Search Console data in database"""
        if not gsc_data:
            return 0
        
        session = get_db_session()
        stored_count = 0
        
        try:
            for record in gsc_data:
                existing = session.query(SearchConsoleData).filter(
                    SearchConsoleData.site_url == record['site_url'],
                    SearchConsoleData.date == record['date']
                ).first()
                
                if existing:
                    for key, value in record.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    new_record = SearchConsoleData(**record)
                    session.add(new_record)
                    stored_count += 1
            
            session.commit()
            return stored_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing search console data: {str(e)}")
            raise
        finally:
            session.close()
    
    def _store_google_ads_data(self, ads_data: List[Dict]) -> int:
        """Store Google Ads data in database"""
        if not ads_data:
            return 0
        
        session = get_db_session()
        stored_count = 0
        
        try:
            for record in ads_data:
                existing = session.query(GoogleAdsData).filter(
                    GoogleAdsData.customer_id == record['customer_id'],
                    GoogleAdsData.campaign_id == record['campaign_id'],
                    GoogleAdsData.date == record['date']
                ).first()
                
                if existing:
                    for key, value in record.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    new_record = GoogleAdsData(**record)
                    session.add(new_record)
                    stored_count += 1
            
            session.commit()
            return stored_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing Google Ads data: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_unified_summary(self) -> Dict:
        """Get comprehensive summary of all stored data"""
        session = get_db_session()
        
        try:
            # Analytics summary
            ga_count = session.query(AnalyticsData).count()
            ga_latest = session.query(AnalyticsData).order_by(AnalyticsData.date.desc()).first()
            
            # Search Console summary
            gsc_count = session.query(SearchConsoleData).count()
            gsc_latest = session.query(SearchConsoleData).order_by(SearchConsoleData.date.desc()).first()
            
            # Google Ads summary
            ads_count = session.query(GoogleAdsData).count()
            ads_latest = session.query(GoogleAdsData).order_by(GoogleAdsData.date.desc()).first()
            
            return {
                'google_analytics': {
                    'total_records': ga_count,
                    'latest_date': ga_latest.date.isoformat() if ga_latest else None,
                    'property_id': ga_latest.property_id if ga_latest else None
                },
                'search_console': {
                    'total_records': gsc_count,
                    'latest_date': gsc_latest.date.isoformat() if gsc_latest else None,
                    'site_url': gsc_latest.site_url if gsc_latest else None
                },
                'google_ads': {
                    'total_records': ads_count,
                    'latest_date': ads_latest.date.isoformat() if ads_latest else None,
                    'customer_id': ads_latest.customer_id if ads_latest else None
                },
                'total_records': ga_count + gsc_count + ads_count
            }
            
        except Exception as e:
            logger.error(f"Error getting unified summary: {str(e)}")
            return {
                'error': str(e),
                'total_records': 0
            }
        finally:
            session.close()
    
    def test_all_connections(self) -> Dict:
        """Test connections to all APIs"""
        return {
            'google_analytics': self.ga_service.get_property_info(),
            'search_console': self.gsc_service.get_site_info(),
            'google_ads': self.ads_service.get_account_info()
        }