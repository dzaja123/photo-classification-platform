# Photo Classification Platform

**WorkNomads R&D Assessment**

A cloud-deployable, microservices-based platform for photo classification with user management and admin analytics.

## 🏗️ Architecture

### Microservices (3 Services)
1. **Auth Service** (Port 8001) - User authentication, JWT, profile management
2. **Application Service** (Port 8002) - Photo upload, storage, ML classification
3. **Admin Service** (Port 8003) - Admin panel, filtering, analytics, audit logs

### Technology Stack
- **Backend**: FastAPI, Python 3.11
- **Databases**: PostgreSQL 16, MongoDB 7, Redis 7.2
- **Storage**: MinIO (S3-compatible)
- **ML**: TensorFlow Lite (MobileNetV2)
- **Frontend**: React 18 + Vite 5
- **Gateway**: Nginx
- **Infrastructure**: Docker, Kubernetes
- **CI/CD**: GitHub Actions

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Node.js 18+
- Git

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd photo-platform

# Start infrastructure services
docker-compose -f infrastructure/docker/docker-compose.dev.yml up -d

# Set up Auth Service
cd services/auth
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
alembic upgrade head
uvicorn app.main:app --reload --port 8001

# Set up Application Service
cd ../application
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8002

# Set up Admin Service
cd ../admin
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8003

# Set up Frontend
cd ../../frontend
npm install
cp .env.example .env
npm run dev
```

### Docker Compose (Full Stack)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 📡 API Endpoints

### Auth Service (Port 8001)
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/users/me` - Get current user
- `GET /health` - Health check

### Application Service (Port 8002)
- `POST /api/v1/app/upload` - Upload photo with metadata
- `GET /api/v1/app/submissions` - List user submissions
- `GET /api/v1/app/submissions/{id}` - Get submission details
- `DELETE /api/v1/app/submissions/{id}` - Delete submission
- `GET /health` - Health check

### Admin Service (Port 8003)
- `GET /api/v1/admin/submissions` - List all submissions (filtered)
- `GET /api/v1/admin/analytics` - Get analytics data
- `GET /api/v1/admin/audit-logs` - View audit logs
- `GET /api/v1/admin/export` - Export data (CSV/JSON)
- `GET /health` - Health check

## 🔐 Security Features

1. **Authentication**: JWT with short-lived access tokens (15min) and refresh tokens (7 days)
2. **Rate Limiting**: Redis-based rate limiting on all endpoints
3. **Input Validation**: Pydantic schemas with comprehensive validation
4. **File Upload**: MIME type validation, size limits, secure filename generation
5. **Audit Logging**: MongoDB-based audit trail for all critical actions
6. **CORS**: Configured for specific origins only
7. **Docker Security**: Non-root users, multi-stage builds, health checks

## 🧪 Testing

```bash
# Run tests for Auth Service
cd services/auth
pytest --cov=app --cov-report=html

# Run tests for Application Service
cd services/application
pytest --cov=app --cov-report=html

# Run tests for Admin Service
cd services/admin
pytest --cov=app --cov-report=html

# Run frontend tests
cd frontend
npm test
```

## 📦 Deployment

### Railway (Recommended for Assessment)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Kubernetes

```bash
# Apply manifests
kubectl apply -f infrastructure/kubernetes/

# Check status
kubectl get pods -n photo-platform
kubectl get services -n photo-platform

# View logs
kubectl logs -f deployment/auth-service -n photo-platform
```

## 📚 Documentation

- [API Documentation](docs/API.md) - Complete API reference
- [Architecture](docs/ARCHITECTURE.md) - System architecture and design
- [Security](docs/SECURITY.md) - Security implementation details
- [Deployment](docs/DEPLOYMENT.md) - Deployment guide

## 🎯 Features

### User Features
- ✅ User registration with email validation
- ✅ Secure login with JWT
- ✅ Photo upload with metadata (name, age, location, gender, country, description)
- ✅ Real-time ML classification (TensorFlow Lite MobileNetV2)
- ✅ View submission history
- ✅ View classification results

### Admin Features
- ✅ Admin-only access with RBAC
- ✅ Advanced filtering (age, gender, location, country, date)
- ✅ Full-text search
- ✅ Analytics dashboard
- ✅ Audit log viewer
- ✅ Data export (CSV/JSON)
- ✅ User activity timeline
- ✅ Security event monitoring

## 🏆 Project Highlights

- **Real ML Model**: TensorFlow Lite MobileNetV2 (not mock classification)
- **Production Patterns**: Repository pattern, Service layer, Dependency Injection
- **Comprehensive Security**: 5-layer security architecture
- **NoSQL Audit Logs**: MongoDB for flexible audit trail
- **Complete CI/CD**: GitHub Actions with linting, testing, building
- **Cloud-Ready**: Kubernetes manifests with scaling strategy

## 📄 License

This project is created for WorkNomads R&D Assessment.

## 👤 Author

Created by [Your Name] - 2026-02-05
