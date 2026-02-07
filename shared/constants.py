"""Shared constants across all services."""

# JWT Configuration
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# File Upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MIN_IMAGE_DIMENSION = 200
MAX_IMAGE_DIMENSION = 4096

# Rate Limiting
RATE_LIMIT_LOGIN = "5/minute"
RATE_LIMIT_REGISTER = "3/minute"
RATE_LIMIT_UPLOAD = "10/minute"
RATE_LIMIT_API = "100/minute"

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# User Roles
ROLE_USER = "user"
ROLE_ADMIN = "admin"

# Submission Status
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

# Classification Categories
CLASSIFICATION_CATEGORIES = [
    "Portrait",
    "Landscape",
    "Object",
    "Animal",
    "Food",
    "Person",
    "Building",
    "Nature"
]

# Cache TTL (seconds)
CACHE_TTL_SHORT = 60  # 1 minute
CACHE_TTL_MEDIUM = 300  # 5 minutes
CACHE_TTL_LONG = 3600  # 1 hour

# Audit Event Types
AUDIT_AUTH_LOGIN = "auth.login"
AUDIT_AUTH_LOGOUT = "auth.logout"
AUDIT_AUTH_REGISTER = "auth.register"
AUDIT_AUTH_FAILED_LOGIN = "auth.failed_login"
AUDIT_SUBMISSION_CREATED = "submission.created"
AUDIT_SUBMISSION_DELETED = "submission.deleted"
AUDIT_ADMIN_USER_DELETE = "admin.user_delete"
AUDIT_ADMIN_DATA_EXPORT = "admin.data_export"
AUDIT_SECURITY_RATE_LIMIT = "security.rate_limit"
