from pydantic import BaseModel
from datetime import date
from typing import Optional, Dict, Any
from uuid import UUID

class MappedFieldCreate(BaseModel):
    provider_id: int
    canonical_id: int
    raw_field_name: str
    company_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    transform_expression: Optional[Dict[str, Any]] = None

class MappedFieldResponse(BaseModel):
    id: UUID
    provider_id: int
    canonical_id: int
    raw_field_name: str
    company_id: Optional[UUID]
    start_date: Optional[date]
    end_date: Optional[date]
    transform_expression: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True