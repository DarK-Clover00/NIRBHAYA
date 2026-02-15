"""
Configuration management for NIRBHAYA application
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis Configuration
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 50
    
    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Google APIs
    GOOGLE_MAPS_API_KEY: str
    GOOGLE_PLACES_API_KEY: str
    GOOGLE_STREET_VIEW_API_KEY: str
    
    # Government System Integration
    GOVERNMENT_API_URL: str
    GOVERNMENT_API_KEY: str
    GOVERNMENT_API_SECRET: str
    
    # SMS/Push Notifications
    SMS_PROVIDER_API_KEY: Optional[str] = None
    PUSH_NOTIFICATION_KEY: Optional[str] = None
    
    # Cloud Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: str = "nirbhaya-evidence"
    AWS_REGION: str = "us-east-1"
    
    # Application Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Performance Settings
    LOCATION_PING_TTL: int = 60
    ROUTE_CACHE_TTL: int = 3600
    CRIME_DATA_CACHE_TTL: int = 86400
    CROWD_ZONE_TTL: int = 120
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
