# KrishiX

KrishiX is an agricultural market-intelligence and selling-decision platform for Indian farmers. It compares available market and buyer opportunities using the farmer's crop, quantity, quality, location, selling window, price requirement, transport preference, and payment requirement.

KrishiX is designed to answer:

```text
Where can I sell this crop?
What is the estimated net realization after selling costs?
Which option is executable, recoverable, not viable, or missing data?
```

It is a decision layer before a transaction. It is not a payment processor, escrow service, guaranteed-price service, or replacement for eNAM.

## Current product flow

1. A farmer signs in or creates an account.
2. The farmer opens **Analyzer** and enters any crop name in one field.
3. Existing commodities appear as suggestions, but the input is not limited to the catalog.
4. New crop names are saved as commodities in the backend.
5. The farmer enters quantity, quality, location, dates, minimum price, and payment requirements.
6. The backend creates the lot and analyzes market and buyer opportunities.
7. Results are ranked by estimated net realization and include feasibility, constraints, recovery options, source type, and data-quality notes.
8. The farmer can inspect opportunities, markets, produce, saved items, activity, buyers, and profile information.

## Important data behavior

KrishiX never invents a market price for a crop.

- A price is shown only when an observed or configured backend price record exists.
- If a crop has no matching market or buyer price, the result is `INSUFFICIENT_DATA`.
- Demo and sample values are labelled as demo/reference data.
- Market price is not the same as guaranteed receipt.
- Transport, market charges, and other cost assumptions are labelled when estimated.
- AI is not required for the core product and must not replace backend feasibility, price, ranking, payment, or transaction logic.

## Features

### Farmer experience

- JWT authentication with bcrypt password hashing.
- Farmer profile and location context.
- Free-text crop/commodity entry with catalog suggestions.
- Farmer produce lots with quantity, grade, dates, price, and payment requirements.
- Backend-backed selling analysis.
- Ranked market and buyer opportunities.
- Executable, recoverable, not-viable, and insufficient-data states.
- Recovery and what-if analysis where supported.
- Offer and transaction lifecycle controls.
- Payment-status tracking without moving money.
- Markets, price observations, saved items, activity, buyers, and profile pages.

### Backend

- FastAPI and SQLAlchemy.
- PostgreSQL for normal deployments; SQLite can be used for local development.
- JWT authentication and role-aware users.
- Commodity, market, price, lot, opportunity, buyer, offer, transaction, payment, weather, MSP, and demo-seed routes.
- Idempotent baseline catalog seed containing 13 sample commodities.
- Central feasibility and opportunity service; React does not independently calculate decisions.

### Frontend

- React 18, TypeScript, Vite, React Router, Tailwind CSS, and Lucide icons.
- Central typed API client in `frontend/src/lib/api.ts`.
- Protected farmer and buyer routes.
- Responsive desktop sidebar and mobile navigation.
- Dark earth / luxury-tech visual system:
  - Midnight `#080B14`
  - Sidebar navy `#0D1020`
  - Elevated surface `#15182A`
  - Aubergine `#24152F`
  - Royal indigo `#5B4BDB`
  - Electric violet `#8B5CF6`
  - Burgundy `#6D2038`
  - Warm gold `#D6A84F`
  - Rich emerald `#176B55`
  - Cream `#F5F1E8`
  - Muted text `#A9A8B3`
- Glass panels, agricultural photography, editorial typography, atmospheric overlays, and restrained transitions.

## Repository layout

```text
KrishiX/
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI route modules
│   │   ├── engines/             # Feasibility and realization logic
│   │   ├── services/            # Opportunity, demo, and catalog services
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── repository.py        # Database access layer
│   │   ├── schemas.py           # Pydantic contracts
│   │   └── main.py              # Application and router registration
│   ├── migrations/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── lib/api.ts           # Typed API client
│   │   └── pages/
│   ├── index.html
│   └── package.json
├── database/
│   └── sample_data.sql
├── docker-compose.yml
└── README.md
```

## Local development

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`.

Build and type-check:

```powershell
npm run build
npm run type-check
```

### Backend

Create a virtual environment and install dependencies:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For local SQLite development:

```powershell
$env:DATABASE_URL = "sqlite:///./test_krishix.db"
$env:SECRET_KEY = "dev-secret"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API runs at `http://localhost:8000` and Swagger UI is available at `http://localhost:8000/docs`.

For PostgreSQL, set `DATABASE_URL` to the deployment connection string before starting the API. Do not commit credentials.

### Demo account

```text
Email:    farmer1@krishix.com
Password: password123
```

Demo and seeded data must be treated as demonstration/reference data, not live adoption or guaranteed market activity.

## API areas

The API is mounted under `/api`:

```text
/api/auth
/api/users
/api/farmer-profile
/api/commodities
/api/markets
/api/market-prices
/api/saved
/api/buyers
/api/weather
/api/msp
/api/lots
/api/lots/{lot_id}/opportunities/analyze
/api/opportunities
/api/transactions
/api/demo
```

The frontend uses the Vite development proxy, so browser requests remain relative to `/api`.

## Environment and secrets

Core KrishiX features do not require an AI API key.

If AI is added later, use a backend-only environment variable such as:

```env
AI_API_KEY=your_key_here
```

Never put provider keys in React code, `VITE_*` variables, committed files, screenshots, or GitHub. AI may explain or summarize backend results, but backend data and deterministic services remain authoritative.

## Validation

The current frontend build command is:

```powershell
cd frontend
npm run build
```

This runs TypeScript checking and the Vite production build.

Backend tests are in `backend/tests` and can be run with the repository's configured pytest environment:

```powershell
cd backend
pytest
```

## Product principles

- Rank by estimated net realization, not raw advertised price.
- Separate observed prices, buyer offers, estimates, and actual transaction states.
- Show source, freshness, and data-quality context.
- Surface constraints instead of hiding them.
- Preserve useful behavior when buyer data is unavailable.
- Never present demo data as verified live adoption.
- Never move money or claim payment guarantees.
