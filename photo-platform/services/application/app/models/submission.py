"""Submission model for photo submissions."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Text, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Submission(Base):
    """
    Photo submission model.
    
    Stores information about uploaded photos and their classification results.
    """
    
    __tablename__ = "submissions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # User information
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User who submitted the photo"
    )
    
    # Personal information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Submitter's name"
    )
    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Submitter's age"
    )
    gender: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Submitter's gender"
    )
    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Submitter's location (city)"
    )
    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Submitter's country"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional description"
    )
    
    # Photo information
    photo_filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Original filename"
    )
    photo_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        unique=True,
        comment="Path in MinIO storage"
    )
    photo_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="File size in bytes"
    )
    photo_mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="MIME type (e.g., image/jpeg)"
    )
    
    # Classification results
    classification_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
        comment="Status: pending, processing, completed, failed"
    )
    classification_results: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Top-3 classification results with confidence scores"
    )
    classification_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if classification failed"
    )
    classified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When classification was completed"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When submission was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="When submission was last updated"
    )
    
    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Soft delete flag"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Submission(id={self.id}, name={self.name}, status={self.classification_status})>"
