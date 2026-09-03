"""FastAPI application initialization."""
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import (
    User, FarmerProfile, Commodity, Market, MarketPrice,
    SavedMarket, SavedCommodity
)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="KrishiX API",
    description="Market intelligence for smarter agricultural decisions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "KrishiX API"}


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
def root():
    """API root endpoint."""
    return {
        "service": "KrishiX",
        "description": "Market intelligence for smarter agricultural decisions",
        "docs": "/docs",
        "version": "1.0.0"
    }


# ============================================================================
# API ROUTE IMPORTS (Phase 3 - Complete)
# ============================================================================

from app.api import auth, users, farmer_profiles, commodities, markets, prices, saved

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(farmer_profiles.router, prefix="/api", tags=["Farmer Profiles"])
app.include_router(commodities.router, prefix="/api", tags=["Commodities"])
app.include_router(markets.router, prefix="/api", tags=["Markets"])
app.include_router(prices.router, prefix="/api", tags=["Market Prices"])
app.include_router(saved.router, prefix="/api", tags=["Saved Preferences"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
