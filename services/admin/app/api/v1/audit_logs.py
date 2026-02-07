"""Audit logs endpoints."""

import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.dependencies import get_current_admin
from app.core.mongodb import get_mongodb
from app.schemas.audit_log import (
    AuditLogResponse,
    AuditLogListResponse,
    UserActivityResponse,
    SecurityEventsResponse,
)


router = APIRouter()


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    event_type: Optional[str] = Query(
        None, description="Filter by event type (auth, admin, submission, security)"
    ),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    _admin: dict = Depends(get_current_admin),
):
    """
    List audit logs with filtering.

    **Admin only endpoint** - requires admin role.

    Filters:
    - event_type: Filter by event category (auth, admin, submission, security)
    - user_id: Filter by specific user
    - date_from/date_to: Date range filter

    Returns paginated audit log entries.
    """
    collection = db.audit_logs

    # Build query
    query = {}

    if event_type:
        query["event_type"] = {"$regex": f"^{event_type}\\."}

    if user_id:
        query["user_id"] = user_id

    if date_from or date_to:
        query["timestamp"] = {}
        if date_from:
            query["timestamp"]["$gte"] = date_from
        if date_to:
            query["timestamp"]["$lte"] = date_to

    # Get total count
    total = await collection.count_documents(query)

    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    # Get logs
    cursor = collection.find(query).sort("timestamp", -1).skip(skip).limit(page_size)
    logs_data = await cursor.to_list(length=page_size)

    # Convert to response format
    logs = [
        AuditLogResponse(
            id=str(log["_id"]),
            timestamp=log.get("timestamp"),
            event_type=log.get("event_type", ""),
            user_id=log.get("user_id"),
            username=log.get("username"),
            action=log.get("action"),
            ip_address=log.get("ip_address"),
            user_agent=log.get("user_agent"),
            metadata=log.get("metadata", {}),
            status=log.get("status", "success"),
        )
        for log in logs_data
    ]

    return AuditLogListResponse(
        total=total, page=page, page_size=page_size, total_pages=total_pages, logs=logs
    )


@router.get("/audit-logs/user/{user_id}", response_model=UserActivityResponse)
async def get_user_activity(
    user_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum events to return"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    _admin: dict = Depends(get_current_admin),
):
    """
    Get activity timeline for a specific user.

    **Admin only endpoint** - requires admin role.

    Returns chronological list of user actions.
    """
    collection = db.audit_logs

    # Get total count for user
    total = await collection.count_documents({"user_id": user_id})

    # Get recent activity
    cursor = collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    logs_data = await cursor.to_list(length=limit)

    # Get username from first log
    username = logs_data[0].get("username") if logs_data else None

    # Convert to response format
    timeline = [
        AuditLogResponse(
            id=str(log["_id"]),
            timestamp=log.get("timestamp"),
            event_type=log.get("event_type", ""),
            user_id=log.get("user_id"),
            username=log.get("username"),
            action=log.get("action"),
            ip_address=log.get("ip_address"),
            user_agent=log.get("user_agent"),
            metadata=log.get("metadata", {}),
            status=log.get("status", "success"),
        )
        for log in logs_data
    ]

    return UserActivityResponse(
        user_id=user_id,
        username=username,
        total_events=total,
        activity_timeline=timeline,
    )


@router.get("/audit-logs/security", response_model=SecurityEventsResponse)
async def get_security_events(
    limit: int = Query(100, ge=1, le=500, description="Maximum events to return"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    _admin: dict = Depends(get_current_admin),
):
    """
    Get security-related events.

    **Admin only endpoint** - requires admin role.

    Returns:
    - Recent security events
    - Failed login attempts count
    - Rate limit violations
    - Invalid token attempts
    - Suspicious activity count
    """
    collection = db.audit_logs

    # Get recent security events
    cursor = (
        collection.find({"event_type": {"$regex": "^security\\."}})
        .sort("timestamp", -1)
        .limit(limit)
    )

    security_logs = await cursor.to_list(length=limit)

    # Convert to response format
    recent_events = [
        AuditLogResponse(
            id=str(log["_id"]),
            timestamp=log.get("timestamp"),
            event_type=log.get("event_type", ""),
            user_id=log.get("user_id"),
            username=log.get("username"),
            action=log.get("action"),
            ip_address=log.get("ip_address"),
            user_agent=log.get("user_agent"),
            metadata=log.get("metadata", {}),
            status=log.get("status", "success"),
        )
        for log in security_logs
    ]

    # Count specific event types
    failed_logins = await collection.count_documents(
        {"event_type": "auth.failed_login"}
    )

    rate_limits = await collection.count_documents(
        {"event_type": "security.rate_limit"}
    )

    invalid_tokens = await collection.count_documents(
        {"event_type": "security.invalid_token"}
    )

    suspicious = await collection.count_documents({"event_type": "security.suspicious"})

    return SecurityEventsResponse(
        recent_events=recent_events,
        failed_login_attempts=failed_logins,
        rate_limit_violations=rate_limits,
        invalid_token_attempts=invalid_tokens,
        suspicious_activity_count=suspicious,
    )
