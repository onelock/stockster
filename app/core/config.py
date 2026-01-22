"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    app_name: str = "Stockster API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "stocksterdb"
    postgres_user: str = "stockster"
    postgres_password: str = "stockster123"
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()