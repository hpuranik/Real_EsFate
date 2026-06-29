"""Census ACS 5-Year Estimates service.

Phase 7a. This is the first REAL external data source wired into the
platform -- everything else so far has been deterministic mock data.

Tract IDs in this project are already 11-digit Census FIPS codes
(state[2] + county[3] + tract[6]), so no geocoding/crosswalk is needed
here -- we can call the Census API directly with the tract_id.

API docs: https://www.census.gov/data/developers/data-sets/acs-5year.html
A key is optional for low request volumes but recommended for anything
beyond local development: https://api.census.gov/data/key_signup.html
Set it via the CENSUS_API_KEY environment variable.

IMPORTANT - sandbox limitation disclosed: the live api.census.gov call in
this function has NOT been exercised against the real network from the
environment this was written in (it can't reach api.census.gov). The
request URL, parameters, and parsing logic are based on the documented
ACS5 response shape and were verified against a hardcoded fixture
response (see tests/test_acs_service.py) but the actual live HTTP round
trip needs verifying on a machine that CAN reach the Census API. If it
fails, this falls back to clearly-labeled mock data automatically rather
than crashing the demo.
"""

import os
from typing import Dict, Any, Optional

import requests

from utils.cache import get_cached, set_cached, cache_key

ACS_YEAR = "2022"
ACS_BASE_URL = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5"

# variable -> human label, for traceability (no unexplained magic codes downstream)
VARIABLES = {
    "B19013_001E": "median_household_income",
    "B25064_001E": "median_gross_rent",
    "B25003_002E": "owner_occupied_units",
    "B25003_003E": "renter_occupied_units",
    "B15003_022E": "bachelors_degree",
    "B15003_023E": "masters_degree",
    "B15003_024E": "professional_degree",
    "B15003_025E": "doctorate_degree",
    "B15003_001E": "population_25_plus",
    "B01003_001E": "total_population",
}

# Census uses large negative sentinels for suppressed/unavailable cells.
_MISSING_SENTINELS = {-666666666, -999999999, -888888888, -222222222}

CACHE_TTL_SECONDS = 60 * 60 * 24 * 30  # 30 days - ACS 5-year estimates update annually


def _decompose_tract_id(tract_id: str) -> Optional[Dict[str, str]]:
    """11-digit FIPS -> {state, county, tract} codes the Census API expects."""
    if not tract_id or len(tract_id) != 11 or not tract_id.isdigit():
        return None
    return {
        "state": tract_id[0:2],
        "county": tract_id[2:5],
        "tract": tract_id[5:11],
    }


def _clean(value: Any) -> Optional[float]:
    """Parse a Census API cell value, treating missing-data sentinels as None."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if int(f) in _MISSING_SENTINELS:
        return None
    return f


def parse_acs_response(header_row: list, data_row: list) -> Dict[str, Any]:
    """Pure parsing function, separated from the network call so it can be
    unit-tested against a fixture without hitting the real API.

    header_row / data_row are exactly what the Census API returns: a list
    of column names and a matching list of string values for one geography.
    """
    raw = dict(zip(header_row, data_row))
    values = {}
    for code, label in VARIABLES.items():
        values[label] = _clean(raw.get(code))

    owner = values.get("owner_occupied_units") or 0
    renter = values.get("renter_occupied_units") or 0
    total_units = owner + renter
    pct_renter_occupied = round(renter / total_units * 100, 1) if total_units > 0 else None

    bachelors_or_higher = sum(
        values.get(k) or 0
        for k in ("bachelors_degree", "masters_degree", "professional_degree", "doctorate_degree")
    )
    pop_25plus = values.get("population_25_plus") or 0
    pct_bachelors_or_higher = (
        round(bachelors_or_higher / pop_25plus * 100, 1) if pop_25plus > 0 else None
    )

    return {
        "median_household_income": values.get("median_household_income"),
        "median_gross_rent": values.get("median_gross_rent"),
        "total_population": values.get("total_population"),
        "pct_renter_occupied": pct_renter_occupied,
        "pct_bachelors_or_higher": pct_bachelors_or_higher,
        "data_source": "Census ACS 5-Year Estimates",
        "acs_year": ACS_YEAR,
    }


def _mock_fallback(tract_id: str) -> Dict[str, Any]:
    """Deterministic mock, used only if the live Census API call fails.
    Clearly labeled so it's never mistaken for real data downstream --
    same transparency principle as signals/tier1_research.py.
    """
    profiles = {
        "42003030100": {"income": 58000, "rent": 1150, "pop": 2400, "renter_pct": 78.0, "ba_pct": 52.0},
        "42003030200": {"income": 52000, "rent": 1050, "pop": 1100, "renter_pct": 65.0, "ba_pct": 41.0},
        "42003030300": {"income": 61000, "rent": 1200, "pop": 9800, "renter_pct": 58.0, "ba_pct": 47.0},
        "42003030400": {"income": 47000, "rent": 980, "pop": 1700, "renter_pct": 70.0, "ba_pct": 33.0},
        "42003030500": {"income": 28000, "rent": 720, "pop": 8600, "renter_pct": 72.0, "ba_pct": 18.0},
        "42003030600": {"income": 31000, "rent": 680, "pop": 4600, "renter_pct": 60.0, "ba_pct": 16.0},
        "42003030700": {"income": 49000, "rent": 1000, "pop": 7200, "renter_pct": 62.0, "ba_pct": 38.0},
        "42003030800": {"income": 35000, "rent": 1100, "pop": 12500, "renter_pct": 81.0, "ba_pct": 55.0},
        "42003030900": {"income": 89000, "rent": 1450, "pop": 13200, "renter_pct": 45.0, "ba_pct": 68.0},
    }
    p = profiles.get(tract_id, {"income": 50000, "rent": 1000, "pop": 5000, "renter_pct": 60.0, "ba_pct": 35.0})
    return {
        "median_household_income": p["income"],
        "median_gross_rent": p["rent"],
        "total_population": p["pop"],
        "pct_renter_occupied": p["renter_pct"],
        "pct_bachelors_or_higher": p["ba_pct"],
        "data_source": "mock_fallback",
        "acs_year": None,
    }


def get_tract_demographics(tract_id: str) -> Dict[str, Any]:
    """Main entry point. Tries the real Census ACS API, caches success for
    30 days, and falls back to clearly-labeled mock data on any failure
    (network, missing key, malformed tract_id, rate limit) so a data
    outage degrades gracefully rather than crashing tract scoring.
    """
    key = cache_key("acs_demographics", tract_id=tract_id, year=ACS_YEAR)
    cached = get_cached(key)
    if cached is not None:
        return cached

    codes = _decompose_tract_id(tract_id)
    if codes is None:
        result = _mock_fallback(tract_id)
        set_cached(key, result, ttl_seconds=300)  # short TTL - this is a real error, not just no key
        return result

    params = {
        "get": "NAME," + ",".join(VARIABLES.keys()),
        "for": f"tract:{codes['tract']}",
        "in": f"state:{codes['state']} county:{codes['county']}",
    }
    api_key = os.environ.get("CENSUS_API_KEY")
    if api_key:
        params["key"] = api_key

    try:
        resp = requests.get(ACS_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        rows = resp.json()  # [[header...], [values...]]
        result = parse_acs_response(rows[0], rows[1])
    except Exception as exc:  # network down, bad key, API shape change, etc.
        result = _mock_fallback(tract_id)
        result["fallback_reason"] = str(exc)

    set_cached(key, result, ttl_seconds=CACHE_TTL_SECONDS)
    return result
