"""Leadership personality model: speculative layer with archetype mapping.

WARNING: This layer is EXPLICITLY SPECULATIVE and must be labeled as such in all outputs.

Model:
1. Collect public statements, interviews, voting records, board decisions
2. Map to decision-making archetypes (historical precedent)
3. Score "stated intent vs. revealed preference" gap
4. Generate probabilistic forecast based on comparable historical cases

All outputs: CLEARLY LABELED as "SPECULATIVE" with confidence intervals.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class LeadershipArchetype(Enum):
    """Decision-making archetypes from urban governance literature."""
    GROWTH_AT_ALL_COSTS = "growth-at-all-costs"
    COMMUNITY_PRESERVATION = "community-preservation"
    OPPORTUNIST = "opportunist"
    MARKET_NEUTRAL = "market-neutral"
    EQUITY_FOCUSED = "equity-focused"
    ABSENT = "absent"


@dataclass
class LeadershipProfile:
    """A city leader's decision-making profile."""
    name: str
    role: str  # "Mayor", "Council Member", "Developer CEO", "Landlord Assoc"
    archetype: LeadershipArchetype
    stated_intent: str  # What they SAY
    revealed_preference: str  # What they actually DO
    intent_gap_score: float  # 0-1 (0 = aligned, 1 = contradictory)
    historical_precedent: str  # What did similar people do elsewhere?
    confidence: float  # 0-1 (how certain is this profile?)


# Example leadership profiles for Pittsburgh (SPECULATIVE ONLY)
EXAMPLE_PROFILES = {
    "mayor_example": LeadershipProfile(
        name="[Example Mayor]",
        role="Mayor",
        archetype=LeadershipArchetype.GROWTH_AT_ALL_COSTS,
        stated_intent="'We prioritize affordable housing and community engagement'",
        revealed_preference="Approved major rezoning without community input; 70% new units market-rate",
        intent_gap_score=0.8,
        historical_precedent="Similar profiles in Denver (2010-2015) led to 2.5x rent growth + 35% displacement",
        confidence=0.65,
    ),
    "developer_example": LeadershipProfile(
        name="[Example Developer]",
        role="Major Real Estate Developer",
        archetype=LeadershipArchetype.OPPORTUNIST,
        stated_intent="'Mixed-income housing and local hiring'",
        revealed_preference="Developed primarily market-rate; minimal local hiring",
        intent_gap_score=0.7,
        historical_precedent="Similar developers in Austin (2012-2018) focused on high-margin segments",
        confidence=0.58,
    ),
    "council_example": LeadershipProfile(
        name="[Example Council Member]",
        role="City Council Member (District 3)",
        archetype=LeadershipArchetype.COMMUNITY_PRESERVATION,
        stated_intent="'We must protect existing residents and businesses'",
        revealed_preference="Voted against zoning changes; advocated for rent control study",
        intent_gap_score=0.2,
        historical_precedent="Similar profiles in San Francisco (2010-2020) successfully slowed displacement",
        confidence=0.72,
    ),
}


@dataclass
class ArchetypeForecast:
    """Probabilistic forecast based on archetype + historical precedent."""
    tract_id: str
    archetype: LeadershipArchetype
    forecast_1yr: str  # What will this archetype likely do in 1 year?
    forecast_3yr: str  # 3-year forecast
    historical_precedent: str  # What did similar people do?
    displacement_probability_1yr: float  # 0-1
    displacement_probability_3yr: float  # 0-1
    confidence: float  # How confident is this forecast?
    caveats: List[str]  # Explicit limitations


def get_archetype_forecast(tract_id: str, archetype: LeadershipArchetype) -> ArchetypeForecast:
    """Generate a speculative forecast based on leadership archetype.
    
    NOTE: This is SPECULATIVE and probabilistic. Historical precedent is not predictive.
    """
    
    forecasts = {
        LeadershipArchetype.GROWTH_AT_ALL_COSTS: ArchetypeForecast(
            tract_id=tract_id,
            archetype=archetype,
            forecast_1yr="Rezoning proposals; reduced parking requirements; tax incentives for development",
            forecast_3yr="Mixed-use development; transit-oriented upzoning; market-rate housing dominates",
            historical_precedent="Denver 2010-2015, Austin 2008-2018: 2-3x rent growth, 30-40% resident displacement",
            displacement_probability_1yr=0.35,
            displacement_probability_3yr=0.72,
            confidence=0.62,
            caveats=[
                "Historical precedent is not predictive of future outcomes",
                "Local factors (regulation, community org) can override archetype",
                "Leadership can change; preferences are not fixed",
            ]
        ),
        LeadershipArchetype.COMMUNITY_PRESERVATION: ArchetypeForecast(
            tract_id=tract_id,
            archetype=archetype,
            forecast_1yr="Anti-displacement ordinances; community land trusts; rent control proposals",
            forecast_3yr="Protected housing stock; slower rent growth; community board power increases",
            historical_precedent="San Francisco 2010-2020, Oakland 2015-2023: Moderated but did not stop displacement",
            displacement_probability_1yr=0.18,
            displacement_probability_3yr=0.42,
            confidence=0.58,
            caveats=[
                "Market forces may overwhelm local policy",
                "Community preservation can slow but rarely stops rent growth",
                "Requires sustained political will (often changes with elections)",
            ]
        ),
        LeadershipArchetype.OPPORTUNIST: ArchetypeForecast(
            tract_id=tract_id,
            archetype=archetype,
            forecast_1yr="Conditional support for any development that benefits them; deal-making",
            forecast_3yr="Mixed outcomes; depends on external market pressure",
            historical_precedent="Highly variable; individual relationships determine outcomes more than policy",
            displacement_probability_1yr=0.28,
            displacement_probability_3yr=0.55,
            confidence=0.45,
            caveats=[
                "Opportunist outcomes are highly variable and unpredictable",
                "Personal relationships matter more than stated policy",
                "Requires individual monitoring, not archetype-level forecasting",
            ]
        ),
        LeadershipArchetype.MARKET_NEUTRAL: ArchetypeForecast(
            tract_id=tract_id,
            archetype=archetype,
            forecast_1yr="Status quo; minimal new policy; follow market signals",
            forecast_3yr="Market-driven outcomes; displacement follows natural supply-demand",
            historical_precedent="Houston 2010-2020 (minimal zoning): Fast growth, fast displacement",
            displacement_probability_1yr=0.42,
            displacement_probability_3yr=0.68,
            confidence=0.65,
            caveats=[
                "'Market-neutral' often means market-favorable to capital",
                "Lack of policy action is itself a choice with consequences",
            ]
        ),
        LeadershipArchetype.EQUITY_FOCUSED: ArchetypeForecast(
            tract_id=tract_id,
            archetype=archetype,
            forecast_1yr="Anti-displacement funding; tenant protections; affordable housing mandates",
            forecast_3yr="Significant policy action; slower displacement; potential affordability preservation",
            historical_precedent="Minneapolis 2020-2023 (zoning reform), Minneapolis Community Land Trust",
            displacement_probability_1yr=0.12,
            displacement_probability_3yr=0.28,
            confidence=0.52,
            caveats=[
                "Equity-focused leadership is rare and often politically fragile",
                "Requires budget + political capital; sustained commitment is difficult",
                "Market pressures can override even strong policy",
            ]
        ),
    }
    
    return forecasts.get(archetype, forecasts[LeadershipArchetype.MARKET_NEUTRAL])


def leadership_layer_disclaimer() -> str:
    """Mandatory disclaimer for all leadership speculation outputs."""
    return (
        "⚠️ SPECULATIVE LAYER DISCLAIMER\n"
        "This forecast is based on probabilistic archetype matching and historical precedent.\n"
        "It is NOT predictive and should NOT be used for investment or policy decisions.\n"
        "Leadership profiles are speculative and based on limited public information.\n"
        "Historical precedent from other cities may not apply to Pittsburgh.\n"
        "This layer is intended for research and discussion purposes only."
    )
