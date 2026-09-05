"""Demo bootstrap endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.schemas import TokenData
from app.services.demo_seed import seed_demo

router = APIRouter()


@router.post("/demo/seed")
def run_seed(token_data: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return seed_demo(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
