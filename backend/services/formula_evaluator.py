from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.db.models.mapping import RawDataEntry, MappedField
from backend.db.models.field import CanonicalField
from backend.services.transform_engine import TransformEngine

class FormulaEvaluator:
    """
    Evaluates formulas and transforms raw data into canonical format.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.transform_engine = TransformEngine()
    
    def transform_raw_data(self, company_id: str, provider_id: int, fiscal_period: str) -> Dict[str, Any]:
        """
        Transform raw data entries into canonical format for a specific company and period.
        
        Args:
            company_id: UUID of the company
            provider_id: ID of the data provider
            fiscal_period: Date string for the fiscal period
            
        Returns:
            Dictionary of canonical_field_name -> transformed_value
        """
        # Get all raw data entries for this company, provider, and period
        raw_entries = self.db.query(RawDataEntry).filter(
            RawDataEntry.company_id == company_id,
            RawDataEntry.provider_id == provider_id,
            RawDataEntry.fiscal_period == fiscal_period
        ).all()
        
        # Create a lookup dictionary of raw field names to values
        raw_data = {}
        for entry in raw_entries:
            if entry.value_type == "number":
                raw_data[entry.raw_field_name] = float(entry.value)
            else:
                raw_data[entry.raw_field_name] = entry.value
        
        # Get all mapping rules for this provider and company
        mappings = self.db.query(MappedField).filter(
            MappedField.provider_id == provider_id
        ).filter(
            # Either company-specific or global mapping
            (MappedField.company_id == company_id) | (MappedField.company_id.is_(None))
        ).all()
        
        # Apply transformations
        canonical_data = {}
        
        for mapping in mappings:
            canonical_field = self.db.query(CanonicalField).filter(
                CanonicalField.id == mapping.canonical_id
            ).first()
            
            if not canonical_field:
                continue
            
            try:
                if mapping.transform_expression:
                    # Apply transformation formula
                    result = self.transform_engine.evaluate_expression(
                        mapping.transform_expression,
                        raw_data
                    )
                    canonical_data[canonical_field.name] = result
                else:
                    # Direct mapping
                    if mapping.raw_field_name in raw_data:
                        canonical_data[canonical_field.name] = raw_data[mapping.raw_field_name]
                        
            except Exception as e:
                # Log the error but continue processing other fields
                print(f"Error transforming {mapping.raw_field_name} -> {canonical_field.name}: {e}")
                continue
        
        return canonical_data
    
    def calculate_computed_fields(self, canonical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate fields that are computed from other canonical fields.
        """
        computed_fields = self.db.query(CanonicalField).filter(
            CanonicalField.is_computed == True
        ).all()
        
        for field in computed_fields:
            try:
                # This would use predefined formulas for computed fields
                # For now, we'll implement some common financial ratios
                if field.name == "debt_to_equity":
                    if "total_debt" in canonical_data and "total_equity" in canonical_data:
                        if canonical_data["total_equity"] != 0:
                            canonical_data[field.name] = canonical_data["total_debt"] / canonical_data["total_equity"]
                
                elif field.name == "current_ratio":
                    if "current_assets" in canonical_data and "current_liabilities" in canonical_data:
                        if canonical_data["current_liabilities"] != 0:
                            canonical_data[field.name] = canonical_data["current_assets"] / canonical_data["current_liabilities"]
                
                elif field.name == "return_on_equity":
                    if "net_income" in canonical_data and "total_equity" in canonical_data:
                        if canonical_data["total_equity"] != 0:
                            canonical_data[field.name] = canonical_data["net_income"] / canonical_data["total_equity"]
                            
            except Exception as e:
                print(f"Error calculating computed field {field.name}: {e}")
                continue
        
        return canonical_data