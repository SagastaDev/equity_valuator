from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db.session import get_db
from backend.db.models.user import User, UserRole
from backend.db.models.mapping import MappedField, RawDataEntry
from backend.db.models.field import CanonicalField
from backend.db.models.provider import Provider
from backend.auth.routes import get_current_user
from backend.schemas.mapping import MappedFieldCreate, MappedFieldResponse
from backend.services.transform_engine import TransformEngine
from fastapi.responses import Response
import json

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

@router.get("/canonical-fields")
async def get_canonical_fields(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all canonical fields"""
    fields = db.query(CanonicalField).all()
    return [
        {
            "id": field.id,
            "code": field.code,
            "name": field.name,
            "display_name": field.display_name,
            "type": field.type,
            "category": field.category,
            "statement": field.statement,
            "is_computed": field.is_computed
        }
        for field in fields
    ]

@router.get("/providers/{provider_id}/raw-fields")
async def get_provider_raw_fields(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available raw field names from a provider's data"""
    raw_fields = db.query(RawDataEntry.raw_field_name).filter(
        RawDataEntry.provider_id == provider_id
    ).distinct().all()
    
    return {
        "provider_id": provider_id,
        "raw_fields": sorted([field[0] for field in raw_fields])
    }

@router.get("/mappings/{provider_id}/{canonical_id}")
async def get_field_mapping(
    provider_id: int,
    canonical_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get mapping for a specific provider and canonical field"""
    mapping = db.query(MappedField).filter(
        MappedField.provider_id == provider_id,
        MappedField.canonical_id == canonical_id
    ).first()
    
    if not mapping:
        return {"raw_field_name": "", "transform_expression": None}
    
    return {
        "id": mapping.id,
        "raw_field_name": mapping.raw_field_name,
        "transform_expression": mapping.transform_expression,
        "company_id": mapping.company_id,
        "start_date": mapping.start_date,
        "end_date": mapping.end_date
    }

@router.get("/mappings/backup/{provider_id}")
async def download_mappings_backup(
    provider_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Download all mappings for a provider as JSON backup"""
    mappings = db.query(MappedField).filter(
        MappedField.provider_id == provider_id
    ).all()
    
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    backup_data = {
        "provider": {
            "id": provider.id,
            "name": provider.name
        },
        "mappings": []
    }
    
    for mapping in mappings:
        canonical_field = db.query(CanonicalField).filter(
            CanonicalField.id == mapping.canonical_id
        ).first()
        
        backup_data["mappings"].append({
            "canonical_field": {
                "id": canonical_field.id,
                "code": canonical_field.code,
                "name": canonical_field.name,
                "display_name": canonical_field.display_name,
                "type": canonical_field.type,
                "category": canonical_field.category,
                "statement": canonical_field.statement
            },
            "mapping": {
                "raw_field_name": mapping.raw_field_name,
                "transform_expression": mapping.transform_expression,
                "company_id": str(mapping.company_id) if mapping.company_id else None,
                "start_date": mapping.start_date.isoformat() if mapping.start_date else None,
                "end_date": mapping.end_date.isoformat() if mapping.end_date else None
            }
        })
    
    json_content = json.dumps(backup_data, indent=2)
    filename = f"mappings_backup_{provider.name.lower().replace(' ', '_')}.json"
    
    return Response(
        content=json_content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

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