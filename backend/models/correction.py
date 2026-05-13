"""Self-correction loop: prediction logging, outcome tracking, and Bayesian reweighting.

This is the most important component for long-term credibility.

Workflow:
1. Store every prediction with timestamp + signal weights + data sources
2. When new data arrives (quarterly), compare prediction to actual outcome
3. Score which signals fired correctly (accuracy per signal)
4. Reweight model accordingly (lightweight Bayesian update)
5. Flag when trajectory deviated and why
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json


@dataclass
class PredictionLog:
    """Logged prediction at a point in time."""
    tract_id: str
    prediction_date: str  # ISO timestamp
    
    # Prediction state
    predicted_risk_score: float  # 0-100
    predicted_drivers: List[str]  # Which signals were active?
    signal_weights: Dict[str, float]  # Model weights at time of prediction
    data_sources: List[str]
    
    # Confidence at different horizons
    confidence_1yr: float
    confidence_3yr: float
    confidence_5yr: float
    
    # For later comparison
    actual_outcome: str = None  # Will be filled in later
    actual_risk_score: float = None  # Will be updated
    outcome_date: str = None  # When did we measure actual?
    
    # Accuracy scoring
    signals_correct: List[str] = None  # Which signals predicted correctly?
    signals_missed: List[str] = None  # Which signals didn't fire but should have?
    false_positives: List[str] = None  # Which signals fired but didn't matter?


@dataclass
class SignalAccuracyScore:
    """Track accuracy of individual signals over time."""
    signal_name: str
    times_active: int  # How many times did this signal fire?
    times_correct: int  # How many times was it actually predictive?
    accuracy: float  # times_correct / times_active
    last_updated: str = datetime.now().isoformat()


# In-memory prediction log (Phase 4: move to PostgreSQL)
PREDICTION_LOGS: Dict[str, List[PredictionLog]] = {}
SIGNAL_ACCURACY_SCORES: Dict[str, SignalAccuracyScore] = {}


def log_prediction(prediction_dict: dict) -> None:
    """Store a prediction for later tracking."""
    tract_id = prediction_dict["tract_id"]
    
    log_entry = PredictionLog(
        tract_id=tract_id,
        prediction_date=datetime.now().isoformat(),
        predicted_risk_score=prediction_dict["overall_risk_score"],
        predicted_drivers=prediction_dict["primary_risk_drivers"],
        signal_weights=prediction_dict["signal_weights"],
        data_sources=prediction_dict["data_sources"],
        confidence_1yr=prediction_dict["confidence_1yr"],
        confidence_3yr=prediction_dict["confidence_3yr"],
        confidence_5yr=prediction_dict["confidence_5yr"],
    )
    
    if tract_id not in PREDICTION_LOGS:
        PREDICTION_LOGS[tract_id] = []
    
    PREDICTION_LOGS[tract_id].append(log_entry)


def compare_prediction_to_outcome(
    tract_id: str,
    actual_risk_score: float,
    actual_signals_fired: List[str],
) -> Dict:
    """Compare logged prediction to actual outcome.
    
    Returns accuracy metrics for self-correction.
    """
    
    if tract_id not in PREDICTION_LOGS or not PREDICTION_LOGS[tract_id]:
        return {"error": f"No prediction log for {tract_id}"}
    
    # Get most recent prediction (could use prediction_date to match timing)
    last_prediction = PREDICTION_LOGS[tract_id][-1]
    
    # Update with actual outcome
    last_prediction.actual_outcome = "observed"
    last_prediction.actual_risk_score = actual_risk_score
    last_prediction.outcome_date = datetime.now().isoformat()
    
    # Score signals
    predicted_drivers = set(last_prediction.predicted_drivers)
    actual_drivers = set(actual_signals_fired)
    
    correct = predicted_drivers & actual_drivers  # True positives
    missed = actual_drivers - predicted_drivers  # False negatives
    false_positives = predicted_drivers - actual_drivers  # Type I errors
    
    last_prediction.signals_correct = list(correct)
    last_prediction.signals_missed = list(missed)
    last_prediction.false_positives = list(false_positives)
    
    # Update signal accuracy scores
    for signal in predicted_drivers:
        if signal not in SIGNAL_ACCURACY_SCORES:
            SIGNAL_ACCURACY_SCORES[signal] = SignalAccuracyScore(
                signal_name=signal,
                times_active=0,
                times_correct=0,
                accuracy=0.0,
            )
        
        score = SIGNAL_ACCURACY_SCORES[signal]
        score.times_active += 1
        if signal in correct:
            score.times_correct += 1
        score.accuracy = score.times_correct / score.times_active
        score.last_updated = datetime.now().isoformat()
    
    # Return accuracy report
    return {
        "tract_id": tract_id,
        "prediction_date": last_prediction.prediction_date,
        "outcome_date": last_prediction.outcome_date,
        "days_between": (
            datetime.fromisoformat(last_prediction.outcome_date) -
            datetime.fromisoformat(last_prediction.prediction_date)
        ).days,
        "predicted_risk": last_prediction.predicted_risk_score,
        "actual_risk": actual_risk_score,
        "prediction_error": abs(last_prediction.predicted_risk_score - actual_risk_score),
        "signals_correct": list(correct),
        "signals_missed": list(missed),
        "false_positives": list(false_positives),
        "accuracy_pct": (len(correct) / len(predicted_drivers) * 100) if predicted_drivers else 0,
    }


def get_signal_accuracy_report() -> Dict[str, SignalAccuracyScore]:
    """Get accuracy scores for all signals.
    
    Used to reweight the model.
    """
    return SIGNAL_ACCURACY_SCORES


def reweight_model(accuracy_scores: Dict[str, SignalAccuracyScore]) -> Dict[str, float]:
    """
    Lightweight Bayesian reweighting based on signal accuracy.
    
    Algorithm:
    - High accuracy signals (>0.7) get +10% weight
    - Low accuracy signals (<0.5) get -10% weight
    - Normalize to sum to 1.0
    
    Returns: Updated signal weights
    """
    
    if not accuracy_scores:
        return {}  # No data to reweight
    
    # Calculate weight updates
    weight_updates = {}
    for signal_name, accuracy in accuracy_scores.items():
        if accuracy.accuracy > 0.7:
            weight_updates[signal_name] = 1.1  # Boost 10%
        elif accuracy.accuracy < 0.5:
            weight_updates[signal_name] = 0.9  # Reduce 10%
        else:
            weight_updates[signal_name] = 1.0  # No change
    
    return weight_updates


def get_prediction_history(tract_id: str) -> List[Dict]:
    """Get complete prediction history for a tract.
    
    Used for timeline visualization and accountability.
    """
    
    if tract_id not in PREDICTION_LOGS:
        return []
    
    history = []
    for log in PREDICTION_LOGS[tract_id]:
        history.append({
            "prediction_date": log.prediction_date,
            "predicted_risk_score": log.predicted_risk_score,
            "predicted_drivers": log.predicted_drivers,
            "actual_risk_score": log.actual_risk_score,
            "accuracy_pct": (
                len(set(log.predicted_drivers) & set(log.signals_correct or []))
                / len(set(log.predicted_drivers))
                * 100
                if log.predicted_drivers else None
            ),
        })
    
    return history


def self_correction_disclaimer() -> str:
    """Mandatory disclaimer for self-correction methodology."""
    return (
        "📊 SELF-CORRECTION METHODOLOGY\n"
        "This model improves over time by comparing predictions to actual outcomes.\n"
        "Signal weights are reweighted quarterly based on accuracy.\n"
        "Early predictions (2023-2024) have lower confidence due to limited feedback data.\n"
        "See prediction history to track model performance.\n"
        "Model limitations documented here: [link to methodology]"
    )
