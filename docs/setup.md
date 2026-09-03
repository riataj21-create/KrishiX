# Setup & Deployment Guide

## Local Development Setup

### Prerequisites

- **Docker** & **Docker Compose** (recommended)
- **Git**
- **Node.js** 18+ (for local frontend development without Docker)
- **Python** 3.11+ (for local backend development without Docker)

### Option 1: Docker Compose (Recommended)

#### 1. Clone Repository

```bash
git clone <repository-url>
cd KrishiX
```

#### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env if needed (optional for local development)
```

#### 3. Start Services

```bash
docker-compose up
```

The first run will:
- Build Docker images
- Initialize PostgreSQL
- Create database schema
- Load sample data
- Start all three services

**Expected output:**
```
krishix-db is healthy
krishix-api | Uvicorn running on 0.0.0.0:8000
krishix-web | ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

#### 4. Access Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |
| Database | localhost:5432 |

#### 5. Database Access (Optional)

Connect to PostgreSQL database:

```bash
# Using psql (if installed locally)
psql -h localhost -U krishix_user -d krishix_db

# Or inside Docker container
docker-compose exec postgres psql -U krishix_user -d krishix_db
```

#### 6. Stop Services

```bash
# Gracefully stop
docker-compose down

# Stop and remove all data
docker-compose down -v
```

---

### Option 2: Local Development (Without Docker)

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env
# Edit .env with local paths
```

#### Database Setup (PostgreSQL Required)

```bash
# Create database
createdb -U postgres krishix_db

# Run migrations
alembic upgrade head

# Load sample data
psql -U postgres -d krishix_db -f ../database/schema.sql
psql -U postgres -d krishix_db -f ../database/sample_data.sql
```

#### Run Backend

```bash
# From backend/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend starts at: http://localhost:8000

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment
cp ../.env.example .env.local
# Edit NEXT_PUBLIC_API_URL if backend is on different port
```

#### Run Frontend

```bash
# From frontend/ directory
npm run dev
```

Frontend starts at: http://localhost:3000

---

## Environment Variables

### Backend (.env)

```ini
# Database
DATABASE_URL=postgresql://krishix_user:krishix_password@localhost:5432/krishix_db

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Environment
ENVIRONMENT=development
```

### Frontend (.env.local)

```ini
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## Common Tasks

### Reset Database

```bash
docker-compose down -v
docker-compose up
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Access Database Shell

```bash
docker-compose exec postgres psql -U krishix_user -d krishix_db
```

### Rebuild Images

```bash
docker-compose build --no-cache
docker-compose up
```

### Run Backend Tests

```bash
docker-compose exec backend pytest
```

---

## Staging Deployment

### Prepare for Staging

1. **Update Environment Variables**
   ```bash
   # Create .env.staging
   cp .env.example .env.staging
   # Edit with staging credentials
   ```

2. **Build Production Images**
   ```bash
   docker build -t krishix-api:staging ./backend
   docker build -t krishix-web:staging ./frontend
   ```

3. **Push to Registry** (e.g., Docker Hub, AWS ECR)
   ```bash
   docker tag krishix-api:staging myregistry/krishix-api:staging
   docker push myregistry/krishix-api:staging
   ```

### Deploy to Staging Server (EC2/GCP)

1. **SSH into server**
   ```bash
   ssh ubuntu@staging-server-ip
   ```

2. **Pull images and run**
   ```bash
   docker pull myregistry/krishix-api:staging
   docker pull myregistry/krishix-web:staging
   
   # Run with docker-compose
   docker-compose -f docker-compose.staging.yml up -d
   ```

---

## Production Deployment

### Pre-Production Checklist

- [ ] Update `SECRET_KEY` to a strong random value
- [ ] Use managed database (AWS RDS, GCP Cloud SQL)
- [ ] Set up SSL certificates (Let's Encrypt via Nginx)
- [ ] Configure domain DNS
- [ ] Set up monitoring and logging
- [ ] Run full test suite
- [ ] Test authentication flow
- [ ] Test price endpoints with real data
- [ ] Set up automated backups

### Production Environment Variables

```ini
# Database (Managed Service)
DATABASE_URL=postgresql://prod_user:strong_password@rds-endpoint:5432/krishix_prod

# Security
SECRET_KEY=<generate-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://krishix.com

# Environment
ENVIRONMENT=production

# Optional
SENTRY_DSN=https://...  # Error tracking
LOG_LEVEL=INFO
```

### Kubernetes Deployment (Optional)

For larger deployments, use Kubernetes:

```bash
# Create namespace
kubectl create namespace krishix

# Create secrets
kubectl create secret generic krishix-secrets \
  --from-literal=DATABASE_URL=... \
  --from-literal=SECRET_KEY=... \
  -n krishix

# Deploy
kubectl apply -f k8s/deployment.yaml -n krishix
```

---

## Monitoring & Logging

### Backend Logs

```bash
# View logs
docker-compose logs -f backend

# Watch specific service
docker-compose logs -f backend | grep -i error
```

### Database Backups

```bash
# Manual backup
docker-compose exec postgres pg_dump -U krishix_user krishix_db > backup.sql

# Restore from backup
docker-compose exec -T postgres psql -U krishix_user krishix_db < backup.sql
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database connection
docker-compose exec postgres pg_isready -U krishix_user
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find and kill process using port 3000 (frontend)
lsof -ti:3000 | xargs kill -9

# Find and kill process using port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Find and kill process using port 5432 (database)
lsof -ti:5432 | xargs kill -9
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps

# Restart database
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Backend Won't Start

```bash
# Check Python dependencies
docker-compose exec backend pip list

# Check for syntax errors
docker-compose exec backend python -m py_compile app/main.py

# View detailed logs
docker-compose logs backend --tail=50
```

### Frontend Won't Build

```bash
# Clear cache and reinstall
docker-compose exec frontend rm -rf node_modules .next
docker-compose exec frontend npm ci
docker-compose restart frontend
```

### Database Initialization Failed

```bash
# Reset database
docker-compose down -v

# Recreate with fresh schema
docker-compose up
```

---

## Performance Optimization

### Database Indexing

Indexes are already defined in `database/schema.sql`. For production, monitor query performance:

```bash
# Connect to database
docker-compose exec postgres psql -U krishix_user -d krishix_db

# Check slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

### Caching (Phase 9+)

When implementing Redis:

```bash
# Add Redis service to docker-compose.yml
# Update backend to use Redis for cache
```

### Connection Pooling

SQLAlchemy is configured with connection pooling. Adjust if needed:

```python
# backend/app/database.py
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # or StaticPool for testing
    pool_size=20,
    max_overflow=0
)
```

---

## Continuous Integration (Optional)

### GitHub Actions Example

```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      
      - name: Run tests
        run: |
          pytest backend/tests/
```

---

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer** (Nginx or AWS ALB)
   - Route requests to multiple backend instances
   - Sticky sessions for state (if needed)

2. **Database Replication**
   - Primary (write) + Read replicas
   - Automatic failover

3. **Caching Layer** (Redis)
   - Cache commodity lists
   - Cache market lists per state
   - Invalidate on data updates

### Vertical Scaling

1. **Database Optimization**
   - Indexes on frequently queried columns ✅
   - Query optimization
   - Connection pooling ✅

2. **Application Optimization**
   - Async endpoints (FastAPI supports this)
   - Batch operations
   - Lazy loading relations

---

## Support & Documentation

- **Issues**: Report on GitHub Issues
- **Architecture**: See [docs/architecture.md](architecture.md)
- **Database**: See [docs/database_schema.md](database_schema.md)
- **API**: See [docs/api_spec.md](api_spec.md)
- **README**: See [README.md](../README.md)

---

**Last Updated**: January 2025
