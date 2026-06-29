"""Tier 3 local signals (low confidence speculative layer)."""

def get_tier3_schema() -> dict:
    """Return Tier 3 signal schema (ready for real data)."""
    return {
        "sentiment_analysis": {
            "description": "Nextdoor/social sentiment (placeholder)",
            "value": None,
            "source": "Nextdoor API",
            "confidence": 0.4,
        },
        "liquor_licenses": {
            "description": "Luxury retail indicator",
            "value": None,
            "source": "Local records",
            "confidence": 0.3,
        },
        "school_enrollment": {
            "description": "Student demographic shifts",
            "value": None,
            "source": "School district",
            "confidence": 0.5,
        },
    }
