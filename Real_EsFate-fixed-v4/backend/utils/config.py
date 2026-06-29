"""System configuration and constants.

Centralizes all tunable parameters.
"""

# Signal weights (must sum to 1.0)
SIGNAL_WEIGHTS = {
    # Tier 1 research signals (60% weight)
    "rent_appreciation": 0.20,
    "permit_surge": 0.18,
    "eviction_uptick": 0.22,
    
    # Tier 2 acceleration signals (30% weight)
    "yelp_business_churn": 0.12,
    "job_posting_shift": 0.10,
    "school_enrollment_decline": 0.08,
    
    # Tier 3 speculative signals (10% weight)
    "nextdoor_sentiment": 0.05,
    "liquor_licenses": 0.05,
}

# Confidence thresholds
MIN_CONFIDENCE_FOR_OUTPUT = 0.40
HIGH_CONFIDENCE_THRESHOLD = 0.75

# Cache settings
CACHE_TTL_SECONDS = {
    "tract_score": 3600,  # 1 hour
    "all_tracts": 1800,   # 30 minutes
    "methodology": 86400, # 24 hours
}

# Data freshness thresholds
DATA_FRESHNESS_DAYS = {
    "permits": 30,
    "eviction_data": 30,
    "rent_data": 90,
    "business_churn": 90,
    "job_postings": 7,
}

# Pittsburgh census tracts
PITTSBURGH_TRACTS = [
    "42003030100", "42003030200", "42003030300", "42003030400", "42003030500",
    "42003030600", "42003030700", "42003030800", "42003030900",
]

# Signal categories
TIER_1_SIGNALS = ["rent_appreciation", "permit_surge", "eviction_uptick"]
TIER_2_SIGNALS = ["yelp_business_churn", "job_posting_shift", "school_enrollment_decline"]
TIER_3_SIGNALS = ["nextdoor_sentiment", "liquor_licenses"]

# Output modes
STAKEHOLDER_VIEWS = {
    "researcher": "Full transparency, methodology-focused",
    "resident": "Actionable, accessible, resource-focused",
    "investor": "Opportunity-focused with impact disclosure",
    "city": "Policy intervention windows",
}

# System mode
MOCK_DATA_MODE = True  # Set False when real APIs are connected
DEBUG_MODE = False
LOG_LEVEL = "INFO"
