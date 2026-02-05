"""FastAPI application entry point for Admin Service."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.database import engine
from app.core.mongodb import close_mongodb
from app.api.v1 import submissions, audit_logs, export


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Handles startup and shutdown events:
    - Startup: Initialize database connections
    - Shutdown: Close database connections
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print("Database engine initialized")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await engine.dispose()
    await close_mongodb()
    print("Connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Admin service for submissions management, filtering, and analytics",
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
)

# Include routers
app.include_router(submissions.router, prefix="/api/v1/admin", tags=["Admin - Submissions"])
app.include_router(audit_logs.router, prefix="/api/v1/admin", tags=["Admin - Audit Logs"])
app.include_router(export.router, prefix="/api/v1/admin", tags=["Admin - Export"])


@app.get("/api/v1/status", tags=["Status"])
async def get_status():
    """
    Get admin service status.
    
    Returns service information and health status.
    """
    return {
        "status": "operational",
        "service": settings.app_name,
        "version": settings.app_version,
        "features": {
            "submissions_filtering": "ready",
            "analytics": "ready",
            "audit_logs": "ready",
            "data_export": "ready"
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
