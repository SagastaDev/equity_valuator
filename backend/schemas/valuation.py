from pydantic import BaseModel
from datetime import date
from typing import Dict, Any
from uuid import UUID

class ValuationResultCreate(BaseModel):
    company_id: UUID
    as_of: date
    results: Dict[str, Any]

class ValuationResultResponse(BaseModel):
    id: UUID
    company_id: UUID
    as_of: date
    user_id: int
    results: Dict[str, Any]
    
    class Config:
        from_attributes = True