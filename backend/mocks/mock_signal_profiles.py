"""Deterministic mock signal profiles for canonical tracts.

This module provides labeled mock profiles used when real data is unavailable.
Rules:
- Deterministic: same tract_id -> same profile every run (no randomness).
- Labeled: every profile contains "is_mock": True and "source": "mock_profile_v1".
- Values are deterministic functions of the tract_id (MD5 hash) and therefore
  reproducible and auditable.

Do NOT use these profiles as "real" forecasts. They exist only as fallbacks
that fail loudly (is_mock=True) if real services are not configured.
"""

from typing import Dict, Any
import hashlib


def _hash_int(tract_id: str) -> int:
    """Return a positive integer derived deterministically from tract_id."""
    h = hashlib.md5(tract_id.encode("utf8")).hexdigest()
    return int(h, 16)


def _scale(h: int, low: float, high: float, precision: int = 2) -> float:
    """Scale hash to a deterministic float between low and high (inclusive).

    Uses modulo arithmetic to keep the result deterministic and stable.
    """
    if high < low:
        raise ValueError("high must be >= low")
    width = high - low
    # Use a slice of the hash space to get distribution across the range
    v = (h % 10000) / 10000.0  # in [0, 1)
    val = low + v * width
    return round(val, precision)


def get_mock_profile(tract_id: str) -> Dict[str, Any]:
    """Return a deterministic mock profile for the given tract_id.

    Profile fields (examples used by frontend and scoring engine):
    - income_growth_pct: estimated household income growth (percent)
    - permit_surge_index: 0-100 indicator of recent permit activity
    - transit_proximity_score: 0.0-1.0 proximity to transit
    - expected_appreciation_1y/3y/5y: deterministic CAGR-like estimates (percent)
    - confidence: low/medium/high (always labeled as MOCK)
    - is_mock: True (must be present so callers can fail loudly if needed)
    - source: "mock_profile_v1"
    """
    if not isinstance(tract_id, str) or not tract_id:
        raise ValueError("tract_id must be a non-empty string")

    h = _hash_int(tract_id)

    # Build deterministic but varied signals
    income_growth_pct = _scale(h, -5.0, 30.0, precision=2)
    permit_surge_index = int(_scale(h >> 12, 0, 100, precision=0))
    transit_proximity_score = _scale(h >> 20, 0.0, 1.0, precision=2)

    # Expected appreciation: use combinations to keep monotonicity
    expected_appreciation_1y = round(income_growth_pct * 0.12 + (permit_surge_index - 50) * 0.02, 2)
    expected_appreciation_3y = round(expected_appreciation_1y * 3.0 * 0.95, 2)
    expected_appreciation_5y = round(expected_appreciation_1y * 5.0 * 0.9, 2)

    # Normalize small values (keep deterministic sign)
    def _clamp(v: float, lo: float = -30.0, hi: float = 100.0) -> float:
        return round(max(lo, min(hi, v)), 2)

    expected_appreciation_1y = _clamp(expected_appreciation_1y)
    expected_appreciation_3y = _clamp(expected_appreciation_3y)
    expected_appreciation_5y = _clamp(expected_appreciation_5y)

    # Confidence is intentionally low for mock data
    confidence = "LOW-MOCK"

    profile = {
        "tract_id": tract_id,
        "is_mock": True,
        "source": "mock_profile_v1",
        "income_growth_pct": income_growth_pct,
        "permit_surge_index": permit_surge_index,
        "transit_proximity_score": transit_proximity_score,
        "expected_appreciation_1y_pct": expected_appreciation_1y,
        "expected_appreciation_3y_pct": expected_appreciation_3y,
        "expected_appreciation_5y_pct": expected_appreciation_5y,
        "confidence_label": confidence,
        "calibration_note": (
            "Deterministic mock calibrated from tract_id hash. "
            "Use only when real data services are unavailable."
        ),
    }

    return profile


if __name__ == "__main__":
    # Quick CLI for manual inspection
    import sys

    if len(sys.argv) < 2:
        print("Usage: python mock_signal_profiles.py <tract_id>")
        sys.exit(2)

    print(get_mock_profile(sys.argv[1]))
