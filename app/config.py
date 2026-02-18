"""
Application Configuration
"""
import os
from typing import Optional

class Settings:
    """Application settings class"""
    
    # Project information
    PROJECT_NAME: str = "Job Aggregator"
    VERSION: str = "0.1.0"
    
    # Data source configuration
    DEFAULT_COUNTRY: str = "Germany"
    DEFAULT_JOB_KEYWORD: str = "software developer"
    
    # Data directories
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    RAW_DATA_DIR: str = os.path.join(DATA_DIR, "raw")
    NORMALIZED_DATA_DIR: str = os.path.join(DATA_DIR, "normalized")
    
    # Database configuration (for future use)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Data source URLs
    STACKOVERFLOW_JOBS_FEED: str = "https://stackoverflow.com/jobs/feed"
    ARBEITNOW_API: str = "https://arbeitnow.com/api/job-board-api"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure data directories exist"""
        os.makedirs(cls.RAW_DATA_DIR, exist_ok=True)
        os.makedirs(cls.NORMALIZED_DATA_DIR, exist_ok=True)


# Create global settings instance
settings = Settings()
settings.ensure_directories()

