"""User API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas import UserResponse, UserUpdate, PasswordChange, TokenData
from app.auth import get_current_user, verify_password, hash_password
from app.repository import UserRepository

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user profile."""
    user = UserRepository.get_by_id(db, UUID(str(token_data.user_id)))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/me", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user email."""
    updated_user = UserRepository.update(
        db,
        UUID(str(token_data.user_id)),
        email=user_update.email
    )
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


@router.put("/me/password")
def change_password(
    body: PasswordChange,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change the authenticated user's password.
    Requires the current password for verification before accepting the new one.
    """
    user = UserRepository.get_by_id(db, UUID(str(token_data.user_id)))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verify current password before allowing change
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update to new hashed password
    user.password_hash = hash_password(body.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
