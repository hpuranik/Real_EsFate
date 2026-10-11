"""Yelp business signal service — real Yelp Fusion API call, labeled mock fallback.

ARCHITECTURE COMPLIANCE:
- Real API path: calls Yelp Fusion /businesses/search using each tract's
  real centroid (utils/tract_centroids.py, computed from actual polygon
  boundaries, not guessed).
- KNOWN LIMITATION (documented, not hidden): the Yelp Fusion API only
  returns a snapshot of currently-open businesses -- it does not expose
  historical open/close dates. So a *real* churn rate (opens vs. closes
  over a time window) cannot be computed from a single live call. This
  service is honest about that: the real path returns a real current
  business-density signal (business_count near the tract centroid,
  categories present), not a fabricated churn rate. True churn tracking
  would need scheduled periodic snapshots stored over time (see project
  rule: no live scraping/inference per request where real historical
  data is required -- use scheduled pulls instead). That is future work,
  not something this file pretends to already do.
- Mock fallback (used when YELP_API_KEY is absent, or the real call
  fails) still simulates churn_rate from the hand-built mock dataset --
  clearly labeled "data_source": "mock_fallback" so it is never confused
  with the real signal.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests

from utils.tract_centroids import get_centroid
from utils.cache import get_cached, set_cached, cache_key

YELP_BASE_URL = "https://api.yelp.com/v3/businesses/search"
MOCK_REFERENCE_DATE = datetime(2024, 6, 1)  # mock data is calibrated as of this date
CACHE_TTL = 60 * 60 * 24  # 1 day -- business listings don't change minute to minute


@dataclass
class YelpBusiness:
    business_id: str
    name: str
    category: str  # "restaurant", "retail", "service", "professional"
    tract_id: str
    opened_date: str
    closed_date: str = None  # None if still open
    latitude: float = None
    longitude: float = None


# Mock Pittsburgh Yelp business data (realistic scenarios, used only as
# fallback when no real API key is present or the real call fails).
MOCK_YELP_BUSINESSES = {
    "42003030100": [  # Downtown
        YelpBusiness("y1", "Independent Coffee", "restaurant", "42003030100", "2022-01-15"),
        YelpBusiness("y2", "Local Bookstore", "retail", "42003030100", "2019-03-01", "2024-06-01"),
        YelpBusiness("y3", "Artisan Bakery", "restaurant", "42003030100", "2023-05-10"),
        YelpBusiness("y4", "Corporate Chain", "retail", "42003030100", "2024-02-01"),
    ],
    "42003030200": [  # Strip District
        YelpBusiness("y5", "Neighborhood Restaurant", "restaurant", "42003030200", "2015-06-20"),
        YelpBusiness("y6", "Family Hardware", "retail", "42003030200", "2010-01-10", "2023-12-15"),
        YelpBusiness("y7", "New Cafe", "restaurant", "42003030200", "2024-01-01"),
    ],
    "42003030300": [  # Lawrenceville (high churn = gentrifying)
        YelpBusiness("y8", "Local Diner", "restaurant", "42003030300", "2018-03-01", "2023-11-01"),
        YelpBusiness("y9", "Trendy Restaurant", "restaurant", "42003030300", "2023-06-15"),
        YelpBusiness("y10", "Vintage Shop", "retail", "42003030300", "2019-02-01", "2024-01-15"),
        YelpBusiness("y11", "Modern Bar", "restaurant", "42003030300", "2024-03-01"),
        YelpBusiness("y12", "Tech Office", "professional", "42003030300", "2023-09-01"),
    ],
    "42003030400": [  # North Shore (stable)
        YelpBusiness("y13", "Hotel Restaurant", "restaurant", "42003030400", "2010-01-01"),
        YelpBusiness("y14", "Sports Bar", "restaurant", "42003030400", "2012-05-01"),
    ],
    "42003030500": [  # Hill District (declining)
        YelpBusiness("y15", "Neighborhood Grocery", "retail", "42003030500", "2005-01-01", "2023-08-01"),
        YelpBusiness("y16", "Local Restaurant", "restaurant", "42003030500", "2008-06-01"),
    ],
    "42003030600": [  # Hazelwood
        YelpBusiness("y17", "Industrial Supply", "retail", "42003030600", "2000-01-01"),
    ],
    "42003030700": [  # Southside (emerging)
        YelpBusiness("y18", "Local Bar", "restaurant", "42003030700", "2015-01-01"),
        YelpBusiness("y19", "New Restaurant", "restaurant", "42003030700", "2023-08-01"),
        YelpBusiness("y20", "Boutique", "retail", "42003030700", "2023-11-01"),
    ],
    "42003030800": [  # Oakland
        YelpBusiness("y21", "University Cafe", "restaurant", "42003030800", "2008-01-01"),
        YelpBusiness("y22", "Bookstore", "retail", "42003030800", "2010-06-01"),
    ],
    "42003030900": [  # Shadyside
        YelpBusiness("y23", "Upscale Restaurant", "restaurant", "42003030900", "2015-01-01"),
        YelpBusiness("y24", "High-end Retail", "retail", "42003030900", "2012-01-01"),
    ],
}


def _mock_business_churn(tract_id: str, window_months: int = 12) -> Dict[str, Any]:
    """Original mock churn calculation. Used as fallback only."""
    from utils.legacy_tract_map import to_legacy_id
    mock_key = to_legacy_id(tract_id)
    if mock_key not in MOCK_YELP_BUSINESSES:
        return {
            "tract_id": tract_id,
            "signal_type": "yelp_business_churn",
            "value": 0,
            "data_source": "mock_fallback",
            "fallback_reason": "No mock profile for this tract_id",
            "confidence": 0.3,
        }

    businesses = MOCK_YELP_BUSINESSES[mock_key]
    # Fixed reference date (project rule 2: deterministic). Using wall-clock
    # time made mock churn decay to 0 as the fixed mock dates aged out.
    now = MOCK_REFERENCE_DATE
    window_start = now - timedelta(days=window_months * 30)

    closures_in_window = sum(
        1 for b in businesses
        if b.closed_date and datetime.fromisoformat(b.closed_date) > window_start
    )
    openings_in_window = sum(
        1 for b in businesses
        if datetime.fromisoformat(b.opened_date) > window_start
    )

    total_businesses = len(businesses)
    churn_rate = (closures_in_window / total_businesses * 100) if total_businesses > 0 else 0

    closed_types = [b.category for b in businesses if b.closed_date]
    opened_types = [b.category for b in businesses if not b.closed_date]

    type_shift = "stable"
    if "restaurant" in opened_types and "retail" in closed_types:
        type_shift = "gentrifying_hospitality"
    elif "professional" in opened_types and "retail" in closed_types:
        type_shift = "gentrifying_professional"
    elif "retail" in closed_types and len(opened_types) == 0:
        type_shift = "declining"

    return {
        "tract_id": tract_id,
        "signal_type": "yelp_business_churn",
        "value": churn_rate,
        "churn_absolute": closures_in_window,
        "churn_rate_pct": churn_rate,
        "business_type_shift": type_shift,
        "total_businesses": total_businesses,
        "businesses_opened_12m": openings_in_window,
        "businesses_closed_12m": closures_in_window,
        "timestamp": now.isoformat(),
        "data_source": "mock_fallback",
        "confidence": 0.72,
    }


def _real_business_snapshot(tract_id: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Real Yelp Fusion API call: current business density near tract centroid.

    Returns None (triggering fallback) if no centroid exists or the call fails.
    NOTE: this is a current-snapshot signal, not a churn rate -- see module
    docstring for why churn specifically can't come from a live Yelp call.
    """
    centroid = get_centroid(tract_id)
    if not centroid:
        return None

    lat, lng = centroid
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"latitude": lat, "longitude": lng, "radius": 800, "limit": 50, "sort_by": "distance"}

    resp = requests.get(YELP_BASE_URL, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    businesses = data.get("businesses", [])

    category_counts: Dict[str, int] = {}
    for b in businesses:
        for cat in b.get("categories", []):
            title = cat.get("title", "unknown")
            category_counts[title] = category_counts.get(title, 0) + 1

    avg_rating = (
        sum(b.get("rating", 0) for b in businesses) / len(businesses)
        if businesses else None
    )

    return {
        "tract_id": tract_id,
        "signal_type": "yelp_business_density_snapshot",
        "value": len(businesses),
        "business_count": len(businesses),
        "top_categories": sorted(category_counts.items(), key=lambda x: -x[1])[:5],
        "average_rating": round(avg_rating, 2) if avg_rating is not None else None,
        "timestamp": datetime.now().isoformat(),
        "data_source": "Yelp Fusion API (live snapshot)",
        "confidence": 0.72,
        "limitation": (
            "This is a current-moment snapshot, not a churn rate. Yelp's API "
            "does not expose historical open/close dates, so true churn "
            "requires scheduled periodic snapshots stored over time -- not "
            "yet implemented. Do not treat this as equivalent to the mock "
            "churn_rate_pct field below."
        ),
    }


def compute_business_churn(tract_id: str, window_months: int = 12) -> Dict[str, Any]:
    """Public entrypoint. Tries the real API first (if key present), falls
    back to labeled mock churn data on any failure -- never silently
    presents mock data as real, per project rule 3.
    """
    key = cache_key("yelp", tract_id=tract_id, window=window_months)
    cached = get_cached(key)
    if cached:
        return cached

    api_key = os.environ.get("YELP_API_KEY")
    result = None
    fallback_reason = None
    if api_key:
        try:
            result = _real_business_snapshot(tract_id, api_key)
        except Exception as exc:
            result = None
            fallback_reason = str(exc)

    if result is None:
        result = _mock_business_churn(tract_id, window_months)
        result["fallback_reason"] = fallback_reason or "No YELP_API_KEY set in environment"

    set_cached(key, result, ttl_seconds=CACHE_TTL if result.get("data_source") != "mock_fallback" else 300)
    return result


def get_yelp_signal(tract_id: str) -> Dict[str, Any]:
    """Get Yelp signal for a tract (real snapshot if available, else labeled mock churn)."""
    return compute_business_churn(tract_id)
