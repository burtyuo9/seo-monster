"""
SEO Monster - Configuration
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "SEO Monster"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # Paths
    BASE_DIR: Path = Path("/home/ubuntu/seo_monster")
    DATA_DIR: Path = BASE_DIR / "backend" / "data"
    
    # API Keys
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    
    # Database (for future use)
    DATABASE_URL: str = "sqlite:///./seo_monster.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
