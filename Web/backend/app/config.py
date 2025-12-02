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
    
    # Database - SQLite by default, PostgreSQL via env var on Railway
    DATABASE_URL: str = "sqlite+aiosqlite:///./ndx_users.db"
    FUND_DB_PATH: str = "./fund.db"  # Original fund database (deprecated)
    
    # Auto invest config file path
    AUTO_INVEST_CONFIG_PATH: Optional[str] = None

    # Admin bootstrap (optional)
    # If provided, the app will auto-create this admin on first start
    ADMIN_EMAIL: Optional[str] = None
    ADMIN_PASSWORD: Optional[str] = None
    ADMIN_USERNAME: Optional[str] = None
    
    @property
    def database_url_async(self) -> str:
        """Ensure DATABASE_URL uses async driver"""
        url = self.DATABASE_URL
        # Convert SQLite to async
        if url.startswith("sqlite:///") and "+aiosqlite" not in url:
            url = url.replace("sqlite:///", "sqlite+aiosqlite:///")
        # Convert PostgreSQL to async (asyncpg)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def database_url_sync(self) -> str:
        """Return sync driver URL for background scripts"""
        url = self.DATABASE_URL
        if url.startswith("sqlite+aiosqlite:///"):
            return url.replace("sqlite+aiosqlite:///", "sqlite:///", 1)
        if url.startswith("sqlite:///"):
            return url
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
        "https://ndx-git-main-yuzukiyins-projects.vercel.app",
        "https://ndx-5ymfcxnqn-yuzukiyins-projects.vercel.app",
    ]
    
    # Email (optional, for verification)
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_PORT: int = 587
    MAIL_SERVER: Optional[str] = None
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    
    @property
    def auto_invest_config_resolved(self) -> str:
        """Get auto invest config path with fallback"""
        import os
        # Try environment variable first
        if self.AUTO_INVEST_CONFIG_PATH and os.path.exists(self.AUTO_INVEST_CONFIG_PATH):
            return self.AUTO_INVEST_CONFIG_PATH
        # Fall back to local backend directory
        local_path = os.path.join(os.path.dirname(__file__), '..', 'auto_invest_setting.json')
        return os.path.abspath(local_path)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
