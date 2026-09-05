"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import LoginRequest, UserCreate, UserResponse, TokenResponse
from app.repository import UserRepository
from app.auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if email already exists
    existing_user = UserRepository.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create new user with role
    new_user = UserRepository.create(db, email=user_data.email, password=user_data.password, role=user_data.role)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login user and get access token."""
    user = UserRepository.get_by_email(db, credentials.email)
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token — include role in JWT payload
    access_token = create_access_token(
        user_id=str(user.id),
        role=user.role,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
def logout():
    """Logout user (frontend handles token removal)."""
    return {"message": "Successfully logged out"}
