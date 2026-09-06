"""Market API endpoints."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.repository import MarketRepository
from app.schemas import TokenData

router = APIRouter()


def _serialize_market(item) -> dict:
    return {
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


@router.get("/markets")
def list_markets(
    state: Optional[str] = Query(None, description="Filter by state (optional)"),
    district: Optional[str] = Query(None, description="Filter by district (optional)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List markets. State and district are now optional.
    Omitting both returns all markets (useful for map views).
    """
    if state:
        total, items = MarketRepository.get_by_location(
            db, state=state, district=district, limit=limit, offset=offset
        )
    else:
        total, items = MarketRepository.get_all(db, limit=limit, offset=offset)

    return {
        "total": total,
        "items": [_serialize_market(m) for m in items],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/markets/{market_id}")
def get_market(
    market_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get market details by ID."""
    market = MarketRepository.get_by_id(db, market_id)
    if not market:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")
    return {
        **_serialize_market(market),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }
