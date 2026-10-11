"""Block-group level scoring.

Real geography: 76 actual Census block groups (GEOID format, e.g.
420031608004) within our 9 tracked neighborhoods, sourced from the
Census Bureau's 2017 cartographic boundary files (state=42 PA, county=003
Allegheny), filtered to the same tract set as utils/tract_registry.py.
See frontend/data/pittsburgh-block-groups.json for the boundaries.

SCORING: block groups do NOT have independent mock signal profiles --
real sub-tract data (ACS publishes most variables at block-group level,
but our current Tier 1/2 mock signals don't). Instead, each block group's
score is its PARENT TRACT's real score, with a small deterministic
intra-tract variation so the map isn't visually flat within a
neighborhood. The variation is a hash-based offset, NOT random (same
block group always gets the same offset on every run), and is clearly
smaller than the variation BETWEEN neighborhoods, so the dominant pattern
on the map still reflects real cross-neighborhood differences, not noise.

This is an honest interim step: real block-group-level signals are a
Phase 7c/8 task once data sources publish at that resolution.
"""

import hashlib
from typing import Dict, Any

from scoring_phase3 import compute_tract_score_phase3
from utils.tract_registry import TRACT_REGISTRY


def _canonical_tract_for(member_tract_fips: str) -> str:
    """A block group's real parent tract (e.g. Crawford-Roberts, 42003030500)
    may not be the single canonical tract_id the scoring engine has a mock
    profile for (Hill District's canonical tract is 42003050100). Map any
    member tract back to its neighborhood's canonical tract_id so scoring
    uses the right profile instead of silently falling back to a generic
    default for every non-canonical member tract.
    """
    for canonical_id, info in TRACT_REGISTRY.items():
        if member_tract_fips in info["all_tracts"]:
            return canonical_id
    return member_tract_fips  # unknown tract, let compute_tract_score_phase3 handle/fallback


def _deterministic_offset(geoid: str, spread: float = 6.0) -> float:
    """Hash-based, reproducible offset in [-spread, +spread]. Same GEOID
    always produces the same offset -- this is NOT random per page load."""
    h = int(hashlib.sha256(geoid.encode()).hexdigest(), 16)
    frac = (h % 10000) / 10000.0  # 0.0 - 1.0
    return (frac * 2 - 1) * spread


def compute_block_group_score(geoid: str, parent_tract_id: str) -> Dict[str, Any]:
    canonical_tract_id = _canonical_tract_for(parent_tract_id)
    parent = compute_tract_score_phase3(canonical_tract_id)
    parent_score = parent["displacement_risk_score"]

    offset = _deterministic_offset(geoid)
    bg_score = max(0, min(100, parent_score + offset))

    return {
        "block_group_geoid": geoid,
        "parent_tract_id": parent_tract_id,
        "canonical_scoring_tract_id": canonical_tract_id,
        "displacement_risk_score": round(bg_score, 1),
        "parent_tract_score": round(parent_score, 1),
        "score_basis": (
            "Derived from parent tract's score with a small deterministic "
            "intra-tract variation. Real block-group-level signals are not "
            "yet integrated (Phase 8) -- this is an honest interim "
            "approximation, not independently measured sub-tract data."
        ),
    }
