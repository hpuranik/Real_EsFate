"""Tier 1 research-validated signals — per-tract mock profiles.

TRACT IDs: now real Pittsburgh Census FIPS codes (verified against
University of Pittsburgh library census tract guide). Previous version
used invented placeholder IDs that matched no real geography.

Mock values are deterministic per tract and calibrated to roughly match
what real historical ACS/FHFA data shows for each neighborhood's known
trajectory (e.g. Lawrenceville high, Shadyside low, Hazelwood critical).
These will be replaced by real API calls in Phase 7b (FHFA + HMDA).
"""

_PROFILES = {
    "42003020100": {"rent_appreciation": 28, "permit_surge": 22, "eviction_uptick": 12, "home_price_growth": 30},  # Downtown
    "42003020300": {"rent_appreciation": 55, "permit_surge": 62, "eviction_uptick": 28, "home_price_growth": 58},  # Strip District
    "42003090100": {"rent_appreciation": 78, "permit_surge": 70, "eviction_uptick": 38, "home_price_growth": 75},  # Lawrenceville
    "42003981200": {"rent_appreciation": 40, "permit_surge": 35, "eviction_uptick": 18, "home_price_growth": 42},  # North Shore
    "42003050100": {"rent_appreciation": 88, "permit_surge": 90, "eviction_uptick": 60, "home_price_growth": 85},  # Hill District
    "42003562300": {"rent_appreciation": 99, "permit_surge": 98, "eviction_uptick": 82, "home_price_growth": 97},  # Hazelwood
    "42003160900": {"rent_appreciation": 50, "permit_surge": 48, "eviction_uptick": 30, "home_price_growth": 52},  # Southside
    "42003040500": {"rent_appreciation": 35, "permit_surge": 30, "eviction_uptick": 15, "home_price_growth": 38},  # Oakland
    "42003070300": {"rent_appreciation": 20, "permit_surge": 15, "eviction_uptick":  8, "home_price_growth": 18},  # Shadyside
}
_DEFAULT = {"rent_appreciation": 45, "permit_surge": 38, "eviction_uptick": 28, "home_price_growth": 52}


def get_tier1_signals(tract_id: str = None) -> dict:
    p = _PROFILES.get(tract_id, _DEFAULT)
    return {
        "rent_appreciation":  {"value": p["rent_appreciation"],  "source": "Zuk et al. 2018",          "confidence": 0.85},
        "permit_surge":       {"value": p["permit_surge"],       "source": "Hwang & Lin 2016",          "confidence": 0.80},
        "eviction_uptick":    {"value": p["eviction_uptick"],    "source": "Princeton Eviction Lab",    "confidence": 0.75},
        "home_price_growth":  {"value": p["home_price_growth"],  "source": "FHFA",                     "confidence": 0.85},
    }


def get_research_citations(tract_id: str = None) -> list:
    return [
        {"authors": ["Zuk", "Bierbaum", "Chapple", "Gorska", "Loukaitou-Sideris"],
         "year": 2018, "source": "Gentrification, Displacement and the Role of Public Investment",
         "doi": "10.1080/01944363.2017.1380215"},
        {"authors": ["Hwang", "Lin"], "year": 2016,
         "source": "What Have We Learned About the Causes of Recent Gentrification?",
         "doi": "10.1080/10511482.2016.1138987"},
        {"authors": ["Desmond"], "year": 2016,
         "source": "Evicted: Poverty and Profit in the American City",
         "doi": "10.1177/0094306117698039b"},
    ]


def validate_signal_value(value: float, signal_name: str) -> bool:
    return 0 <= value <= 100
