"""Phase 3 FastAPI server with new endpoints.

New structure:
- /tract-score/{tract_id} → returns multi-layer score (researcher default)
- /tract-score/{tract_id}?view=resident → resident-friendly output
- /tract-score/{tract_id}?view=investor → investor view
- /tract-score/{tract_id}?view=city → city planner view
- /prediction-history/{tract_id} → see past predictions vs outcomes
- /methodology → full research documentation
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from scoring_phase3 import compute_tract_score_phase3
from signals.tier1_research import get_research_citations
from models.correction import get_prediction_history

import json

app = FastAPI(title="Urban Intelligence Platform - Phase 3", version="0.3.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PITTSBURGH_TRACTS = [
    "42003030100", "42003030200", "42003030300", "42003030400", "42003030500",
    "42003030600", "42003030700", "42003030800", "42003030900",
]


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Urban Intelligence Platform - Phase 3"}


@app.get("/tract-score/{tract_id}")
async def get_tract_score(
    tract_id: str,
    view: str = Query("researcher", regex="^(researcher|resident|investor|city)$")
):
    """
    Get displacement risk score for a tract.
    
    Query params:
    - view: "researcher" (default), "resident", "investor", "city"
    """
    
    full_output = compute_tract_score_phase3(tract_id)
    
    # Return requested view or full output for researcher
    if view == "researcher":
        return full_output
    elif view in full_output["views"]:
        return full_output["views"][view]
    else:
        return {"error": f"Unknown view: {view}"}


@app.get("/all-tracts")
async def get_all_tracts(view: str = Query("researcher", regex="^(researcher|resident|investor|city)$")):
    """Get scores for all Pittsburgh tracts."""
    results = []
    for tract_id in PITTSBURGH_TRACTS:
        full_output = compute_tract_score_phase3(tract_id)
        if view == "researcher":
            results.append(full_output)
        elif view in full_output["views"]:
            results.append(full_output["views"][view])
    
    return {"tracts": results, "count": len(results), "view": view}


@app.get("/prediction-history/{tract_id}")
async def prediction_history(tract_id: str):
    """Get prediction history for self-correction tracking."""
    history = get_prediction_history(tract_id)
    return {
        "tract_id": tract_id,
        "prediction_history": history,
        "count": len(history),
        "note": "Shows all past predictions and their accuracy when compared to actual outcomes.",
    }


@app.get("/methodology")
async def methodology():
    """Return full research methodology and citations."""
    return {
        "system": "Urban Intelligence Platform - Displacement Risk Forecasting",
        "phases": {
            "phase_1": "Deterministic neighborhood scoring (baseline)",
            "phase_2": "Interactive map UI with API integration",
            "phase_3": "Three-tier research signals + prediction engine + self-correction",
            "phase_4": "Real Tier 3 data integration (Yelp, job posts, Nextdoor, liquor licenses)",
            "phase_5_6": "Leadership modeling, advanced forecasting, UX refinement",
        },
        "tier1_research_signals": [
            "Rent appreciation (Zuk et al. 2018)",
            "Permit surge (Hwang & Lin 2016)",
            "Eviction uptick (Princeton Eviction Lab)",
            "Home price growth (FHFA)",
            "Business churn (NYU Furman Center)",
            "Education shift (Urban Institute)",
            "School enrollment decline (NCRC)",
        ],
        "tier2_government_signals": [
            "HUD permit filings",
            "HMDA loan origination data",
            "FHFA house price indexes",
            "Business license data",
            "Eviction court filings (Eviction Lab)",
        ],
        "tier3_local_signals": [
            "Yelp/Google business churn",
            "Job posting shifts",
            "Nextdoor sentiment",
            "Liquor license applications",
            "School enrollment",
            "Retail format changes",
        ],
        "output_structure": {
            "early_stage": "0-2 years (capital inflows)",
            "mid_stage": "2-5 years (rent growth, demographic shift)",
            "late_stage": "now (evictions, direct displacement)",
        },
        "confidence_intervals": {
            "1_year": "High (0.82+)",
            "3_year": "Medium (0.65)",
            "5_year": "Low (0.45)",
        },
        "citations": get_research_citations(),
        "disclaimer": (
            "This system is research-based and for academic/advocacy use. "
            "Not investment advice. Leadership layer is speculative. "
            "Model improves through prediction logging and self-correction."
        ),
    }


@app.get("/tracts")
async def list_tracts():
    return {"tracts": PITTSBURGH_TRACTS, "city": "Pittsburgh, PA", "count": len(PITTSBURGH_TRACTS)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
