from sqlalchemy import Column, Integer, String, Boolean, Enum
from backend.db.base import Base
import enum

class FieldCategory(str, enum.Enum):
    FUNDAMENTAL = "fundamental"
    MARKET = "market"
    RATIO = "ratio"

class CanonicalField(Base):
    __tablename__ = "canonical_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(Integer, unique=True, index=True)
    name = Column(String, nullable=False)  # e.g., "cash_flow"
    display_name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    category = Column(Enum(FieldCategory), nullable=False)
    is_computed = Column(Boolean, default=False)