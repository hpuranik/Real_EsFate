"""Tier 3: Local alpha signals (Yelp churn, job posts, Nextdoor, liquor licenses, etc.).

These are overlooked but predictive signals. Currently a schema for Phase 4 integration.
Phase 4: connect to Yelp API, Indeed job postings, liquor license records, etc.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class YelpBusinessChurn:
    """Business churn from Yelp/Google Maps."""
    tract_id: str
    total_businesses: int
    closed_last_12m: int
    churn_rate: float  # % closed
    business_type_shift: str  # e.g., "local_to_chain" or "independent_stable"
    data_source: str = "Yelp + Google Places"
    last_updated: str = datetime.now().isoformat()


@dataclass
class JobPostingSignal:
    """Job posting location shifts."""
    tract_id: str
    job_postings_12m: int
    avg_salary: float
    location_shift: str  # e.g., "tech_moving_in" or "service_stable"
    employer_tier: str  # "startup", "established", "remote"
    data_source: str = "Indeed, LinkedIn, AngelList"
    last_updated: str = datetime.now().isoformat()


@dataclass
class NextdoorSentiment:
    """Nextdoor keyword analysis (community sentiment)."""
    tract_id: str
    monthly_posts: int
    concern_keywords: List[str]  # ["eviction", "rent increase", "construction"]
    positive_keywords: List[str]  # ["community", "improvement", "event"]
    sentiment_trend: str  # "deteriorating", "stable", "improving"
    data_source: str = "Nextdoor API / Manual Monitoring"
    last_updated: str = datetime.now().isoformat()


@dataclass
class LiquorLicenseSignal:
    """Liquor license applications (early gentrification signal)."""
    tract_id: str
    licenses_issued_12m: int
    license_type_shift: str  # "bar_nightlife" vs "liquor_store"
    avg_location_rent: float  # Location asking rent (if available)
    data_source: str = "Municipal Licensing Records"
    last_updated: str = datetime.now().isoformat()


@dataclass
class SchoolEnrollmentSignal:
    """Public school enrollment shifts."""
    tract_id: str
    public_enrollment_12m: int
    public_enrollment_change_pct: float  # % YoY
    charter_enrollment_12m: int
    charter_enrollment_change_pct: float
    data_source: str = "School District Records"
    last_updated: str = datetime.now().isoformat()


@dataclass
class RetailFormatSignal:
    """Retail format changes (e.g., dollar store → Whole Foods)."""
    tract_id: str
    grocery_format_before: str  # "corner_store", "dollar_store", "whole_foods"
    grocery_format_after: str
    format_shift_indicator: str  # "gentrifying", "stable", "declining"
    data_source: str = "Yelp, Google Maps, Municipal Records"
    last_updated: str = datetime.now().isoformat()


# Schema templates for Phase 4 data integration
TIER3_SIGNAL_SCHEMA = {
    "yelp_churn": {
        "type": "YelpBusinessChurn",
        "description": "Business closure rate (Yelp/Google)",
        "predictive_value": "High (late-stage gentrification indicator)",
        "phase": "4",
    },
    "job_postings": {
        "type": "JobPostingSignal",
        "description": "Job posting volume + salary + type",
        "predictive_value": "High (tech invasion signal)",
        "phase": "4",
    },
    "nextdoor_sentiment": {
        "type": "NextdoorSentiment",
        "description": "Community posts + keyword analysis",
        "predictive_value": "Medium (perception ≠ reality)",
        "phase": "4",
    },
    "liquor_licenses": {
        "type": "LiquorLicenseSignal",
        "description": "License applications + type",
        "predictive_value": "Medium-High (early gentrification)",
        "phase": "4",
    },
    "school_enrollment": {
        "type": "SchoolEnrollmentSignal",
        "description": "Public vs. charter school trends",
        "predictive_value": "High (demographic displacement)",
        "phase": "4",
    },
    "retail_format": {
        "type": "RetailFormatSignal",
        "description": "Grocery/retail format changes",
        "predictive_value": "Medium (amenity gentrification)",
        "phase": "4",
    },
}


def get_tier3_schema() -> Dict[str, Any]:
    """Return Tier 3 schema (Phase 4 integration)."""
    return TIER3_SIGNAL_SCHEMA


def placeholder_tier3_signal(tract_id: str, signal_type: str) -> Dict[str, Any]:
    """Placeholder for Tier 3 signals (to be populated Phase 4)."""
    return {
        "tract_id": tract_id,
        "signal_type": signal_type,
        "status": "PHASE 4 - NOT YET INTEGRATED",
        "data_available": False,
        "expected_phase": "Phase 4",
    }
