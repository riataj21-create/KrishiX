"""Farmer produce lots."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Commodity, FarmerLot
from app.repository import FarmerLotRepository, FarmerProfileRepository
from app.schemas import FarmerLotCreate, FarmerLotResponse, FarmerLotUpdate, TokenData

router = APIRouter()


def _parse_date(value, field: str) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid {field}; use YYYY-MM-DD")


def _serialize_lot(lot: FarmerLot) -> dict:
    commodity = lot.commodity
    return {
        "id": lot.id,
        "farmer_id": lot.farmer_id,
        "commodity_id": lot.commodity_id,
        "commodity_name": commodity.name if commodity else None,
        "quantity": lot.quantity,
        "quantity_kg": float(Decimal(str(lot.quantity)) * 100),
        "unit": lot.unit,
        "state": lot.state,
        "district": lot.district,
        "village": lot.village,
        "latitude": lot.latitude,
        "longitude": lot.longitude,
        "quality_status": lot.quality_status,
        "quality_grade": lot.quality_grade,
        "quality_notes": lot.quality_notes,
        "available_from": str(lot.available_from),
        "sell_by": str(lot.sell_by),
        "minimum_price": lot.minimum_price,
        "max_payment_days": lot.max_payment_days,
        "preferred_payment_method": lot.preferred_payment_method,
        "transport_preference": lot.transport_preference,
        "max_transport_budget": lot.max_transport_budget,
        "status": lot.status,
        "reserved_by_offer_id": lot.reserved_by_offer_id,
        "created_at": lot.created_at,
        "updated_at": lot.updated_at,
    }


def _require_owner(lot: FarmerLot, user_id: UUID):
    if lot.farmer_id != user_id:
        raise HTTPException(status_code=403, detail="You cannot access another farmer's lot")


@router.get("/lots")
def list_lots(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = UUID(str(token_data.user_id))
    total, items = FarmerLotRepository.get_by_farmer(db, user_id, status_filter, limit, offset)
    return {"total": total, "items": [_serialize_lot(x) for x in items]}


@router.post("/lots", status_code=status.HTTP_201_CREATED)
def create_lot(
    body: FarmerLotCreate,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = UUID(str(token_data.user_id))
    commodity = db.query(Commodity).filter(Commodity.id == body.commodity_id).first()
    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")

    data = body.model_dump()
    data["available_from"] = _parse_date(data["available_from"], "available_from")
    data["sell_by"] = _parse_date(data["sell_by"], "sell_by")
    if data["sell_by"] < data["available_from"]:
        raise HTTPException(status_code=400, detail="sell_by cannot be before available_from")

    profile = FarmerProfileRepository.get_by_user_id(db, user_id)
    if profile:
        data.setdefault("state", profile.state)
        data.setdefault("district", profile.district)
        if not data.get("latitude") and profile.latitude:
            data["latitude"] = profile.latitude
        if not data.get("longitude") and profile.longitude:
            data["longitude"] = profile.longitude

    lot = FarmerLotRepository.create(db, farmer_id=user_id, **data)
    db.refresh(lot)
    return _serialize_lot(lot)


@router.get("/lots/{lot_id}")
def get_lot(
    lot_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lot = FarmerLotRepository.get_by_id(db, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    _require_owner(lot, UUID(str(token_data.user_id)))
    return _serialize_lot(lot)


@router.put("/lots/{lot_id}")
def update_lot(
    lot_id: UUID,
    body: FarmerLotUpdate,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lot = FarmerLotRepository.get_by_id(db, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    _require_owner(lot, UUID(str(token_data.user_id)))
    updates = {k: v for k, v in body.model_dump(exclude_unset=True).items() if v is not None}
    if "available_from" in updates:
        updates["available_from"] = _parse_date(updates["available_from"], "available_from")
    if "sell_by" in updates:
        updates["sell_by"] = _parse_date(updates["sell_by"], "sell_by")
    updated = FarmerLotRepository.update(db, lot_id, **updates)
    return _serialize_lot(updated)


@router.delete("/lots/{lot_id}")
def delete_lot(
    lot_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lot = FarmerLotRepository.get_by_id(db, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    _require_owner(lot, UUID(str(token_data.user_id)))
    FarmerLotRepository.delete(db, lot_id)
    return {"deleted": True}
