from fastapi import FastAPI, HTTPException
from app.config.settings import settings
from app.services.data_persistence import DataPersistenceService
from app.services.google_analytics import GoogleAnalyticsService
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Analytics Data Service",
    description="Service for fetching and persisting Google Analytics data",
    version="1.0.0"
)

# Initialize services
data_service = DataPersistenceService()
ga_service = GoogleAnalyticsService()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Analytics Data Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check Google Analytics connection
        ga_info = ga_service.get_property_info()
        
        # Check database
        db_summary = data_service.get_stored_data_summary()
        
        return {
            "status": "healthy",
            "google_analytics": ga_info,
            "database": db_summary,
            "settings": {
                "environment": settings.environment,
                "property_id": settings.google_analytics_property_id,
                "database_url": settings.database_url.split("://")[0] + "://***"  # Hide sensitive parts
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/fetch-data")
async def fetch_analytics_data(days_back: int = 7):
    """
    Manually trigger data fetching from Google Analytics
    
    Args:
        days_back: Number of days to fetch data for (default: 7)
    """
    try:
        if days_back < 1 or days_back > 365:
            raise HTTPException(
                status_code=400, 
                detail="days_back must be between 1 and 365"
            )
        
        logger.info(f"Manual data fetch triggered for {days_back} days")
        result = data_service.fetch_and_store_recent_data(days_back)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['message'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in fetch_analytics_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data-summary")
async def get_data_summary():
    """Get summary of stored analytics data"""
    try:
        summary = data_service.get_stored_data_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting data summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup-data")
async def cleanup_old_data(days_to_keep: int = 90):
    """
    Clean up old data from database
    
    Args:
        days_to_keep: Number of days of data to keep (default: 90)
    """
    try:
        if days_to_keep < 7:
            raise HTTPException(
                status_code=400, 
                detail="days_to_keep must be at least 7"
            )
        
        deleted_count = data_service.cleanup_old_data(days_to_keep)
        
        return {
            "status": "success",
            "message": f"Cleaned up {deleted_count} old records",
            "records_deleted": deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in cleanup_old_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )