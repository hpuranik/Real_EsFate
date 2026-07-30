"""Tier 2 government data signals — deterministic mock per real FIPS tract.

Calibrated to match neighborhood risk profiles established in:
- UCSUR (2020). Pittsburgh Neighborhood Profiles. University of Pittsburgh.
- PCRG (2019). State of Home Mortgage Lending in Pittsburgh. 
  Pittsburgh Community Reinvestment Group.
"""

_PROFILES = {
    # Original 9
    "42003020100": {"eviction_filings": 10, "building_permits": 12, "mortgage_lending": 18},
    "42003020300": {"eviction_filings": 20, "building_permits": 42, "mortgage_lending": 40},
    "42003090100": {"eviction_filings": 25, "building_permits": 55, "mortgage_lending": 58},
    "42003981200": {"eviction_filings": 14, "building_permits": 20, "mortgage_lending": 25},
    "42003050100": {"eviction_filings": 32, "building_permits": 68, "mortgage_lending": 62},
    "42003562300": {"eviction_filings": 48, "building_permits": 97, "mortgage_lending": 95},
    "42003160900": {"eviction_filings": 18, "building_permits": 35, "mortgage_lending": 38},
    "42003040500": {"eviction_filings": 12, "building_permits": 18, "mortgage_lending": 22},
    "42003070300": {"eviction_filings":  6, "building_permits":  8, "mortgage_lending": 12},
    # New 21
    "42003111300": {"eviction_filings": 28, "building_permits": 62, "mortgage_lending": 55},  # East Liberty
    "42003080400": {"eviction_filings": 22, "building_permits": 48, "mortgage_lending": 48},  # Bloomfield
    "42003101900": {"eviction_filings": 26, "building_permits": 42, "mortgage_lending": 38},  # Garfield
    "42003060500": {"eviction_filings": 16, "building_permits": 38, "mortgage_lending": 40},  # Polish Hill
    "42003140400": {"eviction_filings":  5, "building_permits": 10, "mortgage_lending": 15},  # Point Breeze
    "42003080700": {"eviction_filings": 18, "building_permits": 44, "mortgage_lending": 42},  # Friendship
    "42003140200": {"eviction_filings":  4, "building_permits":  8, "mortgage_lending": 12},  # Squirrel Hill N
    "42003140800": {"eviction_filings":  4, "building_permits": 10, "mortgage_lending": 14},  # Squirrel Hill S
    "42003110200": {"eviction_filings": 10, "building_permits": 18, "mortgage_lending": 25},  # Highland Park
    "42003100500": {"eviction_filings":  8, "building_permits": 14, "mortgage_lending": 22},  # Stanton Heights
    "42003151600": {"eviction_filings": 12, "building_permits": 22, "mortgage_lending": 28},  # Greenfield
    "42003191400": {"eviction_filings": 14, "building_permits": 26, "mortgage_lending": 30},  # Mt Washington
    "42003101400": {"eviction_filings":  9, "building_permits": 16, "mortgage_lending": 24},  # Morningside
    "42003563201": {"eviction_filings": 20, "building_permits": 38, "mortgage_lending": 35},  # East Allegheny
    "42003191600": {"eviction_filings": 10, "building_permits": 14, "mortgage_lending": 20},  # Beechview
    "42003290200": {"eviction_filings": 11, "building_permits": 12, "mortgage_lending": 18},  # Carrick
    "42003130800": {"eviction_filings": 45, "building_permits":  8, "mortgage_lending":  6},  # Homewood South
    "42003120900": {"eviction_filings": 42, "building_permits":  6, "mortgage_lending":  5},  # Larimer
    "42003270300": {"eviction_filings": 10, "building_permits": 15, "mortgage_lending": 20},  # Brighton Heights
    "42003261400": {"eviction_filings": 18, "building_permits": 16, "mortgage_lending": 18},  # Perry South
    "42003241300": {"eviction_filings": 10, "building_permits": 16, "mortgage_lending": 20},  # Spring Garden
}
_DEFAULT = {"eviction_filings": 12, "building_permits": 8, "mortgage_lending": 35}


def get_all_tier2_signals(tract_id: str) -> dict:
    p = _PROFILES.get(tract_id, _DEFAULT)
    return {
        "eviction_filings": {"value": p["eviction_filings"], "source": "Eviction Lab",  "confidence": 0.90},
        "building_permits": {"value": p["building_permits"], "source": "HUD",            "confidence": 0.88},
        "mortgage_lending": {"value": p["mortgage_lending"], "source": "HMDA",           "confidence": 0.85},
    }
