"""Submission Pydantic schemas."""

from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SubmissionCreate(BaseModel):
    """Schema for creating a submission."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Submitter's name")
    age: int = Field(..., ge=1, le=150, description="Submitter's age")
    gender: str = Field(..., min_length=1, max_length=50, description="Submitter's gender")
    location: str = Field(..., min_length=1, max_length=255, description="City/Location")
    country: str = Field(..., min_length=1, max_length=100, description="Country")


class SubmissionResponse(BaseModel):
    """Schema for submission response."""
    
    id: UUID
    user_id: UUID
    name: str
    age: int
    gender: str
    location: str
    country: str
    photo_filename: str
    photo_path: str
    photo_size: int
    photo_mime_type: str
    classification_status: str
    classification_results: Optional[List[Dict]] = None
    classification_error: Optional[str] = None
    classified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SubmissionListResponse(BaseModel):
    """Schema for paginated submission list."""
    
    total: int
    page: int
    page_size: int
    submissions: List[SubmissionResponse]
