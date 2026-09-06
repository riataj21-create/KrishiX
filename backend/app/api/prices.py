"""Market Price API endpoints."""
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date, datetime, timezone
from typing import Optional

from app.database import get_db
from app.schemas import (
    PaginatedResponse, PriceComparisonResponse,
    PriceComparisonItem, PriceTrendResponse, PriceTrendItem,
    TokenData,
)
from app.auth import get_current_user
from app.repository import MarketPriceRepository, MarketRepository, CommodityRepository

router = APIRouter()


def _freshness_label(price_date: date, source: str) -> str:
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


def _selling_window_signal(history: list) -> dict:
    """
    Determine a simple sell-now / wait / consider-alternative signal
    based on observed price trend.

    Rules (transparent, not AI):
    - SELL_NOW:  price is at or above 7-day average AND above 3-day average
    - WAIT:      price trending up over last 3 days (>3% increase)
    - CONSIDER_ALTERNATIVE: price trending down over last 3 days (>3% drop)
    - NEUTRAL:   insufficient data or flat trend

    Signal is based on OBSERVED history only.
    Never claims to predict future prices.
    Perishable produce: SELL_NOW signal overrides WAIT if sell_by is today/tomorrow.
    """
    if len(history) < 3:
        return {
            "signal": "NEUTRAL",
            "basis": "INSUFFICIENT_DATA",
            "explanation": "Fewer than 3 data points available — cannot assess trend.",
            "data_points": len(history),
        }

    prices = [float(p.modal_price) for p in history if p.modal_price]
    if len(prices) < 3:
        return {
            "signal": "NEUTRAL",
            "basis": "INSUFFICIENT_DATA",
            "explanation": "Modal price missing from some records.",
            "data_points": len(prices),
        }

    latest = prices[-1]
    prev_3 = prices[-3]
    avg_7 = sum(prices[-7:]) / len(prices[-7:]) if len(prices) >= 7 else sum(prices) / len(prices)
    pct_change_3d = ((latest - prev_3) / prev_3) * 100 if prev_3 > 0 else 0

    if pct_change_3d >= 3.0:
        signal = "WAIT"
        explanation = (
            f"Price has risen {pct_change_3d:.1f}% over the last 3 observed days "
            f"(₹{prev_3:.0f} → ₹{latest:.0f}/quintal). "
            f"Trend suggests prices may continue rising. "
            f"Note: perishable produce has a sell-by deadline — check deadline before waiting."
        )
    elif pct_change_3d <= -3.0:
        signal = "CONSIDER_ALTERNATIVE"
        explanation = (
            f"Price has fallen {abs(pct_change_3d):.1f}% over the last 3 observed days "
            f"(₹{prev_3:.0f} → ₹{latest:.0f}/quintal). "
            f"Selling sooner or considering alternative buyers may be preferable."
        )
    elif latest >= avg_7:
        signal = "SELL_NOW"
        explanation = (
            f"Current price (₹{latest:.0f}/quintal) is at or above the "
            f"{min(len(prices), 7)}-day average (₹{avg_7:.0f}/quintal). "
            f"Conditions are favourable for selling."
        )
    else:
        signal = "NEUTRAL"
        explanation = (
            f"Price (₹{latest:.0f}/quintal) is below the {min(len(prices), 7)}-day "
            f"average (₹{avg_7:.0f}/quintal) but trend is flat. "
            f"No strong signal in either direction."
        )

    return {
        "signal": signal,                  # SELL_NOW | WAIT | CONSIDER_ALTERNATIVE | NEUTRAL
        "basis": "OBSERVED_PRICE_TREND",
        "explanation": explanation,
        "latest_modal_price": latest,
        "three_day_change_pct": round(pct_change_3d, 2),
        "seven_day_average": round(avg_7, 2),
        "data_points_used": len(prices),
        "caveat": (
            "Signal based on observed historical data only. "
            "Not a price prediction. Not financial advice. "
            "Always consider your sell-by deadline before waiting."
        ),
    }


@router.get("/market-prices", response_model=PaginatedResponse)
def get_market_prices(
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    market_id: Optional[str] = Query(None),
    commodity_id: Optional[str] = Query(None),
    date_filter: Optional[date] = Query(None, alias="date"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Get market prices with filtering.
    Every price record includes data_freshness and source.
    Never labelled 'LIVE' unless the source supports it.
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
        offset=offset,
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
            "data_freshness": _freshness_label(item.price_date, item.source),
            "last_updated": item.last_updated.isoformat() if item.last_updated else None,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        enriched_items.append(enriched)

    return {"total": total, "items": enriched_items}


@router.get("/market-prices/compare")
def compare_prices(
    commodity_id: UUID = Query(...),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    date_filter: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db),
):
    """
    Compare prices for a commodity across multiple markets.
    Uses latest available date if no date given.
    """
    commodity = CommodityRepository.get_by_id(db, commodity_id)
    if not commodity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commodity not found")

    prices = MarketPriceRepository.get_commodity_prices_by_date(
        db,
        commodity_id=commodity_id,
        price_date=date_filter,
        state=state,
    )

    comparison_items = [
        {
            "market_id": str(p.market_id),
            "market_name": p.market.name if p.market else None,
            "state": p.market.state if p.market else None,
            "district": p.market.district if p.market else None,
            "modal_price": float(p.modal_price) if p.modal_price else None,
            "min_price": float(p.min_price),
            "max_price": float(p.max_price),
            "quantity_traded": float(p.quantity_traded) if p.quantity_traded else None,
            "price_date": str(p.price_date),
            "data_freshness": _freshness_label(p.price_date, p.source),
            "source": p.source,
        }
        for p in prices
    ]

    actual_date = str(prices[0].price_date) if prices else str(date_filter or date.today())

    return {
        "commodity_id": str(commodity_id),
        "commodity_name": commodity.name,
        "date": actual_date,
        "prices": comparison_items,
        "data_note": "Market price ≠ guaranteed farmer realization. Deduct transport and market charges.",
    }


@router.get("/market-prices/history")
def get_price_history(
    market_id: UUID = Query(...),
    commodity_id: UUID = Query(...),
    days: int = Query(30, ge=1, le=365),
    include_selling_signal: bool = Query(True, description="Include sell-now/wait signal based on observed trend"),
    db: Session = Depends(get_db),
):
    """
    Get historical price trend for a market-commodity pair.
    Anchors to the latest available date in the database.
    Includes selling window signal based on observed trend (not AI, not prediction).
    """
    market = MarketRepository.get_by_id(db, market_id)
    if not market:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")

    commodity = CommodityRepository.get_by_id(db, commodity_id)
    if not commodity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commodity not found")

    history = MarketPriceRepository.get_price_history(db, market_id, commodity_id, days)

    trend = [
        {
            "date": str(p.price_date),
            "min_price": float(p.min_price),
            "max_price": float(p.max_price),
            "modal_price": float(p.modal_price) if p.modal_price else None,
            "quantity_traded": float(p.quantity_traded) if p.quantity_traded else None,
            "data_freshness": _freshness_label(p.price_date, p.source),
            "source": p.source,
        }
        for p in history
    ]

    result = {
        "market_id": str(market_id),
        "market_name": market.name,
        "commodity_id": str(commodity_id),
        "commodity_name": commodity.name,
        "days_requested": days,
        "data_points": len(trend),
        "trend": trend,
        "data_note": (
            "Prices are OBSERVED historical data. Not predictions. "
            "Source and observation date shown per record."
        ),
    }

    if include_selling_signal:
        result["selling_window"] = _selling_window_signal(history)

    return result



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
