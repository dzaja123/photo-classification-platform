"""Shared enums across all services."""

from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    USER = "USER"
    ADMIN = "ADMIN"


class Gender(str, Enum):
    """Gender enumeration."""
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class SubmissionStatus(str, Enum):
    """Submission status enumeration."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AuditEventType(str, Enum):
    """Audit event type enumeration."""
    # Authentication
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_REGISTER = "auth.register"
    AUTH_FAILED_LOGIN = "auth.failed_login"
    AUTH_PASSWORD_CHANGE = "auth.password_change"
    AUTH_TOKEN_REFRESH = "auth.token_refresh"
    
    # Submissions
    SUBMISSION_CREATED = "submission.created"
    SUBMISSION_UPDATED = "submission.updated"
    SUBMISSION_DELETED = "submission.deleted"
    SUBMISSION_CLASSIFIED = "submission.classified"
    SUBMISSION_VIEWED = "submission.viewed"
    
    # Admin Actions
    ADMIN_USER_ROLE_CHANGE = "admin.user_role_change"
    ADMIN_USER_DELETE = "admin.user_delete"
    ADMIN_SUBMISSION_DELETE = "admin.submission_delete"
    ADMIN_DATA_EXPORT = "admin.data_export"
    ADMIN_FILTER_APPLIED = "admin.filter_applied"
    
    # Security
    SECURITY_RATE_LIMIT = "security.rate_limit"
    SECURITY_INVALID_TOKEN = "security.invalid_token"
    SECURITY_SUSPICIOUS = "security.suspicious"
    SECURITY_FILE_REJECTED = "security.file_rejected"


class AuditEventStatus(str, Enum):
    """Audit event status enumeration."""
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
