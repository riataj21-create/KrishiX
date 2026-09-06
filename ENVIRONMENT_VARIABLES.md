# KrishiX — Environment Variables & Configuration

## Backend (.env or docker-compose environment)

### Required

| Variable | Example | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql://krishix_user:krishix_password@postgres:5432/krishix_db` | PostgreSQL connection string. SQLite accepted for tests only. |
| `SECRET_KEY` | `change-me-in-production-min-32-chars` | JWT signing key. Use a strong random string in production. |

### Optional (have sensible defaults)

| Variable | Default | Notes |
|---|---|---|
| `ALGORITHM` | `HS256` | JWT algorithm. Do not change unless you know why. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT expiry in minutes. |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173,http://localhost:8000` | Comma-separated allowed origins. |

### Optional (external services — app degrades gracefully without them)

| Variable | Purpose | Notes |
|---|---|---|
| `DATA_GOV_API_KEY` | Live mandi prices from data.gov.in | Register free at data.gov.in. App uses sample data if not set. |

### No API key required for

- Open-Meteo weather API — completely free, no key
- OSRM road distance routing — public server, no key  
- OpenStreetMap tiles — no key

---

## Frontend (.env in frontend/)

| Variable | Example | Notes |
|---|---|---|
| `VITE_API_URL` | *(not needed — Vite proxy handles /api/*)* | Do NOT put the backend URL here. Vite proxy in `vite.config.ts` routes `/api/*` to the backend. |

**No API keys go in the frontend ever.** All external calls go through the backend proxy.

---

## Demo accounts (seeded by default)

| Email | Password | Role |
|---|---|---|
| `farmer1@krishix.com` | `password123` | Farmer — Madanapalle tomato demo lot |
| `farmer2@krishix.com` | `password123` | Farmer — aggregation participant |
| `farmer3@krishix.com` | `password123` | Farmer — aggregation participant |
| `buyer1@krishix.com` | `password123` | Buyer — linked to demo buyer requirements |

---

## How to run

```bash
# Start everything
docker compose up --build

# Reset database and re-seed
docker compose down -v
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## Running tests locally (without Docker)

```bash
cd backend
pip install -r requirements.txt
pip install bcrypt==4.0.1  # must be pinned for passlib compatibility

# Tests use SQLite automatically — no postgres needed
python -m pytest tests/ -q
```
