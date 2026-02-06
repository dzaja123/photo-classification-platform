"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from jose import JWTError

from app.config import get_settings
from app.core.database import engine
from app.core.cache import close_redis
from app.middleware.error_handler import (
    validation_exception_handler,
    integrity_error_handler,
    jwt_error_handler,
    generic_exception_handler
)
from app.middleware.rate_limit import add_rate_limit_headers


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
    print("Redis connection pool ready")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await engine.dispose()
    await close_redis()
    print("Connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Authentication and user management service",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add rate limit headers middleware
app.middleware("http")(add_rate_limit_headers)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(JWTError, jwt_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
from app.api.v1 import auth, users

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])


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
