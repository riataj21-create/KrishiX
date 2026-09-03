"""Commodity API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas import CommodityResponse, PaginatedResponse
from app.repository import CommodityRepository

router = APIRouter()


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
