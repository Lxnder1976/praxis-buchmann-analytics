from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Configuration
    environment: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    
    # Google Analytics Configuration
    google_analytics_property_id: Optional[str] = None
    google_application_credentials: Optional[str] = None
    
    # Google Search Console Configuration
    google_search_console_site_url: Optional[str] = None
    
    # Google Ads Configuration
    google_ads_customer_id: Optional[str] = None
    google_ads_config_path: Optional[str] = None
    
    # Database Configuration
    database_url: str = "sqlite:///./analytics.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()