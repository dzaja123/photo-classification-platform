"""FastAPI dependencies for authentication in Application Service."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config import get_settings
from shared.enums import TokenType


settings = get_settings()
security = HTTPBearer()


def _decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token string

    Returns:
        Token payload dict

    Raises:
        JWTError: If token is invalid or expired
    """
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    """
    Extract and validate user ID from JWT access token.

    Args:
        credentials: HTTP Bearer token

    Returns:
        Authenticated user's UUID

    Raises:
        HTTPException: If token is invalid or not an access token
    """
    token = credentials.credentials

    try:
        payload = _decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("token_type") != TokenType.ACCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_client_ip(
    x_forwarded_for: Optional[str] = Header(None),
    x_real_ip: Optional[str] = Header(None),
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
        return x_forwarded_for.split(",")[0].strip()
    return x_real_ip
