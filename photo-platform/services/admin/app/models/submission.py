"""Submission model (read-only for Admin Service)."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Text, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Submission(Base):
    """
    Photo submission model (read-only).
    
    Admin service only reads from this table.
    """
    
    __tablename__ = "submissions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    
    # Personal information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Photo information
    photo_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    photo_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    photo_size: Mapped[int] = mapped_column(Integer, nullable=False)
    photo_mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Classification results
    classification_status: Mapped[str] = mapped_column(String(50), nullable=False)
    classification_results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    classification_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    classified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
