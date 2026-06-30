"""Single source of truth for tract definitions.

THE CORE PROBLEM THIS FIXES:
The original codebase used invented FIPS codes (42003030100 through 42003030900).
None of those are real Pittsburgh census tracts. Real Allegheny County tracts
were verified against the University of Pittsburgh library guide:
https://pitt.libguides.com/pghcensus/pghcensustracts

FORMAT: 11-digit FIPS = state(42) + county(003) + tract(6 digits right-padded)

Each neighborhood can span multiple tracts. We pick ONE canonical tract per
neighborhood as the scoring unit for the demo (the most population-central one),
and list all member tracts so real ACS aggregation can be done properly later.
"""

from typing import Dict, List

# tract_id -> neighborhood definition
TRACT_REGISTRY: Dict[str, dict] = {
    "42003020100": {
        "name": "Downtown",
        "canonical": True,
        "all_tracts": ["42003020100"],  # Golden Triangle / tract 201
        "display_order": 1,
    },
    "42003020300": {
        "name": "Strip District",
        "canonical": True,
        "all_tracts": ["42003020300"],  # tract 203
        "display_order": 2,
    },
    "42003090100": {
        "name": "Lawrenceville",
        "canonical": True,  # Central Lawrenceville, tract 901
        "all_tracts": ["42003060300", "42003090100", "42003090200", "42003101100"],
        # Lower (603), Central (901, 902), Upper (1011)
        "display_order": 3,
    },
    "42003981200": {
        "name": "North Shore",
        "canonical": True,
        "all_tracts": ["42003981200"],  # tract 9812
        "display_order": 4,
    },
    "42003050100": {
        "name": "Hill District",
        "canonical": True,  # Middle Hill, tract 501
        "all_tracts": ["42003030500", "42003050100", "42003050600",
                       "42003050900", "42003051000", "42003051100"],
        # Crawford-Roberts (305), Middle Hill (501), Upper Hill (506),
        # Bedford Dwellings (509), Terrace Village (510, 511)
        "display_order": 5,
    },
    "42003562300": {
        "name": "Hazelwood",
        "canonical": True,
        "all_tracts": ["42003562300", "42003562900"],  # tracts 5623, 5629
        "display_order": 6,
    },
    "42003160900": {
        "name": "Southside",
        "canonical": True,  # South Side Flats, tract 1609
        "all_tracts": ["42003160800", "42003160900", "42003170200", "42003170600"],
        # S Side Slopes (1608, 1706) + S Side Flats (1609, 1702)
        "display_order": 7,
    },
    "42003040500": {
        "name": "Oakland",
        "canonical": True,  # Central Oakland, tract 405
        "all_tracts": ["42003040200", "42003040400", "42003040500",
                       "42003040600", "42003040900"],
        # West (402), North (404), Central (405, 406), South (409)
        "display_order": 8,
    },
    "42003070300": {
        "name": "Shadyside",
        "canonical": True,  # tract 703
        "all_tracts": ["42003070300", "42003070500", "42003070600",
                       "42003070800", "42003070900"],
        "display_order": 9,
    },
}

# What the rest of the codebase used to call PITTSBURGH_TRACTS
PITTSBURGH_TRACTS: List[str] = sorted(
    [tid for tid, d in TRACT_REGISTRY.items() if d["canonical"]],
    key=lambda tid: TRACT_REGISTRY[tid]["display_order"],
)

def tract_name(tract_id: str) -> str:
    return TRACT_REGISTRY.get(tract_id, {}).get("name", tract_id)

def all_member_tracts(canonical_id: str) -> List[str]:
    """All real census tracts that make up this neighborhood unit."""
    return TRACT_REGISTRY.get(canonical_id, {}).get("all_tracts", [canonical_id])
