"""Opportunities, feasibility, and recovery."""

import json
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Opportunity
from app.repository import FarmerLotRepository, OpportunityRepository
from app.schemas import TokenData
from app.services.opportunity_service import OpportunityService, overlay_from_dict

router = APIRouter()


class RecoveryApplyRequest(BaseModel):
    change_types: List[str] = Field(..., min_length=1)


def _require_lot_owner(db, lot_id: UUID, user_id: UUID):
    lot = FarmerLotRepository.get_by_id(db, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    if lot.farmer_id != user_id:
        raise HTTPException(status_code=403, detail="You cannot access another farmer's lot")
    return lot


def _hydrate(row: Opportunity) -> dict:
    def parse(raw, default):
        if not raw:
            return default
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return default

    return {
        "id": str(row.id),
        "lot_id": str(row.lot_id),
        "opportunity_type": row.opportunity_type,
        "buyer_requirement_id": str(row.buyer_requirement_id) if row.buyer_requirement_id else None,
        "market_id": str(row.market_id) if row.market_id else None,
        "feasibility_decision": row.feasibility_decision,
        "blocking_constraints": parse(row.blocking_constraints, []),
        "opportunity_gaps": parse(row.opportunity_gap, []),
        "minimum_viable_changes": parse(row.minimum_viable_change, []),
        "offered_price": float(row.offered_price_per_unit) if row.offered_price_per_unit is not None else None,
        "estimated_net_realization": float(row.estimated_net_realization) if row.estimated_net_realization is not None else None,
        "source_type": row.source_type,
        "data_quality": row.data_quality,
        "rank": row.rank,
        "confidence_score": float(row.confidence_score) if row.confidence_score is not None else None,
        "explanation": row.explanation,
        "title": row.title,
        "warnings": parse(row.warnings, []),
        "applied_recovery": parse(row.applied_recovery, None),
        "analyzed_at": row.analyzed_at,
        "price_kind": "buyer_offer" if row.opportunity_type == "BUYER" else "market_price",
    }


@router.post("/lots/{lot_id}/opportunities/analyze")
def analyze_opportunities(
    lot_id: UUID,
    farmer_priority: str = Query("maximize_realization"),
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_lot_owner(db, lot_id, UUID(str(token_data.user_id)))
    service = OpportunityService(db)
    items = service.discover_and_analyze(lot_id, farmer_priority=farmer_priority)

    executable = [i for i in items if i.get("feasibility_decision") == "EXECUTABLE"]
    all_prices = [
        i.get("offered_price") for i in items
        if i.get("offered_price") is not None
    ]

    # Opportunity gap: difference between highest quoted price and best executable price
    opportunity_gap = None
    if executable and all_prices:
        best_executable_price = max(
            i.get("offered_price", 0) for i in executable if i.get("offered_price")
        )
        highest_quoted_price = max(all_prices)
        if highest_quoted_price > best_executable_price:
            opportunity_gap = {
                "highest_quoted_per_quintal": highest_quoted_price,
                "highest_quoted_per_kg": round(highest_quoted_price / 100, 2),
                "best_executable_per_quintal": best_executable_price,
                "best_executable_per_kg": round(best_executable_price / 100, 2),
                "gap_per_quintal": round(highest_quoted_price - best_executable_price, 2),
                "gap_per_kg": round((highest_quoted_price - best_executable_price) / 100, 2),
                "label": "Opportunity gap — not guaranteed lost income. The higher-quoted opportunity has unmet constraints.",
            }

    if executable:
        rec = (
            f"Best executable option: {executable[0].get('title')} "
            f"(ranked by estimated realization, not advertised price)."
        )
    elif any(i.get("feasibility_decision") == "RECOVERABLE" for i in items):
        rec = "No executable option yet — but recoverable options exist. Apply the suggested changes to unlock a sale."
    elif items:
        rec = "No executable option found. All opportunities have unmet constraints. See blocking reasons for details."
    else:
        rec = "No opportunities found for this lot."

    return {
        "lot_id": str(lot_id),
        "items": items,
        "recommendation": rec,
        "opportunity_gap": opportunity_gap,
        "summary": {
            "total": len(items),
            "executable": len([i for i in items if i.get("feasibility_decision") == "EXECUTABLE"]),
            "recoverable": len([i for i in items if i.get("feasibility_decision") == "RECOVERABLE"]),
            "not_viable": len([i for i in items if i.get("feasibility_decision") == "NOT_VIABLE"]),
            "insufficient_data": len([i for i in items if i.get("feasibility_decision") == "INSUFFICIENT_DATA"]),
        },
        "data_caveat": (
            "Buyer offers in this demo are labelled demo/reference. "
            "Market prices are observed sample data, not guaranteed receipts. "
            "Estimated net realization deducts labelled costs only."
        ),
    }


@router.get("/lots/{lot_id}/opportunities")
def list_opportunities(
    lot_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_lot_owner(db, lot_id, UUID(str(token_data.user_id)))
    rows = OpportunityRepository.get_by_lot(db, lot_id)
    if not rows:
        service = OpportunityService(db)
        items = service.discover_and_analyze(lot_id)
        return {"lot_id": str(lot_id), "items": items}
    return {"lot_id": str(lot_id), "items": [_hydrate(r) for r in rows]}


@router.get("/opportunities/{opportunity_id}")
def get_opportunity(
    opportunity_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = OpportunityRepository.get_by_id(db, opportunity_id)
    if not row:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    _require_lot_owner(db, row.lot_id, UUID(str(token_data.user_id)))
    service = OpportunityService(db)
    detail = service.analyze_existing(opportunity_id)
    return detail


@router.post("/opportunities/{opportunity_id}/recovery")
def apply_recovery(
    opportunity_id: UUID,
    body: RecoveryApplyRequest,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = OpportunityRepository.get_by_id(db, opportunity_id)
    if not row:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    _require_lot_owner(db, row.lot_id, UUID(str(token_data.user_id)))
    service = OpportunityService(db)
    try:
        return service.apply_recovery(opportunity_id, body.change_types)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ── What-if ───────────────────────────────────────────────────────────────────

class WhatIfRequest(BaseModel):
    """
    Override any farmer constraint to see how the feasibility result changes.
    The lot in the database is NOT modified — this is a read-only simulation.
    Every change is sent to the backend; the frontend never calculates the result.
    """
    extra_quantity_kg: Optional[float] = Field(None, ge=0, description="Additional kg from aggregation")
    negotiated_payment_days: Optional[int] = Field(None, ge=0)
    negotiated_price_per_kg: Optional[float] = Field(None, gt=0)
    assume_buyer_pickup: Optional[bool] = None
    transport_cost_override: Optional[float] = Field(None, ge=0)


@router.post("/lots/{lot_id}/whatif")
def whatif_recheck(
    lot_id: UUID,
    body: WhatIfRequest,
    farmer_priority: str = Query("maximize_realization"),
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Re-evaluate all opportunities for this lot with modified farmer constraints.

    The lot is NOT changed in the database. This is a pure simulation.
    Useful for demonstrating: "What if I had 300 kg? → EXECUTABLE"

    Returns full opportunity list with recalculated feasibility decisions.
    The frontend must show a clear BEFORE/AFTER comparison.
    """
    _require_lot_owner(db, lot_id, UUID(str(token_data.user_id)))

    # Build overlay from request
    overlay = overlay_from_dict({
        "extra_quantity": (body.extra_quantity_kg / 100) if body.extra_quantity_kg else 0,
        "negotiated_payment_days": body.negotiated_payment_days,
        "negotiated_price": (body.negotiated_price_per_kg * 100) if body.negotiated_price_per_kg else None,
        "transport_cost_override": body.transport_cost_override,
        "assume_buyer_pickup": body.assume_buyer_pickup or False,
    })

    service = OpportunityService(db)
    items = service.discover_and_analyze(
        lot_id,
        farmer_priority=farmer_priority,
        overlay=overlay,
    )

    executable = [i for i in items if i.get("feasibility_decision") == "EXECUTABLE"]
    summary = {
        "total": len(items),
        "executable": len(executable),
        "recoverable": len([i for i in items if i.get("feasibility_decision") == "RECOVERABLE"]),
        "not_viable": len([i for i in items if i.get("feasibility_decision") == "NOT_VIABLE"]),
    }

    return {
        "lot_id": str(lot_id),
        "whatif_applied": {
            "extra_quantity_kg": body.extra_quantity_kg,
            "negotiated_payment_days": body.negotiated_payment_days,
            "negotiated_price_per_kg": body.negotiated_price_per_kg,
            "assume_buyer_pickup": body.assume_buyer_pickup,
            "transport_cost_override": body.transport_cost_override,
        },
        "items": items,
        "summary": summary,
        "note": (
            "Lot NOT modified. This is a simulation. "
            "Apply recovery actions to persist changes."
        ),
    }

