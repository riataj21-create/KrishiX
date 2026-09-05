"""Market Price API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date, datetime, timezone

from app.database import get_db
from app.schemas import (
    PaginatedResponse, PriceComparisonResponse,
    PriceComparisonItem, PriceTrendResponse, PriceTrendItem
)
from app.repository import MarketPriceRepository, MarketRepository, CommodityRepository

router = APIRouter()


def _freshness_label(price_date: date, source: str) -> str:
    """
    Assign a data freshness label to a price record.
    Never calls data 'LIVE' unless the source actually supports it.
    """
    src = source.lower()
    if "sample" in src or "demo" in src:
        return "DEMO"
    days_old = (datetime.now(timezone.utc).date() - price_date).days
    if days_old == 0:
        return "LATEST_AVAILABLE"
    elif days_old <= 3:
        return "RECENT"
    elif days_old <= 14:
        return "STALE"
    else:
        return f"STALE ({days_old}d old)"


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
    """
    Get market prices with filtering.
    Every price record includes:
    - price_date: the date the price was observed
    - data_freshness: DEMO | LATEST_AVAILABLE | RECENT | STALE
    - source: where the price came from
    Data is never labelled 'LIVE' unless the source supports it.
    """
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
            # Freshness metadata — honest label, never 'LIVE' for batch data
            "data_freshness": _freshness_label(item.price_date, item.source),
            "last_updated": item.last_updated.isoformat(),
            "created_at": item.created_at.isoformat(),
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
    """
    Compare prices for a commodity across multiple markets.
    Uses latest available date if no date given — never assumes today's data exists.
    """
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

    # Use the actual date from data, not date.today()
    actual_date = str(prices[0].price_date) if prices else str(date_filter or date.today())

    return PriceComparisonResponse(
        commodity_id=commodity_id,
        commodity_name=commodity.name,
        date=actual_date,
        prices=comparison_items
    )


@router.get("/market-prices/history", response_model=PriceTrendResponse)
def get_price_history(
    market_id: UUID = Query(...),
    commodity_id: UUID = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get historical price trend for a market-commodity pair.
    Anchors to the latest available date in the database —
    works correctly with sample data regardless of when it was loaded.
    """
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
