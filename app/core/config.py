"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from pydantic import SecretStr
from dotenv import load_dotenv
# import os

load_dotenv()

class Settings(BaseSettings):
    # Application
    # API
    app_name: str = "Stockster API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    
    database_type: str  ="postgresql" # Default to PostgreSQL
    postgres_user: str
    postgres_password: SecretStr
    postgres_host: str
    postgres_port: int
    postgres_db: str
    
    # CORS
    cors_origins: list = ["*"]  
        
settings = Settings()