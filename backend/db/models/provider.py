from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.db.base import Base

class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    # Relationships
    raw_data_entries = relationship("RawDataEntry", back_populates="provider")
    mapped_fields = relationship("MappedField", back_populates="provider") 
    price_data = relationship("PriceData", back_populates="provider")