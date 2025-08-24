from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@postgres:5432/datainsider"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379"
    
    # JWT
    JWT_SECRET: str = "dev-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8080", "http://frontend:8080"]
    
    # File upload
    MAX_FILE_SIZE: int = 524288000  # 500MB
    UPLOAD_DIR: str = "/tmp/uploads"
    
    class Config:
        env_file = ".env"


settings = Settings()