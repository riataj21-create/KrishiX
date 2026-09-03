# Architecture & System Design

## System Overview

AgriMandi is a three-tier web application with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     USER BROWSER                            │
├─────────────────────────────────────────────────────────────┤
│                     Next.js Frontend                        │
│         (React Components + TypeScript)                     │
│   - Landing, Auth, Dashboard, Price Search, Charts         │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP/REST (JSON)
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                   FastAPI Backend                           │
│              (Python + SQLAlchemy)                          │
│  - Authentication (JWT)                                    │
│  - Price Retrieval & Comparison                            │
│  - Location-Based Queries                                  │
│  - User Profile Management                                 │
│  - Data Validation & Business Logic                        │
└──────────────────┬──────────────────────────────────────────┘
                   │ SQL Queries
                   │
┌──────────────────▼──────────────────────────────────────────┐
│            PostgreSQL Database                              │
│     (Users, Markets, Prices, Commodities, etc.)            │
│              (Structured, Normalized)                       │
└──────────────────────────────────────────────────────────────┘
```

## Technology Stack Rationale

### Frontend: Next.js + React + TypeScript + Tailwind

**Why Next.js?**
- Server-Side Rendering (SSR) for SEO and performance
- Built-in API routes (if needed)
- File-based routing (simple and scalable)
- Image optimization
- Mobile-first default
- Great developer experience

**Why TypeScript?**
- Type safety catches bugs early
- Better IDE support and refactoring
- Cleaner code documentation
- Easier for teams

**Why Tailwind CSS?**
- Utility-first approach (consistent design)
- Responsive design helpers
- No context switching (stay in JSX)
- Smaller final CSS (PurgeCSS)
- Scales well for large projects

**Why shadcn/ui?**
- Copy-paste components (not a package)
- Built on Radix UI (accessible)
- Tailwind-based (easy to customize)
- No vendor lock-in

### Backend: FastAPI + Python

**Why FastAPI?**
- Automatic API documentation (Swagger UI, ReDoc)
- Type hints with Pydantic (automatic validation)
- Async/await support (better performance)
- Fast development (less boilerplate than Django)
- Great for REST APIs
- Easy to test

**Why SQLAlchemy?**
- ORM abstraction (database agnostic)
- Relationship management
- Query builder
- Migrations with Alembic

**Why Python?**
- Data science ecosystem (NumPy, Pandas for data ingestion)
- Rapid development
- Excellent libraries for web and data
- Large community

### Database: PostgreSQL

**Why PostgreSQL?**
- Structured relational data (normalized schema)
- ACID transactions (data consistency)
- Full-text search capabilities
- JSON support (flexible fields if needed)
- PostGIS extension (geographic queries, future-ready)
- Mature, battle-tested, open-source

### DevOps: Docker & Docker Compose

**Why Docker?**
- Consistent dev/prod environments
- Easy onboarding (just run `docker-compose up`)
- Service isolation
- Horizontal scaling ready
- Reproducible builds

## Data Flow

### 1. User Authentication Flow

```
User inputs credentials
        ↓
Frontend sends POST /api/auth/login
        ↓
Backend validates password (bcrypt)
        ↓
Backend generates JWT token
        ↓
Frontend stores token in secure storage
        ↓
Subsequent requests include Authorization: Bearer <token>
```

### 2. Price Search Flow

```
User selects State → District → Market → Commodity
        ↓
Frontend calls GET /api/market-prices?state=...&district=...&commodity=...
        ↓
Backend repository queries PostgreSQL
        ↓
Backend returns list of prices with metadata
        ↓
Frontend displays latest price + change indicator
```

### 3. Price Comparison Flow

```
User selects a commodity and multiple markets
        ↓
Frontend calls GET /api/market-prices/compare?commodity=...&markets=[...]
        ↓
Backend fetches prices for each market
        ↓
Backend calculates min/max/avg prices
        ↓
Backend sorts by price
        ↓
Frontend displays table/chart with price comparison
```

### 4. User Preferences Flow

```
User clicks "Save this market"
        ↓
Frontend sends POST /api/saved-markets/:market_id
        ↓
Backend creates record: user_id + market_id
        ↓
Backend returns success
        ↓
Frontend shows visual confirmation
        ↓
Later: GET /api/saved-markets returns all saved markets
```

## Database Design Philosophy

### Normalization (3NF)

The schema is normalized to:
- **Eliminate redundancy** (prices don't repeat market/commodity info)
- **Ensure data consistency** (one source of truth)
- **Enable efficient queries** (indexes on foreign keys)

### Key Relationships

```
users (1) ─── (many) farmer_profiles
          \
           ├─ (many) saved_markets
           └─ (many) saved_commodities

markets (1) ─── (many) market_prices
commodities (1) ─── (many) market_prices
```

### Time-Series Data

`market_prices` stores historical data:
- Every `price_date` represents a complete snapshot
- Multiple commodities per market per day
- `source` column tracks data origin (APMC, government, sample)
- `last_updated` tracks when data was fetched

### Geographic Data

Currently uses text fields (state, district, village):
- Simple, queryable, indexable
- Future-ready: can add `latitude`, `longitude`, `postal_code`
- PostGIS upgrade path if complex geographic queries needed

## Backend Architecture

### Layer Structure

```
API Routes (app/api/*.py)
        ↓ (validates input with Pydantic)
Service Layer (app/services/*.py)
        ↓ (business logic)
Repository Layer (app/repository/*.py)
        ↓ (database queries)
SQLAlchemy ORM Models (app/models.py)
        ↓ (SQL)
PostgreSQL Database
```

### Example: Get Market Prices

```python
# API Route (app/api/market_prices.py)
@app.get("/market-prices")
def get_prices(state: str, commodity_id: str):
    return service.get_prices_by_location(state, commodity_id)

# Service (app/services/price_service.py)
def get_prices_by_location(state: str, commodity_id: str):
    prices = repo.fetch_prices(state, commodity_id)
    return [format_price(p) for p in prices]

# Repository (app/repository/price_repo.py)
def fetch_prices(state: str, commodity_id: str):
    return db.query(MarketPrice)\
        .join(Market)\
        .filter(Market.state == state)\
        .filter(MarketPrice.commodity_id == commodity_id)\
        .order_by(MarketPrice.price_date.desc())\
        .all()
```

## Frontend Architecture

### Component Hierarchy

```
App (Next.js Page)
    ├── Navigation Header
    │   └── User Menu
    ├── Main Content
    │   ├── SearchFilters
    │   │   ├── StateSelector
    │   │   ├── DistrictSelector
    │   │   └── MarketSelector
    │   ├── PriceList / PriceComparison
    │   └── Charts (Recharts)
    └── Footer
```

### State Management

- **React Context API** for auth state (user, token)
- **React hooks** (useState, useEffect) for component state
- **API services** (fetch utilities) for data fetching

### Code Organization

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Landing page
│   ├── dashboard/
│   │   └── page.tsx
│   ├── price-search/
│   │   └── page.tsx
│   └── account/
│       └── page.tsx
├── components/
│   ├── Layout.tsx
│   ├── Navigation.tsx
│   ├── SearchFilters.tsx
│   ├── PriceTable.tsx
│   └── PriceChart.tsx
├── services/
│   ├── api.ts             # Axios/fetch client
│   ├── auth.ts            # Auth functions
│   └── prices.ts          # Price API calls
├── hooks/
│   ├── useAuth.ts         # Auth context hook
│   └── usePrices.ts       # Fetch prices hook
└── types/
    └── index.ts           # TypeScript types
```

## Performance Optimization (Future Phases)

### Caching Strategy

**Browser Cache:**
- Cache commodity list (rarely changes)
- Cache market list for a state (changes weekly)

**Server Cache (Redis):**
- Cache latest market prices (5-minute TTL)
- Cache popular searches (1-hour TTL)
- Invalidate on data import

**Database Query Optimization:**
- Indexes on `state`, `district`, `commodity_id`
- Compound indexes on `(market_id, commodity_id, price_date)`

### Data Ingestion (Phase 8+)

```
Government/APMC Data Source
        ↓
ETL Script (Python + Pandas)
        ↓ (validate, transform)
PostgreSQL Bulk Insert
        ↓ (Alembic migrations handle schema)
API Cache Invalidation
```

## Security Architecture

### Authentication

- **JWT-based** with `HS256` algorithm
- **AccessToken** (short-lived, 30 min)
- **RefreshToken** (long-lived, 7 days) – future enhancement
- **HttpOnly Cookies** for token storage – future enhancement

### Authorization

- Verify JWT on protected endpoints
- User ID in token ensures data isolation
- Frontend checks auth state before showing routes

### Data Protection

- **Passwords:** bcrypt with salt (never plain text)
- **Secrets:** Environment variables (.env file)
- **CORS:** Only allow frontend origin
- **HTTPS:** Required in production
- **Input Validation:** Pydantic schemas

## Scalability Considerations

### Horizontal Scaling

1. **Stateless Backend:** FastAPI instances can scale horizontally
2. **Load Balancer:** Nginx in front of multiple backend instances
3. **Database Pooling:** Connection pooling (SQLAlchemy)
4. **Caching Layer:** Redis for distributed cache

### Vertical Scaling

1. **Database Indexing:** Query optimization
2. **Read Replicas:** PostgreSQL replication for read-heavy workloads
3. **Connection Limits:** Tuning pool sizes

### Future Enhancements

- **WebSockets:** Real-time price updates
- **Background Jobs:** Celery for data ingestion
- **Message Queue:** Kafka for event streaming
- **Search Engine:** Elasticsearch for full-text search
- **CDN:** CloudFlare/AWS CloudFront for static assets

## Deployment Architecture

### Development (Current)

- Docker Compose locally
- PostgreSQL container
- Hot-reload for both frontend and backend

### Staging

- Docker containers on cloud VM (AWS EC2 / GCP Compute)
- Managed PostgreSQL (AWS RDS / GCP Cloud SQL)
- Nginx reverse proxy
- SSL certificates (Let's Encrypt)

### Production

- Kubernetes (AWS EKS / GCP GKE) for orchestration
- Managed databases (AWS RDS / GCP Cloud SQL)
- CDN for static assets
- Monitoring & logging (ELK stack, DataDog)
- Auto-scaling policies

## Conclusion

This architecture is:
- ✅ **Clean** – Clear separation of concerns
- ✅ **Scalable** – Can grow from 100 to 1M farmers
- ✅ **Maintainable** – Well-documented, standard patterns
- ✅ **Secure** – Industry-standard practices
- ✅ **Production-Ready** – Proper error handling, logging, testing

The system prioritizes **data structure and backend logic** over frontend complexity, ensuring that price discovery and market linkage remain the core value proposition.
