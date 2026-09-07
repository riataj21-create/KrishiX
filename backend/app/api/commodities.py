"""Commodity API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas import CommodityCreate, CommodityResponse, PaginatedResponse
from app.repository import CommodityRepository

router = APIRouter()


@router.post("/commodities", response_model=CommodityResponse, status_code=status.HTTP_201_CREATED)
def create_commodity(payload: CommodityCreate, db: Session = Depends(get_db)):
    """Create a farmer-entered commodity when it is not in the suggested catalog."""
    name = payload.name.strip()
    existing = db.query(CommodityRepository.model).filter(
        CommodityRepository.model.name.ilike(name)
    ).first()
    if existing:
        return existing
    return CommodityRepository.create(
        db,
        name=name,
        category=payload.category or "Other",
        unit=payload.unit,
        description=payload.description or f"Farmer-entered commodity: {name}",
    )


@router.get("/commodities", response_model=PaginatedResponse)
def list_commodities(
    category: str = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List all commodities with optional filtering."""
    total, items = CommodityRepository.get_all(db, category=category, limit=limit, offset=offset)
    return {
        "total": total,
        "items": [
            {
                "id": str(item.id),
                "name": item.name,
                "category": item.category,
                "unit": item.unit,
                "description": item.description,
                "icon_url": item.icon_url,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in items
        ],
    }


@router.get("/commodities/{commodity_id}", response_model=CommodityResponse)
def get_commodity(commodity_id: UUID, db: Session = Depends(get_db)):
    """Get commodity details."""
    commodity = CommodityRepository.get_by_id(db, commodity_id)
    if not commodity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commodity not found")
    return commodity
