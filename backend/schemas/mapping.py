from pydantic import BaseModel, field_validator
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
    id: str
    provider_id: int
    canonical_id: int
    raw_field_name: str
    company_id: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    transform_expression: Optional[Dict[str, Any]]
    
    @field_validator('id', 'company_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
    
    class Config:
        from_attributes = True