# KrishiX Backend — Implementation Status

**Last updated:** Session complete  
**Tests:** 18/18 feasibility engine unit tests ✅  
**API docs:** http://localhost:8000/docs (Swagger UI, auto-generated)

---

## What is complete and working

### Core feasibility engine (`backend/app/services/feasibility_engine.py`)
The deterministic heart of KrishiX. 100% tested, zero external dependencies.

Evaluates every opportunity against:
- Quantity (min/max) — HARD
- Quality/grade — HARD
- Payment terms — HARD
- Selling deadline — HARD
- Price floor — SOFT/HARD
- Transport cost vs budget — HARD when budget set

Returns exactly one of:
- `EXECUTABLE` — farmer can proceed as-is
- `RECOVERABLE` — blocked but a practical fix exists
- `NOT_VIABLE` — blocked with no feasible recovery
- `INSUFFICIENT_DATA` — missing critical values

For every failed opportunity returns:
- Blocking constraints (list)
- Quantified gaps (required vs available, exact gap value)
- Minimum viable changes (what intervention, feasible yes/no, resulting feasibility)
- Human-readable explanation
- Economics breakdown (sale value, transport, net — all labelled)

### All API endpoints

| Endpoint | Status | Notes |
|---|---|---|
| POST /api/auth/register | ✅ | role: farmer\|buyer |
| POST /api/auth/login | ✅ | returns JWT with role |
| POST /api/auth/logout | ✅ | |
| GET /api/users/me | ✅ | |
| PUT /api/users/me | ✅ | |
| PUT /api/users/me/password | ✅ | |
| GET /api/farmer-profile | ✅ | |
| POST /api/farmer-profile | ✅ | |
| PUT /api/farmer-profile | ✅ | |
| GET /api/lots | ✅ | filter by status |
| POST /api/lots | ✅ | auto-fills from profile |
| GET /api/lots/{id} | ✅ | owner-only |
| PUT /api/lots/{id} | ✅ | owner-only |
| DELETE /api/lots/{id} | ✅ | owner-only |
| POST /api/lots/{id}/opportunities/analyze | ✅ | full feasibility + opportunity gap |
| GET /api/lots/{id}/opportunities | ✅ | returns cached or re-analyzes |
| POST /api/lots/{id}/whatif | ✅ | NEW — simulation without modifying lot |
| GET /api/opportunities/{id} | ✅ | |
| POST /api/opportunities/{id}/recovery | ✅ | aggregation + negotiation |
| POST /api/opportunities/{id}/offer | ✅ | EXECUTABLE only |
| GET /api/lots/{id}/offers | ✅ | |
| POST /api/offers/{id}/accept | ✅ | creates transaction |
| GET /api/transactions | ✅ | |
| GET /api/transactions/{id} | ✅ | party-only |
| POST /api/transactions/{id}/advance | ✅ | accepted→pickup→payment_pending |
| POST /api/transactions/{id}/payment/report | ✅ | demo_as_buyer flag |
| POST /api/transactions/{id}/payment/confirm | ✅ | confirm or dispute |
| GET /api/markets | ✅ | state now optional |
| GET /api/markets/{id} | ✅ | |
| GET /api/market-prices | ✅ | freshness labels |
| GET /api/market-prices/compare | ✅ | |
| GET /api/market-prices/history | ✅ | + selling_window signal |
| GET /api/commodities | ✅ | |
| GET /api/commodities/{id} | ✅ | |
| GET /api/buyers | ✅ | source_type, payment_days, pickup_available |
| GET /api/buyers/{id} | ✅ | includes active_requirements |
| GET /api/buyers/{id}/requirements | ✅ | NEW |
| GET /api/saved-markets | ✅ | |
| POST /api/saved-markets/{id} | ✅ | |
| DELETE /api/saved-markets/{id} | ✅ | |
| GET /api/saved-commodities | ✅ | |
| POST /api/saved-commodities/{id} | ✅ | |
| DELETE /api/saved-commodities/{id} | ✅ | |
| GET /api/weather | ✅ | Open-Meteo, transport risk |
| GET /api/msp | ✅ | |
| GET /api/msp/{commodity} | ✅ | |
| GET /api/selling-decision | ✅ | legacy net-realization |
| GET /api/demo/scenarios | ✅ | 13 scenarios listed |
| POST /api/demo/scenarios/{id}/run | ✅ | through real engine |
| POST /api/demo/seed | ✅ | idempotent |

### Demo data (auto-seeded on startup)
- 3 farmer lots (80kg, 120kg, 100kg tomato, Madanapalle, Grade B)
- 7 buyer requirements (all labelled DEMO):
  - Gulf exporter: ₹34/kg, 300kg min, Grade A, 7-day — **NOT_VIABLE** primary demo
  - Packhouse co-op: ₹32/kg, 300kg, Grade B, 7-day — **RECOVERABLE** via aggregation+payment
  - Farm-gate trader: ₹30/kg, 50kg, Grade B, same-day, pickup — **EXECUTABLE**
  - Distant Bengaluru buyer: ₹36/kg, ₹5000 transport — **transport kills net**
  - Quality-only blocker: ₹33/kg, Grade A only — **quality mismatch**
  - Expired contract: deadline passed — **TIMING**
  - Slow-pay agent: ₹31/kg, Grade B, 7-day payment — **PAYMENT only**

### Demo accounts
```
farmer1@krishix.com / password123  — farmer, has 80kg tomato lot
farmer2@krishix.com / password123  — farmer, aggregation participant 120kg
farmer3@krishix.com / password123  — farmer, aggregation participant 100kg
buyer1@krishix.com  / password123  — buyer, linked to demo buyers
```

---

## Primary demo journey that works end-to-end

```
1. Login: farmer1@krishix.com / password123
2. GET /api/lots → see 80kg Grade B tomato lot
3. POST /api/lots/{id}/opportunities/analyze
   → Gulf buyer: NOT_VIABLE (QUANTITY + QUALITY + PAYMENT)
   → Farm-gate: EXECUTABLE (ranked #1)
   → opportunity_gap: ₹4/kg between highest quoted and best executable
4. POST /api/lots/{id}/whatif { "extra_quantity_kg": 220 }
   → Gulf buyer: still NOT_VIABLE (quality + payment still block)
   → Shows dynamic recalculation without changing data
5. GET /api/opportunities/{gulf_id}/recovery applied: AGGREGATION + NEGOTIATE_PAYMENT
   → Combines 80+120+100 = 300kg demo lots
   → Negotiates payment to 2 days
   → BUT quality (Grade A) still blocks → NOT_VIABLE
6. POST /api/opportunities/{farmgate_id}/offer
   → Creates offer for EXECUTABLE farm-gate opportunity
7. POST /api/offers/{id}/accept
   → Creates transaction, status: accepted, payment: agreed
8. POST /api/transactions/{id}/advance × 2
   → pickup_scheduled → payment_pending
9. POST /api/transactions/{id}/payment/report { "demo_as_buyer": true }
   → payment_status: buyer_reported_paid
10. POST /api/transactions/{id}/payment/confirm { "confirmed": true }
    → status: completed, payment_status: payment_confirmed
```

---

## Key API behaviors for frontend

### 1. Feasibility cards
Every opportunity has `feasibility_decision` — use for color-coding.  
Every gap has `explanation` — show verbatim, it's human-readable.  
Every MVC has `feasible: true/false` — show ✓ or ✗ next to recovery options.

### 2. Opportunity gap
`opportunity_gap` in `/analyze` response — show only when non-null.  
Label: "Opportunity gap" never "Lost income".

### 3. What-if
`POST /api/lots/{id}/whatif` — send only the fields you want to change.  
Returns full re-evaluated opportunity list.  
Show clear BEFORE → AFTER comparison.

### 4. Selling window signal
`selling_window` in price history response.  
Always show the `caveat` field. Never hide it.  
`WAIT` signal: must show sell-by deadline warning.

### 5. Demo labels
`source_type: "demo"` → always show "DEMO DATA" badge.  
Never hide demo status. Never imply demo buyers are real.

### 6. Payment disclaimer
`disclaimer` field in transaction/payment response.  
Show it. KrishiX does not move money.

### 7. Economics labels
`economics.labels` object — show below each cost line.  
Never present estimated_net as "guaranteed income".

---

## What is intentionally NOT built

| Feature | Reason |
|---|---|
| Real payment gateway | Would require real financial provider integration |
| AI copilot | No API key required for demo; deterministic engine is enough |
| Admin portal | Not needed for hackathon demo |
| Full dispute resolution | Basic dispute flag is sufficient |
| Nationwide farmer network | Demo aggregation labelled as simulated |
| Blockchain/tokens | Out of scope |
| Push notifications | Out of scope |

---

## Running locally

```bash
# Start everything (Docker required)
docker compose up --build

# Services
# Backend:  http://localhost:8000
# Swagger:  http://localhost:8000/docs
# Frontend: http://localhost:3000 (or :5173 for Vite dev)

# Reset everything
docker compose down -v && docker compose up --build

# Run backend tests (no Docker needed)
cd backend
pip install -r requirements.txt
pip install bcrypt==4.0.1
python -m pytest tests/test_feasibility_engine.py -q
```

---

## Required environment variables

```bash
# Required
DATABASE_URL=postgresql://krishix_user:krishix_password@postgres:5432/krishix_db
SECRET_KEY=minimum-32-character-random-string

# Optional — app works without these
DATA_GOV_API_KEY=     # Live mandi prices from data.gov.in (free registration)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173  # Add your frontend URL
```

No other API keys are needed. Weather (Open-Meteo) and routing (OSRM) work without keys.
