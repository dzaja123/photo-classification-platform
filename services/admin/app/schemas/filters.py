"""Filter schemas for submissions."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class SubmissionFilters(BaseModel):
    """
    Filters for querying submissions.

    All filters are optional and can be combined.
    """

    # Age filters
    age_min: Optional[int] = Field(None, ge=1, le=150, description="Minimum age")
    age_max: Optional[int] = Field(None, ge=1, le=150, description="Maximum age")

    # Gender filter
    gender: Optional[List[str]] = Field(None, description="List of genders to filter")

    # Location filters
    country: Optional[List[str]] = Field(None, description="List of countries")
    location: Optional[str] = Field(None, description="City/location (partial match)")

    # Classification filters
    classification_status: Optional[str] = Field(
        None, description="Classification status"
    )
    classification_result: Optional[str] = Field(
        None, description="Classification result class"
    )

    # Date filters
    date_from: Optional[datetime] = Field(None, description="Start date (inclusive)")
    date_to: Optional[datetime] = Field(None, description="End date (inclusive)")

    # Search
    search: Optional[str] = Field(None, description="Search in name, location")

    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

    # Sorting
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")
