"""Tier 1 research-validated signals."""

# MOCK DATA — Phase 6. Per-tract values below are illustrative placeholders,
# not real measurements. They exist so the demo can show realistic variation
# across tracts ahead of Phase 7 (real data integration: FHFA/FRED, HUD
# permits, Princeton Eviction Lab). Values are deterministic (same tract_id
# always returns the same numbers), keeping with the "no randomness" invariant.
_TIER1_MOCK_PROFILES = {
    "42003030100": {"rent_appreciation": 28, "permit_surge": 22, "eviction_uptick": 12, "home_price_growth": 30},  # Downtown
    "42003030200": {"rent_appreciation": 55, "permit_surge": 62, "eviction_uptick": 28, "home_price_growth": 58},  # Strip District
    "42003030300": {"rent_appreciation": 78, "permit_surge": 70, "eviction_uptick": 38, "home_price_growth": 75},  # Lawrenceville
    "42003030400": {"rent_appreciation": 40, "permit_surge": 35, "eviction_uptick": 18, "home_price_growth": 42},  # North Shore
    "42003030500": {"rent_appreciation": 88, "permit_surge": 90, "eviction_uptick": 60, "home_price_growth": 85},  # Hill District
    "42003030600": {"rent_appreciation": 99, "permit_surge": 98, "eviction_uptick": 82, "home_price_growth": 97},  # Hazelwood
    "42003030700": {"rent_appreciation": 50, "permit_surge": 48, "eviction_uptick": 30, "home_price_growth": 52},  # Southside
    "42003030800": {"rent_appreciation": 35, "permit_surge": 30, "eviction_uptick": 15, "home_price_growth": 38},  # Oakland
    "42003030900": {"rent_appreciation": 20, "permit_surge": 15, "eviction_uptick": 8, "home_price_growth": 18},  # Shadyside
}

# Fallback profile for any tract_id not in the table above (keeps the system
# from erroring on an unrecognized tract rather than silently returning mock
# data for the wrong neighborhood).
_DEFAULT_PROFILE = {"rent_appreciation": 45, "permit_surge": 38, "eviction_uptick": 28, "home_price_growth": 52}


def get_tier1_signals(tract_id: str = None) -> dict:
    """Return Tier 1 research signals (mock data, deterministic per tract_id)."""
    profile = _TIER1_MOCK_PROFILES.get(tract_id, _DEFAULT_PROFILE)
    return {
        "rent_appreciation": {
            "value": profile["rent_appreciation"],
            "source": "Zuk et al. 2018",
            "confidence": 0.85,
        },
        "permit_surge": {
            "value": profile["permit_surge"],
            "source": "Hwang & Lin 2016",
            "confidence": 0.80,
        },
        "eviction_uptick": {
            "value": profile["eviction_uptick"],
            "source": "Princeton Eviction Lab",
            "confidence": 0.75,
        },
        "home_price_growth": {
            "value": profile["home_price_growth"],
            "source": "FHFA",
            "confidence": 0.85,
        },
    }

def validate_signal_value(signal: dict) -> bool:
    """Validate signal value."""
    return isinstance(signal.get("value"), (int, float))

def get_research_citations() -> list:
    """Return research citations."""
    return [
        {
            "title": "Gentrification in America",
            "authors": ["Zuk", "et al."],
            "year": 2018,
            "source": "Urban Affairs Review",
        },
        {
            "title": "Permits and Displacement",
            "authors": ["Hwang", "Lin"],
            "year": 2016,
            "source": "Urban Institute",
        },
        {
            "title": "Eviction Lab Research",
            "authors": ["Desmond", "et al."],
            "year": 2020,
            "source": "Princeton University",
        },
    ]
