"""WPRDC (Western PA Regional Data Center) building permits service.

Feeds Tier 2's building_permits AND Tier 1's permit_surge -- both were
previously static mock dictionaries with no live source at all.

ARCHITECTURE COMPLIANCE:
- Real API: WPRDC's public CKAN datastore_search endpoint, no API key
  required for public datasets. Resource ID below is the current
  "PLI Permits" dataset (data.wprdc.org/dataset/pli-permits), which
  replaced the old monthly-archive summary files in 2019.
- HONESTLY FLAGGED UNCERTAINTY: this file was written without a live
  test call (data.wprdc.org is outside this dev environment's network
  allowlist). The exact column names below (parcel/address/lat-lon
  fields) are inferred from WPRDC's public documentation and sibling
  datasets, not confirmed against a live response. The code defensively
  tries several plausible field-name variants and falls back to the
  labeled mock if none match -- but this MUST be verified against a
  real response before being trusted, the same way the Census 403 needs
  verifying from your Codespaces (network there is not restricted).
- No randomness in the mock fallback; deterministic per tract_id.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import requests

from utils.tract_centroids import get_centroid
from utils.cache import get_cached, set_cached, cache_key

WPRDC_DATASTORE_URL = "https://data.wprdc.org/api/3/action/datastore_search"
PLI_PERMITS_RESOURCE_ID = "f4d1177a-f597-4c32-8cbf-7885f56253f6"
CACHE_TTL = 60 * 60 * 24  # 1 day

# Candidate field names, since the exact schema hasn't been confirmed
# against a live call. First match wins.
_LAT_FIELDS = ["latitude", "lat", "y", "LATITUDE"]
_LON_FIELDS = ["longitude", "lon", "lng", "x", "LONGITUDE"]
_DATE_FIELDS = ["issue_date", "permit_issue_date", "issued_date", "date_issued", "PERMIT_ISSUE_DATE"]

# Deterministic per-tract mock fallback, calibrated roughly in line with
# the existing tier2_government.py building_permits mock values so this
# doesn't introduce a discontinuity while unverified.
_MOCK_PERMIT_COUNTS = {
    "42003090100": 55,  # Lawrenceville
    "42003070300": 8,   # Shadyside
    "42003562300": 97,  # Hazelwood
}
_DEFAULT_MOCK_COUNT = 20


def _extract_coord(record: dict, candidates: List[str]) -> Optional[float]:
    for field in candidates:
        if field in record and record[field] not in (None, ""):
            try:
                return float(record[field])
            except (TypeError, ValueError):
                continue
    return None


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    from math import radians, sin, cos, sqrt, atan2
    R = 6371
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def _mock_permits(tract_id: str) -> Dict[str, Any]:
    count = _MOCK_PERMIT_COUNTS.get(tract_id, _DEFAULT_MOCK_COUNT)
    return {
        "tract_id": tract_id,
        "permit_count_12mo": count,
        "data_source": "mock_fallback",
        "confidence": 0.55,
    }


def get_tract_permits(tract_id: str, radius_km: float = 0.8, window_days: int = 365) -> Dict[str, Any]:
    """Real building permit count near a tract's centroid, WPRDC live data.

    Falls back to a labeled mock on any failure -- missing centroid,
    network error, unrecognized schema, or empty response.
    """
    key = cache_key("wprdc_permits", tract_id=tract_id, radius=radius_km, window=window_days)
    cached = get_cached(key)
    if cached:
        return cached

    centroid = get_centroid(tract_id)
    if not centroid:
        result = _mock_permits(tract_id)
        result["fallback_reason"] = "No centroid available for this tract_id"
        set_cached(key, result, ttl_seconds=300)
        return result

    lat, lon = centroid

    try:
        resp = requests.get(
            WPRDC_DATASTORE_URL,
            params={"resource_id": PLI_PERMITS_RESOURCE_ID, "limit": 5000},
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()
        records = payload.get("result", {}).get("records", [])
        if not records:
            raise ValueError("WPRDC returned zero records -- unexpected for an active dataset")

        cutoff = datetime.now() - timedelta(days=window_days)
        nearby_count = 0
        matched_any_coords = False

        for rec in records:
            r_lat = _extract_coord(rec, _LAT_FIELDS)
            r_lon = _extract_coord(rec, _LON_FIELDS)
            if r_lat is None or r_lon is None:
                continue
            matched_any_coords = True

            # Optional date filtering -- only applied if a recognizable
            # date field exists; otherwise counts all returned records
            # (dataset may already be windowed server-side).
            in_window = True
            for date_field in _DATE_FIELDS:
                if date_field in rec and rec[date_field]:
                    try:
                        rec_date = datetime.fromisoformat(str(rec[date_field])[:10])
                        in_window = rec_date >= cutoff
                    except ValueError:
                        pass
                    break

            if in_window and _haversine_km(lat, lon, r_lat, r_lon) <= radius_km:
                nearby_count += 1

        if not matched_any_coords:
            raise ValueError(
                "No records matched expected lat/lon field names -- schema "
                "assumption in this file is likely wrong and needs updating "
                "against a real WPRDC response."
            )

        result = {
            "tract_id": tract_id,
            "permit_count_12mo": nearby_count,
            "data_source": "WPRDC PLI Permits (live)",
            "confidence": 0.80,
            "radius_km": radius_km,
        }

    except Exception as exc:
        result = _mock_permits(tract_id)
        result["fallback_reason"] = str(exc)

    set_cached(key, result, ttl_seconds=CACHE_TTL if result.get("data_source") != "mock_fallback" else 300)
    return result
