"""Yelp business churn service.

Ingests business openings/closures.
Classifies businesses by type.
Maps to census tracts.
Emits canonical signals.

Phase 4: Mock data
Phase 5+: Real Yelp API integration
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timedelta


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


# Mock Pittsburgh Yelp business data (realistic scenarios)
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


def compute_business_churn(tract_id: str, window_months: int = 12) -> Dict[str, Any]:
    """Compute business churn rate for a tract.
    
    Churn = closed businesses / total businesses in window
    
    Returns canonical signal.
    """
    
    if tract_id not in MOCK_YELP_BUSINESSES:
        return None
    
    businesses = MOCK_YELP_BUSINESSES[tract_id]
    now = datetime.now()
    window_start = now - timedelta(days=window_months * 30)
    
    # Count closures in window
    closures_in_window = sum(
        1 for b in businesses
        if b.closed_date
        and datetime.fromisoformat(b.closed_date) > window_start
    )
    
    # Count openings in window
    openings_in_window = sum(
        1 for b in businesses
        if datetime.fromisoformat(b.opened_date) > window_start
    )
    
    total_businesses = len(businesses)
    churn_rate = (closures_in_window / total_businesses * 100) if total_businesses > 0 else 0
    
    # Classify business type shift
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
        "source": "Yelp (mock)",
        "confidence": 0.72,
    }


def get_yelp_signal(tract_id: str) -> Dict[str, Any]:
    """Get Yelp churn signal for a tract."""
    return compute_business_churn(tract_id)
