# Architecture

## System Overview

The Photo Classification Platform follows a **microservices architecture** with three backend services, a React frontend, and shared infrastructure.

```
┌─────────────┐
│  Frontend   │  React 18 + Vite 5 + TailwindCSS
│ (port 3000) │
└──────┬──────┘
       │
┌──────▼───────┐
│    Nginx     │  API Gateway / Reverse Proxy
│  (port 80)   │
└──┬───┬───┬───┘
   │   │   │
┌──▼┐ ┌▼──┐ ┌▼──┐
│Auth││App│ │Adm│  FastAPI Microservices
│8001││8002││8003│
└─┬──┘└┬──┘ └┬──┘
  │     │     │
┌─▼─────▼─────▼─┐
│  PostgreSQL 16 │  Users, Submissions
│  (port 5432)   │
└────────────────┘
┌────────────────┐
│   Redis 7.2    │  Caching, Rate Limiting, Token Blacklist
│  (port 6379)   │
└────────────────┘
┌────────────────┐
│  MongoDB 7     │  Audit Logs
│  (port 27017)  │
└────────────────┘
┌────────────────┐
│  MinIO         │  Photo Object Storage (S3-compatible)
│  (port 9000)   │
└────────────────┘
```

## Microservices

### Auth Service (port 8001)
- User registration and login
- JWT access/refresh token management
- Password hashing (bcrypt + SHA256 pre-hash)
- Rate limiting (Redis-backed)
- Audit logging to MongoDB

### Application Service (port 8002)
- Photo upload with validation
- MinIO object storage integration
- Background ML classification (ResNet50 / fallback heuristics)
- User-scoped submission CRUD

### Admin Service (port 8003)
- Admin-only endpoints (JWT role enforcement)
- Advanced filtering and search
- Analytics dashboard (aggregated statistics)
- Audit log viewer
- Data export (CSV / JSON)

## Design Patterns

| Pattern | Usage |
|---------|-------|
| Repository | Data access layer in auth and application services |
| Service Layer | Business logic separated from route handlers |
| Dependency Injection | FastAPI `Depends()` for DB sessions, auth, audit |
| Singleton | StorageClient, ImageClassifier, AuditLogger |
| Background Tasks | Async ML classification via FastAPI BackgroundTasks |

## Security Layers

1. **JWT Authentication** — Short-lived access tokens (15 min), refresh rotation (7 days)
2. **Token Blacklisting** — Redis-based JTI blacklist on logout
3. **Rate Limiting** — Per-IP Redis counters with configurable windows
4. **Input Validation** — Pydantic schemas with password strength, reserved usernames
5. **RBAC** — Admin role enforcement on admin endpoints
6. **Audit Trail** — MongoDB event log for all critical actions

## Database Choices

| Database | Purpose | Justification |
|----------|---------|---------------|
| **PostgreSQL 16** | Users, submissions, refresh tokens | ACID compliance for transactional data, JSONB support for flexible classification results, mature async driver (`asyncpg`), strong indexing (B-tree, GIN for full-text search) |
| **MongoDB 7** | Audit logs | Schema-flexible documents suit heterogeneous event types (auth, admin, security), each with different metadata shapes. TTL indexes enable automatic log rotation. Write-heavy workload benefits from MongoDB's append-optimized storage |
| **Redis 7.2** | Rate limiting, token blacklist, caching | Sub-millisecond reads for hot-path operations (every request checks rate limits and token blacklist). TTL-based expiration aligns naturally with token lifetimes and rate-limit windows |
| **MinIO** | Photo storage | S3-compatible API allows seamless migration to AWS S3 or GCS in production. Presigned URLs offload bandwidth from application servers |

## Database Schema

### PostgreSQL
- `users` — id (UUID PK), email, username, hashed_password, role, is_active, timestamps
- `refresh_tokens` — id (UUID PK), user_id (FK), token, expires_at, revoked
- `submissions` — id (UUID PK), user_id, personal info, photo metadata, classification results, timestamps, soft delete

### MongoDB
- `audit_logs` — timestamp, event_type, user_id, action, ip_address, metadata, status

### Redis
- `rate_limit:{prefix}:{path}:{ip}` — Counter with TTL
- `blacklist:{jti}` — Token blacklist entries with TTL

> **Note on Admin Service**: The Admin Service shares the same PostgreSQL database as the Application Service (read-only access to the `submissions` table). It does not have its own Alembic migrations — schema changes are managed by the Application Service. This avoids migration conflicts and enforces a clear ownership boundary.
