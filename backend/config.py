from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./equity_valuation.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Settings
    api_v1_str: str = "/api/v1"
    project_name: str = "Equity Valuation System"
    
    # External APIs
    yahoo_finance_timeout: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()