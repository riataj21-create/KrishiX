"""Market API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas import MarketResponse, PaginatedResponse
from app.repository import MarketRepository

router = APIRouter()


@router.get("/markets", response_model=PaginatedResponse)
def list_markets(
    state: str = Query(..., description="State name (required)"),
    district: str = Query(None, description="District name (optional)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List markets filtered by location."""
    total, items = MarketRepository.get_by_location(db, state=state, district=district, limit=limit, offset=offset)
    return {
        "total": total,
        "items": [
            {
                "id": str(item.id),
                "name": item.name,
                "state": item.state,
                "district": item.district,
                "village": item.village,
                "postal_code": item.postal_code,
                "market_type": item.market_type,
                "latitude": float(item.latitude) if item.latitude else None,
                "longitude": float(item.longitude) if item.longitude else None,
                "contact_phone": item.contact_phone,
                "contact_email": item.contact_email,
                "website_url": item.website_url,
                "description": item.description,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in items
        ],
    }


@router.get("/markets/{market_id}", response_model=MarketResponse)
def get_market(market_id: UUID, db: Session = Depends(get_db)):
    """Get market details."""
    market = MarketRepository.get_by_id(db, market_id)
    if not market:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")
    return market
