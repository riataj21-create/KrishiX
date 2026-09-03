"""User API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas import UserResponse, UserUpdate
from app.auth import get_current_user
from app.repository import UserRepository
from app.schemas import TokenData

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user profile."""
    user = UserRepository.get_by_id(db, UUID(token_data.user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/me", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    updated_user = UserRepository.update(
        db,
        UUID(token_data.user_id),
        email=user_update.email
    )
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user
