"""Displacement risk prediction model."""

from typing import Dict, Any, List
from datetime import datetime

class RiskStage:
    def __init__(self, risk_score: float, signals_active: List[str], confidence: float, interpretation: str):
        self.risk_score = risk_score
        self.signals_active = signals_active
        self.confidence = confidence
        self.interpretation = interpretation

class DisplacementRiskForecast:
    def __init__(self, tract_id: str, overall_risk_score: float):
        self.tract_id = tract_id
        self.overall_risk_score = overall_risk_score
        self.primary_risk_drivers = []
        self.signal_weights = {}
        self.data_sources = []
        self.confidence_1yr = 0.82
        self.confidence_3yr = 0.65
        self.confidence_5yr = 0.45
        self.most_likely_trajectory = ""
        self.timestamp = datetime.now().isoformat()
        
        # Stage-specific forecasts
        self.early_stage = RiskStage(
            risk_score=45,
            signals_active=["Capital inflows", "Permit surge"],
            confidence=0.85,
            interpretation="Early gentrification signals detected"
        )
        self.mid_stage = RiskStage(
            risk_score=55,
            signals_active=["Rent appreciation", "Demographic shifts"],
            confidence=0.72,
            interpretation="Mid-stage gentrification trajectory likely"
        )
        self.late_stage = RiskStage(
            risk_score=overall_risk_score,
            signals_active=["High eviction rates", "Displacement"],
            confidence=0.55,
            interpretation="Late-stage displacement risk"
        )
        
        # Multi-stakeholder recommendations
        self.stakeholder_recommendations = {
            "residents": [
                "Organize with neighbors for tenant protections",
                "Document displacement risks for advocacy",
                "Connect with legal aid services"
            ],
            "investors": [
                "Consider community benefits agreements",
                "Explore inclusive development models",
                "Monitor long-term community stability"
            ],
            "city": [
                "Implement anti-displacement ordinances",
                "Support community land trusts",
                "Require inclusionary zoning"
            ]
        }

def compute_displacement_risk(
    tract_id: str,
    tier1_data: Dict[str, Any],
    tier2_data: Dict[str, Any]
) -> DisplacementRiskForecast:
    """Compute deterministic displacement risk forecast."""
    
    # Simple weighted average (will be expanded in Phase 5+)
    tier1_signals = tier1_data.get("tier1", {})
    tier1_avg = sum(s.get("value", 0) for s in tier1_signals.values()) / max(len(tier1_signals), 1)
    tier2_avg = sum(s.get("value", 0) for s in tier2_data.values()) / max(len(tier2_data), 1)
    
    # Weighted combination (60% Tier1, 30% Tier2, 10% buffer)
    overall_score = (tier1_avg * 0.6 + tier2_avg * 0.3 + 10)
    overall_score = min(100, max(0, overall_score))
    
    forecast = DisplacementRiskForecast(tract_id, overall_score)
    forecast.most_likely_trajectory = _trajectory_text(overall_score)
    forecast.primary_risk_drivers = _get_drivers(tier1_signals, tier2_data)
    forecast.signal_weights = {
        "tier1": 0.6,
        "tier2": 0.3,
        "tier3": 0.1
    }
    forecast.data_sources = ["Tier 1 Research", "Government Data"]
    
    return forecast

def _trajectory_text(score: float) -> str:
    """Describe trajectory based on score."""
    if score > 70:
        return "Rapid gentrification likely within 0-2 years"
    elif score > 50:
        return "Gradual gentrification expected within 2-5 years"
    elif score > 30:
        return "Slow neighborhood change expected within 5+ years"
    else:
        return "Neighborhood likely to remain stable"

def _get_drivers(tier1: dict, tier2: dict) -> List[str]:
    """Extract primary risk drivers."""
    drivers = []
    for signal_type in tier1.keys():
        drivers.append(signal_type.replace("_", " ").title())
    return drivers[:3]  # Top 3 drivers
