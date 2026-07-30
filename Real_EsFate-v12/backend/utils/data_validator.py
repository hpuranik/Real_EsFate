"""Data validation layer.

Validates all incoming signals and outputs.
Ensures schema compliance.
Rejects malformed inputs.
"""

from typing import Dict, Any, Tuple, List
from datetime import datetime
import re


# Canonical schemas
SIGNAL_SCHEMA = {
    "tract_id": {"type": "string", "pattern": r"^\d{11,12}$"},
    "signal_type": {"type": "string", "pattern": r"^[a-z_]+$"},
    "value": {"type": "number"},
    "timestamp": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}T.*Z?$"},
    "source": {"type": "string"},
    "confidence": {"type": "number", "min": 0, "max": 1},
}

SCORE_SCHEMA = {
    "tract_id": {"type": "string"},
    "score": {"type": "number", "min": 0, "max": 100},
    "confidence": {"type": "number", "min": 0, "max": 1},
    "trend": {"type": "string", "enum": ["increasing", "stable", "decreasing"]},
    "drivers": {"type": "array", "items": {"type": "string"}},
    "explanation": {"type": "object"},
}


def validate_field(value: Any, schema: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a single field against schema.
    
    Returns: (is_valid, error_message)
    """
    
    field_type = schema.get("type")
    
    # Type check
    if field_type == "string" and not isinstance(value, str):
        return False, f"Expected string, got {type(value).__name__}"
    elif field_type == "number" and not isinstance(value, (int, float)):
        return False, f"Expected number, got {type(value).__name__}"
    elif field_type == "array" and not isinstance(value, list):
        return False, f"Expected array, got {type(value).__name__}"
    elif field_type == "object" and not isinstance(value, dict):
        return False, f"Expected object, got {type(value).__name__}"
    
    # Pattern check
    if "pattern" in schema:
        if not re.match(schema["pattern"], str(value)):
            return False, f"Value '{value}' doesn't match pattern {schema['pattern']}"
    
    # Enum check
    if "enum" in schema:
        if value not in schema["enum"]:
            return False, f"Value '{value}' not in {schema['enum']}"
    
    # Range check
    if "min" in schema and value < schema["min"]:
        return False, f"Value {value} below minimum {schema['min']}"
    if "max" in schema and value > schema["max"]:
        return False, f"Value {value} exceeds maximum {schema['max']}"
    
    return True, "Valid"


def validate_signal(signal: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate signal against SIGNAL_SCHEMA.
    
    Returns: (is_valid, errors)
    """
    
    errors = []
    required_fields = ["tract_id", "signal_type", "value", "timestamp", "source"]
    
    # Check required fields
    for field in required_fields:
        if field not in signal:
            errors.append(f"Missing required field: {field}")
    
    # Validate each field
    for field, value in signal.items():
        if field in SIGNAL_SCHEMA:
            valid, error = validate_field(value, SIGNAL_SCHEMA[field])
            if not valid:
                errors.append(f"{field}: {error}")
    
    return len(errors) == 0, errors


def validate_score_output(output: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate score output against SCORE_SCHEMA.
    
    Returns: (is_valid, errors)
    """
    
    errors = []
    required_fields = ["tract_id", "score", "confidence", "trend", "drivers", "explanation"]
    
    # Check required fields
    for field in required_fields:
        if field not in output:
            errors.append(f"Missing required field: {field}")
    
    # Validate each field
    for field, value in output.items():
        if field in SCORE_SCHEMA:
            valid, error = validate_field(value, SCORE_SCHEMA[field])
            if not valid:
                errors.append(f"{field}: {error}")
    
    return len(errors) == 0, errors


def sanitize_tract_id(tract_id: str) -> str:
    """Sanitize and validate tract ID format."""
    # Expect format: SSBBBTTTRRR (state-block-tract-remainder)
    # Example: 42003030100
    if not re.match(r"^\d{11,12}$", tract_id):
        raise ValueError(f"Invalid tract ID format: {tract_id}")
    return tract_id


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide with default for zero division."""
    if denominator == 0:
        return default
    return numerator / denominator
