"""Tier 1 research-validated signals."""

def get_tier1_signals() -> dict:
    """Return Tier 1 research signals with mock data."""
    return {
        "rent_appreciation": {
            "value": 45,
            "source": "Zuk et al. 2018",
            "confidence": 0.85,
        },
        "permit_surge": {
            "value": 38,
            "source": "Hwang & Lin 2016",
            "confidence": 0.80,
        },
        "eviction_uptick": {
            "value": 28,
            "source": "Princeton Eviction Lab",
            "confidence": 0.75,
        },
        "home_price_growth": {
            "value": 52,
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
