"""Refresh token database model."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from app.core.database import Base


class RefreshToken(Base):
    """
    Refresh token model for JWT token rotation.
    
    Attributes:
        id: Unique token identifier (UUID)
        user_id: Foreign key to users table
        token: Hashed refresh token
        expires_at: Token expiration timestamp
        created_at: Token creation timestamp
        revoked: Token revocation status
    """
    
    __tablename__ = "refresh_tokens"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign key to user
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Token data
    token: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Expiration
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Revocation
    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    def __repr__(self) -> str:
        """String representation of RefreshToken."""
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.revoked})>"
