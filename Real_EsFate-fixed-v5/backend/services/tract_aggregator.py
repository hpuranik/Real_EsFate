"""Tract aggregation engine.

Responsibility:
- Group signals by tract_id
- Aggregate by signal_type
- Compute weighted feature vectors
"""

from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime, timedelta


def aggregate_tract_signals(tract_id: str, all_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate all signals for a single tract.
    
    Groups by signal_type, computes statistics.
    """
    
    # Filter to this tract
    tract_signals = [s for s in all_signals if s.get("tract_id") == tract_id]
    
    if not tract_signals:
        return {"tract_id": tract_id, "error": "No signals found"}
    
    # Group by signal type
    by_type = defaultdict(list)
    for signal in tract_signals:
        by_type[signal.get("signal_type")].append(signal)
    
    # Compute per-type aggregations
    aggregated = {}
    for signal_type, signals in by_type.items():
        values = [s.get("value", 0) for s in signals]
        confidences = [s.get("confidence", 0.5) for s in signals]
        
        # Weighted average
        total_confidence = sum(confidences)
        weighted_avg = (
            sum(v * c for v, c in zip(values, confidences)) / total_confidence
            if total_confidence > 0
            else 0
        )
        
        aggregated[signal_type] = {
            "count": len(signals),
            "value": weighted_avg,
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "confidence": sum(confidences) / len(confidences),
            "sources": list(set(s.get("source", "unknown") for s in signals)),
        }
    
    return {
        "tract_id": tract_id,
        "timestamp": datetime.now().isoformat(),
        "signal_count": len(tract_signals),
        "signal_types": list(aggregated.keys()),
        "aggregated_signals": aggregated,
    }


def compute_signal_trends(tract_id: str, historical_signals: List[Dict[str, Any]], days: int = 365) -> Dict[str, str]:
    """Compute trend (increasing/stable/decreasing) for signals.
    
    Compares signals from N days ago vs now.
    """
    
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    
    # Split into recent vs older
    recent = [s for s in historical_signals if datetime.fromisoformat(s.get("timestamp", "")) > cutoff]
    older = [s for s in historical_signals if datetime.fromisoformat(s.get("timestamp", "")) <= cutoff]
    
    trends = {}
    
    for signal_type in set(s.get("signal_type") for s in historical_signals):
        recent_values = [s.get("value", 0) for s in recent if s.get("signal_type") == signal_type]
        older_values = [s.get("value", 0) for s in older if s.get("signal_type") == signal_type]
        
        if not recent_values or not older_values:
            trends[signal_type] = "insufficient_data"
            continue
        
        recent_avg = sum(recent_values) / len(recent_values)
        older_avg = sum(older_values) / len(older_values)
        
        pct_change = ((recent_avg - older_avg) / older_avg * 100) if older_avg != 0 else 0
        
        if pct_change > 5:
            trends[signal_type] = "increasing"
        elif pct_change < -5:
            trends[signal_type] = "decreasing"
        else:
            trends[signal_type] = "stable"
    
    return trends


def validate_tract_data(tract_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate aggregated tract data quality.
    
    Returns: (is_valid, warnings)
    """
    
    warnings = []
    
    # Check signal count
    if tract_data.get("signal_count", 0) == 0:
        warnings.append("No signals available")
    elif tract_data.get("signal_count", 0) < 3:
        warnings.append("Limited signals (<3)")
    
    # Check signal types diversity
    signal_types = len(tract_data.get("signal_types", []))
    if signal_types < 2:
        warnings.append("Low signal diversity")
    
    # Check confidence levels
    aggregated = tract_data.get("aggregated_signals", {})
    low_confidence_signals = [
        st for st, data in aggregated.items()
        if data.get("confidence", 0) < 0.5
    ]
    if low_confidence_signals:
        warnings.append(f"Low confidence signals: {', '.join(low_confidence_signals)}")
    
    is_valid = len(warnings) == 0 or len(warnings) <= 1
    
    return is_valid, warnings
