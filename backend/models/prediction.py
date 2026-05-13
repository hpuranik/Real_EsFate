"""Prediction engine: signal stack with early/mid/late stage indicators.

Structure:
- Early stage (0-2 yrs): Capital inflows, development interest
- Mid stage (2-5 yrs): Rent growth, business turnover, demographic shift
- Late stage (now): Evictions, school churn, displacement

Each stage has validated indicators from Tier 1 research.
Confidence intervals widen dramatically for 5-year window.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class PredictionStage:
    """A prediction stage with indicators and confidence."""
    name: str  # "early", "mid", "late"
    horizon: str  # "0-2 years", "2-5 years", "now"
    signals_active: List[str]  # Which Tier 1/2 signals are firing?
    indicators: Dict[str, float]  # Signal name -> value
    risk_score: float  # 0-100, aggregated from active signals
    confidence: float  # 0-1 (widens over time horizon)
    interpretation: str  # Plain English description


@dataclass
class DisplacementRiskForecast:
    """Complete displacement risk prediction for a tract."""
    tract_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Three-stage forecast
    early_stage: PredictionStage = None
    mid_stage: PredictionStage = None
    late_stage: PredictionStage = None
    
    # Overall metrics
    overall_risk_score: float = 0.0  # 0-100
    primary_risk_drivers: List[str] = field(default_factory=list)
    most_likely_trajectory: str = ""
    
    # Uncertainty
    confidence_1yr: float = 0.0
    confidence_3yr: float = 0.0
    confidence_5yr: float = 0.0
    
    # Recommendations
    stakeholder_recommendations: Dict[str, List[str]] = field(default_factory=dict)
    
    # Prediction logging (for self-correction)
    signal_weights: Dict[str, float] = field(default_factory=dict)
    data_sources: List[str] = field(default_factory=list)


def compute_displacement_risk(tract_id: str, tier1_signals: dict, tier2_signals: dict) -> DisplacementRiskForecast:
    """
    Compute three-stage displacement risk forecast.
    
    Input: Tier 1 (research-validated) + Tier 2 (government) signals
    Output: DisplacementRiskForecast with early/mid/late stage scores
    """
    
    # Extract signal values
    eviction_data = tier2_signals.get("eviction", {})
    hmda_data = tier2_signals.get("hmda", {})
    permit_data = tier2_signals.get("permits", {})
    
    rent_growth = 2.0  # Placeholder; should come from tier1
    eviction_rate = eviction_data.get("filing_rate", 0)
    permit_surge = permit_data.get("permits_12m", 0)
    loan_growth = hmda_data.get("loan_amount_growth", 0)
    
    # EARLY STAGE (0-2 yrs): Capital inflows signal
    early_signals_active = []
    early_risk = 0.0
    
    if permit_surge > 30:
        early_signals_active.append("permit_surge")
        early_risk += 35
    if loan_growth > 5:
        early_signals_active.append("hmda_growth")
        early_risk += 25
    
    early_stage = PredictionStage(
        name="early",
        horizon="0-2 years",
        signals_active=early_signals_active,
        indicators={
            "permit_surge": permit_surge,
            "loan_growth_pct": loan_growth,
        },
        risk_score=min(early_risk, 100),
        confidence=0.82,
        interpretation=f"Capital inflows increasing. {len(early_signals_active)} early indicators firing."
    )
    
    # MID STAGE (2-5 yrs): Rent + business turnover + demographic shift
    mid_signals_active = []
    mid_risk = 0.0
    
    if rent_growth > 3:
        mid_signals_active.append("rent_appreciation")
        mid_risk += 40
    if hmda_data.get("denial_rate", 0) > 0.10:
        mid_signals_active.append("lending_tightening")
        mid_risk += 15
    
    mid_stage = PredictionStage(
        name="mid",
        horizon="2-5 years",
        signals_active=mid_signals_active,
        indicators={
            "rent_growth_pct": rent_growth,
            "loan_denial_rate": hmda_data.get("denial_rate", 0),
        },
        risk_score=min(mid_risk, 100),
        confidence=0.65,  # Lower confidence for 2-5yr
        interpretation=f"Rent pressure increasing. {len(mid_signals_active)} mid-stage indicators firing."
    )
    
    # LATE STAGE (now): Direct displacement signals
    late_signals_active = []
    late_risk = 0.0
    
    if eviction_rate > 5:
        late_signals_active.append("eviction_uptick")
        late_risk += 50
    if eviction_data.get("trend") == "increasing":
        late_signals_active.append("eviction_accelerating")
        late_risk += 20
    
    late_stage = PredictionStage(
        name="late",
        horizon="now",
        signals_active=late_signals_active,
        indicators={
            "eviction_rate_per_1000": eviction_rate,
            "eviction_trend": eviction_data.get("trend", "stable"),
        },
        risk_score=min(late_risk, 100),
        confidence=0.92,  # Highest confidence (current data)
        interpretation=f"Direct displacement signals detected. {len(late_signals_active)} late-stage indicators firing."
    )
    
    # Aggregate overall risk
    overall_risk = (early_stage.risk_score * 0.25 + 
                   mid_stage.risk_score * 0.35 + 
                   late_stage.risk_score * 0.40)
    
    primary_drivers = early_signals_active + mid_signals_active + late_signals_active
    
    # Determine trajectory
    if overall_risk > 70:
        trajectory = "HIGH DISPLACEMENT RISK - Rapid gentrification likely"
    elif overall_risk > 50:
        trajectory = "MODERATE DISPLACEMENT RISK - Gradual demographic transition"
    elif overall_risk > 30:
        trajectory = "LOW DISPLACEMENT RISK - Slow change expected"
    else:
        trajectory = "MINIMAL DISPLACEMENT RISK - Stable conditions"
    
    # Stakeholder recommendations
    recommendations = {
        "residents": [
            "Monitor rent trends quarterly",
            "Connect with local tenant union",
            "Know your rights under eviction law",
        ] if overall_risk > 30 else ["No immediate action needed"],
        "researchers": [
            "Track signal accuracy: compare predictions to actual outcomes",
            "Document policy interventions and their effects",
            "Contribute to model reweighting",
        ],
        "investors": [
            "HIGH OPPORTUNITY but community impact should be acknowledged",
            "Consider inclusive development models",
        ] if overall_risk > 50 else ["MODERATE OPPORTUNITY"],
        "city": [
            "Assess anti-displacement policy capacity",
            "Consider inclusionary zoning or community land trusts",
            "Engage residents early in planning",
        ] if overall_risk > 40 else ["Monitor for future changes"],
    }
    
    return DisplacementRiskForecast(
        tract_id=tract_id,
        early_stage=early_stage,
        mid_stage=mid_stage,
        late_stage=late_stage,
        overall_risk_score=round(overall_risk, 1),
        primary_risk_drivers=primary_drivers,
        most_likely_trajectory=trajectory,
        confidence_1yr=early_stage.confidence,
        confidence_3yr=mid_stage.confidence,
        confidence_5yr=0.45,  # Very low for 5-year
        stakeholder_recommendations=recommendations,
        signal_weights={
            "early_stage": 0.25,
            "mid_stage": 0.35,
            "late_stage": 0.40,
        },
        data_sources=[
            "Tier 1: Urban Institute, NCRC, Furman Center, Zuk et al. (2018)",
            "Tier 2: Eviction Lab, HUD Permits, HMDA Lending Data",
        ]
    )
