"""Farmer Profile API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas import FarmerProfileCreate, FarmerProfileUpdate, FarmerProfileResponse
from app.auth import get_current_user
from app.repository import FarmerProfileRepository
from app.schemas import TokenData

router = APIRouter()


@router.get("/farmer-profile", response_model=FarmerProfileResponse)
def get_farmer_profile(
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's farmer profile."""
    profile = FarmerProfileRepository.get_by_user_id(db, UUID(token_data.user_id))
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found"
        )
    return profile


@router.post("/farmer-profile", response_model=FarmerProfileResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_farmer_profile(
    profile_data: FarmerProfileCreate,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update farmer profile."""
    user_id = UUID(token_data.user_id)
    
    # Check if profile exists
    existing_profile = FarmerProfileRepository.get_by_user_id(db, user_id)
    
    if existing_profile:
        # Update existing profile
        updated = FarmerProfileRepository.update(db, user_id, **profile_data.dict())
        return updated
    else:
        # Create new profile
        new_profile = FarmerProfileRepository.create(db, user_id, **profile_data.dict())
        return new_profile


@router.put("/farmer-profile", response_model=FarmerProfileResponse)
def update_farmer_profile(
    profile_data: FarmerProfileUpdate,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update farmer profile."""
    updated = FarmerProfileRepository.update(db, UUID(token_data.user_id), **profile_data.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")
    return updated
