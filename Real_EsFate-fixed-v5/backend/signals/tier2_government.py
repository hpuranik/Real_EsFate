"""Tier 2 government data signals — deterministic mock per real FIPS tract."""

_PROFILES = {
    "42003020100": {"eviction_filings": 10, "building_permits": 12, "mortgage_lending": 18},
    "42003020300": {"eviction_filings": 20, "building_permits": 42, "mortgage_lending": 40},
    "42003090100": {"eviction_filings": 25, "building_permits": 55, "mortgage_lending": 58},
    "42003981200": {"eviction_filings": 14, "building_permits": 20, "mortgage_lending": 25},
    "42003050100": {"eviction_filings": 32, "building_permits": 68, "mortgage_lending": 62},
    "42003562300": {"eviction_filings": 48, "building_permits": 97, "mortgage_lending": 95},
    "42003160900": {"eviction_filings": 18, "building_permits": 35, "mortgage_lending": 38},
    "42003040500": {"eviction_filings": 12, "building_permits": 18, "mortgage_lending": 22},
    "42003070300": {"eviction_filings":  6, "building_permits":  8, "mortgage_lending": 12},
}
_DEFAULT = {"eviction_filings": 12, "building_permits": 8, "mortgage_lending": 35}


def get_all_tier2_signals(tract_id: str) -> dict:
    p = _PROFILES.get(tract_id, _DEFAULT)
    return {
        "eviction_filings": {"value": p["eviction_filings"], "source": "Eviction Lab",   "confidence": 0.90},
        "building_permits": {"value": p["building_permits"], "source": "HUD",             "confidence": 0.88},
        "mortgage_lending": {"value": p["mortgage_lending"], "source": "HMDA",            "confidence": 0.85},
    }
