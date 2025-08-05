from pydantic import BaseModel, EmailStr
from backend.db.models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.VIEWER

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    avatar_url: str | None = None
    
    class Config:
        from_attributes = True