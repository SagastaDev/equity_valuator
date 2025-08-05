from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db.session import get_db
from backend.db.models.user import User, UserRole
from backend.db.models.mapping import MappedField
from backend.auth.routes import get_current_user
from backend.schemas.mapping import MappedFieldCreate, MappedFieldResponse
from backend.services.transform_engine import TransformEngine

router = APIRouter()

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.post("/mappings", response_model=MappedFieldResponse)
async def create_mapping(
    mapping: MappedFieldCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    db_mapping = MappedField(**mapping.dict())
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.get("/mappings", response_model=List[MappedFieldResponse])
async def get_mappings(
    provider_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(MappedField)
    if provider_id:
        query = query.filter(MappedField.provider_id == provider_id)
    return query.all()

@router.put("/mappings/{mapping_id}", response_model=MappedFieldResponse)
async def update_mapping(
    mapping_id: str,
    mapping: MappedFieldCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    db_mapping = db.query(MappedField).filter(MappedField.id == mapping_id).first()
    if not db_mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    for field, value in mapping.dict().items():
        setattr(db_mapping, field, value)
    
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.post("/test-transform")
async def test_transform(
    transform_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Test a transformation expression without saving it"""
    try:
        engine = TransformEngine()
        result = engine.evaluate_expression(
            transform_data.get("expression"),
            transform_data.get("sample_data", {})
        )
        return {"result": result, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}