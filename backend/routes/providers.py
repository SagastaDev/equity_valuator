from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db.session import get_db
from backend.db.models.user import User, UserRole
from backend.db.models.provider import Provider
from backend.auth.routes import get_current_user
from backend.schemas.provider import ProviderCreate, ProviderResponse

router = APIRouter()

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.post("/", response_model=ProviderResponse)
async def create_provider(
    provider: ProviderCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    db_provider = Provider(name=provider.name)
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

@router.get("/", response_model=List[ProviderResponse])
async def get_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Provider).all()

@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider