import json
from typing import Dict, Any, Union
import math
import operator

class TransformEngine:
    """
    Secure formula evaluator that processes JSON-structured transformation expressions.
    Supports basic mathematical operations without allowing arbitrary code execution.
    """
    
    def __init__(self):
        self.operators = {
            'add': operator.add,
            'subtract': operator.sub,
            'multiply': operator.mul,
            'divide': operator.truediv,
            'power': operator.pow,
            'modulo': operator.mod,
        }
        
        self.functions = {
            'abs': abs,
            'round': round,
            'max': max,
            'min': min,
            'sum': sum,
            'sqrt': math.sqrt,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
        }
    
    def evaluate_expression(self, expression: Dict[str, Any], data: Dict[str, Union[int, float]]) -> Union[int, float]:
        """
        Evaluate a JSON-structured expression against provided data.
        
        Args:
            expression: JSON structure defining the calculation
            data: Dictionary of field_name -> value
            
        Returns:
            Calculated result
            
        Example expression:
        {
            "op": "divide",
            "args": [
                {"field": "total_liabilities"},
                {"field": "total_assets"}
            ]
        }
        """
        if not isinstance(expression, dict):
            raise ValueError("Expression must be a dictionary")
        
        if 'field' in expression:
            # Direct field reference
            field_name = expression['field']
            if field_name not in data:
                raise ValueError(f"Field '{field_name}' not found in data")
            return data[field_name]
        
        if 'value' in expression:
            # Literal value
            return expression['value']
        
        if 'op' in expression:
            # Operation
            op_name = expression['op']
            args = expression.get('args', [])
            
            if op_name in self.operators:
                if len(args) != 2:
                    raise ValueError(f"Operator '{op_name}' requires exactly 2 arguments")
                
                left = self.evaluate_expression(args[0], data)
                right = self.evaluate_expression(args[1], data)
                
                # Handle division by zero
                if op_name == 'divide' and right == 0:
                    raise ValueError("Division by zero")
                
                return self.operators[op_name](left, right)
            
            elif op_name in self.functions:
                evaluated_args = [self.evaluate_expression(arg, data) for arg in args]
                return self.functions[op_name](*evaluated_args)
            
            else:
                raise ValueError(f"Unknown operation: {op_name}")
        
        raise ValueError("Invalid expression structure")
    
    def validate_expression(self, expression: Dict[str, Any]) -> bool:
        """
        Validate that an expression is well-formed without evaluating it.
        """
        try:
            # Test with dummy data
            dummy_data = {}
            self._collect_field_names(expression, dummy_data)
            # Fill with dummy values
            for field in dummy_data:
                dummy_data[field] = 1.0
            
            self.evaluate_expression(expression, dummy_data)
            return True
        except Exception:
            return False
    
    def _collect_field_names(self, expression: Dict[str, Any], fields: Dict[str, float]):
        """Recursively collect all field names referenced in an expression."""
        if isinstance(expression, dict):
            if 'field' in expression:
                fields[expression['field']] = 0.0
            elif 'args' in expression:
                for arg in expression['args']:
                    self._collect_field_names(arg, fields)