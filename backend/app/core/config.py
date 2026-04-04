"""
Application configuration using Pydantic Settings.
All sensitive values are loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "DisruptShield"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database — Render Postgres URL from environment
    DATABASE_URL: str

    # Environment
    ENVIRONMENT: str = "production"

    # Frontend URL for CORS
    FRONTEND_URL: str = "https://your-frontend.onrender.com"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://your-frontend.onrender.com"

    # Premium defaults
    DEFAULT_ZONE_RISK: float = 0.5
    DEFAULT_RISK_WEIGHT: float = 0.60

    # JWT Authentication
    JWT_SECRET_KEY: str = "disruptshield-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
