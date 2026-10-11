"""Phase 3.5: Researcher signal breakdown + comparables, and City Planner
infrastructure recommendations.

ARCHITECTURE COMPLIANCE:
- Deterministic: pure functions of tract_id and already-computed signals.
- No new external calls, no randomness.
- All comparisons based on the existing Tier 1 (signals/tier1_research.py)
  and Tier 2 (signals/tier2_government.py) mock profiles, calibrated per
  Chapple & Zuk (2016) and UCSUR (2020) as already documented in those
  files. This module adds no new data sources, only new views of existing
  ones.
"""

from typing import Dict, Any, List
from signals.tier1_research import _PROFILES as TIER1_PROFILES
from utils.tract_registry import TRACT_REGISTRY

# Signal fires if it crosses this normalized threshold (0-100 scale),
# consistent with the "signals_active" thresholding already used in
# models/prediction.py's RiskStage early/mid/late buckets.
_SIGNAL_FIRE_THRESHOLD = 50


def get_signal_breakdown(tract_id: str) -> List[Dict[str, Any]]:
    """Which Tier 1 signals fired for this tract, and why.

    Returns each signal with its raw value, whether it crossed the fire
    threshold, and a one-line explanation of what that signal measures.
    """
    profile = TIER1_PROFILES.get(tract_id, {})

    explanations = {
        "rent_appreciation": "Rate of rent growth relative to citywide baseline (Chapple & Zuk 2016 core indicator).",
        "permit_surge": "Building permit volume increase, a leading indicator of capital inflow (Zuk et al. 2018).",
        "eviction_uptick": "Rise in eviction filings, associated with displacement pressure (Hwang & Lin 2016).",
        "home_price_growth": "Home sale price appreciation relative to citywide baseline.",
    }

    breakdown = []
    for signal_name, value in profile.items():
        breakdown.append({
            "signal": signal_name,
            "value": value,
            "fired": value >= _SIGNAL_FIRE_THRESHOLD,
            "explanation": explanations.get(signal_name, "No description available."),
        })
    return sorted(breakdown, key=lambda s: s["value"], reverse=True)


def get_comparable_neighborhoods(tract_id: str, top_n: int = 3) -> List[Dict[str, Any]]:
    """Find neighborhoods with the most similar Tier 1 signal profile.

    Similarity = inverse Euclidean distance across the 4 Tier 1 signal
    dimensions. This is nearest-neighbor matching on existing mock/real
    signal values, not a trained model -- consistent with "no ML before
    20+ validated tracts."
    """
    target = TIER1_PROFILES.get(tract_id)
    if not target:
        return []

    def distance(a: dict, b: dict) -> float:
        keys = set(a.keys()) & set(b.keys())
        if not keys:
            return float("inf")
        return sum((a[k] - b[k]) ** 2 for k in keys) ** 0.5

    scored = []
    for other_id, profile in TIER1_PROFILES.items():
        if other_id == tract_id:
            continue
        d = distance(target, profile)
        scored.append((d, other_id))

    scored.sort(key=lambda x: x[0])

    results = []
    for dist, other_id in scored[:top_n]:
        name = TRACT_REGISTRY.get(other_id, {}).get("name", other_id)
        # Normalize distance into a rough 0-100 similarity score (max
        # possible distance across 4 signals each 0-100 is 200, per the
        # Euclidean formula above; used only for display, not a metric
        # claiming precision).
        similarity_pct = round(max(0, 100 - (dist / 200 * 100)), 1)
        results.append({
            "tract_id": other_id,
            "name": name,
            "similarity_pct": similarity_pct,
            "note": f"Similar Tier 1 signal profile to {name} (nearest-neighbor match, not a trained model).",
        })
    return results


# Infrastructure priority thresholds. A tract is flagged for a given
# intervention type when the underlying signal crosses these cutoffs.
# These are heuristic planning triggers, not zoning law -- labeled as such.
def get_infrastructure_recommendations(tract_id: str, tier2_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Deterministic 'where to prioritize infrastructure' suggestions for city planners.

    Based on existing Tier 2 government signals (building_permits,
    mortgage_lending, eviction_filings) already computed elsewhere in the
    pipeline -- this function adds no new inputs.
    """
    recs = []
    permits = tier2_data.get("building_permits", {}).get("value", 0)
    lending = tier2_data.get("mortgage_lending", {}).get("value", 0)
    evictions = tier2_data.get("eviction_filings", {}).get("value", 0)

    if permits >= 50 and lending >= 40:
        recs.append({
            "type": "Transit expansion",
            "rationale": (
                "High permit volume + high mortgage lending suggests sustained "
                "growth capacity; transit access could relieve emerging congestion "
                "before it becomes a bottleneck."
            ),
        })
    if evictions >= 30 and permits < 20:
        recs.append({
            "type": "Affordable housing / anti-displacement infrastructure",
            "rationale": (
                "High eviction filings without matching new development suggests "
                "existing housing stress rather than new-supply-driven growth -- "
                "a candidate for community land trusts or rent stabilization pilots, "
                "not new market-rate construction."
            ),
        })
    if permits >= 30 and evictions < 20:
        recs.append({
            "type": "Parks / public green space",
            "rationale": (
                "Moderate-to-high development activity with lower displacement "
                "pressure suggests room to add amenities without immediately "
                "accelerating displacement risk."
            ),
        })
    if not recs:
        recs.append({
            "type": "Monitor only",
            "rationale": "No signal combination currently crosses an intervention threshold for this tract.",
        })
    return recs
