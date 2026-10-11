"""Tract crosswalk: maps a lat/lon point to the tract_id whose boundary
contains it.

Phase 7a foundation. Any data source that arrives keyed by address or
lat/lon rather than tract_id (building permits, property sales, tax
assessments, etc.) goes through this, NOT a one-off geocoder per source.
Geocoding the address to lat/lon is each source's own job (e.g. via the
Census Geocoder API, or because the source dataset already includes
coordinates -- many city open-data permit datasets do). This module only
solves the "which polygon is this point inside" half of the problem.

Census ACS and HMDA do NOT need this module -- they're already keyed by
tract FIPS, which is exactly our tract_id format (see services/acs_service.py).
"""

import json
import os
from functools import lru_cache
from typing import Optional

from shapely.geometry import shape, Point

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pittsburgh-tracts.json")


@lru_cache(maxsize=1)
def _load_tract_polygons():
    """Load and parse the tract boundaries once, cache for the process lifetime.

    Boundaries are real Pittsburgh neighborhood shapes (sourced from
    OpenStreetMap-derived data, see frontend/data/pittsburgh-tracts.json for
    provenance), not the original placeholder rectangles.
    """
    with open(_DATA_PATH) as f:
        geojson = json.load(f)

    polygons = []
    for feature in geojson["features"]:
        tract_id = feature["properties"]["tract_id"]
        geom = shape(feature["geometry"])
        polygons.append((tract_id, geom))
    return polygons


def tract_for_point(lon: float, lat: float) -> Optional[str]:
    """Return the tract_id whose boundary contains (lon, lat), or None if
    the point doesn't fall inside any of our 9 covered areas.

    Note the argument order: (lon, lat), matching GeoJSON's [x, y] = [lon, lat]
    convention, NOT the (lat, lon) order common in human-facing map UIs.
    """
    point = Point(lon, lat)
    for tract_id, polygon in _load_tract_polygons():
        if polygon.contains(point) or polygon.touches(point):
            return tract_id
    return None


def tract_ids_covered() -> list:
    """All tract_ids this crosswalk can resolve to. Useful for sanity checks
    in callers that don't want to silently drop unmatched records."""
    return [tract_id for tract_id, _ in _load_tract_polygons()]
