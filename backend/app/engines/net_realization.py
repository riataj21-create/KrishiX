"""
Net Realization Engine

Calculates the estimated amount a farmer actually receives after all
selling costs are deducted from the gross sale value.

IMPORTANT: Every cost assumption in this file is explicitly labelled with:
  - assumption_type: ESTIMATED | CONFIGURED | SOURCE_BACKED | DEMO
  - source: where the value comes from
  - scope: which region/commodity/context it applies to
  - unit: what the number represents

No value is presented as a universal authoritative fact.
All estimates must be shown to the farmer with their labels.

The formula:
  Gross = modal_price_per_quintal × quantity_quintal
  Net   = Gross
        - transport_cost      (road_km × rate_per_km_per_quintal × quintals)
        - mandi_charges       (cess_pct × Gross + flat_market_fee)
        - loading_unloading   (flat_per_quintal × quintals)

Distance: Haversine straight-line between farmer GPS and market GPS.
OSRM road distance is preferred but we fall back to Haversine × 1.3
(the 1.3 factor accounts for road curvature — labelled as ESTIMATED).
"""

import math
import logging
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger("krishix.engine.net_realization")

# ---------------------------------------------------------------------------
# Cost assumptions — ALL labelled explicitly
# ---------------------------------------------------------------------------

# Transport cost per quintal per km
# assumption_type: ESTIMATED
# source: General agricultural logistics estimates for medium trucks in India
# scope: All states, all commodities (crop/vehicle-specific rates vary)
# unit: ₹ per quintal per km
# note: Actual rate depends on vehicle type, diesel price, load factor.
#       This is a mid-range estimate for a 5-tonne truck.
#       Farmer can override via query param.
DEFAULT_TRANSPORT_RATE_PER_QTL_PER_KM = 0.50  # ₹/quintal/km

# Road distance correction factor when OSRM is unavailable
# assumption_type: ESTIMATED
# source: Rule of thumb — Indian roads average 1.2–1.4x straight-line distance
# scope: India (plains regions); hill routes may be significantly higher
HAVERSINE_TO_ROAD_FACTOR = 1.3

# Loading and unloading charges
# assumption_type: ESTIMATED
# source: Commonly observed range in North Indian APMC markets (₹100–₹250/quintal)
# scope: Punjab, Haryana, UP — may differ significantly in other states
# unit: ₹ per quintal (both loading at farm + unloading at mandi)
DEFAULT_LOADING_UNLOADING_PER_QTL = 150.0  # ₹/quintal

# State-wise mandi cess / market fee percentages
# assumption_type: SOURCE_BACKED (official state APMC Acts — approximate)
# source: Various state APMC regulations (approximate; actual rates vary by
#         commodity, market, and year — verify before use in production)
# unit: fraction of gross sale value
STATE_MANDI_CESS = {
    "Punjab":        0.020,   # ~2% (APMC Punjab)
    "Haryana":       0.020,   # ~2% (APMC Haryana)
    "Uttar Pradesh": 0.025,   # ~2.5% (APMC UP)
    "Maharashtra":   0.010,   # ~1% (APMC Maharashtra — reduced after reforms)
    "Karnataka":     0.015,   # ~1.5%
    "Rajasthan":     0.016,   # ~1.6%
    "Madhya Pradesh": 0.020,  # ~2%
    "Gujarat":       0.010,   # ~1%
    "Andhra Pradesh": 0.010,  # ~1%
    "Telangana":     0.010,   # ~1%
}
DEFAULT_MANDI_CESS = 0.020   # fallback if state not in table — ESTIMATED

# Flat market fee per transaction (separate from cess)
# assumption_type: ESTIMATED
# source: Commonly observed range across mandis
# unit: ₹ per transaction (not per quintal)
DEFAULT_MARKET_FEE_FLAT = 50.0  # ₹ per transaction


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CostBreakdown:
    """Fully labelled cost breakdown for one market option."""
    market_id: str
    market_name: str
    state: str
    district: str
    market_lat: Optional[float]
    market_lon: Optional[float]

    # Price data
    modal_price_per_quintal: float
    price_date: str
    price_source: str           # "Sample Data" | "data.gov.in" etc.
    price_freshness: str        # "DEMO" | "LATEST_AVAILABLE" | "STALE"

    # Distance
    distance_km: float
    distance_method: str        # "OSRM_ROAD" | "HAVERSINE_ESTIMATED"
    distance_note: str

    # Costs — all labelled
    gross_value: float
    transport_cost: float
    transport_rate_per_qkm: float
    transport_assumption: str   # label for UI

    mandi_cess_pct: float
    mandi_cess_amount: float
    mandi_cess_assumption: str

    loading_unloading: float
    loading_assumption: str

    market_fee_flat: float

    # Result
    estimated_net: float
    net_per_quintal: float

    # Ranking context
    rank: int = 0
    vs_best_rupees: float = 0.0   # difference vs #1 option


@dataclass
class SellingDecisionResult:
    """Full ranked result returned by the engine."""
    commodity_id: str
    commodity_name: str
    quantity_quintal: float
    farmer_lat: float
    farmer_lon: float
    price_observation_date: str
    options: list           # list[CostBreakdown] sorted by estimated_net desc
    recommendation_text: str
    data_caveat: str


# ---------------------------------------------------------------------------
# Distance helpers
# ---------------------------------------------------------------------------

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Straight-line distance in km between two GPS coordinates."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def _osrm_road_distance_km(
    src_lat: float, src_lon: float,
    dst_lat: float, dst_lon: float
) -> Optional[float]:
    """
    Fetch real road distance from OSRM public API.
    Returns None if OSRM is unavailable — caller falls back to Haversine.
    OSRM is free and requires no API key.
    """
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{src_lon},{src_lat};{dst_lon},{dst_lat}"
        f"?overview=false"
    )
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == "Ok" and data.get("routes"):
                return data["routes"][0]["distance"] / 1000.0  # metres → km
    except Exception as exc:
        logger.warning("OSRM unavailable (%s) — falling back to Haversine", exc)
    return None


async def get_distance_km(
    farmer_lat: float, farmer_lon: float,
    market_lat: float, market_lon: float,
) -> tuple[float, str, str]:
    """
    Returns (distance_km, method, note).
    Tries OSRM first, falls back to Haversine × correction factor.
    """
    road_km = await _osrm_road_distance_km(farmer_lat, farmer_lon, market_lat, market_lon)
    if road_km is not None:
        return (
            road_km,
            "OSRM_ROAD",
            "Actual road distance from OSRM routing engine (router.project-osrm.org)",
        )

    straight_km = _haversine_km(farmer_lat, farmer_lon, market_lat, market_lon)
    estimated_km = straight_km * HAVERSINE_TO_ROAD_FACTOR
    return (
        estimated_km,
        "HAVERSINE_ESTIMATED",
        (
            f"Estimated road distance: straight-line {straight_km:.1f} km × {HAVERSINE_TO_ROAD_FACTOR} "
            f"correction factor (OSRM unavailable). Actual road distance may differ, "
            f"especially in hilly terrain."
        ),
    )


# ---------------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------------

def _price_freshness_label(source: str) -> str:
    """Assign a freshness label based on price source."""
    s = source.lower()
    if "sample" in s or "demo" in s:
        return "DEMO"
    if "data.gov" in s or "agmarknet" in s:
        return "LATEST_AVAILABLE"
    return "LATEST_AVAILABLE"


def calculate_net_realization(
    market_id: str,
    market_name: str,
    state: str,
    district: str,
    market_lat: Optional[float],
    market_lon: Optional[float],
    modal_price_per_quintal: float,
    price_date: str,
    price_source: str,
    quantity_quintal: float,
    distance_km: float,
    distance_method: str,
    distance_note: str,
    transport_rate_override: Optional[float] = None,
) -> CostBreakdown:
    """
    Calculate estimated net realization for selling at one market.
    All cost assumptions are labelled in the returned object.
    """
    # Transport
    rate = transport_rate_override if transport_rate_override is not None else DEFAULT_TRANSPORT_RATE_PER_QTL_PER_KM
    transport_cost = rate * distance_km * quantity_quintal
    if transport_rate_override is not None:
        transport_assumption = "USER_PROVIDED — transport rate entered by farmer"
    else:
        transport_assumption = (
            f"ESTIMATED — ₹{rate}/quintal/km (mid-range estimate for 5-tonne truck; "
            "actual rate depends on vehicle type, diesel price, and route)"
        )

    # Mandi cess
    cess_pct = STATE_MANDI_CESS.get(state, DEFAULT_MANDI_CESS)
    gross = modal_price_per_quintal * quantity_quintal
    cess_amount = cess_pct * gross

    if state in STATE_MANDI_CESS:
        cess_assumption = (
            f"SOURCE_BACKED — approximate {cess_pct*100:.1f}% based on {state} "
            "APMC regulations (verify current rate before use in production)"
        )
    else:
        cess_assumption = (
            f"ESTIMATED — {cess_pct*100:.1f}% default applied (state-specific rate "
            f"for '{state}' not in database)"
        )

    # Loading / unloading
    loading = DEFAULT_LOADING_UNLOADING_PER_QTL * quantity_quintal
    loading_assumption = (
        f"ESTIMATED — ₹{DEFAULT_LOADING_UNLOADING_PER_QTL}/quintal "
        "(commonly observed range in North Indian APMC markets; "
        "actual charges vary by market and commodity)"
    )

    # Market flat fee
    market_fee = DEFAULT_MARKET_FEE_FLAT

    # Net
    net = gross - transport_cost - cess_amount - loading - market_fee
    net_per_quintal = net / quantity_quintal if quantity_quintal > 0 else 0.0

    return CostBreakdown(
        market_id=market_id,
        market_name=market_name,
        state=state,
        district=district,
        market_lat=market_lat,
        market_lon=market_lon,
        modal_price_per_quintal=round(modal_price_per_quintal, 2),
        price_date=price_date,
        price_source=price_source,
        price_freshness=_price_freshness_label(price_source),
        distance_km=round(distance_km, 2),
        distance_method=distance_method,
        distance_note=distance_note,
        gross_value=round(gross, 2),
        transport_cost=round(transport_cost, 2),
        transport_rate_per_qkm=rate,
        transport_assumption=transport_assumption,
        mandi_cess_pct=round(cess_pct * 100, 2),
        mandi_cess_amount=round(cess_amount, 2),
        mandi_cess_assumption=cess_assumption,
        loading_unloading=round(loading, 2),
        loading_assumption=loading_assumption,
        market_fee_flat=round(market_fee, 2),
        estimated_net=round(net, 2),
        net_per_quintal=round(net_per_quintal, 2),
    )


def rank_options(options: list[CostBreakdown]) -> list[CostBreakdown]:
    """
    Rank options by estimated net realization (highest first).
    Attaches rank and vs_best_rupees to each option.

    Note: Net rupees is the primary ranking factor here.
    The calling endpoint should also surface payment_terms and other
    non-financial factors so the farmer can make an informed decision.
    Highest net ≠ always best — but it is the primary quantitative signal.
    """
    sorted_options = sorted(options, key=lambda x: x.estimated_net, reverse=True)
    best_net = sorted_options[0].estimated_net if sorted_options else 0.0
    for i, opt in enumerate(sorted_options):
        opt.rank = i + 1
        opt.vs_best_rupees = round(opt.estimated_net - best_net, 2)
    return sorted_options


def build_recommendation_text(options: list[CostBreakdown], commodity_name: str) -> str:
    """
    Build a plain-language recommendation string.
    Does NOT claim certainty — presents the best available option
    based on estimated net realization.
    """
    if not options:
        return "No market price data available to generate a recommendation."

    best = options[0]
    if len(options) == 1:
        return (
            f"Only one market has price data for {commodity_name}. "
            f"Estimated net at {best.market_name}: ₹{best.estimated_net:,.0f} "
            f"for {best.market_name} after estimated transport and mandi charges."
        )

    second = options[1]
    diff = abs(best.estimated_net - second.estimated_net)
    return (
        f"Based on estimated net realization, {best.market_name} is the best available option "
        f"(₹{best.estimated_net:,.0f} estimated in hand). "
        f"This is ₹{diff:,.0f} more than {second.market_name} after estimated transport and charges. "
        f"All cost figures are estimates — verify actual charges before travelling."
    )
