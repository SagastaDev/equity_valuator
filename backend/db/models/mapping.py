from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from backend.db.base import Base

class ValueType(str, enum.Enum):
    NUMBER = "number"
    STRING = "string"
    LIST = "list"
    OBJECT = "object"

class PeriodType(str, enum.Enum):
    ANNUAL = "annual"
    QUARTERLY = "quarterly"

class RawDataEntry(Base):
    __tablename__ = "raw_data_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    fiscal_period = Column(Date, nullable=False)
    period_type = Column(Enum(PeriodType), nullable=False)
    raw_field_name = Column(String, nullable=False)
    value_type = Column(Enum(ValueType), nullable=False)
    value = Column(JSONB)  # Can store float, string, list, or object
    upload_id = Column(UUID(as_uuid=True))  # For tracking batch uploads
    
    # Relationships
    provider = relationship("Provider", back_populates="raw_data_entries")
    company = relationship("Company", back_populates="raw_data_entries")

class MappedField(Base):
    __tablename__ = "mapped_fields"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    canonical_id = Column(Integer, ForeignKey("canonical_fields.id"), nullable=False)
    raw_field_name = Column(String, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)  # Optional scoping
    start_date = Column(Date, nullable=True)  # Optional date range
    end_date = Column(Date, nullable=True)
    transform_expression = Column(JSON, nullable=True)  # Structured formula expression
    
    # Relationships
    provider = relationship("Provider", back_populates="mapped_fields")
    canonical_field = relationship("CanonicalField")
    company = relationship("Company", back_populates="mapped_fields")
    change_logs = relationship("ChangeLog", back_populates="mapped_field")