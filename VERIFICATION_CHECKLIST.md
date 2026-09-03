# KrishiX — Verification Checklist

**Last updated:** September 2026  
**Build status:** `npm run build` passes (exit 0, 12/12 routes)  
**Runtime status:** Requires Docker — not verified in this environment

---

## Backend

### Models & Database
- [x] 7 SQLAlchemy ORM models (User, FarmerProfile, Commodity, Market, MarketPrice, SavedMarket, SavedCommodity)
- [x] Unique index names across all models (no duplicate `idx_state_district`)
- [x] Compound indexes: `(state, district)`, `(market_id, commodity_id, price_date)`
- [x] `schema.sql` uses valid PostgreSQL `CREATE INDEX` statements (no inline INDEX syntax)
- [x] Sample data prices in ₹/quintal (corrected from ₹/kg)
- [x] Historical price data for trend charts (7-day history at Ludhiana Central)

### Repository Layer
- [x] `get_latest_prices` uses `MAX(price_date)` fallback — sample data works on any day
- [x] `get_price_history` anchored to latest available date per market+commodity pair
- [x] `get_commodity_prices_by_date` accepts `Optional[date]` and uses MAX fallback

### API Endpoints
- [x] Auth: register (201), login (JWT), logout (stateless)
- [x] Users: GET/PUT `/api/users/me`
- [x] Farmer profiles: GET/POST/PUT `/api/farmer-profile`
- [x] Commodities: list (paginated), get by id — Pydantic v2 compatible (no `from_orm().dict()`)
- [x] Markets: list by location, get by id — Pydantic v2 compatible
- [x] Market prices: latest with filters, compare across markets, 30-day history
- [x] Saved markets: GET/POST/DELETE
- [x] Saved commodities: GET/POST/DELETE
- [x] Login accepts JSON body (not query params)
- [x] Price enrichment includes `market_name`, `commodity_name`, `state`, `district`

### Security
- [x] bcrypt password hashing
- [x] JWT HS256, 30-minute expiry
- [x] Bearer token auth via `HTTPBearer` dependency
- [x] CORS configured via env var
- [ ] `SECRET_KEY` still defaults to dev placeholder — must be changed before production
- [ ] No rate limiting
- [ ] No token refresh flow

### Testing
- [x] `conftest.py` with test fixtures (SQLite, test users, markets, commodities)
- [x] Basic auth test file exists
- [ ] Full test coverage not implemented
- [ ] Integration tests not implemented

---

## Frontend

### Build
- [x] `npm run type-check` passes (0 errors)
- [x] `npm run build` passes (exit 0, all 12 routes)
- [x] `tsconfig.json` path alias `@/*` points to `./` (not `./src/`)

### Pages
- [x] `/` — Landing page: hero, features, CTA strip, CTASection banner
- [x] `/auth/login` — Login with `useSearchParams` wrapped in `Suspense` (Next.js 14 compliant)
- [x] `/auth/register` — Registration with client-side validation
- [x] `/dashboard` — Dynamic greeting (time-of-day + profile name), state/district selector, price grid, decision support links, followed commodities
- [x] `/search` — Debounced search, save/unsave commodity buttons on PriceCard, loading/empty/error states
- [x] `/comparison` — Commodity selector, state selector, summary stats, comparison table with save/unsave market buttons
- [x] `/trends` — Market + commodity selector, Recharts line chart (min/modal/max), statistics cards
- [x] `/saved` — Tabbed markets + commodities, remove functionality, empty states
- [x] `/profile` — POST for new users, PUT for existing; district required; state dropdown

### Components
- [x] `Navbar` — Desktop sidebar + mobile top bar, active route highlighting, logout button, dynamic user name from profile API
- [x] `AppFrame` — Route-aware shell separating marketing pages from app routes
- [x] `PriceCard` — Bookmark icon, save/unsave callbacks, `/quintal` unit label
- [x] `CTASection` — Used on landing page (was previously orphaned)
- [x] `Footer` — Shown on marketing pages only

### Design System
- [x] Tailwind color tokens aligned with CSS custom properties (`primary: #17624f` = `--accent`)
- [x] No "live" or "real-time" wording in any page
- [x] Data freshness label: "Latest available" on all price displays
- [x] Source attribution on price cards
- [x] Skeleton shimmer loading states on dashboard and search

### Auth Flow
- [x] Login stores `access_token` in localStorage
- [x] All app pages redirect to `/auth/login` if no token
- [x] Logout clears token and redirects to login
- [x] `authAPI.login()` used (not raw `fetch`)

### Known Gaps
- [ ] `useAuth` hook exists but is not used — pages do their own localStorage checks
- [ ] No error boundary components
- [ ] `zustand` and `axios` installed but unused (dead dependencies)
- [ ] "Forgot password" is a dead link
- [ ] Footer links are all `href="#"` placeholders
- [ ] Only 5 states in dropdowns — more requires real data

---

## Database

- [x] `schema.sql` — valid PostgreSQL DDL, `CREATE INDEX` as separate statements
- [x] `sample_data.sql` — all prices in ₹/quintal, commodity unit = 'quintal'
- [x] 3 users, 3 farmer profiles, 13 commodities, 6 markets, 17 current-date price rows + 14 historical rows
- [x] 4 saved markets, 4 saved commodities pre-seeded for demo account
- [ ] Real APMC data ingestion not implemented

---

## Infrastructure

- [x] `docker-compose.yml` — postgres, backend, frontend services with health checks
- [x] Backend `Dockerfile`
- [x] Frontend `Dockerfile.dev`
- [x] `.env.example` templates for both backend and frontend
- [ ] Production Dockerfile for frontend (not present — Dockerfile.dev is dev-only)
- [ ] No CI/CD pipeline

---

## How to Verify (Once Docker Is Running)

```bash
# Start all services
docker-compose up

# Check health
curl http://localhost:8000/health

# Login with demo account
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"farmer1@krishix.com","password":"password123"}'

# Get latest prices (use token from login response)
curl "http://localhost:8000/api/market-prices?state=Punjab" \
  -H "Authorization: Bearer <token>"

# Frontend
open http://localhost:3000
```

**Expected user flow:**
1. Visit `http://localhost:3000` → landing page
2. Click "Create a free account" → register
3. Login → dashboard with greeting and market prices
4. Search → find and bookmark commodities
5. Comparison → compare commodity across Punjab markets
6. Trends → view 7-day price chart for Rice at Ludhiana Central
7. Saved → review bookmarks, remove items
8. Profile → fill in name, state, district → greeting updates on next dashboard visit

---

## What Requires Attention Before Production

| Item | Risk | Notes |
|------|------|-------|
| `SECRET_KEY` in `.env` | High | Must be replaced with a random 32-byte secret |
| Real APMC data source | High | Sample data only; pipeline not built |
| Token refresh | Medium | 30-min expiry with no refresh means users get logged out |
| Rate limiting | Medium | API has no request throttling |
| Test coverage | Medium | Only one test file, no integration tests |
| Frontend production Dockerfile | Low | Only a dev Dockerfile exists |
| Dead links in Footer and profile | Low | All `href="#"` |
