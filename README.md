# KrishiX — Agricultural Market Intelligence & Selling Decision Platform

**SIH Problem Statement SIH26132** — Strengthening market linkages and price discovery for farmers.

---

## What KrishiX actually is

KrishiX is a pre-transaction decision platform for Indian farmers.

The problem it solves is not that market price data is unavailable. The problem is that a farmer cannot act on raw price data alone. A farmer in Madanapalle growing tomatoes needs to know:

- Which market gives the highest net amount in hand after all costs?
- Should they sell today or wait based on weather, price trends, and risk?
- Is there a direct buyer or FPO offering better terms than the nearest mandi?

Existing systems show prices. KrishiX answers the decision.

---

## The three questions KrishiX answers

```
WHERE should I sell?   WHEN should I sell?   WHO should I sell to?
```

These three questions drive every feature in the product.

---

## The core decision flow

```
FARMER INPUTS
 Crop + Quantity + Location + Selling window
         ↓
MARKET DISCOVERY
 Candidate mandis within configurable radius
 Registered buyers and FPOs on the platform
         ↓
PRICE + DISTANCE + COSTS
 Latest available price per market (source + observation date shown)
 Real road distance via OSRM routing (not straight-line)
 Transport cost: road_km × estimated rate (clearly labelled as estimate)
 Market charges: state/market-specific where data available (labelled)
 Loading/unloading: configurable estimate (labelled as demo assumption)
         ↓
ESTIMATED NET REALIZATION
 Gross = modal_price × quantity
 Estimated Net = Gross − transport − market charges − loading
 (All cost assumptions carry source/estimate labels — no magic numbers)
         ↓
RANKED OPTIONS (by estimated net, not by raw price)
 Market A   Modal ₹2,400   Transport ₹900   Est. Net ₹22,800
 Market B   Modal ₹2,700   Transport ₹2,800  Est. Net ₹23,700  ← RANKED #1
 Market C   Modal ₹2,500   Transport ₹1,500  Est. Net ₹23,150
 (Highest net ≠ always best — payment timing and risk shown where available)
         ↓
WHEN INTELLIGENCE
 Sell-now / Sell-soon / Monitor / Wait
 Based on: observed price trend + weather risk + volatility
 (Historical observation and recommendation clearly separated — no false predictions)
         ↓
BUYER MATCHING (where registered buyers exist)
 Matching by crop, quantity, grade, location
 Confidence score explained — not an opaque AI number
 Offer / counter-offer / accept workflow
 Empty state when no buyers registered — WHERE and WHEN still work
         ↓
FARMER ACTION
 View ranked options on map
 Contact buyer via WhatsApp link
 Book mandi time slot
 Generate produce listing
 Set price alert
```

---

## What this is not

- Not a mandi price dashboard (prices alone are not actionable)
- Not an AI chatbot (no LLM for deterministic queries)
- Not a replacement for eNAM (a decision layer before the transaction, not a trading platform)
- Not a system that only works when buyers are registered (WHERE and WHEN work independently)

---

## Important product principles

### Cost assumptions are labelled
Every hardcoded cost value carries one of these labels:
- **SOURCE-BACKED** — from a documented official source
- **CONFIGURED** — set per region/market in the database
- **ESTIMATED** — clearly marked as an approximation
- **DEMO** — seed data for demonstration purposes

No value is presented as authoritative without a defensible basis.

### Data freshness is honest
- Prices from data.gov.in are labelled **LATEST AVAILABLE** with the observation date
- Sample data is labelled **DEMO DATA**
- Cached/stale data is labelled **STALE — last updated [timestamp]**
- Nothing is called "LIVE" or "REAL-TIME" unless the source timestamp supports it

### Recommendations are explained
Every WHEN signal (SELL NOW / MONITOR / WAIT) shows:
- What evidence supports it
- What evidence contradicts it
- What confidence level applies

Historical price movement is presented as observation, not prediction.
No statement like "waiting 4 days will increase income by 40%" is made without sufficient historical evidence clearly labelled as probabilistic.

### Buyer marketplace has a cold-start state
If no buyers are registered:
> "No active KrishiX buyers currently match this listing."

The platform continues to work for WHERE and WHEN decisions.
Demo/seed buyer accounts are clearly identified as demo data — not presented as real platform adoption.

---

## Current implementation status

### What exists and works

**Backend (Python + FastAPI + PostgreSQL)**
- Authentication — JWT (HS256), bcrypt password hashing, HTTPBearer
- User management — register, login, get current user
- Farmer profiles — create, read, update with GPS coordinates
- Commodities — list (paginated, filterable by category), get by ID
- Markets — list by state/district (required), get by ID
- Market prices — latest prices with MAX(price_date) fallback, comparison across markets, 30-day history
- Saved markets + commodities — full CRUD with duplicate prevention
- Database — PostgreSQL with compound indexes, normalized schema, sample data (₹/quintal)

**Frontend (React 18 + Vite + TypeScript + Tailwind CSS)**
- Vite SPA with React Router v6
- AuthContext — login, logout, token refresh on mount (TechVision pattern)
- ToastContext — success/error/warning/info notifications (TechVision pattern)
- RoleGuard — authentication guard on protected routes
- Centralized API client at `src/lib/api.ts` — typed, single location for all requests, Vite proxy handles routing
- Design system — CSS custom properties + Tailwind, consistent card/button/badge/input classes

**Infrastructure**
- Docker Compose — 3 containers: postgres, backend, frontend
- Vite proxy — `/api/*` routed to backend at build time (no env var baking issue)
- Sample data — 6 markets, 13 commodities, 7-day price history

---

### What is partially built

| Item | Status | Gap |
|---|---|---|
| Buyer model | DB table defined | No repository, no API endpoint, no seeded buyers |
| Decision API | Frontend client exists | Backend endpoint `/api/selling-decision` does not exist |
| Buyer API | Frontend client exists | Backend endpoint `/api/buyers` does not exist |
| Change password | Frontend client exists | Backend endpoint `/api/users/me/password` does not exist |
| Net realization engine | Not started | No transport/cess calculation anywhere |
| Role system | Not started | No `role` column on users, no role in JWT |

---

### What does not exist yet

**Backend — missing**
- `/api/selling-decision` — the net realization engine
- `/api/buyers` — buyer listing and filtering
- `/api/weather` — Open-Meteo proxy
- `/api/msp` — MSP comparison
- `/api/listings` — farmer produce listings
- `/api/matches` — buyer-farmer matching
- `/api/fpo/simulate` — FPO aggregation calculator
- `/api/market-prices/pattern` — historical week-over-week pattern
- `/api/users/me/password` — change password
- `/api/schemes` — government scheme matching
- Role column on users table
- Service layer (routes call repositories directly — no business logic separation)

**Frontend — missing (src/ pages not yet created)**
- Decision page (the hero feature)
- Dashboard (Vite version — Next.js version exists as dead code)
- All other pages (Next.js versions exist as dead code, Vite versions not started)
- Leaflet map component
- Weather widget
- MSP badge on price cards
- Buyer discovery page
- Farmer listing page

**Infrastructure — issues**
- `tailwind.config.ts` content paths scan `app/` and `components/` (Next.js) instead of `src/` (Vite) — Tailwind classes in `src/` will be purged in production build
- `next.config.js` exists but Next.js is not installed — unused/misleading
- `.env.example` contains `NEXT_PUBLIC_API_URL` — a Next.js variable unused in Vite

---

### What should be removed or deferred

| Item | Action | Reason |
|---|---|---|
| `frontend/app/` Next.js pages | DELETE | Dead code — Vite tsconfig excludes them |
| `frontend/components/` Next.js components | DELETE | Same — dead code |
| `frontend/lib/api.ts` (old Next.js version) | DELETE | Replaced by `src/lib/api.ts` |
| `frontend/hooks/useAuth.ts` | DELETE | Replaced by AuthContext |
| `frontend/next.config.js` | DELETE | Next.js not installed |
| `frontend/tailwind.config.ts` content path fix | FIX | Must point to `src/` not `app/` |
| QR Produce Passport | DEFER | Evaluate whether it materially improves buyer trust or traceability before building |
| Admin portal | DEFER | Non-essential for core WHERE/WHEN/WHO decision |
| Mandi slot booking | DEFER | Useful but not core to the selling decision |
| Government scheme matching | P2 | Valuable but secondary to the core engine |

---

## Tech stack

### Frontend
- React 18 + Vite 6 (SPA — loads under 2 seconds)
- TypeScript (strict)
- React Router v6 with RoleGuard
- Tailwind CSS 3
- Recharts — price trend charts
- Leaflet + OpenStreetMap — market and buyer maps (free, no API key)
- AuthContext + ToastContext (patterns from TechVision reference project)
- Centralized API client with Vite proxy

### Backend
- Python 3.11 + FastAPI 0.104
- SQLAlchemy 2.0 ORM
- Pydantic 2.0 validation
- PostgreSQL 15
- bcrypt password hashing (passlib + bcrypt 4.0.1 — pinned for passlib compatibility)
- JWT authentication (python-jose, HS256)
- httpx — for calling external APIs (Open-Meteo, OSRM, data.gov.in)

### External services (planned)
| Service | Purpose | Key required |
|---|---|---|
| data.gov.in / Agmarknet | Live mandi prices | Free — register at data.gov.in |
| Open-Meteo | Weather + 7-day forecast | None |
| OSRM (router.project-osrm.org) | Real road distance | None |
| OpenStreetMap | Map tiles for Leaflet | None |

App works fully without external keys using seeded sample data.

### Infrastructure
- Docker Compose — postgres:15-alpine, python:3.11-slim, node:20-alpine
- Vite preview server (not Next.js)

---

## Database schema

| Table | Purpose | Status |
|---|---|---|
| users | Auth, email, password_hash | ✅ Exists — needs `role` column |
| farmer_profiles | Location, GPS, crop preferences | ✅ Exists |
| commodities | 13 crops with unit | ✅ Exists — needs MSP fields |
| markets | 6 APMC mandis with GPS | ✅ Exists |
| market_prices | Time-series prices, source, date | ✅ Exists |
| saved_markets | User bookmarks | ✅ Exists |
| saved_commodities | User bookmarks | ✅ Exists |
| buyers | Trader/FPO profiles | ⚠️ Model exists, no endpoint/seed data |
| listings | Farmer produce offers | ❌ Missing |
| matches | Listing ↔ buyer with confidence score | ❌ Missing |
| price_alerts | Target price notifications | ❌ Missing |

---

## API endpoints

### Working
```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/users/me
PUT  /api/users/me
GET  /api/farmer-profile
POST /api/farmer-profile
PUT  /api/farmer-profile
GET  /api/commodities
GET  /api/commodities/{id}
GET  /api/markets
GET  /api/markets/{id}
GET  /api/market-prices
GET  /api/market-prices/compare
GET  /api/market-prices/history
GET  /api/saved-markets
POST /api/saved-markets/{id}
DELETE /api/saved-markets/{id}
GET  /api/saved-commodities
POST /api/saved-commodities/{id}
DELETE /api/saved-commodities/{id}
```

### Missing (frontend already calls these — backend not built yet)
```
GET  /api/selling-decision       ← the core feature
GET  /api/buyers                 ← buyer discovery
PUT  /api/users/me/password      ← change password
GET  /api/weather                ← Open-Meteo proxy
GET  /api/msp                    ← MSP comparison
GET  /api/listings               ← farmer produce listings
POST /api/listings
GET  /api/matches                ← buyer matching
GET  /api/fpo/simulate           ← FPO aggregation calculator
GET  /api/market-prices/pattern  ← week-over-week historical pattern
```

---

## Demo accounts (seed data)

| Email | Password | Role |
|---|---|---|
| farmer1@krishix.com | password123 | Farmer (Ludhiana, Punjab) |
| farmer2@krishix.com | password123 | Farmer (Nashik, Maharashtra) |
| farmer3@krishix.com | password123 | Farmer (Hisar, Haryana) |

Buyer accounts and admin account to be added when role system is implemented.

---

## How to run

```bash
git clone https://github.com/riataj21-create/KrishiX
cd KrishiX
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

### Reset database
```bash
docker compose down -v
docker compose up --build
```

### Optional — enable live mandi prices
1. Register at [data.gov.in](https://data.gov.in/user/register)
2. Get your free API key
3. Add to `.env`: `DATA_GOV_API_KEY=your_key_here`

App works without this key using seeded sample data labelled as DEMO DATA.

---

## Implementation priority

Build in this order. Each phase must work before the next starts.

| Phase | What | Why first |
|---|---|---|
| 1 | Fix Tailwind config to scan `src/` | CSS will be broken in production without this |
| 2 | Delete dead Next.js code from `frontend/app/`, `frontend/components/`, `frontend/lib/`, `frontend/hooks/` | Confusion eliminated |
| 3 | Add `role` to users table + JWT | Foundation for farmer/buyer portals |
| 4 | Build all Vite frontend pages (farmer portal) | WHERE/WHEN visible to users |
| 5 | `/api/selling-decision` backend engine (OSRM + net realization + ranking) | The core feature |
| 6 | `/api/weather` + weather widget on dashboard | WHEN answer |
| 7 | `/api/msp` + MSP badge on price cards | WHEN answer (policy context) |
| 8 | `/api/buyers` + seed 10 demo buyers + buyer discovery page | WHO answer |
| 9 | `/api/listings` + `/api/matches` + confidence scoring | Full marketplace loop |
| 10 | Offer/negotiation workflow | Completes the WHO flow |
| 11 | `/api/fpo/simulate` + FPO page | Collective bargaining feature |
| 12 | Price alerts, saved items polish, profile + change password | Secondary features |
| 13 | Offline fallback + stale data labelling | Resilience |
| 14 | Testing, security review, final polish | Readiness |

---

## Competitive position

KrishiX does not claim to provide price data that does not already exist publicly. The underlying market price data is available from data.gov.in.

The differentiation is the decision layer:

```
Fragmented public data
→ Integration with source + timestamp
→ Farmer-specific calculation (crop + quantity + location)
→ Estimated net realization per market
→ Explainable ranking
→ Timing/risk signal with supporting evidence
→ Buyer feasibility check
→ Actionable recommendation
```

This is a pre-transaction intelligence layer, not a trading platform. It helps farmers decide before they travel to a market or commit to a buyer.

---

## Known limitations (honest)

- Transport cost estimates are configurable approximations — not sourced live from diesel prices
- State-wise APMC cess rates require official per-state-per-commodity data — demo values are estimates
- Price forecasting is not implemented — WHEN signals are evidence-based rules, not ML predictions
- Buyer marketplace requires registered buyers to be useful — empty-state handled correctly
- Live mandi prices require data.gov.in API key — falls back to sample data without it
- 30-minute JWT expiry (extend to 8h in `.env` for demo: `ACCESS_TOKEN_EXPIRE_MINUTES=480`)
