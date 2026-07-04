"""Income-based gentrification signals: sweet-spot and trajectory.

WHY THIS EXISTS: the 2010 backtest (models/backtest.py) found that a naive
"lower income = higher displacement risk" formula misses the actual
gentrification pattern documented in the literature. Zuk et al. 2018 and
Hwang & Lin 2016 both find displacement pressure peaks in neighborhoods at
roughly 75-120% of area median income -- accessible enough for capital to
move in, not so poor that investors ignore the area, and not already
priced out of reach. This module implements that inverted-U relationship,
plus an income-trajectory signal (rising income = early gentrification
marker) where we have real two-point historical data to compute it.

CITYWIDE REFERENCE: Pittsburgh median household income $65,742 (2024 est.,
ACS-based). Source: pennsylvania-demographics.com, citing Census ACS.
"""

from typing import Optional

PITTSBURGH_CITYWIDE_MEDIAN_INCOME_2024 = 65742

# Real verified historical income trajectories, used only for the 2 tracts
# we have actual two-point historical data for (see models/backtest.py for
# full citations). NOT extended to other tracts with invented numbers --
# trajectory signal is omitted (returns None) for any tract not in this dict.
_VERIFIED_TRAJECTORIES = {
    "42003090100": {"income_2000": 27031, "income_2010": 39635},  # Lawrenceville
    "42003070300": {"income_2000": 46000, "income_2010": 51323},  # Shadyside (2000 est.)
}


def income_sweet_spot_signal(tract_income: float, citywide_income: float = PITTSBURGH_CITYWIDE_MEDIAN_INCOME_2024) -> float:
    """Inverted-U: peak displacement risk at 75-120% of citywide median income.
    Returns 0-100, higher = more displacement pressure from this signal."""
    if citywide_income <= 0:
        return 50.0  # neutral fallback, shouldn't happen with real data
    ratio = tract_income / citywide_income
    if ratio < 0.50:
        return 30.0   # too poor, capital largely avoids (lower gentrification risk)
    elif ratio < 0.75:
        return 55.0   # approaching the sweet spot
    elif ratio <= 1.20:
        return 85.0   # SWEET SPOT -- prime gentrification target (Zuk et al. 2018)
    elif ratio <= 1.60:
        return 40.0   # above median, displacement pressure declining
    else:
        return 10.0   # already affluent, stable


def income_trajectory_signal(tract_id: str) -> Optional[float]:
    """Rising income trajectory = early gentrification marker (Hwang & Lin 2016).
    Returns None (not 0, not a guess) when we don't have real two-point
    historical data for this tract -- an honest gap, not a fabricated value."""
    hist = _VERIFIED_TRAJECTORIES.get(tract_id)
    if hist is None:
        return None
    pct_change = (hist["income_2010"] - hist["income_2000"]) / hist["income_2000"] * 100
    if pct_change > 40: return 90.0
    if pct_change > 20: return 70.0
    if pct_change > 10: return 50.0
    if pct_change > 0:  return 30.0
    return 10.0


def has_verified_trajectory(tract_id: str) -> bool:
    return tract_id in _VERIFIED_TRAJECTORIES
