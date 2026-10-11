"""Phase 3 Investment Forecast: investor-facing appreciation view.

ARCHITECTURE COMPLIANCE (per project rules):
1. Every number traceable to a named source -- no black boxes.
2. No randomness. Same tract_id always returns same output.
3. Mock/placeholder values are labeled explicitly, never presented as real.

CURRENT DATA STATE:
- Median price per neighborhood: PLACEHOLDER. No live MLS/Redfin/Rocket
  feed is wired in yet. A prior handoff note claimed real July 2026 MLS
  prices were already integrated here -- that was not true of this
  codebase, and this module intentionally does not repeat that claim.
  Replace PLACEHOLDER_MEDIAN_PRICE with a real pricing service before
  showing this to actual investors.
- Investment grade and appreciation %: DERIVED, not looked up. They are
  a deterministic function of the existing displacement-risk /
  opportunity-score model (scoring_phase3.py), which itself already
  cites Chapple & Zuk (2016), Zuk et al. (2018), and Hwang & Lin (2016).
  This is a reframing of validated inputs, not a new predictive model --
  consistent with "no ML until 20+ validated tracts."
"""

from typing import Dict, Any

# Placeholder median prices. NOT sourced from a live feed. Deterministic
# per tract so scoring stays reproducible until real pricing is wired in.
# TODO(next): replace with a real service (see services/acs_service.py
# for the pattern -- real call + labeled mock fallback).
PLACEHOLDER_MEDIAN_PRICE: Dict[str, int] = {}
_DEFAULT_PLACEHOLDER_PRICE = 185_000  # Pittsburgh citywide rough midpoint, not a live figure


def _get_median_price(tract_id: str) -> Dict[str, Any]:
    price = PLACEHOLDER_MEDIAN_PRICE.get(tract_id, _DEFAULT_PLACEHOLDER_PRICE)
    return {
        "value": price,
        "data_source": "placeholder_not_live",
        "note": (
            "No live MLS/Redfin/Rocket feed connected yet. This is a flat "
            "placeholder, not a real current price. Do not use for actual "
            "investment decisions until a real pricing service replaces this."
        ),
    }


def _investment_grade(opportunity_score: float, displacement_risk: float) -> str:
    """Deterministic A-D letter grade.

    Grade rewards high opportunity_score but penalizes very high
    displacement risk, since rapid-displacement tracts carry more
    regulatory/reputational/exit-liquidity risk for investors, not less.
    """
    adjusted = opportunity_score - max(0, displacement_risk - 70) * 0.5
    if adjusted >= 75:
        return "A"
    elif adjusted >= 60:
        return "B"
    elif adjusted >= 45:
        return "C"
    else:
        return "D"


def _expected_appreciation(opportunity_score: float, risk_score: float) -> Dict[str, float]:
    """Deterministic appreciation estimate derived from the existing risk model.

    NOT an ML prediction. Simple linear mapping calibrated so that
    opportunity_score=50 (citywide average risk profile) maps to
    Pittsburgh's approximate long-run metro appreciation trend (~3%/yr),
    scaling up toward higher-opportunity tracts. This is a placeholder
    heuristic pending real historical panel data (see backtest.py) --
    it should be replaced once 20+ tracts have validated real appreciation
    history per the project's own "no ML before 20+ tracts" rule, and
    this heuristic is one step below that: not ML, just a labeled formula.
    """
    base_rate = 0.03  # long-run Pittsburgh metro trend, informal baseline
    delta = (opportunity_score - 50) / 50 * 0.05  # +/-5% swing at extremes
    annual_rate = max(-0.02, base_rate + delta)

    one_yr = round(annual_rate * 100, 1)
    five_yr_cagr_total = round(((1 + annual_rate) ** 5 - 1) * 100, 1)

    return {
        "one_year_pct": one_yr,
        "five_year_total_pct": five_yr_cagr_total,
        "methodology": (
            "Deterministic linear heuristic on top of the existing "
            "opportunity_score (itself derived from Chapple & Zuk 2016, "
            "Zuk et al. 2018 displacement signals). Not an ML forecast."
        ),
    }


def compute_investment_forecast(tract_id: str, opportunity_score: float, displacement_risk: float) -> Dict[str, Any]:
    """Build the Phase 3 investor-facing forecast block.

    Called from scoring_phase3.py's investor_output, using values already
    computed there -- this function adds no new signal inputs, only
    reframes existing ones plus the (placeholder) price.
    """
    grade = _investment_grade(opportunity_score, displacement_risk)
    appreciation = _expected_appreciation(opportunity_score, displacement_risk)
    price = _get_median_price(tract_id)

    return {
        "investment_grade": grade,
        "expected_appreciation": appreciation,
        "current_median_price": price,
        "confidence": {
            "value": 0.65 if displacement_risk < 70 else 0.50,
            "note": "Lower confidence assigned to high-displacement-risk tracts (more volatile).",
        },
    }
