"""
MSP (Minimum Support Price) API

GET /api/msp              — list all MSP rates
GET /api/msp/{commodity}  — get MSP for a specific commodity

MSP is the government-declared floor price for agricultural commodities.
It is a REFERENCE VALUE, not a guaranteed price available to every farmer
in every market.

Data source: Cabinet Committee on Economic Affairs (CCEA), Government of India
Data type: SOURCE_BACKED — official government notifications
Scope: Pan-India (central government MSP)
Note: Some states offer additional bonuses above central MSP.
      Actual procurement depends on government agencies being present
      in the farmer's market. MSP does not guarantee a buyer.

These values are hardcoded from official notifications and must be
updated when the government announces new MSP rates each season.
Last updated: Kharif 2024-25 and Rabi 2024-25 announcements.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional

router = APIRouter()

# ---------------------------------------------------------------------------
# MSP data — SOURCE_BACKED
# Source: CCEA notifications, Government of India
# Season: Kharif 2024-25 and Rabi 2024-25
# Unit: ₹ per quintal
# Note: Update these values each crop season from official PIB announcements.
# ---------------------------------------------------------------------------
MSP_DATA = {
    # Kharif crops 2024-25
    "Rice": {
        "msp_per_quintal": 2300.00,
        "season": "Kharif 2024-25",
        "announced_date": "2024-06-19",
        "source": "CCEA, Government of India",
        "note": "Common grade. A-grade MSP is ₹20 higher."
    },
    "Maize": {
        "msp_per_quintal": 2225.00,
        "season": "Kharif 2024-25",
        "announced_date": "2024-06-19",
        "source": "CCEA, Government of India",
        "note": None
    },

    # Rabi crops 2024-25
    "Wheat": {
        "msp_per_quintal": 2275.00,
        "season": "Rabi 2024-25",
        "announced_date": "2023-10-18",
        "source": "CCEA, Government of India",
        "note": None
    },

    # Other kharif crops
    "Onion": {
        "msp_per_quintal": None,
        "season": None,
        "announced_date": None,
        "source": None,
        "note": "Onion does not have a central government MSP. "
                "Some states run procurement schemes during glut periods."
    },
    "Tomato": {
        "msp_per_quintal": None,
        "season": None,
        "announced_date": None,
        "source": None,
        "note": "Tomato does not have a central government MSP. "
                "Price stabilisation may occur through NAFED operations."
    },
    "Potato": {
        "msp_per_quintal": None,
        "season": None,
        "announced_date": None,
        "source": None,
        "note": "Potato does not have a central government MSP."
    },
    "Turmeric": {
        "msp_per_quintal": None,
        "season": None,
        "announced_date": None,
        "source": None,
        "note": "Turmeric does not currently have a central government MSP. "
                "Discussions about inclusion are ongoing."
    },
}


def _build_comparison(commodity_name: str, current_price: Optional[float]) -> dict:
    """Build MSP comparison for a commodity against a current market price."""
    entry = MSP_DATA.get(commodity_name)
    if not entry:
        return {
            "commodity": commodity_name,
            "has_msp": False,
            "note": f"No MSP data available for '{commodity_name}' in this system.",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    msp = entry["msp_per_quintal"]
    result = {
        "commodity": commodity_name,
        "has_msp": msp is not None,
        "msp_per_quintal": msp,
        "season": entry["season"],
        "announced_date": entry["announced_date"],
        "source": entry["source"],
        "data_type": "SOURCE_BACKED" if msp else "NOT_APPLICABLE",
        "note": entry["note"],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }

    # Add comparison if current price provided
    if current_price is not None and msp is not None:
        diff = current_price - msp
        pct_above = (diff / msp) * 100 if msp > 0 else 0
        result["current_price_comparison"] = {
            "current_price_per_quintal": current_price,
            "difference_vs_msp": round(diff, 2),
            "pct_above_msp": round(pct_above, 1),
            "status": "ABOVE_MSP" if diff >= 0 else "BELOW_MSP",
            "alert": (
                f"Current market price ₹{current_price:,.0f} is BELOW MSP ₹{msp:,.0f}. "
                "Government procurement may be available through your state's procurement agency."
                if diff < 0 else None
            ),
        }

    return result


@router.get("/msp")
def list_msp(
    commodity: Optional[str] = Query(None, description="Filter by commodity name"),
):
    """
    List MSP (Minimum Support Price) reference rates.

    MSP is a government-declared floor price. It is a reference value,
    not a guaranteed price. Actual procurement depends on government
    agencies operating in your market.

    Data: SOURCE_BACKED — CCEA, Government of India notifications.
    Must be updated each crop season.
    """
    if commodity:
        # Try exact match first, then case-insensitive
        match = MSP_DATA.get(commodity) or next(
            (v for k, v in MSP_DATA.items() if k.lower() == commodity.lower()),
            None
        )
        commodity_key = commodity if commodity in MSP_DATA else next(
            (k for k in MSP_DATA if k.lower() == commodity.lower()), commodity
        )
        return _build_comparison(commodity_key, None)

    return {
        "data_type": "SOURCE_BACKED",
        "source": "CCEA, Government of India",
        "note": (
            "MSP is a reference floor price. Not all commodities have MSP. "
            "Actual procurement availability depends on your state and market."
        ),
        "items": [
            {
                "commodity": name,
                "msp_per_quintal": entry["msp_per_quintal"],
                "season": entry["season"],
                "has_msp": entry["msp_per_quintal"] is not None,
            }
            for name, entry in MSP_DATA.items()
        ],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/msp/compare")
def compare_with_msp(
    commodity: str = Query(..., description="Commodity name"),
    current_price: float = Query(..., gt=0, description="Current market price in ₹/quintal"),
):
    """
    Compare a current market price against MSP.
    Returns ABOVE_MSP or BELOW_MSP with the difference and an alert if below.
    """
    commodity_key = commodity if commodity in MSP_DATA else next(
        (k for k in MSP_DATA if k.lower() == commodity.lower()), commodity
    )
    return _build_comparison(commodity_key, current_price)
