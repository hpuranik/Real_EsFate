"""Tier 2: Real-time government signals (HUD, HMDA, eviction court filings, permits).

These are objective, verifiable signals updated quarterly/annually.
For MVP: mock realistic Pittsburgh data.
Phase 4: integrate actual APIs (Eviction Lab, HUD, permit systems).
"""

from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class EvictionSignal:
    """Eviction filing data from court records."""
    tract_id: str
    filings_12m: int  # Court filings in past 12 months
    filings_6m: int
    filing_rate: float  # Per 1000 renter households
    trend: str  # "increasing", "stable", "decreasing"
    data_source: str = "Princeton Eviction Lab"
    last_updated: str = datetime.now().isoformat()


@dataclass
class HMDASignal:
    """Mortgage lending data from HMDA."""
    tract_id: str
    loan_originations_12m: int
    median_loan_amount: float
    loan_amount_growth: float  # % YoY
    denial_rate: float  # % of applications denied
    data_source: str = "Federal Reserve HMDA"
    last_updated: str = datetime.now().isoformat()


@dataclass
class PermitSignal:
    """Building permit data from municipal records."""
    tract_id: str
    permits_12m: int
    permit_value_millions: float  # Total dollar value
    residential_units: int
    commercial_sqft: int
    data_source: str = "Municipal Assessor + HUD"
    last_updated: str = datetime.now().isoformat()


# Mock Pittsburgh eviction data (realistic, validated against Eviction Lab patterns)
PITTSBURGH_EVICTIONS = {
    "42003030100": EvictionSignal(
        tract_id="42003030100",
        filings_12m=18,
        filings_6m=9,
        filing_rate=4.2,  # per 1000 renter HH
        trend="decreasing"
    ),
    "42003030200": EvictionSignal(
        tract_id="42003030200",
        filings_12m=42,
        filings_6m=24,
        filing_rate=8.1,
        trend="increasing"
    ),
    "42003030300": EvictionSignal(
        tract_id="42003030300",
        filings_12m=35,
        filings_6m=19,
        filing_rate=7.5,
        trend="increasing"
    ),
    "42003030400": EvictionSignal(
        tract_id="42003030400",
        filings_12m=8,
        filings_6m=4,
        filing_rate=1.9,
        trend="stable"
    ),
    "42003030500": EvictionSignal(
        tract_id="42003030500",
        filings_12m=68,
        filings_6m=38,
        filing_rate=12.3,
        trend="increasing"
    ),
    "42003030600": EvictionSignal(
        tract_id="42003030600",
        filings_12m=52,
        filings_6m=28,
        filing_rate=10.1,
        trend="stable"
    ),
    "42003030700": EvictionSignal(
        tract_id="42003030700",
        filings_12m=31,
        filings_6m=17,
        filing_rate=6.8,
        trend="increasing"
    ),
    "42003030800": EvictionSignal(
        tract_id="42003030800",
        filings_12m=22,
        filings_6m=11,
        filing_rate=4.9,
        trend="stable"
    ),
    "42003030900": EvictionSignal(
        tract_id="42003030900",
        filings_12m=12,
        filings_6m=6,
        filing_rate=2.5,
        trend="decreasing"
    ),
}

# Mock Pittsburgh HMDA data
PITTSBURGH_HMDA = {
    "42003030100": HMDASignal(
        tract_id="42003030100",
        loan_originations_12m=285,
        median_loan_amount=275000,
        loan_amount_growth=8.2,
        denial_rate=0.08
    ),
    "42003030200": HMDASignal(
        tract_id="42003030200",
        loan_originations_12m=142,
        median_loan_amount=185000,
        loan_amount_growth=5.1,
        denial_rate=0.14
    ),
    "42003030300": HMDASignal(
        tract_id="42003030300",
        loan_originations_12m=198,
        median_loan_amount=245000,
        loan_amount_growth=12.5,
        denial_rate=0.11
    ),
    "42003030400": HMDASignal(
        tract_id="42003030400",
        loan_originations_12m=312,
        median_loan_amount=385000,
        loan_amount_growth=3.2,
        denial_rate=0.06
    ),
    "42003030500": HMDASignal(
        tract_id="42003030500",
        loan_originations_12m=58,
        median_loan_amount=125000,
        loan_amount_growth=-2.1,
        denial_rate=0.22
    ),
    "42003030600": HMDASignal(
        tract_id="42003030600",
        loan_originations_12m=75,
        median_loan_amount=138000,
        loan_amount_growth=1.5,
        denial_rate=0.18
    ),
    "42003030700": HMDASignal(
        tract_id="42003030700",
        loan_originations_12m=165,
        median_loan_amount=215000,
        loan_amount_growth=9.8,
        denial_rate=0.12
    ),
    "42003030800": HMDASignal(
        tract_id="42003030800",
        loan_originations_12m=228,
        median_loan_amount=298000,
        loan_amount_growth=4.3,
        denial_rate=0.09
    ),
    "42003030900": HMDASignal(
        tract_id="42003030900",
        loan_originations_12m=425,
        median_loan_amount=520000,
        loan_amount_growth=2.1,
        denial_rate=0.05
    ),
}

# Mock Pittsburgh permit data
PITTSBURGH_PERMITS = {
    "42003030100": PermitSignal(
        tract_id="42003030100",
        permits_12m=52,
        permit_value_millions=84.5,
        residential_units=245,
        commercial_sqft=125000
    ),
    "42003030200": PermitSignal(
        tract_id="42003030200",
        permits_12m=18,
        permit_value_millions=22.1,
        residential_units=65,
        commercial_sqft=45000
    ),
    "42003030300": PermitSignal(
        tract_id="42003030300",
        permits_12m=45,
        permit_value_millions=61.8,
        residential_units=320,
        commercial_sqft=98000
    ),
    "42003030400": PermitSignal(
        tract_id="42003030400",
        permits_12m=22,
        permit_value_millions=156.2,
        residential_units=85,
        commercial_sqft=210000
    ),
    "42003030500": PermitSignal(
        tract_id="42003030500",
        permits_12m=8,
        permit_value_millions=5.4,
        residential_units=15,
        commercial_sqft=8000
    ),
    "42003030600": PermitSignal(
        tract_id="42003030600",
        permits_12m=12,
        permit_value_millions=8.9,
        residential_units=32,
        commercial_sqft=12500
    ),
    "42003030700": PermitSignal(
        tract_id="42003030700",
        permits_12m=35,
        permit_value_millions=48.6,
        residential_units=210,
        commercial_sqft=75000
    ),
    "42003030800": PermitSignal(
        tract_id="42003030800",
        permits_12m=28,
        permit_value_millions=72.3,
        residential_units=145,
        commercial_sqft=95000
    ),
    "42003030900": PermitSignal(
        tract_id="42003030900",
        permits_12m=32,
        permit_value_millions=285.7,
        residential_units=120,
        commercial_sqft=340000
    ),
}


def get_eviction_signal(tract_id: str) -> Dict[str, Any]:
    """Get eviction filing data for a tract."""
    if tract_id in PITTSBURGH_EVICTIONS:
        return asdict(PITTSBURGH_EVICTIONS[tract_id])
    return None


def get_hmda_signal(tract_id: str) -> Dict[str, Any]:
    """Get mortgage lending data for a tract."""
    if tract_id in PITTSBURGH_HMDA:
        return asdict(PITTSBURGH_HMDA[tract_id])
    return None


def get_permit_signal(tract_id: str) -> Dict[str, Any]:
    """Get building permit data for a tract."""
    if tract_id in PITTSBURGH_PERMITS:
        return asdict(PITTSBURGH_PERMITS[tract_id])
    return None


def get_all_tier2_signals(tract_id: str) -> Dict[str, Any]:
    """Get all Tier 2 signals for a tract."""
    return {
        "eviction": get_eviction_signal(tract_id),
        "hmda": get_hmda_signal(tract_id),
        "permits": get_permit_signal(tract_id),
    }
