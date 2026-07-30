"""Prediction history and self-correction tracking."""

from datetime import datetime

# Mock prediction history storage
_prediction_log = {}

def log_prediction(prediction: dict) -> None:
    """Log a prediction for self-correction tracking."""
    tract_id = prediction.get("tract_id")
    if tract_id not in _prediction_log:
        _prediction_log[tract_id] = []
    
    _prediction_log[tract_id].append({
        "timestamp": datetime.now().isoformat(),
        "score": prediction.get("overall_risk_score"),
        "drivers": prediction.get("primary_risk_drivers"),
        "confidence_1yr": prediction.get("confidence_1yr"),
    })

def get_prediction_history(tract_id: str) -> list:
    """Get prediction history for a tract."""
    return _prediction_log.get(tract_id, [])
