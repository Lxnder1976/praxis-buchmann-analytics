from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class AnalyticsData(Base):
    __tablename__ = "analytics_data"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(String, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Traffic Metrics
    sessions = Column(Integer, default=0)
    users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    page_views = Column(Integer, default=0)
    
    # Engagement Metrics
    average_session_duration = Column(Float, default=0.0)
    bounce_rate = Column(Float, default=0.0)
    pages_per_session = Column(Float, default=0.0)
    
    # Conversion Metrics
    conversions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    
    # Traffic Sources
    organic_sessions = Column(Integer, default=0)
    direct_sessions = Column(Integer, default=0)
    referral_sessions = Column(Integer, default=0)
    social_sessions = Column(Integer, default=0)
    
    # Additional Data (JSON format for flexibility)
    raw_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SearchConsoleData(Base):
    __tablename__ = "search_console_data"
    
    id = Column(Integer, primary_key=True, index=True)
    site_url = Column(String, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Search Performance
    clicks = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)  # Click-through rate
    position = Column(Float, default=0.0)  # Average position
    
    # Query/Page specific data (if applicable)
    query = Column(String, nullable=True)
    page = Column(String, nullable=True)
    
    # Raw data
    raw_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GoogleAdsData(Base):
    __tablename__ = "google_ads_data"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, nullable=False, index=True)
    campaign_id = Column(String, nullable=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Performance Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Float, default=0.0)
    cost_micros = Column(Integer, default=0)  # Cost in micro currency units
    
    # Calculated Metrics
    ctr = Column(Float, default=0.0)
    cpc = Column(Float, default=0.0)  # Cost per click
    conversion_rate = Column(Float, default=0.0)
    cost_per_conversion = Column(Float, default=0.0)
    
    # Campaign Info
    campaign_name = Column(String, nullable=True)
    campaign_status = Column(String, nullable=True)
    
    # Raw data
    raw_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database Engine and Session
def get_database_url():
    from app.config.settings import settings
    return settings.database_url

def create_db_engine():
    database_url = get_database_url()
    if database_url.startswith("sqlite"):
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(database_url)
    return engine

def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """Get database session"""
    engine = create_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()