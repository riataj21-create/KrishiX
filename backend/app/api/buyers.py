"""
Buyers API

GET /api/buyers      — list/filter buyers (WHO should I sell to?)
GET /api/buyers/{id} — single buyer detail

IMPORTANT — Cold-start transparency:
The buyer records returned are DEMO seed data for the hackathon demonstration.
They are NOT real registered marketplace users.
Every response includes a data_status field to make this explicit.

When real buyers register on the platform, they will appear here alongside
or instead of the demo records. The empty-state case (no buyers match) is
handled correctly — the selling decision still works without buyers.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.repository import BuyerRepository
from app.schemas import TokenData

logger = logging.getLogger("krishix.api.buyers")
router = APIRouter()


def _serialize_buyer(buyer) -> dict:
    """Serialize a Buyer ORM object to a plain dict."""
    return {
        "id": str(buyer.id),
        "name": buyer.name,
        "buyer_type": buyer.buyer_type,
        "contact_name": buyer.contact_name,
        "contact_phone": buyer.contact_phone,
        "contact_email": buyer.contact_email,
        "state": buyer.state,
        "district": buyer.district,
        "city": buyer.city,
        "latitude": float(buyer.latitude) if buyer.latitude else None,
        "longitude": float(buyer.longitude) if buyer.longitude else None,
        "commodity_name": buyer.commodity_name,
        "min_quantity_quintal": float(buyer.min_quantity_quintal) if buyer.min_quantity_quintal else None,
        "max_quantity_quintal": float(buyer.max_quantity_quintal) if buyer.max_quantity_quintal else None,
        "quality_grade": buyer.quality_grade,
        "price_premium_pct": float(buyer.price_premium_pct) if buyer.price_premium_pct else 0.0,
        "is_verified": buyer.is_verified,
        "years_active": buyer.years_active,
        "rating": float(buyer.rating) if buyer.rating else None,
        "payment_terms": buyer.payment_terms,
        "notes": buyer.notes,
        "whatsapp_link": (
            f"https://wa.me/91{buyer.contact_phone.replace(' ', '').replace('-', '')}"
            if buyer.contact_phone else None
        ),
    }


@router.get("/buyers")
def list_buyers(
    commodity: Optional[str] = Query(
        None,
        description="Filter by commodity name (partial match, case-insensitive)"
    ),
    state: Optional[str] = Query(None, description="Filter by state"),
    buyer_type: Optional[str] = Query(
        None,
        description="Filter by type: Trader | Exporter | FPO | Processor | Retailer"
    ),
    quantity: Optional[float] = Query(
        None, gt=0,
        description="Farmer's quantity in quintals — filters buyers who can absorb this volume"
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List buyers matching the given filters.

    WHO should I sell to? — returns verified and rated buyers
    who buy the specified commodity, filtered by state and quantity capacity.

    Results are ordered by: verified first, then by rating.

    Data note: buyers in the demo system are seed data, not real registered users.
    The data_status field in the response makes this explicit.
    """
    total, buyers = BuyerRepository.get_all(
        db,
        commodity_name=commodity,
        state=state,
        buyer_type=buyer_type,
        min_quantity=quantity,
        limit=limit,
        offset=offset,
    )

    # Determine data status — if all buyers have known demo IDs, mark as DEMO
    data_status = "DEMO"  # will become "LIVE" when real buyers register

    if total == 0:
        return {
            "total": 0,
            "items": [],
            "data_status": data_status,
            "empty_state_message": (
                "No active KrishiX buyers currently match this listing. "
                "The selling decision (WHERE/WHEN) still works without buyer matches."
            ),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    return {
        "total": total,
        "items": [_serialize_buyer(b) for b in buyers],
        "data_status": data_status,
        "data_note": (
            "Buyer records marked as DEMO are seed data for demonstration purposes. "
            "They are not real registered marketplace users."
        ),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/buyers/{buyer_id}")
def get_buyer(
    buyer_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed profile of a single buyer."""
    buyer = BuyerRepository.get_by_id(db, buyer_id)
    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer not found"
        )
    return {
        **_serialize_buyer(buyer),
        "data_status": "DEMO",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }
