"""Analytics schemas."""

from typing import Dict, List
from pydantic import BaseModel


class AgeDistribution(BaseModel):
    """Age distribution data."""
    range: str
    count: int


class AnalyticsResponse(BaseModel):
    """
    Analytics dashboard response.
    
    Contains aggregated statistics for the admin dashboard.
    """
    
    # Overall stats
    total_submissions: int
    total_users: int
    submissions_today: int
    submissions_this_week: int
    submissions_this_month: int
    
    # By gender
    by_gender: Dict[str, int]
    
    # By country (top 10)
    by_country: Dict[str, int]
    
    # By classification result (top 10)
    by_classification: Dict[str, int]
    
    # By status
    by_status: Dict[str, int]
    
    # Age distribution
    age_distribution: List[AgeDistribution]
    
    # Average classification confidence
    avg_confidence: float
