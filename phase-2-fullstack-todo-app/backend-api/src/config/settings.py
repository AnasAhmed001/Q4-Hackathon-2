"""
Application settings and configuration management
"""
from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database - Use Neon with asyncpg driver
    database_url: str = os.getenv("DATABASE_URL", "") or os.getenv("NEON_DATABASE_URL", "")
    
    # Better Auth Secret (for JWT validation)
    better_auth_secret: str = os.getenv("BETTER_AUTH_SECRET", "")
    
    # JWT Configuration (Legacy)
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # API Configuration
    api_prefix: str = os.getenv("API_PREFIX", "/api")
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    @model_validator(mode="after")
    def normalize_database_url(self) -> "Settings":
        """Ensure the database URL uses the asyncpg driver and correct ssl flag."""
        url = self.database_url or ""

        # Accept postgres:// and postgresql:// and coerce to asyncpg
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]

        if url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        if "sslmode=require" in url and "ssl=" not in url:
            url = url.replace("sslmode=require", "ssl=require")

        self.database_url = url
        return self
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
