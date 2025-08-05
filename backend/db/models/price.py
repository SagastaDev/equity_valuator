from sqlalchemy import Column, Integer, ForeignKey, Date, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from backend.db.base import Base

class PricePeriodType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MINUTE = "minute"
    SECOND = "second"

class PriceData(Base):
    __tablename__ = "price_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    date = Column(Date, nullable=False)
    period_type = Column(Enum(PricePeriodType), nullable=False, default=PricePeriodType.DAILY)
    open = Column(Float)
    close = Column(Float) 
    adj_close = Column(Float)
    volume = Column(Integer)
    
    # Relationships
    company = relationship("Company", back_populates="price_data")
    provider = relationship("Provider", back_populates="price_data")