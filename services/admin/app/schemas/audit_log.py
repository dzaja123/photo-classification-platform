"""Audit log schemas."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Single audit log entry."""

    id: str = Field(..., description="MongoDB ObjectId as string")
    timestamp: datetime
    event_type: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    action: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str = "success"


class AuditLogListResponse(BaseModel):
    """Paginated audit log list."""

    total: int
    page: int
    page_size: int
    total_pages: int
    logs: List[AuditLogResponse]


class UserActivityResponse(BaseModel):
    """User activity timeline."""

    user_id: str
    username: Optional[str] = None
    total_events: int
    activity_timeline: List[AuditLogResponse]


class SecurityEventsResponse(BaseModel):
    """Security events summary."""

    recent_events: List[AuditLogResponse]
    failed_login_attempts: int
    rate_limit_violations: int
    invalid_token_attempts: int
    suspicious_activity_count: int
