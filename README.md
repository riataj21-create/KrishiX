# KrishiX

> **Market intelligence for smarter agricultural decisions**

KrishiX is an agricultural marketplace intelligence platform built for Indian farmers. It provides reliable, location-specific commodity price data from APMC markets to help farmers compare opportunities and make informed selling decisions.

**Status:** MVP complete — frontend build passing, backend compiled, runtime verification requires Docker

---

## Problem Statement

Farmers across India face critical challenges in price discovery:

- **Information asymmetry** — Limited access to commodity prices across markets
- **Market fragmentation** — Difficult to compare prices across different APMC markets
- **Intermediary dependency** — Farmers often sell at lower rates due to lack of market knowledge
- **Poor decision making** — Without reliable data, farmers cannot identify optimal selling opportunities

---

## What KrishiX Does

- **Location-specific prices** — Search by State → District → Market hierarchy
- **Price comparison** — Compare the same commodity across multiple markets on the same date
- **Historical trends** — 30-day price history with interactive line charts
- **Saved markets and commodities** — Bookmark items for quick access
- **Transparent sourcing** — Every price shows its source and the date it was recorded
- **No false real-time claims** — Data is labelled "latest available", not "live"

---

## Technology Stack

### Frontend
- **Next.js 14** (App Router, static generation)
- **React 18** + **TypeScript**
- **Tailwind CSS** with a unified design token system
- **Recharts** for price trend visualisations
- **Lucide React** for icons

### Backend
- **Python 3.11** + **FastAPI**
- **SQLAlchemy 2.0** ORM
- **Pydantic 2.0** request/response validation
- **passlib + bcrypt** password hashing
- **python-jose** JWT authentication
- **Alembic** schema migrations

### Database
- **PostgreSQL 15** with 7 normalised tables
- UUID primary keys, compound indexes on (state, district) and (market_id, commodity_id, price_date)
- All prices stored and displayed in **₹ per quintal**

### Infrastructure
- **Docker + Docker Compose** — three services: postgres, backend, frontend
- Environment variables for all secrets and URLs

---

## Project Structure

```
KrishiX/
├── frontend/
│   ├── app/                  # Next.js App Router pages
│   │   ├── page.tsx          # Landing page
│   │   ├── dashboard/        # Main dashboard (auth required)
│   │   ├── search/           # Market price search
│   │   ├── comparison/       # Price comparison across markets
│   │   ├── trends/           # 30-day price trend charts
│   │   ├── saved/            # Saved markets & commodities
│   │   ├── profile/          # Farmer profile settings
│   │   └── auth/             # Login & registration
│   ├── components/
│   │   ├── Navigation/Navbar.tsx   # Sidebar (app) + header (marketing)
│   │   ├── layout/AppFrame.tsx     # Route-aware shell
│   │   ├── PriceCard.tsx           # Price display with save button
│   │   ├── CTASection.tsx          # Landing page CTA banner
│   │   └── Footer.tsx
│   ├── lib/api.ts            # Typed HTTP client for all endpoints
│   └── hooks/useAuth.ts      # Auth state hook
│
├── backend/
│   └── app/
│       ├── main.py           # FastAPI app, CORS, router registration
│       ├── models.py         # SQLAlchemy ORM (7 models)
│       ├── schemas.py        # Pydantic schemas (20+ classes)
│       ├── repository.py     # Data access layer
│       ├── auth.py           # JWT + bcrypt
│       └── api/              # Route handlers
│
├── database/
│   ├── schema.sql            # Valid PostgreSQL DDL with CREATE INDEX
│   └── sample_data.sql       # Demo data — prices in ₹/quintal
│
├── docs/                     # Architecture, schema, API spec, setup guide
├── docker-compose.yml
└── .env.example
```

---

## Quick Start

### Prerequisites
- Docker and Docker Compose

### Run

```bash
git clone <repo-url>
cd KrishiX
cp .env.example .env
docker-compose up
```

| Service   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:3000        |
| API       | http://localhost:8000        |
| API Docs  | http://localhost:8000/docs   |
| Health    | http://localhost:8000/health |

### Demo account
```
Email:    farmer1@krishix.com
Password: password123
```

### Reset database
```bash
docker-compose down -v
docker-compose up
```

---

## API Endpoints

### Authentication
```
POST /api/auth/register     Create account
POST /api/auth/login        Login, returns JWT
POST /api/auth/logout       Logout (stateless)
```

### User & Profile
```
GET  /api/users/me               Current user
PUT  /api/users/me               Update email
GET  /api/farmer-profile         Farmer profile (404 if not set)
POST /api/farmer-profile         Create profile
PUT  /api/farmer-profile         Update profile
```

### Market Data
```
GET /api/commodities             List commodities (paginated)
GET /api/commodities/{id}        Single commodity
GET /api/markets                 Markets by state/district
GET /api/markets/{id}            Single market
GET /api/market-prices           Latest prices (filterable)
GET /api/market-prices/compare   Compare one commodity across markets
GET /api/market-prices/history   30-day trend for a market+commodity pair
```

### Saved Items
```
GET    /api/saved-markets          List saved markets
POST   /api/saved-markets/{id}     Save market
DELETE /api/saved-markets/{id}     Unsave market
GET    /api/saved-commodities      List saved commodities
POST   /api/saved-commodities/{id} Save commodity
DELETE /api/saved-commodities/{id} Unsave commodity
```

---

## Database Schema

7 tables: `users`, `farmer_profiles`, `commodities`, `markets`, `market_prices`, `saved_markets`, `saved_commodities`

Key constraints:
- `UNIQUE (market_id, commodity_id, price_date)` prevents duplicate price rows
- `UNIQUE (name, state, district)` prevents duplicate markets
- Compound index on `(market_id, commodity_id, price_date DESC)` for fast history queries
- Price queries fall back to the most recent available date, not `date.today()`, so sample data always works

---

## Design Decisions

**No "live" price claims** — data freshness is shown explicitly on every price card. The word "live" does not appear in the UI.

**No LLM dependencies** — all retrieval is structured SQL via SQLAlchemy. The search page filters results from a PostgreSQL query, not a language model.

**Unified design tokens** — Tailwind color values and CSS custom properties (`--accent`, `--success`, etc.) are aligned to the same hex values to prevent rendering inconsistencies.

**₹/quintal everywhere** — all prices in the database, UI, and sample data use quintal as the unit (1 quintal = 100 kg), matching APMC reporting conventions.

---

## Environment Variables

### Backend
```env
DATABASE_URL=postgresql://krishix_user:krishix_password@postgres:5432/krishix_db
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000
```

### Frontend
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## What Still Needs Work

- **Comprehensive test suite** — `backend/tests/` has fixtures and one auth test; full coverage is not done
- **Real APMC data ingestion** — currently uses static sample data; a data pipeline reading from government APIs or scrapers is not implemented
- **Redis caching** — high-frequency price queries are not cached
- **Rate limiting** — the API has no rate limiting
- **Password reset flow** — the "Forgot password" link is a placeholder
- **Token refresh** — JWT expiry is 30 minutes; there is no refresh token flow
- **More states** — the state dropdown covers 5 states; real coverage requires more market data

---

## Documentation

- [Architecture](docs/architecture.md)
- [Database Schema](docs/database_schema.md)
- [API Specification](docs/api_spec.md)
- [Setup Guide](docs/setup.md)

---

**KrishiX** — Market intelligence for smarter agricultural decisions.
