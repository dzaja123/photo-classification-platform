"""FastAPI dependencies for authentication and authorization in Admin Service."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config import get_settings
from shared.enums import TokenType, UserRole


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
        algorithms=[settings.jwt_algorithm],
    )


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate JWT and enforce admin role.

    Returns:
        Token payload dict with at least 'sub', 'username', 'role'

    Raises:
        HTTPException 401: Invalid or missing token
        HTTPException 403: Token is valid but user is not an admin
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

    role = payload.get("role", "")
    if role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return payload
