"""Authentication Pydantic schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from shared.enums import UserRole


class LoginRequest(BaseModel):
    """Schema for login request."""
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Username or email",
        examples=["johndoe"]
    )
    password: str = Field(
        ...,
        min_length=1,
        description="User password",
        examples=["SecurePass123!"]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "password": "SecurePass123!"
            }
        }
    }


class TokenResponse(BaseModel):
    """Schema for token response."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }
        }
    }


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    
    sub: UUID = Field(..., description="Subject (user ID)")
    username: str = Field(..., description="Username")
    role: UserRole = Field(..., description="User role")
    exp: datetime = Field(..., description="Expiration timestamp")
    iat: datetime = Field(..., description="Issued at timestamp")
    jti: str = Field(..., description="JWT ID (for blacklisting)")
    token_type: str = Field(..., description="Token type (access or refresh)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "sub": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "role": "user",
                "exp": "2026-02-05T21:15:00Z",
                "iat": "2026-02-05T21:00:00Z",
                "jti": "unique-token-id",
                "token_type": "access"
            }
        }
    }


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    
    refresh_token: str = Field(
        ...,
        description="JWT refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


class PasswordChangeRequest(BaseModel):
    """Schema for password change request."""
    
    current_password: str = Field(
        ...,
        min_length=1,
        description="Current password",
        examples=["OldPass123!"]
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="New password (min 8 chars, must include uppercase, lowercase, digit, special char)",
        examples=["NewSecurePass456!"]
    )
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """
        Validate new password strength.
        
        Same requirements as registration password.
        """
        import re
        
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "current_password": "OldPass123!",
                "new_password": "NewSecurePass456!"
            }
        }
    }


class LogoutRequest(BaseModel):
    """Schema for logout request."""
    
    refresh_token: Optional[str] = Field(
        None,
        description="Refresh token to revoke (optional)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }
