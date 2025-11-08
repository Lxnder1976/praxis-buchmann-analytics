from sqlalchemy.orm import Session
from app.models.database import AnalyticsData, get_db_session, create_db_engine, create_tables
from app.services.google_analytics import GoogleAnalyticsService
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class DataPersistenceService:
    """Service for persisting analytics data to database"""
    
    def __init__(self):
        self.ga_service = GoogleAnalyticsService()
        # Ensure database tables exist
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables"""
        try:
            engine = create_db_engine()
            create_tables(engine)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def store_analytics_data(self, analytics_data: List[Dict]) -> int:
        """
        Store Google Analytics data in database
        
        Args:
            analytics_data: List of analytics data dictionaries
            
        Returns:
            Number of records stored
        """
        session = get_db_session()
        stored_count = 0
        
        try:
            for record in analytics_data:
                # Check if record already exists for this date and property
                existing = session.query(AnalyticsData).filter(
                    AnalyticsData.property_id == record['property_id'],
                    AnalyticsData.date == record['date']
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in record.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    logger.debug(f"Updated existing record for {record['date']}")
                else:
                    # Create new record
                    new_record = AnalyticsData(**record)
                    session.add(new_record)
                    stored_count += 1
                    logger.debug(f"Created new record for {record['date']}")
            
            session.commit()
            logger.info(f"Successfully stored/updated {len(analytics_data)} analytics records")
            return stored_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing analytics data: {str(e)}")
            raise
        finally:
            session.close()
    
    def fetch_and_store_recent_data(self, days_back: int = 7) -> Dict:
        """
        Fetch recent data from Google Analytics and store it in database
        
        Args:
            days_back: Number of days to fetch data for
            
        Returns:
            Summary of the operation
        """
        try:
            logger.info(f"Fetching Google Analytics data for last {days_back} days")
            
            # Fetch data from Google Analytics
            analytics_data = self.ga_service.fetch_data_for_date_range(days_back)
            
            if not analytics_data:
                return {
                    'status': 'warning',
                    'message': 'No data received from Google Analytics',
                    'records_processed': 0
                }
            
            # Store in database
            stored_count = self.store_analytics_data(analytics_data)
            
            return {
                'status': 'success',
                'message': f'Successfully processed {len(analytics_data)} records',
                'records_processed': len(analytics_data),
                'new_records': stored_count,
                'updated_records': len(analytics_data) - stored_count,
                'date_range': {
                    'start': analytics_data[0]['date'].isoformat(),
                    'end': analytics_data[-1]['date'].isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in fetch_and_store_recent_data: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'records_processed': 0
            }
    
    def get_stored_data_summary(self) -> Dict:
        """Get summary of stored analytics data"""
        session = get_db_session()
        
        try:
            # Get basic statistics
            total_records = session.query(AnalyticsData).count()
            
            if total_records == 0:
                return {
                    'total_records': 0,
                    'date_range': None,
                    'properties': []
                }
            
            # Get date range
            oldest_record = session.query(AnalyticsData).order_by(AnalyticsData.date.asc()).first()
            newest_record = session.query(AnalyticsData).order_by(AnalyticsData.date.desc()).first()
            
            # Get unique properties
            properties = session.query(AnalyticsData.property_id).distinct().all()
            
            return {
                'total_records': total_records,
                'date_range': {
                    'start': oldest_record.date.isoformat() if oldest_record else None,
                    'end': newest_record.date.isoformat() if newest_record else None
                },
                'properties': [prop[0] for prop in properties],
                'last_updated': newest_record.updated_at.isoformat() if newest_record else None
            }
            
        except Exception as e:
            logger.error(f"Error getting stored data summary: {str(e)}")
            return {
                'total_records': 0,
                'date_range': None,
                'properties': [],
                'error': str(e)
            }
        finally:
            session.close()
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> int:
        """
        Remove old data from database
        
        Args:
            days_to_keep: Number of days of data to keep
            
        Returns:
            Number of records deleted
        """
        session = get_db_session()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            deleted_count = session.query(AnalyticsData).filter(
                AnalyticsData.date < cutoff_date
            ).delete()
            
            session.commit()
            logger.info(f"Cleaned up {deleted_count} old records")
            return deleted_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error cleaning up old data: {str(e)}")
            raise
        finally:
            session.close()