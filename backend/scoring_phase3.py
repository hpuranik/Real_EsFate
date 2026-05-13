"""Phase 3 Scoring Engine: integrates Tier 1/2/3 signals + prediction layers.

Replaces Phase 1 deterministic scoring with research-validated, multi-layer approach.
"""

from signals.tier1_research import get_tier1_signals, get_research_citations, validate_signal_value
from signals.tier2_government import get_all_tier2_signals
from signals.tier3_local import get_tier3_schema
from models.prediction import compute_displacement_risk, DisplacementRiskForecast
from models.leadership import get_archetype_forecast, leadership_layer_disclaimer
from models.correction import log_prediction, get_prediction_history

from typing import Dict, Any


def compute_tract_score_phase3(tract_id: str) -> Dict[str, Any]:
    """
    Phase 3 comprehensive scoring:
    1. Tier 1: Research-validated signals
    2. Tier 2: Government data (evictions, permits, HMDA)
    3. Tier 3: Local alpha signals (placeholder)
    4. Prediction: Early/mid/late stage forecast
    5. Leadership: Speculative layer
    6. Self-correction: Prediction logging
    
    Output is multi-stakeholder (researcher, resident, investor, city).
    """
    
    # Gather all signals
    tier1_signals = get_tier1_signals()
    tier2_data = get_all_tier2_signals(tract_id)
    tier3_schema = get_tier3_schema()
    
    # Compute displacement risk forecast
    prediction = compute_displacement_risk(
        tract_id,
        {"tier1": tier1_signals},
        tier2_data
    )
    
    # Log for self-correction
    log_prediction({
        "tract_id": tract_id,
        "overall_risk_score": prediction.overall_risk_score,
        "primary_risk_drivers": prediction.primary_risk_drivers,
        "signal_weights": prediction.signal_weights,
        "data_sources": prediction.data_sources,
        "confidence_1yr": prediction.confidence_1yr,
        "confidence_3yr": prediction.confidence_3yr,
        "confidence_5yr": prediction.confidence_5yr,
    })
    
    # Build researcher view (full transparency)
    researcher_output = {
        "tract_id": tract_id,
        "view": "researcher",
        "displacement_risk_score": prediction.overall_risk_score,
        "trajectory": prediction.most_likely_trajectory,
        "early_stage": {
            "risk_score": prediction.early_stage.risk_score,
            "signals_active": prediction.early_stage.signals_active,
            "confidence": prediction.early_stage.confidence,
            "interpretation": prediction.early_stage.interpretation,
        },
        "mid_stage": {
            "risk_score": prediction.mid_stage.risk_score,
            "signals_active": prediction.mid_stage.signals_active,
            "confidence": prediction.mid_stage.confidence,
            "interpretation": prediction.mid_stage.interpretation,
        },
        "late_stage": {
            "risk_score": prediction.late_stage.risk_score,
            "signals_active": prediction.late_stage.signals_active,
            "confidence": prediction.late_stage.confidence,
            "interpretation": prediction.late_stage.interpretation,
        },
        "confidence_intervals": {
            "1_year": prediction.confidence_1yr,
            "3_year": prediction.confidence_3yr,
            "5_year": prediction.confidence_5yr,
        },
        "methodology": {
            "tier1_signals": list(tier1_signals.keys()),
            "tier2_sources": ["Eviction Lab", "HUD Permits", "HMDA Lending"],
            "signal_weights": prediction.signal_weights,
        },
        "citations": get_research_citations(),
    }
    
    # Build resident view (actionable, accessible)
    resident_output = {
        "tract_id": tract_id,
        "view": "resident",
        "displacement_risk": prediction.overall_risk_score,
        "risk_level": _risk_level_text(prediction.overall_risk_score),
        "what_it_means": prediction.most_likely_trajectory,
        "tenant_resources": _get_tenant_resources(tract_id),
        "historical_context": "Historical rent trends and demographic changes in this neighborhood...",
        "recommendations": prediction.stakeholder_recommendations.get("residents", []),
    }
    
    # Build investor view (opportunity with ethics)
    investor_output = {
        "tract_id": tract_id,
        "view": "investor",
        "opportunity_score": 100 - prediction.overall_risk_score,  # Inverse of risk
        "displacement_risk_disclosure": prediction.overall_risk_score,  # Required transparency
        "market_signals": {
            "early_stage_capital_inflow": prediction.early_stage.risk_score > 50,
            "rent_appreciation_trajectory": prediction.mid_stage.risk_score > 50,
        },
        "community_impact_acknowledgment": (
            f"High opportunity neighborhood with {prediction.overall_risk_score:.0f}/100 displacement risk. "
            "Consider inclusive development models and community benefits agreements."
            if prediction.overall_risk_score > 60
            else "Moderate opportunity. Community impact should be monitored."
        ),
        "recommendations": prediction.stakeholder_recommendations.get("investors", []),
    }
    
    # Build city/planner view
    city_output = {
        "tract_id": tract_id,
        "view": "city",
        "displacement_risk": prediction.overall_risk_score,
        "policy_intervention_window": _get_policy_window(prediction.overall_risk_score),
        "early_warning_signals": prediction.early_stage.signals_active,
        "recommendations": prediction.stakeholder_recommendations.get("city", []),
        "tools": ["Anti-displacement ordinance", "Community land trusts", "Inclusionary zoning"],
    }
    
    # Speculative leadership layer
    leadership_layer = {
        "status": "SPECULATIVE - RESEARCH ONLY",
        "disclaimer": leadership_layer_disclaimer(),
        "note": "This layer is not enabled by default. Contact researchers for access.",
    }
    
    # Prediction history (self-correction)
    prediction_history = get_prediction_history(tract_id)
    
    # Unified output
    return {
        "tract_id": tract_id,
        "displacement_risk_score": prediction.overall_risk_score,
        "trajectory": prediction.most_likely_trajectory,
        "views": {
            "researcher": researcher_output,
            "resident": resident_output,
            "investor": investor_output,
            "city": city_output,
        },
        "leadership_layer": leadership_layer,
        "prediction_history": prediction_history,
        "data_sources": prediction.data_sources,
        "timestamp": prediction.timestamp,
    }


def _risk_level_text(score: float) -> str:
    """Translate risk score to text."""
    if score > 70:
        return "HIGH RISK - Rapid gentrification likely"
    elif score > 50:
        return "MODERATE RISK - Gradual change expected"
    elif score > 30:
        return "LOW RISK - Slow change likely"
    else:
        return "MINIMAL RISK - Stable conditions"


def _get_tenant_resources(tract_id: str) -> list:
    """Return relevant tenant resources and rights."""
    return [
        "PA Tenants' Rights: www.phila.gov/tenants",
        "Legal Aid: 215-241-9950",
        "Eviction Prevention: Emergency rental assistance available",
        "Organizing: Join local tenant union",
    ]


def _get_policy_window(risk_score: float) -> str:
    """Determine policy intervention window."""
    if risk_score > 70:
        return "URGENT: 0-6 months. Early gentrification phase. Act now."
    elif risk_score > 50:
        return "NEAR-TERM: 6-18 months. Capital inflows starting. Plan interventions."
    elif risk_score > 30:
        return "MEDIUM-TERM: 18-36 months. Monitor signals. Build capacity."
    else:
        return "NO IMMEDIATE ACTION: Monitor for trajectory changes."
