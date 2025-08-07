from sqlalchemy import Column, Integer, String, Boolean, Enum
from backend.db.base import Base
import enum

class FieldCategory(str, enum.Enum):
    FUNDAMENTAL = "fundamental"
    MARKET = "market"
    RATIO = "ratio"

class FieldType(str, enum.Enum):
    CURRENCY = "currency"
    NUMBER = "number"
    PERCENTAGE = "percentage"
    RATIO = "ratio"

class StatementType(str, enum.Enum):
    CASH_FLOW = "cash_flow"
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    MARKET_DATA = "market_data"

class CanonicalField(Base):
    __tablename__ = "canonical_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(Integer, unique=True, index=True)
    name = Column(String, nullable=False)  # e.g., "cash_flow"
    display_name = Column(String, nullable=False)
    type = Column(Enum(FieldType), nullable=False)
    category = Column(Enum(FieldCategory), nullable=False)
    statement = Column(Enum(StatementType), nullable=True)
    is_computed = Column(Boolean, default=False)