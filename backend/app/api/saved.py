"""Saved Markets and Commodities API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas import SavedMarketResponse, SavedCommodityResponse, PaginatedResponse
from app.auth import get_current_user
from app.repository import SavedMarketRepository, SavedCommodityRepository, MarketRepository, CommodityRepository
from app.schemas import TokenData

router = APIRouter()


# ============================================================================
# SAVED MARKETS ENDPOINTS
# ============================================================================

@router.get("/saved-markets", response_model=PaginatedResponse)
def get_saved_markets(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's saved markets."""
    user_id = UUID(token_data.user_id)
    total, items = SavedMarketRepository.get_by_user(db, user_id, limit=limit, offset=offset)
    
    enriched_items = []
    for item in items:
        enriched = {
            "id": str(item.id),
            "market_id": str(item.market_id),
            "market_name": item.market.name,
            "state": item.market.state,
            "district": item.market.district,
            "saved_at": item.saved_at.isoformat()
        }
        enriched_items.append(enriched)
    
    return {"total": total, "items": enriched_items}


@router.post("/saved-markets/{market_id}", response_model=SavedMarketResponse, status_code=status.HTTP_201_CREATED)
def save_market(
    market_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a market to user's favorites."""
    user_id = UUID(token_data.user_id)
    
    # Check if market exists
    market = MarketRepository.get_by_id(db, market_id)
    if not market:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")
    
    # Check if already saved
    existing = SavedMarketRepository.get_by_user_and_market(db, user_id, market_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Market already saved")
    
    saved = SavedMarketRepository.create(db, user_id, market_id)
    return SavedMarketResponse(
        id=saved.id,
        market_id=saved.market_id,
        market_name=market.name,
        state=market.state,
        district=market.district,
        saved_at=saved.saved_at
    )


@router.delete("/saved-markets/{market_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_market(
    market_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove market from user's favorites."""
    user_id = UUID(token_data.user_id)
    deleted = SavedMarketRepository.delete(db, user_id, market_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved market not found")


# ============================================================================
# SAVED COMMODITIES ENDPOINTS
# ============================================================================

@router.get("/saved-commodities", response_model=PaginatedResponse)
def get_saved_commodities(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's saved commodities."""
    user_id = UUID(token_data.user_id)
    total, items = SavedCommodityRepository.get_by_user(db, user_id, limit=limit, offset=offset)
    
    enriched_items = []
    for item in items:
        enriched = {
            "id": str(item.id),
            "commodity_id": str(item.commodity_id),
            "commodity_name": item.commodity.name,
            "category": item.commodity.category,
            "saved_at": item.saved_at.isoformat()
        }
        enriched_items.append(enriched)
    
    return {"total": total, "items": enriched_items}


@router.post("/saved-commodities/{commodity_id}", response_model=SavedCommodityResponse, status_code=status.HTTP_201_CREATED)
def save_commodity(
    commodity_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a commodity to user's favorites."""
    user_id = UUID(token_data.user_id)
    
    # Check if commodity exists
    commodity = CommodityRepository.get_by_id(db, commodity_id)
    if not commodity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commodity not found")
    
    # Check if already saved
    existing = SavedCommodityRepository.get_by_user_and_commodity(db, user_id, commodity_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Commodity already saved")
    
    saved = SavedCommodityRepository.create(db, user_id, commodity_id)
    return SavedCommodityResponse(
        id=saved.id,
        commodity_id=saved.commodity_id,
        commodity_name=commodity.name,
        category=commodity.category,
        saved_at=saved.saved_at
    )


@router.delete("/saved-commodities/{commodity_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_commodity(
    commodity_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove commodity from user's favorites."""
    user_id = UUID(token_data.user_id)
    deleted = SavedCommodityRepository.delete(db, user_id, commodity_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved commodity not found")
