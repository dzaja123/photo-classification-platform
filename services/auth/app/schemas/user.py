"""User Pydantic schemas with validation."""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from shared.enums import UserRole


# Reserved usernames that cannot be used
RESERVED_USERNAMES = {
    "admin", "administrator", "root", "system", "api", "auth",
    "user", "guest", "public", "private", "test", "demo",
    "support", "help", "info", "contact", "webmaster",
    "moderator", "mod", "staff", "team"
}


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(
        ...,
        description="User email address (RFC 5322 compliant)",
        examples=["user@example.com"]
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Username (3-30 characters, alphanumeric and underscore)",
        examples=["johndoe"]
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="User's full name",
        examples=["John Doe"]
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validate username format and check reserved names.
        
        Rules:
        - Only alphanumeric characters and underscores
        - Cannot be a reserved username
        - Case-insensitive check
        """
        # Check format
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError(
                "Username must contain only letters, numbers, and underscores"
            )
        
        # Check reserved names
        if v.lower() in RESERVED_USERNAMES:
            raise ValueError(
                f"Username '{v}' is reserved and cannot be used"
            )
        
        return v.lower()  # Store as lowercase
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize full name."""
        if v is None:
            return v
        
        # Strip whitespace
        v = v.strip()
        
        # Check if empty after stripping
        if not v:
            return None
        
        # Remove multiple spaces
        v = re.sub(r'\s+', ' ', v)
        
        return v


class UserCreate(UserBase):
    """Schema for user registration."""
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 chars, must include uppercase, lowercase, digit, special char)",
        examples=["SecurePass123!"]
    )
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength.
        
        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
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


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="User's full name"
    )
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize full name."""
        if v is None:
            return v
        
        v = v.strip()
        if not v:
            return None
        
        v = re.sub(r'\s+', ' ', v)
        return v


class UserResponse(BaseModel):
    """Schema for user response (public data)."""
    
    id: UUID = Field(..., description="User unique identifier")
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Account active status")
    is_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "john@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "role": "user",
                "is_active": True,
                "is_verified": True,
                "created_at": "2026-02-05T20:00:00Z",
                "last_login": "2026-02-05T21:00:00Z"
            }
        }
    }


class UserInDB(UserResponse):
    """Schema for user in database (includes sensitive data)."""
    
    hashed_password: str = Field(..., description="Bcrypt hashed password")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True
    }
