# Services Module

## Overview

The services module contains the core business logic and data processing engines for the Equity Valuation System. This module implements the computational components that transform raw financial data into actionable insights through secure formula evaluation and data transformation pipelines.

## Role and Responsibilities

### Primary Functions
- **Data Transformation**: Convert raw financial data into standardized canonical formats
- **Formula Evaluation**: Execute mathematical calculations and financial ratios securely
- **Financial Data Processing**: Aggregate, normalize, and validate financial metrics
- **Business Logic Orchestration**: Coordinate complex multi-step data processing workflows

### Key Components
- `TransformEngine`: Secure JSON-based formula evaluator for data transformations
- `FormulaEvaluator`: Financial calculation engine for valuation models
- `FinancialDataService`: High-level service for financial data operations

## Architecture

### Transform Engine Design
The `TransformEngine` provides a secure, sandboxed environment for executing mathematical transformations:

```python
# JSON-structured expression evaluation
expression = {
    "op": "divide",
    "args": [
        {"field": "total_debt"},
        {"field": "total_equity"}  
    ]
}

result = transform_engine.evaluate_expression(expression, financial_data)
```

### Security Model
- **No Arbitrary Code Execution**: Only predefined mathematical operations allowed
- **Whitelisted Functions**: Limited set of safe mathematical functions (abs, round, sqrt, etc.)
- **Input Validation**: Strict validation of expression structure and data types
- **Error Boundaries**: Controlled error handling prevents system compromise

### Data Flow Architecture
1. **Raw Data Ingestion**: Financial data received from providers
2. **Transformation Mapping**: Apply field mappings and transformation rules
3. **Formula Evaluation**: Execute calculations using transform engine
4. **Validation Pipeline**: Validate results against business rules
5. **Canonical Storage**: Store standardized data in database

## Key Dependencies

### External Libraries
- `operator`: Python built-in operator functions for mathematical operations
- `math`: Standard mathematical functions and constants
- `json`: JSON parsing and serialization for expressions
- `typing`: Type hints for better code documentation

### Internal Dependencies
- `backend.db.models`: Database models for data persistence
- `backend.schemas`: Pydantic schemas for data validation
- `backend.data_providers`: Data provider interfaces

## Setup Instructions

### Environment Configuration
```bash
# Configure calculation precision
export FINANCIAL_PRECISION=6
export ROUNDING_METHOD="round_half_up"

# Set formula validation mode
export STRICT_FORMULA_VALIDATION=true
```

### Service Initialization
```python
from backend.services import TransformEngine, FinancialDataService

# Initialize transform engine
transform_engine = TransformEngine()

# Initialize financial data service
financial_service = FinancialDataService(
    db_session=db,
    transform_engine=transform_engine
)
```

## Usage Guide

### Creating Transformation Expressions

#### Basic Field Reference
```python
expression = {"field": "revenue"}
```

#### Mathematical Operations
```python
# Debt-to-equity ratio
debt_to_equity = {
    "op": "divide",
    "args": [
        {"field": "total_debt"},
        {"field": "total_equity"}
    ]
}

# Current ratio
current_ratio = {
    "op": "divide", 
    "args": [
        {"field": "current_assets"},
        {"field": "current_liabilities"}
    ]
}
```

#### Complex Calculations
```python
# ROE = Net Income / Shareholder Equity
roe_calculation = {
    "op": "multiply",
    "args": [
        {
            "op": "divide",
            "args": [
                {"field": "net_income"},
                {"field": "shareholders_equity"}
            ]
        },
        {"value": 100}  # Convert to percentage
    ]
}
```

#### Function Usage
```python
# Absolute value of earnings change
earnings_change_abs = {
    "op": "abs",
    "args": [
        {
            "op": "subtract",
            "args": [
                {"field": "current_earnings"},
                {"field": "previous_earnings"}
            ]
        }
    ]
}
```

### Data Processing Workflow

#### Transform Raw Data
```python
# Define transformation mapping
transformation_config = {
    "provider_field": "total_revenue",
    "canonical_field": "revenue",
    "transformation": {
        "op": "multiply",
        "args": [
            {"field": "total_revenue"},
            {"value": 1000000}  # Convert millions to actual value
        ]
    }
}

# Execute transformation  
result = financial_service.transform_raw_data(
    raw_data=provider_data,
    transformation_config=transformation_config
)
```

#### Financial Ratio Calculations
```python
# Calculate multiple financial ratios
ratio_definitions = {
    "pe_ratio": {
        "op": "divide",
        "args": [
            {"field": "share_price"},
            {"field": "earnings_per_share"}
        ]
    },
    "price_to_book": {
        "op": "divide", 
        "args": [
            {"field": "share_price"},
            {"field": "book_value_per_share"}
        ]
    }
}

ratios = financial_service.calculate_ratios(
    financial_data=company_data,
    ratio_definitions=ratio_definitions
)
```

## Testing Instructions

### Unit Tests
```bash
# Run service layer tests
pytest tests/test_services.py -v

# Test transform engine specifically  
pytest tests/test_transform_engine.py -v

# Test with coverage
pytest tests/test_services.py --cov=backend.services --cov-report=html
```

### Integration Tests
```bash
# Test full data transformation pipeline
pytest tests/integration/test_data_transformation.py -v

# Test financial calculations
pytest tests/integration/test_financial_calculations.py -v
```

### Manual Testing
```python
from backend.services import TransformEngine

# Test expression validation
engine = TransformEngine()

# Valid expression
valid_expr = {
    "op": "divide",
    "args": [
        {"field": "numerator"},
        {"field": "denominator"}
    ]
}

is_valid = engine.validate_expression(valid_expr)
print(f"Expression valid: {is_valid}")

# Test calculation
data = {"numerator": 100, "denominator": 4}
result = engine.evaluate_expression(valid_expr, data)
print(f"Result: {result}")  # Should print 25.0
```

## Supported Operations

### Mathematical Operators
- `add`: Addition of two values
- `subtract`: Subtraction of two values  
- `multiply`: Multiplication of two values
- `divide`: Division of two values (with zero-division protection)
- `power`: Exponentiation
- `modulo`: Modulo operation

### Mathematical Functions
- `abs`: Absolute value
- `round`: Round to specified decimal places
- `max`: Maximum of multiple values
- `min`: Minimum of multiple values
- `sum`: Sum of multiple values
- `sqrt`: Square root
- `log`: Natural logarithm
- `log10`: Base-10 logarithm
- `exp`: Exponential function
- `sin`, `cos`, `tan`: Trigonometric functions

### Expression Structure
```python
{
    "op": "operation_name",           # Required: operation to perform
    "args": [                         # Required: list of arguments
        {"field": "field_name"},      # Field reference
        {"value": 123.45},            # Literal value
        {                             # Nested expression
            "op": "nested_operation",
            "args": [...]
        }
    ]
}
```

## Error Handling

### Expression Validation Errors
- **Malformed JSON**: Invalid JSON structure in expressions
- **Unknown Operations**: References to unsupported operations or functions
- **Missing Arguments**: Operations without required arguments
- **Type Mismatches**: Arguments of incorrect types

### Runtime Calculation Errors
- **Division by Zero**: Automatic detection and error reporting
- **Missing Fields**: Field references not found in data
- **Overflow/Underflow**: Mathematical operations resulting in invalid numbers
- **Invalid Function Arguments**: Functions called with inappropriate parameters

### Error Recovery Strategies
- **Graceful Degradation**: Return null values for failed calculations
- **Default Values**: Use predefined defaults for missing data
- **Partial Results**: Return successfully calculated fields even if others fail
- **Detailed Logging**: Comprehensive error logging for debugging

## Performance Considerations

### Expression Optimization
- **Expression Caching**: Cache compiled expressions for repeated use
- **Lazy Evaluation**: Only evaluate expressions when results are needed
- **Parallel Processing**: Execute independent calculations concurrently
- **Memory Management**: Efficient handling of large datasets

### Calculation Efficiency  
- **Batch Processing**: Process multiple companies/periods in single operations
- **Vectorized Operations**: Use efficient mathematical libraries when available
- **Result Caching**: Cache frequently accessed calculation results
- **Database Optimization**: Minimize database round trips

### Monitoring and Profiling
- **Execution Metrics**: Track calculation times and success rates
- **Memory Usage**: Monitor memory consumption during large batch operations
- **Error Rates**: Track and alert on calculation failures
- **Performance Regression**: Detect performance degradation over time

## Security Considerations

### Code Injection Prevention
- **No eval() or exec()**: Never execute arbitrary code strings
- **Whitelisted Operations**: Only allow predefined, safe operations
- **Input Sanitization**: Validate all expression inputs thoroughly
- **Sandboxed Execution**: Isolated execution environment

### Data Protection
- **Input Validation**: Strict validation of financial data inputs
- **Output Sanitization**: Clean calculation results before storage
- **Access Control**: Restrict access to transformation definitions
- **Audit Trail**: Log all transformations for compliance and debugging

## Configuration Reference

### Transform Engine Settings
```python
TRANSFORM_ENGINE_CONFIG = {
    "precision": 6,                    # Decimal precision for calculations
    "rounding_mode": "round_half_up",  # Rounding method
    "max_recursion_depth": 10,         # Maximum expression nesting
    "enable_caching": True,            # Enable expression result caching
    "cache_size": 1000,               # Maximum cached expressions
    "strict_validation": True          # Enable strict input validation
}
```

### Supported Field Types
- `integer`: Whole numbers
- `decimal`: Floating-point numbers
- `percentage`: Values representing percentages (0.0-1.0)
- `currency`: Monetary values
- `ratio`: Financial ratios and multipliers
- `date`: Date values for temporal calculations