"""
Unit tests for the FormulaEvaluator service.
"""
import pytest
from unittest.mock import Mock, patch
from backend.services.formula_evaluator import FormulaEvaluator
from backend.db.models.mapping import RawDataEntry, MappedField, ValueType, PeriodType
from backend.db.models.field import CanonicalField, FieldCategory
from backend.db.models.provider import Provider
from backend.db.models.company import Company
from datetime import date
from uuid import uuid4


class TestFormulaEvaluator:
    """Test the FormulaEvaluator service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.evaluator = FormulaEvaluator(self.mock_db)
        
        # Create test objects
        self.company_id = str(uuid4())
        self.provider_id = 1
        self.fiscal_period = "2023-12-31"

    def test_transform_raw_data_simple_mapping(self):
        """Test transformation of raw data with simple field mapping."""
        # Mock raw data entries
        raw_entry = Mock()
        raw_entry.raw_field_name = "total_revenue_raw"
        raw_entry.value_type = "number"
        raw_entry.value = "1000000"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [raw_entry]
        
        # Mock mapping
        canonical_field = Mock()
        canonical_field.id = 1
        canonical_field.name = "total_revenue"
        
        mapping = Mock()
        mapping.canonical_id = 1
        mapping.raw_field_name = "total_revenue_raw"
        mapping.transform_expression = None  # Simple direct mapping
        
        # Set up query chain for mappings
        self.mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = [mapping]
        self.mock_db.query.return_value.filter.return_value.first.return_value = canonical_field
        
        result = self.evaluator.transform_raw_data(self.company_id, self.provider_id, self.fiscal_period)
        
        assert result == {"total_revenue": 1000000.0}

    def test_transform_raw_data_with_transformation(self):
        """Test transformation with mathematical expression."""
        # Mock raw data entries
        raw_entry = Mock()
        raw_entry.raw_field_name = "revenue_thousands"
        raw_entry.value_type = "number"
        raw_entry.value = "1000"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [raw_entry]
        
        # Mock mapping with transformation
        canonical_field = Mock()
        canonical_field.id = 1
        canonical_field.name = "total_revenue"
        
        mapping = Mock()
        mapping.canonical_id = 1
        mapping.raw_field_name = "revenue_thousands"
        mapping.transform_expression = {
            "op": "multiply",
            "args": [
                {"field": "revenue_thousands"},
                {"value": 1000}
            ]
        }
        
        # Set up query chain
        self.mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = [mapping]
        self.mock_db.query.return_value.filter.return_value.first.return_value = canonical_field
        
        result = self.evaluator.transform_raw_data(self.company_id, self.provider_id, self.fiscal_period)
        
        assert result == {"total_revenue": 1000000.0}  # 1000 * 1000

    def test_transform_raw_data_missing_canonical_field(self):
        """Test transformation when canonical field is missing."""
        # Mock raw data
        raw_entry = Mock()
        raw_entry.raw_field_name = "test_field"
        raw_entry.value_type = "number"
        raw_entry.value = "100"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [raw_entry]
        
        # Mock mapping but no canonical field found
        mapping = Mock()
        mapping.canonical_id = 1
        mapping.raw_field_name = "test_field"
        mapping.transform_expression = None
        
        self.mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = [mapping]
        self.mock_db.query.return_value.filter.return_value.first.return_value = None  # No canonical field
        
        result = self.evaluator.transform_raw_data(self.company_id, self.provider_id, self.fiscal_period)
        
        assert result == {}  # Should skip the mapping

    def test_transform_raw_data_transformation_error(self):
        """Test handling of transformation errors."""
        # Mock raw data
        raw_entry = Mock()
        raw_entry.raw_field_name = "test_field"
        raw_entry.value_type = "number"
        raw_entry.value = "100"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [raw_entry]
        
        # Mock mapping with invalid transformation
        canonical_field = Mock()
        canonical_field.id = 1
        canonical_field.name = "test_canonical"
        
        mapping = Mock()
        mapping.canonical_id = 1
        mapping.raw_field_name = "test_field"
        mapping.transform_expression = {
            "op": "divide",
            "args": [
                {"field": "test_field"},
                {"value": 0}  # Division by zero
            ]
        }
        
        self.mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = [mapping]
        self.mock_db.query.return_value.filter.return_value.first.return_value = canonical_field
        
        # Should handle the error gracefully and continue
        result = self.evaluator.transform_raw_data(self.company_id, self.provider_id, self.fiscal_period)
        
        assert result == {}  # Should be empty due to transformation error

    def test_transform_raw_data_string_values(self):
        """Test transformation of string values."""
        # Mock raw data with string value
        raw_entry = Mock()
        raw_entry.raw_field_name = "company_description"
        raw_entry.value_type = "string"
        raw_entry.value = "Technology Company"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [raw_entry]
        
        # Mock mapping for string field
        canonical_field = Mock()
        canonical_field.id = 1
        canonical_field.name = "description"
        
        mapping = Mock()
        mapping.canonical_id = 1
        mapping.raw_field_name = "company_description"
        mapping.transform_expression = None
        
        self.mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = [mapping]
        self.mock_db.query.return_value.filter.return_value.first.return_value = canonical_field
        
        result = self.evaluator.transform_raw_data(self.company_id, self.provider_id, self.fiscal_period)
        
        assert result == {"description": "Technology Company"}

    def test_calculate_computed_fields_debt_to_equity(self):
        """Test calculation of debt-to-equity ratio."""
        # Mock computed field
        computed_field = Mock()
        computed_field.name = "debt_to_equity"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [computed_field]
        
        canonical_data = {
            "total_debt": 2000000,
            "total_equity": 1000000
        }
        
        result = self.evaluator.calculate_computed_fields(canonical_data)
        
        assert result["debt_to_equity"] == 2.0
        assert "total_debt" in result  # Original data should remain
        assert "total_equity" in result

    def test_calculate_computed_fields_current_ratio(self):
        """Test calculation of current ratio."""
        computed_field = Mock()
        computed_field.name = "current_ratio"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [computed_field]
        
        canonical_data = {
            "current_assets": 3000000,
            "current_liabilities": 1500000
        }
        
        result = self.evaluator.calculate_computed_fields(canonical_data)
        
        assert result["current_ratio"] == 2.0

    def test_calculate_computed_fields_return_on_equity(self):
        """Test calculation of return on equity."""
        computed_field = Mock()
        computed_field.name = "return_on_equity"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [computed_field]
        
        canonical_data = {
            "net_income": 500000,
            "total_equity": 2500000
        }
        
        result = self.evaluator.calculate_computed_fields(canonical_data)
        
        assert result["return_on_equity"] == 0.2

    def test_calculate_computed_fields_zero_denominator(self):
        """Test handling of zero denominators in computed fields."""
        computed_field = Mock()
        computed_field.name = "debt_to_equity"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [computed_field]
        
        canonical_data = {
            "total_debt": 2000000,
            "total_equity": 0  # Zero equity
        }
        
        result = self.evaluator.calculate_computed_fields(canonical_data)
        
        # Should not calculate the ratio when denominator is zero
        assert "debt_to_equity" not in result
        assert "total_debt" in result  # Original data should remain

    def test_calculate_computed_fields_missing_required_fields(self):
        """Test handling of missing required fields for computed fields."""
        computed_field = Mock()
        computed_field.name = "debt_to_equity"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [computed_field]
        
        canonical_data = {
            "total_debt": 2000000
            # Missing total_equity
        }
        
        result = self.evaluator.calculate_computed_fields(canonical_data)
        
        # Should not calculate the ratio when required fields are missing
        assert "debt_to_equity" not in result
        assert "total_debt" in result

    def test_calculate_computed_fields_unknown_field(self):
        """Test handling of unknown computed field names."""
        computed_field = Mock()
        computed_field.name = "unknown_ratio"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [computed_field]
        
        canonical_data = {
            "field1": 100,
            "field2": 50
        }
        
        # Should handle gracefully when computed field is not implemented
        result = self.evaluator.calculate_computed_fields(canonical_data)
        
        assert "unknown_ratio" not in result
        assert "field1" in result  # Original data should remain

    def test_calculate_computed_fields_calculation_error(self):
        """Test handling of calculation errors in computed fields."""
        computed_field = Mock()
        computed_field.name = "current_ratio"
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [computed_field]
        
        canonical_data = {
            "current_assets": "not_a_number",  # Invalid data type
            "current_liabilities": 1500000
        }
        
        # Should handle calculation errors gracefully
        result = self.evaluator.calculate_computed_fields(canonical_data)
        
        assert "current_ratio" not in result
        assert "current_assets" in result  # Original data should remain

    def test_multiple_computed_fields(self):
        """Test calculation of multiple computed fields."""
        computed_fields = []
        for name in ["debt_to_equity", "current_ratio", "return_on_equity"]:
            field = Mock()
            field.name = name
            computed_fields.append(field)
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = computed_fields
        
        canonical_data = {
            "total_debt": 2000000,
            "total_equity": 1000000,
            "current_assets": 3000000,
            "current_liabilities": 1500000,
            "net_income": 200000
        }
        
        result = self.evaluator.calculate_computed_fields(canonical_data)
        
        assert result["debt_to_equity"] == 2.0
        assert result["current_ratio"] == 2.0
        assert result["return_on_equity"] == 0.2
        # Check that the computed fields were calculated
        computed_field_names = ["debt_to_equity", "current_ratio", "return_on_equity"]
        assert all(field_name in result for field_name in computed_field_names)