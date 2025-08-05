from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.base import Base

class ChangeLog(Base):
    __tablename__ = "change_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    mapped_field_id = Column(UUID(as_uuid=True), ForeignKey("mapped_fields.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    change_description = Column(String, nullable=False)
    
    # Relationships
    mapped_field = relationship("MappedField", back_populates="change_logs")
    user = relationship("User", back_populates="change_logs")