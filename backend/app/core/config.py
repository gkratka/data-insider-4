from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql://user:password@localhost/data_intelligence_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Anthropic Claude API
    anthropic_api_key: Optional[str] = None
    claude_model: str = "claude-3-sonnet-20240229"
    claude_max_tokens: int = 4000
    claude_temperature: float = 0.1
    
    # File upload
    upload_directory: str = "uploads"
    max_file_size: int = 500 * 1024 * 1024  # 500MB
    
    # Rate limiting
    rate_limit_requests_per_minute: int = 100
    
    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()