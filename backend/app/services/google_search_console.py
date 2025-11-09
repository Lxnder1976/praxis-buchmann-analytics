from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GoogleSearchConsoleService:
    """Service for fetching Google Search Console data"""
    
    def __init__(self):
        self.site_url = settings.google_search_console_site_url
        self.service = self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Search Console service with credentials"""
        try:
            if settings.google_application_credentials:
                # Use service account credentials
                credentials = service_account.Credentials.from_service_account_file(
                    settings.google_application_credentials,
                    scopes=['https://www.googleapis.com/auth/webmasters.readonly']
                )
                service = build('searchconsole', 'v1', credentials=credentials)
            else:
                # Use default credentials
                service = build('searchconsole', 'v1')
            
            logger.info("Google Search Console service initialized successfully")
            return service
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Search Console service: {str(e)}")
            raise
    
    def fetch_search_performance(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch search performance data from Search Console
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of dictionaries containing search performance data
        """
        try:
            request_body = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['date'],
                'rowLimit': 1000
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url,
                body=request_body
            ).execute()
            
            data = []
            if 'rows' in response:
                for row in response['rows']:
                    record = {
                        'site_url': self.site_url,
                        'date': datetime.strptime(row['keys'][0], '%Y-%m-%d').date(),
                        'clicks': int(row.get('clicks', 0)),
                        'impressions': int(row.get('impressions', 0)),
                        'ctr': float(row.get('ctr', 0)),
                        'position': float(row.get('position', 0)),
                        'raw_data': row
                    }
                    data.append(record)
            
            logger.info(f"Fetched {len(data)} search console records for {start_date} to {end_date}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching search console data: {str(e)}")
            raise
    
    def fetch_top_queries(self, start_date: str, end_date: str, limit: int = 100) -> List[Dict]:
        """
        Fetch top performing queries
        """
        try:
            request_body = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query'],
                'rowLimit': limit,
                'startRow': 0
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url,
                body=request_body
            ).execute()
            
            data = []
            if 'rows' in response:
                for row in response['rows']:
                    record = {
                        'site_url': self.site_url,
                        'query': row['keys'][0],
                        'clicks': int(row.get('clicks', 0)),
                        'impressions': int(row.get('impressions', 0)),
                        'ctr': float(row.get('ctr', 0)),
                        'position': float(row.get('position', 0)),
                        'raw_data': row
                    }
                    data.append(record)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching top queries: {str(e)}")
            raise
    
    def fetch_top_pages(self, start_date: str, end_date: str, limit: int = 100) -> List[Dict]:
        """
        Fetch top performing pages
        """
        try:
            request_body = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['page'],
                'rowLimit': limit
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url,
                body=request_body
            ).execute()
            
            data = []
            if 'rows' in response:
                for row in response['rows']:
                    record = {
                        'site_url': self.site_url,
                        'page': row['keys'][0],
                        'clicks': int(row.get('clicks', 0)),
                        'impressions': int(row.get('impressions', 0)),
                        'ctr': float(row.get('ctr', 0)),
                        'position': float(row.get('position', 0)),
                        'raw_data': row
                    }
                    data.append(record)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching top pages: {str(e)}")
            raise
    
    def fetch_data_for_date_range(self, days_back: int = 7) -> List[Dict]:
        """
        Convenience method to fetch data for the last N days
        """
        # Search Console data has a 3-day delay
        end_date = datetime.now().date() - timedelta(days=3)
        start_date = end_date - timedelta(days=days_back)
        
        return self.fetch_search_performance(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
    
    def get_site_info(self) -> Dict:
        """Get basic information about the connected site"""
        try:
            # Test connection by fetching recent data
            data = self.fetch_data_for_date_range(days_back=1)
            
            return {
                'site_url': self.site_url,
                'status': 'connected',
                'last_data_date': data[0]['date'].isoformat() if data else None,
                'records_available': len(data)
            }
        except Exception as e:
            return {
                'site_url': self.site_url,
                'status': 'error',
                'error': str(e)
            }