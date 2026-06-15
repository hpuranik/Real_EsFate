"""
Phase 3 FastAPI server with stable frontend-compatible endpoints.

KEY FIXES:
- Ensures /all-tracts matches frontend expectations exactly
- Ensures tract_id + displacement_risk_score always present
- Removes ambiguity between view formats for map rendering
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from scoring_phase3 import compute_tract_score_phase3
from signals.tier1_research import get_research_citations
from models.correction import get_prediction_history

app = FastAPI(title="Urban Intelligence Platform - Phase 3", version="0.3.1")

# -----------------------------
# CORS (frontend compatibility)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Static tract universe
# -----------------------------
PITTSBURGH_TRACTS = [
    "42003030100", "42003030200", "42003030300", "42003030400",
    "42003030500", "42003030600", "42003030700", "42003030800",
    "42003030900",
]

# -----------------------------
# HEALTH
# -----------------------------
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "Urban Intelligence Platform - Phase 3",
        "version": "0.3.1"
    }

# -----------------------------
# SINGLE TRACT SCORE
# -----------------------------
@app.get("/tract-score/{tract_id}")
async def get_tract_score(
    tract_id: str,
    view: str = Query("researcher")
):
    """
    Returns full structured score object.
    Frontend uses this for click interactions.
    """

    full_output = compute_tract_score_phase3(tract_id)

    if view == "researcher":
        return full_output

    if view in full_output.get("views", {}):
        return full_output["views"][view]

    return {"error": f"Unknown view: {view}"}


# -----------------------------
# ALL TRACTS (CRITICAL FIX)
# -----------------------------
@app.get("/all-tracts")
async def get_all_tracts():
    """
    Frontend expects:
    {
      count: number,
      tracts: [
        { tract_id, displacement_risk_score }
      ]
    }
    """

    results = []

    for tract_id in PITTSBURGH_TRACTS:
        try:
            full_output = compute_tract_score_phase3(tract_id)

            # Normalize score (robust extraction)
            score = None

            if isinstance(full_output, dict):
                score = full_output.get("displacement_risk_score")

                # fallback if nested
                if score is None and "views" in full_output:
                    score = full_output["views"].get("researcher", {}).get("displacement_risk_score")

            if score is None:
                score = 0

            results.append({
                "tract_id": tract_id,
                "displacement_risk_score": float(score)
            })

        except Exception as e:
            # Never break frontend if one tract fails
            results.append({
                "tract_id": tract_id,
                "displacement_risk_score": 0.0,
                "error": str(e)
            })

    return {
        "tracts": results,
        "count": len(results)
    }


# -----------------------------
# PREDICTION HISTORY
# -----------------------------
@app.get("/prediction-history/{tract_id}")
async def prediction_history(tract_id: str):
    history = get_prediction_history(tract_id)

    return {
        "tract_id": tract_id,
        "prediction_history": history,
        "count": len(history),
        "note": "Historical predictions vs outcomes for calibration."
    }


# -----------------------------
# METHODOLOGY (STATIC RESEARCH LAYER)
# -----------------------------
@app.get("/methodology")
async def methodology():
    return {
        "system": "Urban Intelligence Platform - Displacement Risk Forecasting",
        "phases": {
            "phase_1": "Baseline deterministic neighborhood scoring",
            "phase_2": "Map visualization + tract interaction layer",
            "phase_3": "Multi-tier signal fusion + prediction engine",
            "phase_4": "Real-world Tier 3 data integration (Yelp, jobs, sentiment)",
            "phase_5_6": "Advanced forecasting + governance + UX refinement",
        },
        "tier1_research_signals": [
            "Rent appreciation (Zuk et al. 2018)",
            "Permit surge (Hwang & Lin 2016)",
            "Eviction patterns (Princeton Eviction Lab)",
            "Home price growth (FHFA)",
            "Business churn (NYU Furman Center)"
        ],
        "tier2_government_signals": [
            "HUD permits",
            "HMDA lending data",
            "FHFA housing indexes",
            "Business license filings"
        ],
        "tier3_local_signals": [
            "Yelp business churn",
            "Job posting shifts",
            "Community sentiment (Nextdoor-like)",
            "Liquor license applications"
        ],
        "output_structure": {
            "early_stage": "0–2 years",
            "mid_stage": "2–5 years",
            "late_stage": "5+ years"
        },
        "confidence_intervals": {
            "1_year": 0.82,
            "3_year": 0.65,
            "5_year": 0.45
        },
        "citations": get_research_citations(),
        "disclaimer": "Research prototype. Not financial advice. Outputs are probabilistic and for civic analysis only."
    }


# -----------------------------
# LIST TRACTS
# -----------------------------
@app.get("/tracts")
async def list_tracts():
    return {
        "tracts": PITTSBURGH_TRACTS,
        "city": "Pittsburgh, PA",
        "count": len(PITTSBURGH_TRACTS)
    }


# -----------------------------
# ENTRYPOINT
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
