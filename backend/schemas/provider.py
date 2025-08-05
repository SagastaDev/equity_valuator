from pydantic import BaseModel

class ProviderCreate(BaseModel):
    name: str

class ProviderResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True