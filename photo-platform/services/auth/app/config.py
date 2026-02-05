"""Application configuration using Pydantic settings."""

from functools import lru_cache
from typing import List
from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic BaseSettings for type-safe configuration with validation.
    Settings are cached using lru_cache for performance.
    """
    
    # Application
    app_name: str = Field(default="Photo Platform Auth Service")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # Database
    database_url: PostgresDsn = Field(
        description="PostgreSQL connection URL"
    )
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=20)
    
    # Redis
    redis_url: RedisDsn = Field(
        description="Redis connection URL"
    )
    redis_max_connections: int = Field(default=10)
    
    # MongoDB
    mongodb_url: str = Field(
        description="MongoDB connection URL for audit logs"
    )
    
    # JWT
    jwt_secret_key: str = Field(
        description="Secret key for JWT signing (use openssl rand -hex 32)"
    )
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=15)
    refresh_token_expire_days: int = Field(default=7)
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )
    cors_allow_credentials: bool = Field(default=True)
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_login: str = Field(default="5/minute")
    rate_limit_register: str = Field(default="3/minute")
    
    # Password Requirements
    password_min_length: int = Field(default=8)
    password_require_uppercase: bool = Field(default=True)
    password_require_lowercase: bool = Field(default=True)
    password_require_digit: bool = Field(default=True)
    password_require_special: bool = Field(default=True)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are loaded only once.
    
    Returns:
        Settings instance
    """
    return Settings()
