try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_ADS_AVAILABLE = True
except ImportError:
    # Google Ads library not installed
    GoogleAdsClient = None
    GoogleAdsException = Exception
    GOOGLE_ADS_AVAILABLE = False

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GoogleAdsService:
    """Service for fetching Google Ads data"""
    
    def __init__(self):
        self.customer_id = settings.google_ads_customer_id
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Ads client with credentials"""
        if not GOOGLE_ADS_AVAILABLE:
            logger.warning("Google Ads library not installed. Install with: pip install google-ads")
            return None
        
        try:
            # Google Ads API requires a separate configuration file
            if settings.google_ads_config_path:
                client = GoogleAdsClient.load_from_storage(path=settings.google_ads_config_path)
            else:
                logger.warning("Google Ads configuration not found. Service will return mock data.")
                return None
            
            logger.info("Google Ads client initialized successfully")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {str(e)}")
            return None
    
    def fetch_campaign_performance(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch campaign performance data from Google Ads
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of dictionaries containing campaign performance data
        """
        if not self.client:
            logger.warning("Google Ads client not available. Returning empty data.")
            return []
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    segments.date,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc
                FROM campaign
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY segments.date ASC
            """
            
            search_request = self.client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = self.customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            data = []
            for row in response:
                record = {
                    'customer_id': self.customer_id,
                    'campaign_id': str(row.campaign.id),
                    'campaign_name': row.campaign.name,
                    'campaign_status': row.campaign.status.name,
                    'date': datetime.strptime(row.segments.date, '%Y-%m-%d').date(),
                    'impressions': row.metrics.impressions,
                    'clicks': row.metrics.clicks,
                    'cost_micros': row.metrics.cost_micros,
                    'conversions': row.metrics.conversions,
                    'ctr': row.metrics.ctr,
                    'cpc': row.metrics.average_cpc / 1000000,  # Convert from micros
                    'cost_per_conversion': (row.metrics.cost_micros / 1000000) / max(row.metrics.conversions, 1),
                    'conversion_rate': (row.metrics.conversions / max(row.metrics.clicks, 1)) * 100,
                    'raw_data': {
                        'campaign_id': str(row.campaign.id),
                        'campaign_name': row.campaign.name,
                        'date': row.segments.date,
                        'metrics': {
                            'impressions': row.metrics.impressions,
                            'clicks': row.metrics.clicks,
                            'cost_micros': row.metrics.cost_micros,
                            'conversions': row.metrics.conversions
                        }
                    }
                }
                data.append(record)
            
            logger.info(f"Fetched {len(data)} Google Ads records for {start_date} to {end_date}")
            return data
            
        except GoogleAdsException as e:
            logger.error(f"Google Ads API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching Google Ads data: {str(e)}")
            raise
    
    def fetch_account_performance(self, start_date: str, end_date: str) -> Dict:
        """
        Fetch account-level performance summary
        """
        if not self.client:
            return {
                'customer_id': self.customer_id,
                'status': 'not_configured',
                'message': 'Google Ads API not configured'
            }
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc
                FROM customer
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            search_request = self.client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = self.customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            # Aggregate results
            total_impressions = 0
            total_clicks = 0
            total_cost = 0
            total_conversions = 0
            
            for row in response:
                total_impressions += row.metrics.impressions
                total_clicks += row.metrics.clicks
                total_cost += row.metrics.cost_micros
                total_conversions += row.metrics.conversions
            
            return {
                'customer_id': self.customer_id,
                'status': 'connected',
                'date_range': {'start': start_date, 'end': end_date},
                'summary': {
                    'total_impressions': total_impressions,
                    'total_clicks': total_clicks,
                    'total_cost': total_cost / 1000000,  # Convert from micros
                    'total_conversions': total_conversions,
                    'average_ctr': (total_clicks / max(total_impressions, 1)) * 100,
                    'average_cpc': (total_cost / 1000000) / max(total_clicks, 1),
                    'cost_per_conversion': (total_cost / 1000000) / max(total_conversions, 1)
                }
            }
            
        except Exception as e:
            return {
                'customer_id': self.customer_id,
                'status': 'error',
                'error': str(e)
            }
    
    def fetch_data_for_date_range(self, days_back: int = 7) -> List[Dict]:
        """
        Convenience method to fetch data for the last N days
        """
        end_date = datetime.now().date() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=days_back)
        
        return self.fetch_campaign_performance(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
    
    def get_account_info(self) -> Dict:
        """Get basic information about the connected account"""
        if not self.client:
            return {
                'customer_id': self.customer_id,
                'status': 'not_configured',
                'message': 'Google Ads client not initialized. Check configuration.'
            }
        
        try:
            # Test connection with a simple query
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            account_data = self.fetch_account_performance(yesterday, yesterday)
            
            return {
                'customer_id': self.customer_id,
                'status': 'connected',
                'account_summary': account_data.get('summary', {})
            }
        except Exception as e:
            return {
                'customer_id': self.customer_id,
                'status': 'error',
                'error': str(e)
            }