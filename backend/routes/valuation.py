from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db.session import get_db
from backend.db.models.user import User
from backend.db.models.valuation import ValuationResult
from backend.auth.routes import get_current_user
from backend.schemas.valuation import ValuationResultCreate, ValuationResultResponse

router = APIRouter()

@router.post("/", response_model=ValuationResultResponse)
async def create_valuation(
    valuation: ValuationResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_valuation = ValuationResult(
        company_id=valuation.company_id,
        as_of=valuation.as_of,
        user_id=current_user.id,
        results=valuation.results
    )
    db.add(db_valuation)
    db.commit()
    db.refresh(db_valuation)
    return db_valuation

@router.get("/{company_id}", response_model=List[ValuationResultResponse])
async def get_valuations_by_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    valuations = db.query(ValuationResult).filter(
        ValuationResult.company_id == company_id
    ).all()
    return valuations

@router.get("/", response_model=List[ValuationResultResponse])
async def get_all_valuations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    valuations = db.query(ValuationResult).offset(skip).limit(limit).all()
    return valuations