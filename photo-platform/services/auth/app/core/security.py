"""Security utilities for password hashing and JWT tokens."""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings
from shared.enums import UserRole


settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password
    
    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> verify_password("SecurePass123!", hashed)
        True
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
    
    Returns:
        True if password matches, False otherwise
    
    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> verify_password("SecurePass123!", hashed)
        True
        >>> verify_password("WrongPass", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: UUID,
    username: str,
    role: UserRole,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User UUID
        username: Username
        role: User role
        expires_delta: Token expiration time (default: from settings)
    
    Returns:
        Encoded JWT token
    
    Example:
        >>> token = create_access_token(
        ...     user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        ...     username="johndoe",
        ...     role=UserRole.USER
        ... )
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    
    now = datetime.utcnow()
    expire = now + expires_delta
    
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role.value,
        "exp": expire,
        "iat": now,
        "jti": secrets.token_urlsafe(32),  # JWT ID for blacklisting
        "token_type": "access"
    }
    
    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def create_refresh_token(
    user_id: UUID,
    username: str,
    role: UserRole,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        user_id: User UUID
        username: Username
        role: User role
        expires_delta: Token expiration time (default: from settings)
    
    Returns:
        Encoded JWT refresh token
    
    Example:
        >>> token = create_refresh_token(
        ...     user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        ...     username="johndoe",
        ...     role=UserRole.USER
        ... )
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.refresh_token_expire_days)
    
    now = datetime.utcnow()
    expire = now + expires_delta
    
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role.value,
        "exp": expire,
        "iat": now,
        "jti": secrets.token_urlsafe(32),
        "token_type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token to decode
    
    Returns:
        Token payload as dictionary
    
    Raises:
        JWTError: If token is invalid or expired
    
    Example:
        >>> token = create_access_token(...)
        >>> payload = decode_token(token)
        >>> print(payload["sub"])  # User ID
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")


def get_token_jti(token: str) -> Optional[str]:
    """
    Extract JTI (JWT ID) from token without full validation.
    
    Useful for blacklisting tokens.
    
    Args:
        token: JWT token
    
    Returns:
        JTI string or None if not found
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False}  # Don't verify expiration
        )
        return payload.get("jti")
    except JWTError:
        return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Extract expiration time from token.
    
    Args:
        token: JWT token
    
    Returns:
        Expiration datetime or None if not found
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False}
        )
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp)
        return None
    except JWTError:
        return None
