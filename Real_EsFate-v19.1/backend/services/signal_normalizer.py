"""Signal normalization layer.

Responsibility:
- Convert raw signals → canonical schema
- Normalize numeric ranges
- Enforce consistency across sources
"""

from typing import Dict, Any, List
import math


def normalize_min_max(value: float, min_val: float, max_val: float) -> float:
    """Min-max normalization to [0, 1]."""
    if min_val == max_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def normalize_z_score(value: float, mean: float, stddev: float) -> float:
    """Z-score normalization.
    
    Returns value in roughly [-3, 3] range.
    Clip to [-1, 1] for practical use.
    """
    if stddev == 0:
        return 0.0
    z = (value - mean) / stddev
    return max(-1.0, min(1.0, z))


def normalize_percentile(value: float, distribution: List[float]) -> float:
    """Percentile rank normalization.
    
    Returns rank of value in distribution [0, 1].
    """
    if not distribution:
        return 0.5
    sorted_dist = sorted(distribution)
    rank = sum(1 for v in sorted_dist if v <= value) / len(sorted_dist)
    return rank


def winsorize(value: float, lower_pct: float = 0.05, upper_pct: float = 0.95, distribution: List[float] = None) -> float:
    """Winsorize extreme outliers.
    
    Caps at percentiles to reduce noise.
    """
    if not distribution:
        return value
    
    sorted_dist = sorted(distribution)
    lower_bound = sorted_dist[int(len(sorted_dist) * lower_pct)]
    upper_bound = sorted_dist[int(len(sorted_dist) * upper_pct)]
    
    return max(lower_bound, min(upper_bound, value))


def normalize_signal(signal_dict: Dict[str, Any], signal_type: str) -> Dict[str, Any]:
    """Normalize a raw signal to canonical schema.
    
    Applies appropriate normalization based on signal type.
    """
    
    normalized = {
        "tract_id": signal_dict.get("tract_id"),
        "signal_type": signal_type,
        "timestamp": signal_dict.get("timestamp"),
        "source": signal_dict.get("source"),
        "confidence": signal_dict.get("confidence", 0.5),
        "raw_value": signal_dict.get("value"),
    }
    
    # Normalize based on signal type
    raw_value = signal_dict.get("value", 0)
    
    if signal_type == "eviction_rate":
        # Normalize eviction rate (0-15 per 1000 is typical range)
        normalized["normalized_value"] = normalize_min_max(raw_value, 0, 15)
    
    elif signal_type == "rent_growth_pct":
        # Normalize rent growth (-5% to +15% typical range)
        normalized["normalized_value"] = normalize_min_max(raw_value, -5, 15)
    
    elif signal_type == "permit_volume":
        # Normalize permit volume (0-100 per year typical)
        normalized["normalized_value"] = normalize_min_max(raw_value, 0, 100)
    
    elif signal_type == "yelp_business_churn":
        # Normalize churn rate (0-50% typical)
        normalized["normalized_value"] = normalize_min_max(raw_value, 0, 50)
    
    elif signal_type == "job_posting_shift":
        # Normalize tech % (0-100%)
        normalized["normalized_value"] = normalize_min_max(raw_value, 0, 100)
    
    else:
        # Default: assume value is already 0-1
        normalized["normalized_value"] = max(0, min(1, raw_value))
    
    return normalized


def aggregate_signals(signals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate multiple signals into composite feature.
    
    Ensures:
    - All signals are normalized
    - Missing values handled
    - Weights are explicit
    """
    
    if not signals:
        return {"error": "No signals to aggregate"}
    
    normalized_signals = [
        normalize_signal(s, s.get("signal_type", "unknown"))
        for s in signals
    ]
    
    # Weighted average
    total_weight = sum(s.get("confidence", 0.5) for s in normalized_signals)
    if total_weight == 0:
        total_weight = len(normalized_signals)
    
    weighted_value = sum(
        s.get("normalized_value", 0) * s.get("confidence", 0.5)
        for s in normalized_signals
    ) / total_weight
    
    return {
        "composite_value": weighted_value,
        "component_signals": normalized_signals,
        "total_weight": total_weight,
        "count": len(normalized_signals),
    }


def validate_signal_schema(signal: Dict[str, Any]) -> tuple[bool, str]:
    """Validate signal matches canonical schema.
    
    Returns: (is_valid, error_message)
    """
    
    required_fields = ["tract_id", "signal_type", "value", "timestamp", "source"]
    
    for field in required_fields:
        if field not in signal:
            return False, f"Missing required field: {field}"
    
    if not isinstance(signal["value"], (int, float)):
        return False, f"Value must be numeric, got {type(signal['value'])}"
    
    if not isinstance(signal["timestamp"], str):
        return False, "Timestamp must be ISO string"
    
    if not (0 <= signal.get("confidence", 0.5) <= 1):
        return False, "Confidence must be 0-1"
    
    return True, "Valid"
