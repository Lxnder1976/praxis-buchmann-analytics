from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GoogleAnalyticsService:
    """Service for fetching Google Analytics data"""
    
    def __init__(self):
        self.property_id = settings.google_analytics_property_id
        self.client = self._initialize_client()
    
    def _initialize_client(self) -> BetaAnalyticsDataClient:
        """Initialize Google Analytics client with service account credentials"""
        try:
            if settings.google_application_credentials:
                # Use service account credentials
                credentials = service_account.Credentials.from_service_account_file(
                    settings.google_application_credentials,
                    scopes=['https://www.googleapis.com/auth/analytics.readonly']
                )
                client = BetaAnalyticsDataClient(credentials=credentials)
            else:
                # Use default credentials (for development/testing)
                client = BetaAnalyticsDataClient()
            
            logger.info("Google Analytics client initialized successfully")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Analytics client: {str(e)}")
            raise
    
    def fetch_basic_metrics(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch basic analytics metrics for the specified date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of dictionaries containing analytics data
        """
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[
                    Dimension(name="date")
                ],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="totalUsers"),
                    Metric(name="newUsers"),
                    Metric(name="screenPageViews"),
                    Metric(name="averageSessionDuration"),
                    Metric(name="bounceRate"),
                    Metric(name="screenPageViewsPerSession"),
                    Metric(name="conversions"),
                ]
            )
            
            response = self.client.run_report(request=request)
            
            # Process response into structured data
            data = []
            for row in response.rows:
                record = {
                    'date': datetime.strptime(row.dimension_values[0].value, '%Y%m%d').date(),
                    'property_id': self.property_id,
                    'sessions': int(row.metric_values[0].value or 0),
                    'users': int(row.metric_values[1].value or 0),
                    'new_users': int(row.metric_values[2].value or 0),
                    'page_views': int(row.metric_values[3].value or 0),
                    'average_session_duration': float(row.metric_values[4].value or 0),
                    'bounce_rate': float(row.metric_values[5].value or 0),
                    'pages_per_session': float(row.metric_values[6].value or 0),
                    'conversions': int(row.metric_values[7].value or 0),
                    'raw_data': {
                        'dimensions': [dim.value for dim in row.dimension_values],
                        'metrics': [metric.value for metric in row.metric_values]
                    }
                }
                data.append(record)
            
            logger.info(f"Fetched {len(data)} records for date range {start_date} to {end_date}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching analytics data: {str(e)}")
            raise
    
    def fetch_traffic_sources(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch traffic source data
        """
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[
                    Dimension(name="date"),
                    Dimension(name="sessionDefaultChannelGrouping")
                ],
                metrics=[
                    Metric(name="sessions"),
                ]
            )
            
            response = self.client.run_report(request=request)
            
            # Group by date and channel
            traffic_by_date = {}
            for row in response.rows:
                date_str = row.dimension_values[0].value
                channel = row.dimension_values[1].value
                sessions = int(row.metric_values[0].value or 0)
                
                if date_str not in traffic_by_date:
                    traffic_by_date[date_str] = {
                        'date': datetime.strptime(date_str, '%Y%m%d').date(),
                        'property_id': self.property_id,
                        'organic_sessions': 0,
                        'direct_sessions': 0,
                        'referral_sessions': 0,
                        'social_sessions': 0,
                        'paid_sessions': 0
                    }
                
                # Map channels to our standardized categories
                if channel.lower() in ['organic search']:
                    traffic_by_date[date_str]['organic_sessions'] += sessions
                elif channel.lower() in ['direct']:
                    traffic_by_date[date_str]['direct_sessions'] += sessions
                elif channel.lower() in ['referral']:
                    traffic_by_date[date_str]['referral_sessions'] += sessions
                elif channel.lower() in ['organic social', 'social']:
                    traffic_by_date[date_str]['social_sessions'] += sessions
                elif channel.lower() in ['paid search', 'paid social', 'display']:
                    traffic_by_date[date_str]['paid_sessions'] = traffic_by_date[date_str].get('paid_sessions', 0) + sessions
            
            return list(traffic_by_date.values())
            
        except Exception as e:
            logger.error(f"Error fetching traffic source data: {str(e)}")
            raise
    
    def fetch_enhanced_metrics(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch enhanced analytics metrics including traffic sources and page data
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of dictionaries containing enhanced analytics data
        """
        try:
            # First get basic metrics
            basic_data = self.fetch_basic_metrics(start_date, end_date)
            
            # Then get traffic sources data
            traffic_data = self.fetch_traffic_sources(start_date, end_date)
            
            # Merge the data by date
            enhanced_data = []
            for basic_record in basic_data:
                # Find matching traffic data for the same date
                traffic_record = next(
                    (t for t in traffic_data if t['date'] == basic_record['date']), 
                    {
                        'organic_sessions': 0,
                        'direct_sessions': 0,
                        'referral_sessions': 0,
                        'social_sessions': 0,
                        'paid_sessions': 0
                    }
                )
                
                # Merge basic and traffic data
                enhanced_record = {
                    **basic_record,
                    'organic_sessions': traffic_record.get('organic_sessions', 0),
                    'direct_sessions': traffic_record.get('direct_sessions', 0),
                    'referral_sessions': traffic_record.get('referral_sessions', 0),
                    'social_sessions': traffic_record.get('social_sessions', 0),
                }
                
                enhanced_data.append(enhanced_record)
            
            logger.info(f"Fetched enhanced data with traffic sources for {len(enhanced_data)} dates")
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error fetching enhanced metrics: {str(e)}")
            # Fallback to basic metrics if traffic sources fail
            logger.warning("Falling back to basic metrics without traffic sources")
            return self.fetch_basic_metrics(start_date, end_date)
    
    def fetch_page_analytics(self, start_date: str, end_date: str, limit: int = 50) -> List[Dict]:
        """
        Fetch page-level analytics data
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of pages to return
            
        Returns:
            List of dictionaries containing page analytics data
        """
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[
                    Dimension(name="pagePath"),
                    Dimension(name="pageTitle")
                ],
                metrics=[
                    Metric(name="screenPageViews"),
                    Metric(name="sessions"),
                    Metric(name="totalUsers"),
                    Metric(name="averageSessionDuration"),
                    Metric(name="bounceRate"),
                ],
                limit=limit
            )
            
            response = self.client.run_report(request=request)
            
            # Process response into structured data
            data = []
            for row in response.rows:
                record = {
                    'property_id': self.property_id,
                    'page_path': row.dimension_values[0].value,
                    'page_title': row.dimension_values[1].value,
                    'page_views': int(row.metric_values[0].value or 0),
                    'sessions': int(row.metric_values[1].value or 0),
                    'users': int(row.metric_values[2].value or 0),
                    'average_session_duration': float(row.metric_values[3].value or 0),
                    'bounce_rate': float(row.metric_values[4].value or 0),
                    'date_range': f"{start_date}_{end_date}",
                    'raw_data': {
                        'dimensions': [dim.value for dim in row.dimension_values],
                        'metrics': [metric.value for metric in row.metric_values]
                    }
                }
                data.append(record)
            
            logger.info(f"Fetched page analytics for {len(data)} pages")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching page analytics: {str(e)}")
            raise
    
    def fetch_data_for_date_range(self, days_back: int = 7) -> List[Dict]:
        """
        Convenience method to fetch enhanced data for the last N days
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        return self.fetch_enhanced_metrics(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
    
    def get_property_info(self) -> Dict:
        """Get basic information about the connected property"""
        try:
            # This is a simple check to verify the connection works
            data = self.fetch_basic_metrics(
                start_date=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                end_date=datetime.now().strftime('%Y-%m-%d')
            )
            
            return {
                'property_id': self.property_id,
                'status': 'connected',
                'last_data_date': data[0]['date'].isoformat() if data else None,
                'records_available': len(data)
            }
        except Exception as e:
            return {
                'property_id': self.property_id,
                'status': 'error',
                'error': str(e)
            }