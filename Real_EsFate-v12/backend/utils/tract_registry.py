"""Single source of truth for tract definitions.

VERIFICATION SOURCE:
All 2020 tract numbers verified against:
University of Pittsburgh Library census tract guide
https://pitt.libguides.com/pghcensus/pghcensustracts
(Christopher Lemery, Government Information Librarian, last updated Oct 14 2025)

FORMAT: 11-digit FIPS = state(42) + county(003) + tract(6 digits right-padded)

SIGNAL CALIBRATION BASIS:
- Chapple, K., & Zuk, M. (2016). Forewarned: The Use of Neighborhood Early 
  Warning Systems for Gentrification and Displacement. Cityscape, 18(3), 109-130.
- UCSUR (2020). Pittsburgh Neighborhood Profiles. University Center for Social 
  and Urban Research, University of Pittsburgh.
- Swanstrom, T. et al. (2021). Inclusive Growth in Pittsburgh: Opportunities 
  and Risks. Federal Reserve Bank of Philadelphia.
"""

from typing import Dict, List

TRACT_REGISTRY: Dict[str, dict] = {
    # ORIGINAL 9
    "42003020100": {"name": "Downtown",           "canonical": True, "display_order": 1,
                    "all_tracts": ["42003020100"]},
    "42003020300": {"name": "Strip District",     "canonical": True, "display_order": 2,
                    "all_tracts": ["42003020300"]},
    "42003090100": {"name": "Lawrenceville",      "canonical": True, "display_order": 3,
                    "all_tracts": ["42003060300","42003090100","42003090200","42003101100"]},
    "42003981200": {"name": "North Shore",        "canonical": True, "display_order": 4,
                    "all_tracts": ["42003981200"]},
    "42003050100": {"name": "Hill District",      "canonical": True, "display_order": 5,
                    "all_tracts": ["42003030500","42003050100","42003050600","42003050900","42003051000","42003051100"]},
    "42003562300": {"name": "Hazelwood",          "canonical": True, "display_order": 6,
                    "all_tracts": ["42003562300","42003562900"]},
    "42003160900": {"name": "Southside",          "canonical": True, "display_order": 7,
                    "all_tracts": ["42003160800","42003160900","42003170200","42003170600"]},
    "42003040500": {"name": "Oakland",            "canonical": True, "display_order": 8,
                    "all_tracts": ["42003040200","42003040400","42003040500","42003040600","42003040900"]},
    "42003070300": {"name": "Shadyside",          "canonical": True, "display_order": 9,
                    "all_tracts": ["42003070300","42003070500","42003070600","42003070800","42003070900"]},
    # NEW 21
    "42003111300": {"name": "East Liberty",       "canonical": True, "display_order": 10,
                    "all_tracts": ["42003111300","42003111500"]},
    "42003080400": {"name": "Bloomfield",         "canonical": True, "display_order": 11,
                    "all_tracts": ["42003080200","42003080400","42003080600","42003080900","42003090300"]},
    "42003101900": {"name": "Garfield",           "canonical": True, "display_order": 12,
                    "all_tracts": ["42003101900","42003111400"]},
    "42003060500": {"name": "Polish Hill",        "canonical": True, "display_order": 13,
                    "all_tracts": ["42003060500"]},
    "42003140400": {"name": "Point Breeze",       "canonical": True, "display_order": 14,
                    "all_tracts": ["42003140400","42003140500","42003141200","42003981100"]},
    "42003080700": {"name": "Friendship",         "canonical": True, "display_order": 15,
                    "all_tracts": ["42003080700"]},
    "42003140200": {"name": "Squirrel Hill North","canonical": True, "display_order": 16,
                    "all_tracts": ["42003140100","42003140200","42003140300"]},
    "42003140800": {"name": "Squirrel Hill South","canonical": True, "display_order": 17,
                    "all_tracts": ["42003140800","42003141300","42003141400","42003980300","42003980500"]},
    "42003110200": {"name": "Highland Park",      "canonical": True, "display_order": 18,
                    "all_tracts": ["42003110200","42003110600"]},
    "42003100500": {"name": "Stanton Heights",    "canonical": True, "display_order": 19,
                    "all_tracts": ["42003100500","42003101800"]},
    "42003151600": {"name": "Greenfield",         "canonical": True, "display_order": 20,
                    "all_tracts": ["42003151600","42003151700"]},
    "42003191400": {"name": "Mount Washington",   "canonical": True, "display_order": 21,
                    "all_tracts": ["42003180700","42003190300","42003191400","42003191500"]},
    "42003101400": {"name": "Morningside",        "canonical": True, "display_order": 22,
                    "all_tracts": ["42003101400"]},
    "42003563201": {"name": "East Allegheny",     "canonical": True, "display_order": 23,
                    "all_tracts": ["42003563201","42003563202"]},
    "42003191600": {"name": "Beechview",          "canonical": True, "display_order": 24,
                    "all_tracts": ["42003191600","42003192000"]},
    "42003290200": {"name": "Carrick",            "canonical": True, "display_order": 25,
                    "all_tracts": ["42003290100","42003290200","42003290400"]},
    "42003130800": {"name": "Homewood South",     "canonical": True, "display_order": 26,
                    "all_tracts": ["42003130800"]},
    "42003120900": {"name": "Larimer",            "canonical": True, "display_order": 27,
                    "all_tracts": ["42003120900"]},
    "42003270300": {"name": "Brighton Heights",   "canonical": True, "display_order": 28,
                    "all_tracts": ["42003270100","42003270300","42003270800"]},
    "42003261400": {"name": "Perry South",        "canonical": True, "display_order": 29,
                    "all_tracts": ["42003261400","42003261500"]},
    "42003241300": {"name": "Spring Garden",      "canonical": True, "display_order": 30,
                    "all_tracts": ["42003241300"]},
}

PITTSBURGH_TRACTS: List[str] = sorted(
    [tid for tid, d in TRACT_REGISTRY.items() if d["canonical"]],
    key=lambda tid: TRACT_REGISTRY[tid]["display_order"],
)

def tract_name(tract_id: str) -> str:
    return TRACT_REGISTRY.get(tract_id, {}).get("name", tract_id)

def all_member_tracts(canonical_id: str) -> List[str]:
    return TRACT_REGISTRY.get(canonical_id, {}).get("all_tracts", [canonical_id])
