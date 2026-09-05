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
    if executable:
        rec = f"Best executable option: {executable[0].get('title')} (ranked by estimated realization, not advertised price)."
    elif items:
        rec = "No executable option yet. Open a recoverable opportunity to see the smallest change that could make a sale work."
    else:
        rec = "No opportunities found for this lot."
    return {
        "lot_id": str(lot_id),
        "items": items,
        "recommendation": rec,
        "data_caveat": "Buyer offers in this demo are labelled demo/reference. Market prices are observed sample data, not guaranteed receipts.",
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
