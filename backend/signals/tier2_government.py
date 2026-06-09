"""Tier 2 government data signals."""

def get_all_tier2_signals(tract_id: str) -> dict:
    """Get all Tier 2 government signals for a tract."""
    return {
        "eviction_filings": {
            "value": 12,
            "source": "Eviction Lab",
            "confidence": 0.90,
        },
        "building_permits": {
            "value": 8,
            "source": "HUD",
            "confidence": 0.88,
        },
        "mortgage_lending": {
            "value": 35,
            "source": "HMDA",
            "confidence": 0.85,
        },
    }
