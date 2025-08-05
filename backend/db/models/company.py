from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from backend.db.base import Base

class Industry(Base):
    __tablename__ = "industries"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Relationships
    companies = relationship("Company", back_populates="industry")

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    industry_id = Column(Integer, ForeignKey("industries.id"))
    
    # Relationships
    industry = relationship("Industry", back_populates="companies")
    raw_data_entries = relationship("RawDataEntry", back_populates="company")
    mapped_fields = relationship("MappedField", back_populates="company")
    valuations = relationship("ValuationResult", back_populates="company")
    price_data = relationship("PriceData", back_populates="company")