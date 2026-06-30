"""Fixture test for acs_service parsing logic.

This does NOT hit the real Census API (api.census.gov isn't reachable from
the sandbox this was developed in). It validates parse_acs_response()
against a hardcoded response shaped exactly like a real ACS5 API reply, so
the parsing/percentage math is verified even though the live HTTP round
trip has not been. Run the live path on a machine with real network access
before trusting it in production.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.acs_service import parse_acs_response, VARIABLES

# Real ACS5 API responses look like: [[header...], [row1...], [row2...]]
# Header order matches whatever you passed in `get=`. This fixture uses our
# actual VARIABLES dict order plus NAME/state/county/tract, mirroring a real reply.
HEADER = ["NAME"] + list(VARIABLES.keys()) + ["state", "county", "tract"]
FIXTURE_ROW = [
    "Census Tract 3, Allegheny County, Pennsylvania",
    "52000",   # median_household_income
    "950",     # median_gross_rent
    "1200",    # owner_occupied_units
    "1800",    # renter_occupied_units
    "400",     # bachelors
    "150",     # masters
    "30",      # professional
    "20",      # doctorate
    "5500",    # population_25_plus
    "9800",    # total_population
    "42", "003", "030300",
]


def test_basic_parse():
    result = parse_acs_response(HEADER, FIXTURE_ROW)
    assert result["median_household_income"] == 52000
    assert result["median_gross_rent"] == 950
    assert result["total_population"] == 9800
    # renter_pct = 1800 / (1200+1800) * 100 = 60.0
    assert result["pct_renter_occupied"] == 60.0
    # bachelors_or_higher = 400+150+30+20 = 600; 600/5500*100 = 10.9
    assert result["pct_bachelors_or_higher"] == 10.9
    assert result["data_source"] == "Census ACS 5-Year Estimates"
    print("test_basic_parse: PASS")


def test_missing_sentinel():
    row = list(FIXTURE_ROW)
    # Census uses -666666666 for suppressed cells (small sample size)
    idx = HEADER.index("B19013_001E")
    row[idx] = "-666666666"
    result = parse_acs_response(HEADER, row)
    assert result["median_household_income"] is None
    print("test_missing_sentinel: PASS")


def test_zero_denominator_no_crash():
    row = list(FIXTURE_ROW)
    row[HEADER.index("B25003_002E")] = "0"
    row[HEADER.index("B25003_003E")] = "0"
    result = parse_acs_response(HEADER, row)
    assert result["pct_renter_occupied"] is None
    print("test_zero_denominator_no_crash: PASS")


if __name__ == "__main__":
    test_basic_parse()
    test_missing_sentinel()
    test_zero_denominator_no_crash()
    print("All ACS parsing tests passed.")
