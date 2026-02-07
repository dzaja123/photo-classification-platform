# Deployment Guide

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

### Docker Compose (recommended)

```bash
# Start all infrastructure + services
docker-compose -f infrastructure/docker/docker-compose.dev.yml up -d

# View logs
docker-compose -f infrastructure/docker/docker-compose.dev.yml logs -f

# Stop
docker-compose -f infrastructure/docker/docker-compose.dev.yml down
```

### Manual Setup

```bash
# 1. Start infrastructure only
docker-compose -f infrastructure/docker/docker-compose.dev.yml up -d postgres redis minio mongodb

# 2. Auth Service
cd services/auth
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit as needed
alembic upgrade head
uvicorn app.main:app --reload --port 8001

# 3. Application Service (new terminal)
cd services/application
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8002

# 4. Admin Service (new terminal)
cd services/admin
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8003

# 5. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Production Build

All services use multi-stage Docker builds:

```bash
# Build from project root
docker build -f services/auth/Dockerfile -t photo-platform/auth .
docker build -f services/application/Dockerfile -t photo-platform/application .
docker build -f services/admin/Dockerfile -t photo-platform/admin .
docker build -f frontend/Dockerfile -t photo-platform/frontend .
```

Production images:
- Run as non-root `app` user
- Include health checks
- Use uvicorn with 2 workers (no --reload)
- Frontend served via nginx

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):

1. **Lint** — Ruff linter + formatter check per service
2. **Test** — pytest with PostgreSQL, Redis, MongoDB service containers
3. **Build** — Docker build + push to GitHub Container Registry (GHCR)
4. **Deploy** — kubectl apply to Kubernetes cluster (main branch only)

## Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Verify
kubectl get pods -n photo-platform
kubectl get services -n photo-platform
kubectl get hpa -n photo-platform

# Logs
kubectl logs -f deployment/auth-service -n photo-platform
```

### Scaling Strategy
- HorizontalPodAutoscaler configured for each service
- Target CPU utilization: 70%
- Min replicas: 2, Max replicas: 10

## Observability

### Logging
- All services use Python's `logging` module with `getLogger(__name__)` per module
- Structured log output (service name, module, level, message) for log aggregation
- Log levels configurable per service via `LOG_LEVEL` env var (default: `INFO`)
- Uvicorn access logs are enabled in development, disabled in production via `--no-access-log`

### Metrics (Production)
For production deployments, add Prometheus metrics collection:
- **prometheus-fastapi-instrumentator** exposes `/metrics` on each service
- Scrape interval: 15s per pod via Kubernetes `ServiceMonitor`
- Key metrics: request latency (p50/p95/p99), error rate, active connections, classification duration
- Grafana dashboards for per-service and aggregate views

### Tracing (Production)
- OpenTelemetry SDK with OTLP exporter for distributed tracing
- Trace context propagated via `traceparent` header across services
- Jaeger or Tempo as trace backend
- Key spans: HTTP handler, DB query, MinIO operation, ML classification

### Health Checks
- All services expose `GET /health` returning `{"status": "healthy"}`
- Docker `HEALTHCHECK` configured in every Dockerfile (30s interval, 5s timeout, 3 retries)
- Kubernetes liveness and readiness probes configured on each deployment

## Environment Variables

### Required (all services)
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async connection string |
| `REDIS_URL` | Redis connection string |
| `MONGODB_URL` | MongoDB connection string |
| `JWT_SECRET_KEY` | JWT signing key (min 32 chars) |

### Application Service
| Variable | Description |
|----------|-------------|
| `MINIO_ENDPOINT` | MinIO host:port |
| `MINIO_ACCESS_KEY` | MinIO access key |
| `MINIO_SECRET_KEY` | MinIO secret key |
| `MINIO_BUCKET_NAME` | Storage bucket name |

### Optional
| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode + Swagger docs |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
| `MAX_FILE_SIZE_MB` | `10` | Max upload size |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | JWT access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | JWT refresh token TTL |
