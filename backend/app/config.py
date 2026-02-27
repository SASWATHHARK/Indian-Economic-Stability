"""
Application configuration via environment variables.
Production-ready: supports Render, Railway, Supabase/Neon.
"""
import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Central config. Override via env vars or .env file."""

    # App
    APP_NAME: str = "Economic Stability API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database (SQLite for demo; PostgreSQL for production)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./economic_stability.db"
    )
    # Render/Neon often provide postgres:// -> use async with sqlalchemy 2.0
    # For SQLite we use sync engine

    # Cache (seconds)
    MARKET_CACHE_TTL: int = 86400   # 1 day
    STABILITY_CACHE_TTL: int = 300  # 5 min

    # Scheduler (daily refresh at 6:00 AM IST approx = 00:30 UTC for IST+5:30)
    SCHEDULER_ENABLED: bool = True
    DAILY_REFRESH_CRON: str = "30 0 * * *"  # 00:30 UTC daily

    # Logging
    LOG_LEVEL: str = "INFO"

    # Offline fallback
    OFFLINE_FALLBACK_ENABLED: bool = True
    DEMO_MODE_WHEN_OFFLINE: bool = True
    SAMPLE_DATA_SEMI_DYNAMIC: bool = False  # ±0.5% random variation on sample
    # Skip live APIs entirely when True – instant load, no timeouts (set via FORCE_SAMPLE_DATA=1)
    FORCE_SAMPLE_DATA: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
