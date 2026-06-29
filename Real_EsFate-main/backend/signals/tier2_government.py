"""Tier 2 government data signals."""

# MOCK DATA — Phase 6 placeholder, deterministic per tract_id. See
# signals/tier1_research.py for the rationale; same approach here.
_TIER2_MOCK_PROFILES = {
    "42003030100": {"eviction_filings": 10, "building_permits": 12, "mortgage_lending": 18},  # Downtown
    "42003030200": {"eviction_filings": 20, "building_permits": 42, "mortgage_lending": 40},  # Strip District
    "42003030300": {"eviction_filings": 25, "building_permits": 55, "mortgage_lending": 58},  # Lawrenceville
    "42003030400": {"eviction_filings": 14, "building_permits": 20, "mortgage_lending": 25},  # North Shore
    "42003030500": {"eviction_filings": 32, "building_permits": 68, "mortgage_lending": 62},  # Hill District
    "42003030600": {"eviction_filings": 48, "building_permits": 97, "mortgage_lending": 95},  # Hazelwood
    "42003030700": {"eviction_filings": 18, "building_permits": 35, "mortgage_lending": 38},  # Southside
    "42003030800": {"eviction_filings": 12, "building_permits": 18, "mortgage_lending": 22},  # Oakland
    "42003030900": {"eviction_filings": 6, "building_permits": 8, "mortgage_lending": 12},  # Shadyside
}

_DEFAULT_PROFILE = {"eviction_filings": 12, "building_permits": 8, "mortgage_lending": 35}


def get_all_tier2_signals(tract_id: str) -> dict:
    """Get all Tier 2 government signals for a tract (mock, deterministic per tract_id)."""
    profile = _TIER2_MOCK_PROFILES.get(tract_id, _DEFAULT_PROFILE)
    return {
        "eviction_filings": {
            "value": profile["eviction_filings"],
            "source": "Eviction Lab",
            "confidence": 0.90,
        },
        "building_permits": {
            "value": profile["building_permits"],
            "source": "HUD",
            "confidence": 0.88,
        },
        "mortgage_lending": {
            "value": profile["mortgage_lending"],
            "source": "HMDA",
            "confidence": 0.85,
        },
    }
