"""Configuration settings for Application Service."""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with validation.
    
    Loads configuration from environment variables and .env file.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(
        default="Photo Platform Application Service",
        description="Application name"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )
    
    # Database
    database_url: str = Field(
        ...,
        description="PostgreSQL database URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    redis_max_connections: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum Redis connections"
    )
    
    # MinIO
    minio_endpoint: str = Field(
        default="localhost:9000",
        description="MinIO endpoint"
    )
    minio_access_key: str = Field(
        default="minioadmin",
        description="MinIO access key"
    )
    minio_secret_key: str = Field(
        default="minioadmin",
        description="MinIO secret key"
    )
    minio_bucket_name: str = Field(
        default="photos",
        description="MinIO bucket name"
    )
    minio_secure: bool = Field(
        default=False,
        description="Use HTTPS for MinIO"
    )
    
    # Auth Service
    auth_service_url: str = Field(
        default="http://localhost:8001",
        description="Auth service URL"
    )
    jwt_secret_key: str = Field(
        ...,
        min_length=32,
        description="JWT secret key (must match Auth Service)"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    
    # MongoDB
    mongodb_url: str = Field(
        default="mongodb://admin:admin@localhost:27017",
        description="MongoDB connection URL"
    )
    
    # File Upload
    max_file_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum file size in MB"
    )
    allowed_extensions: str = Field(
        default="jpg,jpeg,png,gif,webp",
        description="Allowed file extensions (comma-separated)"
    )
    
    # ML Model
    model_path: str = Field(
        default="app/ml/models/mobilenet_v2.tflite",
        description="Path to TensorFlow Lite model"
    )
    labels_path: str = Field(
        default="app/ml/models/imagenet_labels.txt",
        description="Path to ImageNet labels file"
    )
    
    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Allowed CORS origins (comma-separated)"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed extensions as list."""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings instance
    """
    return Settings()
