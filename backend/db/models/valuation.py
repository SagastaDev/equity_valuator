from sqlalchemy import Column, Integer, ForeignKey, Date, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from backend.db.base import Base

class ValuationResult(Base):
    __tablename__ = "valuation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    as_of = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    results = Column(JSONB)  # Dictionary of field_name → value
    
    # Relationships
    company = relationship("Company", back_populates="valuations")
    user = relationship("User", back_populates="valuations")