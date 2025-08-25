"""
Unit tests for the TransformEngine service.
"""
import pytest
from backend.services.transform_engine import TransformEngine


class TestTransformEngine:
    """Test the TransformEngine service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TransformEngine()
        self.test_data = {
            "revenue": 1000000,
            "expenses": 750000,
            "assets": 5000000,
            "liabilities": 2000000,
            "shares": 100000
        }

    def test_evaluate_field_reference(self):
        """Test evaluation of direct field references."""
        expression = {"field": "revenue"}
        result = self.engine.evaluate_expression(expression, self.test_data)
        assert result == 1000000

    def test_evaluate_literal_value(self):
        """Test evaluation of literal values."""
        expression = {"value": 42.5}
        result = self.engine.evaluate_expression(expression, {})
        assert result == 42.5

    def test_evaluate_add_operation(self):
        """Test addition operation."""
        expression = {
            "op": "add",
            "args": [
                {"field": "revenue"},
                {"value": 50000}
            ]
        }
        result = self.engine.evaluate_expression(expression, self.test_data)
        assert result == 1050000

    def test_evaluate_subtract_operation(self):
        """Test subtraction operation."""
        expression = {
            "op": "subtract",
            "args": [
                {"field": "revenue"},
                {"field": "expenses"}
            ]
        }
        result = self.engine.evaluate_expression(expression, self.test_data)
        assert result == 250000

    def test_evaluate_multiply_operation(self):
        """Test multiplication operation."""
        expression = {
            "op": "multiply",
            "args": [
                {"field": "revenue"},
                {"value": 1.1}
            ]
        }
        result = self.engine.evaluate_expression(expression, self.test_data)
        assert result == 1100000

    def test_evaluate_divide_operation(self):
        """Test division operation."""
        expression = {
            "op": "divide",
            "args": [
                {"field": "revenue"},
                {"field": "shares"}
            ]
        }
        result = self.engine.evaluate_expression(expression, self.test_data)
        assert result == 10.0

    def test_evaluate_power_operation(self):
        """Test power operation."""
        expression = {
            "op": "power",
            "args": [
                {"value": 2},
                {"value": 3}
            ]
        }
        result = self.engine.evaluate_expression(expression, {})
        assert result == 8

    def test_evaluate_modulo_operation(self):
        """Test modulo operation."""
        expression = {
            "op": "modulo",
            "args": [
                {"value": 10},
                {"value": 3}
            ]
        }
        result = self.engine.evaluate_expression(expression, {})
        assert result == 1

    def test_evaluate_nested_operations(self):
        """Test nested operations."""
        # Calculate (revenue - expenses) / shares
        expression = {
            "op": "divide",
            "args": [
                {
                    "op": "subtract",
                    "args": [
                        {"field": "revenue"},
                        {"field": "expenses"}
                    ]
                },
                {"field": "shares"}
            ]
        }
        result = self.engine.evaluate_expression(expression, self.test_data)
        assert result == 2.5

    def test_evaluate_math_functions(self):
        """Test mathematical functions."""
        # Test sqrt function
        expression = {
            "op": "sqrt",
            "args": [{"value": 16}]
        }
        result = self.engine.evaluate_expression(expression, {})
        assert result == 4.0

        # Test abs function
        expression = {
            "op": "abs",
            "args": [{"value": -10}]
        }
        result = self.engine.evaluate_expression(expression, {})
        assert result == 10

        # Test max function
        expression = {
            "op": "max",
            "args": [{"value": 5}, {"value": 10}]
        }
        result = self.engine.evaluate_expression(expression, {})
        assert result == 10

    def test_evaluate_round_function(self):
        """Test round function."""
        expression = {
            "op": "round",
            "args": [{"value": 3.14159}, {"value": 2}]
        }
        result = self.engine.evaluate_expression(expression, {})
        assert result == 3.14

    def test_division_by_zero_error(self):
        """Test that division by zero raises an error."""
        expression = {
            "op": "divide",
            "args": [
                {"value": 10},
                {"value": 0}
            ]
        }
        with pytest.raises(ValueError, match="Division by zero"):
            self.engine.evaluate_expression(expression, {})

    def test_missing_field_error(self):
        """Test that missing field raises an error."""
        expression = {"field": "nonexistent_field"}
        with pytest.raises(ValueError, match="Field 'nonexistent_field' not found"):
            self.engine.evaluate_expression(expression, self.test_data)

    def test_unknown_operation_error(self):
        """Test that unknown operation raises an error."""
        expression = {
            "op": "unknown_operation",
            "args": [{"value": 1}, {"value": 2}]
        }
        with pytest.raises(ValueError, match="Unknown operation"):
            self.engine.evaluate_expression(expression, {})

    def test_invalid_argument_count_error(self):
        """Test that invalid argument count for operations raises an error."""
        # Add operation requires exactly 2 arguments
        expression = {
            "op": "add",
            "args": [{"value": 1}]  # Only 1 argument provided
        }
        with pytest.raises(ValueError, match="requires exactly 2 arguments"):
            self.engine.evaluate_expression(expression, {})

        # Test with too many arguments
        expression = {
            "op": "add",
            "args": [{"value": 1}, {"value": 2}, {"value": 3}]  # 3 arguments provided
        }
        with pytest.raises(ValueError, match="requires exactly 2 arguments"):
            self.engine.evaluate_expression(expression, {})

    def test_invalid_expression_structure(self):
        """Test that invalid expression structure raises an error."""
        # Expression must be a dictionary
        with pytest.raises(ValueError, match="Expression must be a dictionary"):
            self.engine.evaluate_expression("invalid", {})

        # Expression must have valid structure
        expression = {"invalid_key": "invalid_value"}
        with pytest.raises(ValueError, match="Invalid expression structure"):
            self.engine.evaluate_expression(expression, {})

    def test_validate_expression_valid(self):
        """Test validation of valid expressions."""
        expression = {
            "op": "add",
            "args": [
                {"field": "field1"},
                {"value": 10}
            ]
        }
        assert self.engine.validate_expression(expression) is True

    def test_validate_expression_invalid(self):
        """Test validation of invalid expressions."""
        # Invalid operation
        expression = {
            "op": "invalid_op",
            "args": [{"value": 1}, {"value": 2}]
        }
        assert self.engine.validate_expression(expression) is False

        # Division by zero
        expression = {
            "op": "divide",
            "args": [{"value": 1}, {"value": 0}]
        }
        assert self.engine.validate_expression(expression) is False

    def test_collect_field_names(self):
        """Test field name collection from expressions."""
        expression = {
            "op": "divide",
            "args": [
                {
                    "op": "add",
                    "args": [
                        {"field": "revenue"},
                        {"field": "other_income"}
                    ]
                },
                {"field": "shares"}
            ]
        }
        
        fields = {}
        self.engine._collect_field_names(expression, fields)
        
        expected_fields = {"revenue", "other_income", "shares"}
        assert set(fields.keys()) == expected_fields

    def test_complex_financial_ratio_calculation(self):
        """Test a complex financial ratio calculation."""
        # Calculate debt-to-equity ratio: liabilities / (assets - liabilities)
        expression = {
            "op": "divide",
            "args": [
                {"field": "liabilities"},
                {
                    "op": "subtract",
                    "args": [
                        {"field": "assets"},
                        {"field": "liabilities"}
                    ]
                }
            ]
        }
        
        result = self.engine.evaluate_expression(expression, self.test_data)
        expected = 2000000 / (5000000 - 2000000)  # 2000000 / 3000000 ≈ 0.667
        assert abs(result - expected) < 0.001