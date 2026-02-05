"""Shared audit logging utility for MongoDB."""

from datetime import datetime
from typing import Any, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from shared.enums import AuditEventType, AuditEventStatus


class AuditLogger:
    """
    Audit logger for tracking system events in MongoDB.
    
    Usage:
        audit_logger = AuditLogger(mongodb_uri)
        await audit_logger.log_event(
            event_type=AuditEventType.AUTH_LOGIN,
            user_id="uuid",
            action="login_success",
            ip_address="192.168.1.1"
        )
    """
    
    def __init__(self, mongodb_uri: str, database_name: str = "photo_platform"):
        """
        Initialize audit logger.
        
        Args:
            mongodb_uri: MongoDB connection string
            database_name: Database name (default: photo_platform)
        """
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(mongodb_uri)
        self.db: AsyncIOMotorDatabase = self.client[database_name]
        self.collection = self.db.audit_logs
    
    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        action: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: AuditEventStatus = AuditEventStatus.SUCCESS
    ) -> str:
        """
        Log an audit event to MongoDB.
        
        Args:
            event_type: Type of event (from AuditEventType enum)
            user_id: User UUID (optional)
            username: Username (optional)
            action: Action description (optional)
            ip_address: IP address (optional)
            user_agent: User agent string (optional)
            metadata: Additional metadata (optional)
            status: Event status (default: success)
        
        Returns:
            Inserted document ID as string
        
        Example:
            >>> await audit_logger.log_event(
            ...     event_type=AuditEventType.AUTH_LOGIN,
            ...     user_id="uuid-123",
            ...     username="johndoe",
            ...     action="login_success",
            ...     ip_address="192.168.1.100",
            ...     metadata={"login_method": "password"}
            ... )
        """
        log_entry = {
            "timestamp": datetime.utcnow(),
            "event_type": event_type.value,
            "user_id": user_id,
            "username": username,
            "action": action,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "metadata": metadata or {},
            "status": status.value
        }
        
        result = await self.collection.insert_one(log_entry)
        return str(result.inserted_id)
    
    async def get_user_activity(
        self,
        user_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> list:
        """
        Get activity timeline for a specific user.
        
        Args:
            user_id: User UUID
            limit: Maximum number of events to return
            skip: Number of events to skip (for pagination)
        
        Returns:
            List of audit log entries
        """
        cursor = self.collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).skip(skip).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def get_security_events(
        self,
        limit: int = 100,
        skip: int = 0
    ) -> list:
        """
        Get recent security-related events.
        
        Args:
            limit: Maximum number of events to return
            skip: Number of events to skip
        
        Returns:
            List of security audit log entries
        """
        cursor = self.collection.find(
            {"event_type": {"$regex": "^security\\."}}
        ).sort("timestamp", -1).skip(skip).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def close(self):
        """Close MongoDB connection."""
        self.client.close()
