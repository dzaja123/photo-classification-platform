"""Submission response schemas."""

from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel


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
    total_pages: int
    submissions: List[SubmissionResponse]
    filters_applied: Optional[Dict] = None
