"""FastAPI application initialization."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, get_db
import app.models  # noqa: F401 — registers all models with Base.metadata

# Create all tables (idempotent; Alembic handles schema changes)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KrishiX API",
    description="Agricultural market intelligence and transaction-feasibility platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:8080,http://localhost:8000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ───────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "KrishiX API", "version": "2.0.0"}


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "KrishiX",
        "description": "Agricultural market intelligence and transaction-feasibility platform",
        "docs": "/docs",
        "version": "2.0.0",
    }


# ── Routers ──────────────────────────────────────────────────────────────────
from app.api import (  # noqa: E402
    auth, users, farmer_profiles,
    commodities, markets, prices,
    saved, decisions, buyers,
    weather, msp,
    lots, opportunities, transactions, demo,
)

app.include_router(auth.router,             prefix="/api/auth",         tags=["Authentication"])
app.include_router(users.router,            prefix="/api/users",        tags=["Users"])
app.include_router(farmer_profiles.router,  prefix="/api",              tags=["Farmer Profiles"])
app.include_router(commodities.router,      prefix="/api",              tags=["Commodities"])
app.include_router(markets.router,          prefix="/api",              tags=["Markets"])
app.include_router(prices.router,           prefix="/api",              tags=["Market Prices"])
app.include_router(saved.router,            prefix="/api",              tags=["Saved"])
app.include_router(decisions.router,        prefix="/api",              tags=["Selling Decision"])
app.include_router(buyers.router,           prefix="/api",              tags=["Buyers"])
app.include_router(weather.router,          prefix="/api",              tags=["Weather"])
app.include_router(msp.router,              prefix="/api",              tags=["MSP"])
# ── New v2 routers ───────────────────────────────────────────────────────────
app.include_router(lots.router,             prefix="/api",              tags=["Lots"])
app.include_router(opportunities.router,    prefix="/api",              tags=["Opportunities"])
app.include_router(transactions.router,     prefix="/api",              tags=["Transactions"])
app.include_router(demo.router,             prefix="/api/demo",         tags=["Demo"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
