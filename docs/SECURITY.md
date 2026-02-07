# Security Implementation

This document explains **what** safety rules are implemented, **where** in the codebase, and **why**.

## Authentication

### JWT Token Strategy
- **Access tokens**: 15-minute expiry, contains user ID, username, role
- **Refresh tokens**: 7-day expiry, stored in PostgreSQL with revocation support
- **Token rotation**: Each refresh issues a new access + refresh pair; old refresh token is revoked
- **JTI blacklisting**: On logout, token JTI is added to Redis with TTL matching remaining expiry

**Where**: `services/auth/app/core/security.py`, `services/auth/app/services/auth_service.py`
**Why**: Short-lived tokens limit the window of compromise. Redis blacklist ensures logout is immediate, not eventual.

### Password Security
- **Hashing**: bcrypt with SHA256 pre-hash (handles passwords > 72 bytes)
- **Strength requirements**: Min 8 chars, uppercase, lowercase, digit, special character
- **Reserved usernames**: Blocked list prevents impersonation (admin, root, system, etc.)

**Where**: `services/auth/app/schemas/auth.py` (validation), `services/auth/app/core/security.py` (hashing)
**Why**: bcrypt is intentionally slow to resist brute-force. SHA256 pre-hash avoids bcrypt's 72-byte truncation.

## Authorization

### Role-Based Access Control (RBAC)

| Role | Access |
|------|--------|
| `USER` | Own submissions (CRUD), own profile |
| `ADMIN` | All submissions (read), analytics, audit logs, export |

**Where**: `services/admin/app/api/dependencies.py` → `get_current_admin`
**Why**: Single dependency enforces admin role on every admin endpoint — no endpoint can accidentally skip the check.

## Rate Limiting

Redis-backed per-IP rate limiting with configurable windows:

| Endpoint | Limit | Why |
|----------|-------|-----|
| Registration | 3/minute | Prevents mass account creation |
| Login | 5/minute | Mitigates credential stuffing |
| Token refresh | 10/minute | Limits token abuse |
| General API | 60/minute | Prevents DoS from single IP |

Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

**Where**: `services/auth/app/api/middleware/rate_limiter.py`
**Why**: Redis counters with TTL are atomic and fast enough for the hot path (every request).

## Input Validation

| Check | Where | Why |
|-------|-------|-----|
| Pydantic schemas | All request bodies | Type-safe validation rejects malformed input before business logic |
| File MIME whitelist | Application Service upload | Prevents non-image uploads |
| Extension whitelist | Application Service upload | Defense-in-depth alongside MIME check |
| 10 MB size limit | Application Service upload | Prevents storage abuse |
| Parameterized queries | SQLAlchemy ORM | Prevents SQL injection by design |

## Audit Logging

All security-relevant events are logged to MongoDB:
- Login / logout / failed login
- Registration
- Password changes
- Rate limit violations
- Invalid token attempts
- Admin actions (export, filter)

**Where**: `shared/audit_logger.py` → `AuditLogger` class, called from service layers
**Why**: MongoDB's schema flexibility handles different event types with varying metadata shapes. Separate from PostgreSQL to avoid write contention on the transactional database.

## Infrastructure Security

| Measure | Where | Why |
|---------|-------|-----|
| Non-root user | All production Dockerfiles (`USER app`) | Limits blast radius if container is compromised |
| Multi-stage builds | All Dockerfiles | Smaller images, no build tools in production |
| CORS allowlist | All services (`cors_origins` config) | Prevents cross-origin requests from untrusted domains |
| Secrets via env vars | `docker-compose.dev.yml`, `k8s/secrets.yaml` | Never hardcoded in source |
| Health checks | All services (`/health`) | Enables container orchestrator to restart unhealthy instances |
| Network isolation | Docker bridge network | Services communicate internally, not exposed to host unnecessarily |
