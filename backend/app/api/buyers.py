"""
Buyers API

GET /api/buyers               — list/filter buyers
GET /api/buyers/{id}          — single buyer detail
GET /api/buyers/{id}/requirements — buyer's active purchase requirements
"""
import logging
from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.database import get_db
from app.models import Buyer, BuyerRequirement
from app.repository import BuyerRepository
from app.schemas import TokenData

logger = logging.getLogger("krishix.api.buyers")
router = APIRouter()


def _serialize_requirement(req: BuyerRequirement) -> dict:
    return {
        "id": str(req.id),
        "commodity_id": str(req.commodity_id),
        "minimum_quantity": float(req.minimum_quantity),
        "minimum_quantity_kg": float(req.minimum_quantity) * 100,
        "maximum_quantity": float(req.maximum_quantity) if req.maximum_quantity else None,
        "required_grade": req.required_grade,
        "offered_price": float(req.offered_price),
        "offered_price_per_kg": round(float(req.offered_price) / 100, 2),
        "payment_days": req.payment_days,
        "payment_method": req.payment_method,
        "pickup_available": bool(req.pickup_available),
        "pickup_location_state": req.pickup_location_state,
        "pickup_location_district": req.pickup_location_district,
        "transport_cost_total": float(req.transport_cost_total) if req.transport_cost_total else None,
        "transport_cost_source": req.transport_cost_source,
        "active_from": str(req.active_from),
        "active_until": str(req.active_until),
        "is_active": bool(req.is_active),
        "source_type": req.source_type,
        "notes": req.notes,
    }


def _serialize_buyer(buyer: Buyer, include_requirements: bool = False) -> dict:
    reqs = buyer.buyer_requirements if include_requirements else []
    active_reqs = [r for r in reqs if r.is_active and r.active_until >= date.today()]

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
        # ── Fields missing from old serializer ─────────────────────
        "source_type": buyer.source_type,                       # DEMO | REFERENCE | VERIFIED_ACTIVE
        "payment_days": buyer.payment_days,
        "payment_method": buyer.payment_method,
        "pickup_available": bool(buyer.pickup_available) if buyer.pickup_available is not None else False,
        "verification_status": buyer.verification_status,
        "active_until": str(buyer.active_until) if buyer.active_until else None,
        # ── Existing fields ─────────────────────────────────────────
        "min_quantity_quintal": float(buyer.min_quantity_quintal) if buyer.min_quantity_quintal else None,
        "max_quantity_quintal": float(buyer.max_quantity_quintal) if buyer.max_quantity_quintal else None,
        "quality_grade": buyer.quality_grade,
        "price_premium_pct": float(buyer.price_premium_pct) if buyer.price_premium_pct else 0.0,
        "is_verified": bool(buyer.is_verified),
        "years_active": buyer.years_active,
        "rating": float(buyer.rating) if buyer.rating else None,
        "notes": buyer.notes,
        "active_requirements_count": len(active_reqs),
        "active_requirements": [_serialize_requirement(r) for r in active_reqs] if include_requirements else None,
        "whatsapp_link": (
            f"https://wa.me/91{buyer.contact_phone.replace(' ', '').replace('-', '')}"
            if buyer.contact_phone else None
        ),
    }


@router.get("/buyers")
def list_buyers(
    commodity: Optional[str] = Query(None, description="Commodity name (partial, case-insensitive)"),
    state: Optional[str] = Query(None, description="Filter by state"),
    buyer_type: Optional[str] = Query(None, description="Trader | Exporter | FPO | Processor | Retailer"),
    quantity: Optional[float] = Query(None, gt=0, description="Farmer quantity in quintals"),
    source_type: Optional[str] = Query(None, description="Filter by source_type: demo | reference | verified_active"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List buyers with filters. Results include source_type so the frontend
    can clearly label DEMO buyers and never present them as real adoption.
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

    # Apply source_type filter in Python (small result set in demo)
    if source_type:
        buyers = [b for b in buyers if b.source_type == source_type]
        total = len(buyers)

    data_status = "DEMO" if all(
        (b.source_type or "demo") in ("demo", "reference") for b in buyers
    ) else "MIXED"

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
        "items": [_serialize_buyer(b, include_requirements=False) for b in buyers],
        "data_status": data_status,
        "data_note": (
            "Buyers marked DEMO are seed data for demonstration. "
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
    """Get detailed buyer profile including active requirements."""
    buyer = (
        db.query(Buyer)
        .options(joinedload(Buyer.buyer_requirements))
        .filter(Buyer.id == buyer_id)
        .first()
    )
    if not buyer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyer not found")

    return {
        **_serialize_buyer(buyer, include_requirements=True),
        "data_status": buyer.source_type or "demo",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/buyers/{buyer_id}/requirements")
def get_buyer_requirements(
    buyer_id: UUID,
    active_only: bool = Query(True, description="Return only currently active requirements"),
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all purchase requirements for a buyer.
    Active requirements drive the opportunity discovery engine.
    """
    buyer = db.query(Buyer).filter(Buyer.id == buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyer not found")

    query = db.query(BuyerRequirement).filter(BuyerRequirement.buyer_id == buyer_id)
    if active_only:
        today = date.today()
        query = query.filter(
            BuyerRequirement.is_active == True,
            BuyerRequirement.active_until >= today,
        )

    reqs = query.all()
    return {
        "buyer_id": str(buyer_id),
        "buyer_name": buyer.name,
        "source_type": buyer.source_type,
        "total": len(reqs),
        "active_only": active_only,
        "requirements": [_serialize_requirement(r) for r in reqs],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }
