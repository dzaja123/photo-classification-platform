"""FastAPI application entry point for Application Service."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.database import engine

from app.api.v1 import submissions

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Handles startup and shutdown events:
    - Startup: Initialize database connections
    - Shutdown: Close database connections
    """
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    
    yield
    
    logger.info("Shutting down")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Photo upload and classification service with ML",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(submissions.router, prefix="/api/v1/submissions", tags=["Submissions"])


@app.get("/api/v1/status", tags=["Status"])
async def get_status():
    """
    Get application service status.
    
    Returns service information and health status.
    """
    return {
        "status": "operational",
        "service": settings.app_name,
        "version": settings.app_version,
        "features": {
            "photo_upload": "ready",
            "ml_classification": "pending",
            "storage": "minio"
        }
    }


@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint for load balancers."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version
        }
    )


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "disabled"
    }
