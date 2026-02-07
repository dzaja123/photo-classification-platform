"""FastAPI dependencies for authentication and authorization."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.database import get_db
from app.core.security import decode_token
from app.core.cache import is_token_blacklisted
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from shared.enums import TokenType, UserRole
from shared.audit_logger import AuditLogger, get_audit_logger_singleton


settings = get_settings()
security = HTTPBearer()


async def get_audit_logger() -> AuditLogger:
    """
    Get audit logger instance (singleton).
    
    Returns:
        AuditLogger instance
    """
    return get_audit_logger_singleton(settings.mongodb_url)


async def get_auth_service(
    db: AsyncSession = Depends(get_db),
    audit_logger: AuditLogger = Depends(get_audit_logger)
) -> AuthService:
    """
    Get auth service instance.
    
    Args:
        db: Database session
        audit_logger: Audit logger instance
    
    Returns:
        AuthService instance
    """
    return AuthService(db, audit_logger)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
    
    Returns:
        Current user
    
    Raises:
        HTTPException: If token is invalid or user not found
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user_id": user.id}
    """
    token = credentials.credentials
    
    # Decode token
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check token type
    if payload.get("token_type") != TokenType.ACCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if token is blacklisted
    jti = payload.get("jti")
    if jti and await is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_id = UUID(payload.get("sub"))
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Args:
        user: Current user from token
    
    Returns:
        Active user
    
    Raises:
        HTTPException: If user is inactive
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory for role-based access control.
    
    Args:
        *allowed_roles: Roles allowed to access the endpoint
    
    Returns:
        Dependency function
    
    Usage:
        @app.get("/admin")
        async def admin_route(user: User = Depends(require_role(UserRole.ADMIN))):
            return {"message": "Admin access granted"}
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    
    return role_checker


async def get_client_ip(
    x_forwarded_for: Optional[str] = Header(None),
    x_real_ip: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Extract client IP address from headers.
    
    Args:
        x_forwarded_for: X-Forwarded-For header
        x_real_ip: X-Real-IP header
    
    Returns:
        Client IP address or None
    """
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return x_forwarded_for.split(",")[0].strip()
    return x_real_ip


async def get_user_agent(
    user_agent: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Extract user agent from headers.
    
    Args:
        user_agent: User-Agent header
    
    Returns:
        User agent string or None
    """
    return user_agent
