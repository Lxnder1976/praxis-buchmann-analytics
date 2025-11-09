from app.services.google_analytics import GoogleAnalyticsService
from app.services.google_search_console import GoogleSearchConsoleService
from app.services.google_ads import GoogleAdsService
from app.models.database import (
    AnalyticsData, SearchConsoleData, GoogleAdsData, 
    PageAnalyticsData, SearchQueryData, SearchPageData,
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
    
    def fetch_and_store_enhanced_data(self, days_back: int = 7) -> Dict:
        """
        Fetch enhanced data including traffic sources, page analytics, and keyword data
        
        Args:
            days_back: Number of days to fetch data for
            
        Returns:
            Summary of the operation for all services
        """
        results = {
            'google_analytics': {'status': 'skipped', 'message': 'Not attempted'},
            'page_analytics': {'status': 'skipped', 'message': 'Not attempted'},
            'search_console': {'status': 'skipped', 'message': 'Not attempted'},
            'search_queries': {'status': 'skipped', 'message': 'Not attempted'},
            'search_pages': {'status': 'skipped', 'message': 'Not attempted'},
            'google_ads': {'status': 'skipped', 'message': 'Not attempted'},
            'overall_status': 'unknown',
            'total_records_processed': 0
        }
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        date_range_str = f"{start_date}_{end_date}"
        
        # Fetch Enhanced Google Analytics Data (with traffic sources)
        try:
            logger.info("Fetching enhanced Google Analytics data...")
            ga_data = self.ga_service.fetch_data_for_date_range(days_back)  # Already uses enhanced_metrics
            ga_stored = self._store_analytics_data(ga_data)
            
            results['google_analytics'] = {
                'status': 'success',
                'records_fetched': len(ga_data),
                'records_stored': ga_stored,
                'message': f'Successfully processed {len(ga_data)} GA records with traffic sources'
            }
        except Exception as e:
            logger.error(f"Enhanced Google Analytics fetch failed: {str(e)}")
            results['google_analytics'] = {
                'status': 'error',
                'message': str(e),
                'records_fetched': 0,
                'records_stored': 0
            }
        
        # Fetch Page Analytics Data
        try:
            logger.info("Fetching page analytics data...")
            page_data = self.ga_service.fetch_page_analytics(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                limit=50
            )
            page_stored = self._store_page_analytics_data(page_data)
            
            results['page_analytics'] = {
                'status': 'success',
                'records_fetched': len(page_data),
                'records_stored': page_stored,
                'message': f'Successfully processed {len(page_data)} page analytics records'
            }
        except Exception as e:
            logger.error(f"Page analytics fetch failed: {str(e)}")
            results['page_analytics'] = {
                'status': 'error',
                'message': str(e),
                'records_fetched': 0,
                'records_stored': 0
            }
        
        # Fetch Search Console Data (basic)
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
        
        # Fetch Search Queries Data
        try:
            logger.info("Fetching search queries data...")
            query_data = self.gsc_service.fetch_top_queries(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                limit=100
            )
            # Add date_range to each record
            for record in query_data:
                record['date_range'] = date_range_str
            
            query_stored = self._store_search_query_data(query_data)
            
            results['search_queries'] = {
                'status': 'success',
                'records_fetched': len(query_data),
                'records_stored': query_stored,
                'message': f'Successfully processed {len(query_data)} search query records'
            }
        except Exception as e:
            logger.error(f"Search queries fetch failed: {str(e)}")
            results['search_queries'] = {
                'status': 'error',
                'message': str(e),
                'records_fetched': 0,
                'records_stored': 0
            }
        
        # Fetch Search Pages Data
        try:
            logger.info("Fetching search pages data...")
            pages_data = self.gsc_service.fetch_top_pages(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                limit=50
            )
            # Add date_range to each record
            for record in pages_data:
                record['date_range'] = date_range_str
            
            pages_stored = self._store_search_page_data(pages_data)
            
            results['search_pages'] = {
                'status': 'success',
                'records_fetched': len(pages_data),
                'records_stored': pages_stored,
                'message': f'Successfully processed {len(pages_data)} search page records'
            }
        except Exception as e:
            logger.error(f"Search pages fetch failed: {str(e)}")
            results['search_pages'] = {
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
        total_services = 6  # Updated for enhanced services
        
        if success_count >= 4:  # Allow some services to fail
            results['overall_status'] = 'success'
        elif success_count >= 2:
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
        
        logger.info(f"Enhanced data fetch complete. Status: {results['overall_status']}, Total records: {total_records}")
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
    
    def _store_page_analytics_data(self, page_data: List[Dict]) -> int:
        """Store page analytics data in database"""
        if not page_data:
            return 0
        
        session = get_db_session()
        stored_count = 0
        
        try:
            for record in page_data:
                existing = session.query(PageAnalyticsData).filter(
                    PageAnalyticsData.property_id == record['property_id'],
                    PageAnalyticsData.page_path == record['page_path'],
                    PageAnalyticsData.date_range == record['date_range']
                ).first()
                
                if existing:
                    for key, value in record.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    new_record = PageAnalyticsData(**record)
                    session.add(new_record)
                    stored_count += 1
            
            session.commit()
            return stored_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing page analytics data: {str(e)}")
            raise
        finally:
            session.close()
    
    def _store_search_query_data(self, query_data: List[Dict]) -> int:
        """Store search query data in database"""
        if not query_data:
            return 0
        
        session = get_db_session()
        stored_count = 0
        
        try:
            for record in query_data:
                existing = session.query(SearchQueryData).filter(
                    SearchQueryData.site_url == record['site_url'],
                    SearchQueryData.query == record['query'],
                    SearchQueryData.date_range == record['date_range']
                ).first()
                
                if existing:
                    for key, value in record.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    new_record = SearchQueryData(**record)
                    session.add(new_record)
                    stored_count += 1
            
            session.commit()
            return stored_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing search query data: {str(e)}")
            raise
        finally:
            session.close()
    
    def _store_search_page_data(self, page_data: List[Dict]) -> int:
        """Store search page data in database"""
        if not page_data:
            return 0
        
        session = get_db_session()
        stored_count = 0
        
        try:
            for record in page_data:
                existing = session.query(SearchPageData).filter(
                    SearchPageData.site_url == record['site_url'],
                    SearchPageData.page == record['page'],
                    SearchPageData.date_range == record['date_range']
                ).first()
                
                if existing:
                    for key, value in record.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    new_record = SearchPageData(**record)
                    session.add(new_record)
                    stored_count += 1
            
            session.commit()
            return stored_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing search page data: {str(e)}")
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