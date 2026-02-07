"""Configuration settings for Admin Service."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Admin Service settings with validation.

    Loads configuration from environment variables and .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application
    app_name: str = Field(
        default="Photo Platform Admin Service", description="Application name"
    )
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # Database
    database_url: str = Field(..., description="PostgreSQL database URL")

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    redis_max_connections: int = Field(
        default=10, ge=1, le=100, description="Maximum Redis connections"
    )

    # MongoDB
    mongodb_url: str = Field(
        default="mongodb://admin:admin@localhost:27017",
        description="MongoDB connection URL",
    )
    mongodb_database: str = Field(
        default="photo_platform", description="MongoDB database name"
    )

    # Auth Service
    auth_service_url: str = Field(
        default="http://localhost:8001", description="Auth service URL"
    )
    jwt_secret_key: str = Field(
        ..., min_length=32, description="JWT secret key (must match Auth Service)"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")

    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Allowed CORS origins (comma-separated)",
    )
    cors_allow_credentials: bool = Field(
        default=True, description="Allow credentials in CORS"
    )

    # Export
    export_max_records: int = Field(
        default=10000, ge=1, le=100000, description="Maximum records for export"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings instance
    """
    return Settings()
