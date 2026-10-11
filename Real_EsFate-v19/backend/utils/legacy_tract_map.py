"""Maps legacy mock-dataset tract IDs (42003030xxx) to canonical registry IDs.

The early Yelp/Jobs mock datasets used placeholder IDs that never matched
real FIPS codes, so Tier 3 silently found no data for real neighborhoods.
Mapping is by neighborhood name (stated in the original mock data comments).
Remove this file once those services pull real data keyed by canonical IDs.
"""

LEGACY_TO_CANONICAL = {
    "42003030100": "42003020100",  # Downtown
    "42003030200": "42003020300",  # Strip District
    "42003030300": "42003090100",  # Lawrenceville
    "42003030400": "42003981200",  # North Shore
    "42003030500": "42003050100",  # Hill District
    "42003030600": "42003562300",  # Hazelwood
    "42003030700": "42003160900",  # Southside
    "42003030800": "42003040500",  # Oakland
    "42003030900": "42003070300",  # Shadyside
}
CANONICAL_TO_LEGACY = {v: k for k, v in LEGACY_TO_CANONICAL.items()}


def to_legacy_id(tract_id: str) -> str:
    """Return the legacy mock-data key for a canonical ID (or the ID unchanged)."""
    return CANONICAL_TO_LEGACY.get(tract_id, tract_id)
