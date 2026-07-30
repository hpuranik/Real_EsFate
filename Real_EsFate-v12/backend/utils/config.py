"""Platform configuration.

TRACT IDs: all tract_ids now use real 11-digit Census FIPS codes.
The original codebase had invented placeholder IDs (42003030100 etc.)
that didn't correspond to any real Pittsburgh census tracts.
Fixed via utils/tract_registry.py -- see there for provenance.
"""
from utils.tract_registry import PITTSBURGH_TRACTS, tract_name

# Re-export so existing imports of PITTSBURGH_TRACTS from config still work
__all__ = ["PITTSBURGH_TRACTS", "SIGNAL_WEIGHTS", "STAKEHOLDER_VIEWS"]

SIGNAL_WEIGHTS = {
    "rent_appreciation":    0.20,
    "permit_surge":         0.18,
    "eviction_uptick":      0.22,
    "home_price_growth":    0.20,
    "mortgage_lending":     0.10,
    "yelp_business_churn":  0.05,
    "job_posting_shift":    0.05,
}

STAKEHOLDER_VIEWS = {
    "researcher": "Academic/policy view: raw signals, citations, confidence intervals",
    "resident":   "Tenant view: plain-language risk, local resources",
    "investor":   "Capital view: opportunity score, ROI framing, risk disclosure",
    "city":       "Planner view: policy window, intervention tools",
}

# Runtime flags kept for backward compat
CACHE_TTL_SECONDS = {
    "tract_score": 300,
    "all_tracts": 60,
    "signals": 300,
    "methodology": 3600,
}
MOCK_DATA_MODE = True
DEBUG_MODE = False
