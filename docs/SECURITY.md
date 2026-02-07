# Security Implementation

## Authentication

### JWT Token Strategy
- **Access tokens**: 15-minute expiry, contains user ID, username, role
- **Refresh tokens**: 7-day expiry, stored in PostgreSQL with revocation support
- **Token rotation**: Each refresh issues a new access + refresh pair; old refresh token is revoked
- **JTI blacklisting**: On logout, token JTI is added to Redis with TTL matching remaining expiry

### Password Security
- **Hashing**: bcrypt with SHA256 pre-hash (handles passwords > 72 bytes)
- **Strength requirements**: Min 8 chars, uppercase, lowercase, digit, special character
- **Reserved usernames**: Blocked list prevents impersonation (admin, root, system, etc.)

## Authorization

### Role-Based Access Control (RBAC)
| Role | Access |
|------|--------|
| `USER` | Own submissions (CRUD), own profile |
| `ADMIN` | All submissions (read), analytics, audit logs, export |

Admin role is enforced via `get_current_admin` dependency on every admin endpoint.

## Rate Limiting

Redis-backed per-IP rate limiting with configurable windows:

| Endpoint | Limit |
|----------|-------|
| Registration | 3/minute |
| Login | 5/minute |
| Token refresh | 10/minute |
| General API | 60/minute |

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## Input Validation

- All request bodies validated via Pydantic schemas
- File uploads: MIME type whitelist (image/*), extension whitelist, max 10 MB
- SQL injection prevented by SQLAlchemy ORM parameterized queries
- XSS prevention via string sanitization utilities

## Audit Logging

All security-relevant events are logged to MongoDB:
- Login / logout / failed login
- Registration
- Password changes
- Rate limit violations
- Invalid token attempts
- Admin actions (export, filter)

## Infrastructure Security

- **Docker**: Non-root user in production images, multi-stage builds
- **CORS**: Configured allowed origins (not wildcard in production)
- **Secrets**: Environment variables, never hardcoded
- **Health checks**: All services expose `/health` endpoint
- **Network isolation**: Docker network separates services from host
