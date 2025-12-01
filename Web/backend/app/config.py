"""Configuration settings for the application"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "NDX Fund Manager"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password requirements
    PASSWORD_MIN_LENGTH: int = 8
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ndx_users.db"
    FUND_DB_PATH: str = "../../../fund.db"  # Original fund database
    
    # PostgreSQL support (Render uses DATABASE_URL env var)
    # If DATABASE_URL starts with postgres://, it's PostgreSQL
    @property
    def is_postgres(self) -> bool:
        return self.DATABASE_URL.startswith("postgres")
    
    @property
    def async_database_url(self) -> str:
        """Get async database URL"""
        if self.is_postgres:
            # Replace postgres:// with postgresql+asyncpg://
            return self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
        return self.DATABASE_URL
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://*.vercel.app",  # Vercel部署域名
    ]
    
    # Email (optional, for verification)
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_PORT: int = 587
    MAIL_SERVER: Optional[str] = None
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
