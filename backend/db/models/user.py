from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
import enum
from backend.db.base import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    avatar_url = Column(String)
    
    # Relationships
    valuations = relationship("ValuationResult", back_populates="user")
    change_logs = relationship("ChangeLog", back_populates="user")