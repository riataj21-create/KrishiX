"""Market Price API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date

from app.database import get_db
from app.schemas import (
    MarketPriceWithDetails, PaginatedResponse, PriceComparisonResponse,
    PriceComparisonItem, PriceTrendResponse, PriceTrendItem
)
from app.repository import MarketPriceRepository, MarketRepository, CommodityRepository

router = APIRouter()


@router.get("/market-prices", response_model=PaginatedResponse)
def get_market_prices(
    state: str = Query(None),
    district: str = Query(None),
    market_id: str = Query(None),
    commodity_id: str = Query(None),
    date_filter: date = Query(None, alias="date"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get market prices with filtering."""
    market_id_uuid = UUID(market_id) if market_id else None
    commodity_id_uuid = UUID(commodity_id) if commodity_id else None
    
    total, items = MarketPriceRepository.get_latest_prices(
        db,
        state=state,
        district=district,
        market_id=market_id_uuid,
        commodity_id=commodity_id_uuid,
        price_date=date_filter,
        limit=limit,
        offset=offset
    )
    
    # Enrich with market and commodity names
    enriched_items = []
    for item in items:
        enriched = {
            "id": str(item.id),
            "market_id": str(item.market_id),
            "market_name": item.market.name if item.market else None,
            "commodity_id": str(item.commodity_id),
            "commodity_name": item.commodity.name if item.commodity else None,
            "state": item.market.state if item.market else None,
            "district": item.market.district if item.market else None,
            "price_date": str(item.price_date),
            "min_price": float(item.min_price),
            "max_price": float(item.max_price),
            "modal_price": float(item.modal_price) if item.modal_price else None,
            "quantity_traded": float(item.quantity_traded) if item.quantity_traded else None,
            "source": item.source,
            "last_updated": item.last_updated.isoformat(),
            "created_at": item.created_at.isoformat()
        }
        enriched_items.append(enriched)
    
    return {"total": total, "items": enriched_items}


@router.get("/market-prices/compare", response_model=PriceComparisonResponse)
def compare_prices(
    commodity_id: UUID = Query(...),
    state: str = Query(None),
    district: str = Query(None),
    date_filter: date = Query(None, alias="date"),
    db: Session = Depends(get_db)
):
    """Compare prices for a commodity across multiple markets."""
    commodity = CommodityRepository.get_by_id(db, commodity_id)
    if not commodity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commodity not found")
    
    prices = MarketPriceRepository.get_commodity_prices_by_date(
        db,
        commodity_id=commodity_id,
        price_date=date_filter,
        state=state
    )
    
    comparison_items = []
    for price in prices:
        item = PriceComparisonItem(
            market_id=price.market_id,
            market_name=price.market.name,
            state=price.market.state,
            district=price.market.district,
            modal_price=price.modal_price,
            min_price=price.min_price,
            max_price=price.max_price,
            quantity_traded=price.quantity_traded
        )
        comparison_items.append(item)
    
    return PriceComparisonResponse(
        commodity_id=commodity_id,
        commodity_name=commodity.name,
        date=str(date_filter or date.today()),
        prices=comparison_items
    )


@router.get("/market-prices/history", response_model=PriceTrendResponse)
def get_price_history(
    market_id: UUID = Query(...),
    commodity_id: UUID = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get historical price trend for a market-commodity pair."""
    market = MarketRepository.get_by_id(db, market_id)
    if not market:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")
    
    commodity = CommodityRepository.get_by_id(db, commodity_id)
    if not commodity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commodity not found")
    
    history = MarketPriceRepository.get_price_history(db, market_id, commodity_id, days)
    
    trend_items = [
        PriceTrendItem(
            date=str(price.price_date),
            min_price=price.min_price,
            max_price=price.max_price,
            modal_price=price.modal_price
        )
        for price in history
    ]
    
    return PriceTrendResponse(
        market_id=market_id,
        market_name=market.name,
        commodity_id=commodity_id,
        commodity_name=commodity.name,
        trend=trend_items
    )
