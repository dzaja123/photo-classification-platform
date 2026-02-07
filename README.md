# Photo Classification Platform

A cloud-deployable, microservices-based platform where users register, upload photos with metadata, and receive ML classification results. An admin panel provides filtering, search, analytics, and audit logging.

## Architecture

![System Architecture](diagrams/system-architecture.png)

### Microservices (3 Backend Services + Frontend)

| Service | Port | Responsibility |
|---------|------|----------------|
| **Auth Service** | 8001 | Registration, login, JWT tokens, profile management |
| **Application Service** | 8002 | Photo upload, MinIO storage, ML classification |
| **Admin Service** | 8003 | Admin panel, filtering, analytics, audit logs, export |
| **Frontend** | 3000 | React SPA served via Nginx |

### Data Flow

![Data Flow](diagrams/data-flow.png)

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, Python 3.11, async/await |
| **Databases** | PostgreSQL 16 (users, submissions), MongoDB 7 (audit logs), Redis 7.2 (rate limiting, token blacklist) |
| **Storage** | MinIO (S3-compatible object storage) |
| **ML** | ResNet50 (Keras) with fallback heuristic classifier |
| **Frontend** | React 18 + Vite 5 + TailwindCSS |
| **Gateway** | Nginx reverse proxy |
| **Infrastructure** | Docker, Kubernetes, GitHub Actions CI/CD |

### Database Justification

| Database | Purpose | Why |
|----------|---------|-----|
| **PostgreSQL 16** | Users, submissions, refresh tokens | ACID transactions, UUID support, JSONB for classification results, async driver (`asyncpg`), B-tree + GIN indexes |
| **MongoDB 7** | Audit logs | Schema-flexible documents for heterogeneous event types, TTL indexes for log rotation, append-optimized writes |
| **Redis 7.2** | Rate limiting, token blacklist | Sub-millisecond reads on every request, TTL-based expiration matches token lifetimes |
| **MinIO** | Photo storage | S3-compatible API for seamless migration to AWS S3 or GCS in production |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- Python 3.11+ (for local development without Docker)
- Node.js 18+ (for frontend development without Docker)

### Docker Compose (Recommended)

```bash
git clone https://github.com/dzaja123/photo-classification-platform.git
cd photo-classification-platform

# Start all services (backend + frontend + infrastructure)
docker-compose -f infrastructure/docker/docker-compose.dev.yml up -d

# Verify
docker ps  # All containers should be healthy

# Run database migrations
docker exec photo-platform-auth alembic upgrade head
docker exec photo-platform-application alembic upgrade head

# Create admin user
docker exec photo-platform-auth python scripts/create_admin.py
```

Services are now available:
- **Frontend**: http://localhost:3000
- **Auth API**: http://localhost:8001/docs (Swagger UI)
- **Application API**: http://localhost:8002/docs
- **Admin API**: http://localhost:8003/docs
- **MinIO Console**: http://localhost:9001

### Local Development (Without Docker)

```bash
# Start infrastructure only
docker-compose -f infrastructure/docker/docker-compose.dev.yml up -d postgres redis minio mongodb

# Auth Service
cd services/auth
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit as needed
alembic upgrade head
uvicorn app.main:app --reload --port 8001

# Application Service (new terminal)
cd services/application
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8002

# Admin Service (new terminal)
cd services/admin
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8003

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Creating the Admin User

All users register with the `USER` role by default. To create the first admin:

```bash
# Default credentials
docker exec photo-platform-auth python scripts/create_admin.py

# Custom credentials
docker exec -e ADMIN_EMAIL=admin@example.com \
            -e ADMIN_USERNAME=myadmin \
            -e ADMIN_PASSWORD='MySecure123!@#' \
            photo-platform-auth python scripts/create_admin.py
```

| Field | Default Value |
|-------|---------------|
| Email | `admin@admin.com` |
| Username | `admin_user` |
| Password | `Admin123!@#` |

The script is idempotent — re-running it is safe.

## API Endpoints

Interactive Swagger docs available at `http://localhost:{port}/docs` when `DEBUG=true`.

### Auth Service (Port 8001)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Revoke tokens |
| GET | `/api/v1/users/me` | Current user profile |
| PUT | `/api/v1/users/me` | Update profile |
| POST | `/api/v1/users/change-password` | Change password |
| GET | `/health` | Health check |

### Application Service (Port 8002)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/submissions/upload` | Upload photo + metadata |
| GET | `/api/v1/submissions/` | List user submissions (paginated, filterable) |
| GET | `/api/v1/submissions/{id}` | Get submission details |
| DELETE | `/api/v1/submissions/{id}` | Soft-delete submission |
| GET | `/api/v1/submissions/{id}/photo` | Serve photo (JWT via query param) |
| GET | `/api/v1/status` | Service status |
| GET | `/health` | Health check |

### Admin Service (Port 8003)
All endpoints require `ADMIN` role.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/submissions` | List/filter all submissions |
| GET | `/api/v1/admin/submissions/{id}` | Get submission by ID |
| GET | `/api/v1/admin/analytics` | Aggregated statistics |
| GET | `/api/v1/admin/audit-logs` | Paginated audit logs |
| GET | `/api/v1/admin/audit-logs/user/{id}` | User activity timeline |
| GET | `/api/v1/admin/audit-logs/security` | Security events summary |
| GET | `/api/v1/admin/export/submissions/csv` | Export as CSV |
| GET | `/api/v1/admin/export/submissions/json` | Export as JSON |
| GET | `/api/v1/status` | Service status |
| GET | `/health` | Health check |

## Safety Rules & Security

| Rule | Where | Why |
|------|-------|-----|
| **JWT with short-lived tokens** | Auth Service | 15-min access tokens limit exposure; refresh rotation prevents replay |
| **Token blacklisting** | Redis | Logout immediately invalidates tokens via JTI blacklist with TTL |
| **Rate limiting** | All services (Redis) | Per-IP counters prevent brute-force (3/min register, 5/min login, 60/min general) |
| **Password strength** | Auth Service | Min 8 chars, uppercase, lowercase, digit, special char required |
| **Input validation** | All services (Pydantic) | Type-safe schemas reject malformed input before it reaches business logic |
| **File validation** | Application Service | MIME whitelist, extension whitelist, 10 MB size limit |
| **RBAC** | Admin Service | `get_current_admin` dependency enforces admin role on every endpoint |
| **Audit logging** | MongoDB | All auth events, admin actions, and security violations are logged |
| **Non-root Docker** | All Dockerfiles | Production images run as unprivileged `app` user |
| **CORS** | All services | Explicit origin allowlist, not wildcard |

See [docs/SECURITY.md](docs/SECURITY.md) for full details.

## Testing

```bash
# Via Docker
docker exec photo-platform-auth python -m pytest tests/ -v
docker exec photo-platform-application python -m pytest tests/ -v
docker exec photo-platform-admin python -m pytest tests/ -v

# Via Makefile
make test
```

Coverage thresholds enforced per service (minimum 60%).

## CI/CD Pipeline

GitHub Actions (`.github/workflows/ci.yml`):

1. **Lint** — Ruff linter + formatter per service
2. **Test** — pytest with PostgreSQL, Redis, MongoDB service containers
3. **Build** — Docker images pushed to GitHub Container Registry (GHCR)
4. **Deploy** — `kubectl apply` to Kubernetes (main branch, manifests in `k8s/`)

## Kubernetes Deployment

```bash
kubectl apply -f k8s/
kubectl get pods -n photo-platform
```

- HorizontalPodAutoscaler per service (min 2, max 5–15 replicas, 70% CPU target)
- Liveness + readiness probes on `/health`
- Secrets via `k8s/secrets.yaml`, ConfigMap via `k8s/configmap.yaml`
- Ingress with TLS (cert-manager), path-based routing

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for scaling, secrets, and observability notes.

## Documentation

| Document | Contents |
|----------|----------|
| [API Reference](docs/API.md) | Full endpoint specs with request/response examples |
| [Architecture](docs/ARCHITECTURE.md) | System design, database choices, design patterns |
| [Security](docs/SECURITY.md) | Auth, RBAC, rate limiting, audit logging |
| [Deployment](docs/DEPLOYMENT.md) | Docker, K8s, scaling, observability, env vars |

## Diagrams

Source files (`.drawio`) are in `diagrams/`. Exported PNGs:

- `diagrams/system-architecture.png` — Block diagram of all services, databases, and communication paths
- `diagrams/data-flow.png` — Request flow from user upload through classification to admin view
