"""
Selling Decision API

GET /api/selling-decision

The core KrishiX endpoint. Given a farmer's crop, quantity, and GPS location,
it returns all markets with available price data ranked by estimated net
realization — not by raw price.

Every cost assumption in the response is explicitly labelled.
Data freshness is shown for every price record.
The recommendation is explainable, not an opaque AI score.

The endpoint works even when:
- OSRM is down (falls back to Haversine × 1.3)
- Some markets have no price data (those markets are omitted with a note)
- Farmer has no GPS (state-level fallback using district centre coordinates)
"""

import logging
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.engines.net_realization import (
    build_recommendation_text,
    calculate_net_realization,
    get_distance_km,
    rank_options,
)
from app.repository import CommodityRepository, MarketPriceRepository
from app.schemas import TokenData

logger = logging.getLogger("krishix.api.decisions")
router = APIRouter()


# ---------------------------------------------------------------------------
# District-centre fallback coordinates
# Used when farmer has no GPS recorded in their profile.
# assumption_type: ESTIMATED — approximate district centres
# ---------------------------------------------------------------------------
DISTRICT_CENTRES: dict[str, tuple[float, float]] = {
    "Ludhiana":   (30.9000, 75.8573),
    "Nashik":     (19.9975, 73.7898),
    "Hisar":      (29.1897, 75.7330),
    "Amritsar":   (31.6340, 74.8723),
    "Jalandhar":  (31.3260, 75.5762),
    "Pune":       (18.5204, 73.8567),
    "Nagpur":     (21.1458, 79.0882),
    "Rohtak":     (28.8955, 76.6066),
    "Karnal":     (29.6857, 76.9905),
    "Meerut":     (28.9845, 77.7064),
    "Agra":       (27.1767, 78.0081),
    "Madanapalle":(13.5504, 78.5024),
}

STATE_CENTRES: dict[str, tuple[float, float]] = {
    "Punjab":        (30.9000, 75.8573),
    "Maharashtra":   (19.9975, 73.7898),
    "Haryana":       (29.1897, 75.7330),
    "Uttar Pradesh": (26.8467, 80.9462),
    "Karnataka":     (15.3173, 75.7139),
    "Rajasthan":     (27.0238, 74.2179),
}


def _resolve_farmer_location(
    farmer_lat: Optional[float],
    farmer_lon: Optional[float],
    district: Optional[str],
    state: Optional[str],
) -> tuple[float, float, str]:
    """
    Returns (lat, lon, location_note).
    Priority: explicit GPS > district centre > state centre > India centre.
    """
    if farmer_lat is not None and farmer_lon is not None:
        return farmer_lat, farmer_lon, "GPS coordinates from farmer profile"

    if district and district in DISTRICT_CENTRES:
        lat, lon = DISTRICT_CENTRES[district]
        return lat, lon, (
            f"ESTIMATED — using approximate centre of {district} district "
            "(farmer GPS not recorded in profile)"
        )

    if state and state in STATE_CENTRES:
        lat, lon = STATE_CENTRES[state]
        return lat, lon, (
            f"ESTIMATED — using approximate centre of {state} state "
            "(farmer district/GPS not recorded in profile)"
        )

    # Last resort: central India
    return 22.9734, 78.6569, (
        "ESTIMATED — farmer location unknown; using central India coordinates. "
        "Distance calculations will be inaccurate. Please update your profile with your location."
    )


def _price_date_freshness(price_date_str: str, source: str) -> str:
    """Determine a freshness label from the price date and source."""
    src_lower = source.lower()
    if "sample" in src_lower or "demo" in src_lower:
        return "DEMO"
    try:
        price_date = datetime.strptime(price_date_str, "%Y-%m-%d").date()
        days_old = (datetime.now(timezone.utc).date() - price_date).days
        if days_old == 0:
            return "LATEST_AVAILABLE"
        elif days_old <= 3:
            return "RECENT"
        elif days_old <= 14:
            return "STALE"
        else:
            return f"STALE ({days_old} days old)"
    except Exception:
        return "UNKNOWN"


@router.get("/selling-decision")
async def get_selling_decision(
    commodity_id: UUID = Query(..., description="Commodity UUID"),
    quantity_quintal: float = Query(..., gt=0, description="Quantity farmer wants to sell in quintals"),
    farmer_lat: Optional[float] = Query(None, ge=-90, le=90, description="Farmer GPS latitude"),
    farmer_lon: Optional[float] = Query(None, ge=-180, le=180, description="Farmer GPS longitude"),
    state: Optional[str] = Query(None, description="Farmer's state (used if GPS not available)"),
    district: Optional[str] = Query(None, description="Farmer's district (used if GPS not available)"),
    transport_rate: Optional[float] = Query(
        None, gt=0,
        description="Farmer-provided transport rate in ₹/quintal/km (overrides default estimate)"
    ),
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return ranked selling options with estimated net realization for a crop.

    WHERE should I sell? — markets ranked by ₹ in hand after all estimated costs.

    The response includes:
    - Estimated net realization per market (not just raw price)
    - Every cost assumption clearly labelled (ESTIMATED / SOURCE_BACKED / USER_PROVIDED)
    - Data freshness label per price record
    - Distance method (OSRM_ROAD or HAVERSINE_ESTIMATED)
    - Plain-language recommendation text
    - Data caveat reminding farmer these are estimates

    Works even when OSRM is unavailable or farmer has no GPS.
    """
    # 1. Validate commodity exists
    commodity = CommodityRepository.get_by_id(db, commodity_id)
    if not commodity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commodity '{commodity_id}' not found"
        )

    # 2. Resolve farmer location
    f_lat, f_lon, location_note = _resolve_farmer_location(
        farmer_lat, farmer_lon, district, state
    )

    # 3. Get latest prices for this commodity across all markets
    prices = MarketPriceRepository.get_commodity_prices_by_date(
        db,
        commodity_id=commodity_id,
        price_date=None,   # auto-selects MAX(price_date)
        state=None,        # all states — farmer may want to compare across states
        limit=20,
    )

    if not prices:
        return {
            "commodity_id": str(commodity_id),
            "commodity_name": commodity.name,
            "quantity_quintal": quantity_quintal,
            "farmer_location": {
                "latitude": f_lat,
                "longitude": f_lon,
                "note": location_note,
            },
            "options": [],
            "recommendation": "No market price data is currently available for this commodity.",
            "data_caveat": (
                "No price records found. This may mean the commodity has not been "
                "priced recently in any seeded market. Try a different commodity."
            ),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    # 4. Calculate net realization for each market
    options = []
    skipped_markets = []

    for price_record in prices:
        market = price_record.market

        if market is None:
            continue

        # Skip markets with no GPS — can't calculate distance
        if market.latitude is None or market.longitude is None:
            skipped_markets.append({
                "market_name": market.name,
                "reason": "Market has no GPS coordinates — distance cannot be calculated"
            })
            continue

        if price_record.modal_price is None:
            skipped_markets.append({
                "market_name": market.name,
                "reason": "Modal price not available for this market"
            })
            continue

        # Get distance (async — tries OSRM first, falls back to Haversine)
        distance_km, distance_method, distance_note = await get_distance_km(
            f_lat, f_lon,
            float(market.latitude), float(market.longitude)
        )

        price_date_str = str(price_record.price_date)
        freshness = _price_date_freshness(price_date_str, price_record.source)

        breakdown = calculate_net_realization(
            market_id=str(market.id),
            market_name=market.name,
            state=market.state,
            district=market.district,
            market_lat=float(market.latitude),
            market_lon=float(market.longitude),
            modal_price_per_quintal=float(price_record.modal_price),
            price_date=price_date_str,
            price_source=price_record.source,
            quantity_quintal=quantity_quintal,
            distance_km=distance_km,
            distance_method=distance_method,
            distance_note=distance_note,
            transport_rate_override=transport_rate,
        )
        # Attach freshness directly (engine returns price_source but not freshness label)
        breakdown.price_freshness = freshness
        options.append(breakdown)

    # 5. Rank by estimated net
    ranked = rank_options(options)

    # 6. Observation date (the price_date of the data used)
    obs_date = str(prices[0].price_date) if prices else "unknown"

    # 7. Recommendation text
    recommendation = build_recommendation_text(ranked, commodity.name)

    return {
        "commodity_id": str(commodity_id),
        "commodity_name": commodity.name,
        "quantity_quintal": quantity_quintal,
        "price_observation_date": obs_date,
        "data_status": "DEMO" if prices and "Sample" in prices[0].source else "LATEST_AVAILABLE",
        "farmer_location": {
            "latitude": f_lat,
            "longitude": f_lon,
            "note": location_note,
        },
        "options": [asdict(o) for o in ranked],
        "skipped_markets": skipped_markets,
        "recommendation": recommendation,
        "data_caveat": (
            "All cost figures (transport, mandi charges, loading) are estimates. "
            "Actual costs depend on vehicle type, market-specific fees, and current diesel prices. "
            "Verify charges with the market before travelling. "
            "This is decision support — not a guaranteed price or financial advice."
        ),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }
