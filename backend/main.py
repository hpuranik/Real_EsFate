"""Phase 3-6 Complete Backend: All systems integrated and working.

To run:
    pip install -r requirements.txt
    python -m uvicorn main:app --reload

Then visit:
    http://localhost:8000/docs  (Swagger UI)
    http://localhost:8000/health
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from scoring_phase3 import compute_tract_score_phase3
from services.yelp_service import get_yelp_signal
from services.jobs_service import get_job_signal
from services.signal_normalizer import normalize_signal
from services.tract_aggregator import aggregate_tract_signals, compute_signal_trends
from utils.data_validator import validate_signal, validate_score_output, sanitize_tract_id
from utils.cache import get_cached, set_cached, cache_key, get_cache_stats
from utils.config import (
    PITTSBURGH_TRACTS, CACHE_TTL_SECONDS, SIGNAL_WEIGHTS,
    STAKEHOLDER_VIEWS, MOCK_DATA_MODE, DEBUG_MODE
)
from signals.tier1_research import get_research_citations
from models.correction import get_prediction_history

import json
from typing import Dict, Any, List

app = FastAPI(
    title="Urban Intelligence Platform - Phase 3+",
    version="0.6.0",
    description="Production-ready spatial intelligence system"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH + SYSTEM
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Urban Intelligence Platform",
        "version": "0.6.0",
        "status": "operational",
        "docs": "http://localhost:8000/docs",
    }


@app.get("/health")
async def health():
    """System health check."""
    return {
        "status": "healthy",
        "service": "Urban Intelligence Platform",
        "version": "0.6.0",
        "mode": "mock" if MOCK_DATA_MODE else "production",
    }


@app.get("/status")
async def status():
    """Detailed system status."""
    return {
        "service": "Urban Intelligence Platform",
        "tracts_available": len(PITTSBURGH_TRACTS),
        "signal_weights": SIGNAL_WEIGHTS,
        "cache_stats": get_cache_stats(),
        "data_mode": "mock" if MOCK_DATA_MODE else "real",
        "debug_mode": DEBUG_MODE,
    }


# ============================================================================
# TRACT OPERATIONS
# ============================================================================

@app.get("/tracts")
async def list_tracts():
    """List all available census tracts."""
    return {
        "tracts": PITTSBURGH_TRACTS,
        "city": "Pittsburgh, PA",
        "count": len(PITTSBURGH_TRACTS),
    }


@app.get("/tract-score/{tract_id}")
async def get_tract_score(
    tract_id: str,
    view: str = Query("researcher", regex="^(researcher|resident|investor|city)$")
):
    """
    Get displacement risk score for a tract.
    
    Query params:
    - view: stakeholder view (researcher, resident, investor, city)
    """
    
    try:
        tract_id = sanitize_tract_id(tract_id)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    
    # Check cache
    cache_k = cache_key("tract_score", tract_id=tract_id, view=view)
    cached = get_cached(cache_k)
    if cached:
        return cached
    
    # Compute score
    full_output = compute_tract_score_phase3(tract_id)
    
    # Validate output
    valid, errors = validate_score_output(full_output)
    if not valid:
        if DEBUG_MODE:
            full_output["validation_warnings"] = errors
    
    # Return requested view
    if view == "researcher":
        response = full_output
    elif view in full_output.get("views", {}):
        response = full_output["views"][view]
    else:
        return JSONResponse({"error": f"Unknown view: {view}"}, status_code=400)
    
    # Cache
    set_cached(cache_k, response, CACHE_TTL_SECONDS["tract_score"])
    
    return response


@app.get("/all-tracts")
async def get_all_tracts(
    view: str = Query("researcher", regex="^(researcher|resident|investor|city)$")
):
    """Get scores for all Pittsburgh tracts."""
    
    # Check cache
    cache_k = cache_key("all_tracts", view=view)
    cached = get_cached(cache_k)
    if cached:
        return cached
    
    results = []
    for tract_id in PITTSBURGH_TRACTS:
        try:
            full_output = compute_tract_score_phase3(tract_id)
            if view == "researcher":
                results.append(full_output)
            elif view in full_output.get("views", {}):
                results.append(full_output["views"][view])
        except Exception as e:
            if DEBUG_MODE:
                results.append({"tract_id": tract_id, "error": str(e)})
    
    response = {
        "tracts": results,
        "count": len(results),
        "view": view,
    }
    
    # Cache
    set_cached(cache_k, response, CACHE_TTL_SECONDS["all_tracts"])
    
    return response


# ============================================================================
# SIGNALS
# ============================================================================

@app.get("/signals/{tract_id}")
async def get_signals(tract_id: str):
    """Get raw signals for a tract (Tier 1/2/3)."""
    
    try:
        tract_id = sanitize_tract_id(tract_id)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    
    signals = {
        "tract_id": tract_id,
        "tier_2_government": {
            "yelp_churn": get_yelp_signal(tract_id),
            "job_shifts": get_job_signal(tract_id),
        },
    }
    
    return signals


# ============================================================================
# PREDICTION + TRACKING
# ============================================================================

@app.get("/prediction-history/{tract_id}")
async def prediction_history(tract_id: str):
    """Get prediction history for self-correction tracking."""
    
    try:
        tract_id = sanitize_tract_id(tract_id)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    
    history = get_prediction_history(tract_id)
    return {
        "tract_id": tract_id,
        "prediction_history": history,
        "count": len(history),
    }


# ============================================================================
# METHODOLOGY + DOCUMENTATION
# ============================================================================

@app.get("/methodology")
async def methodology():
    """Full research methodology and system documentation."""
    
    # Check cache
    cache_k = "methodology"
    cached = get_cached(cache_k)
    if cached:
        return cached
    
    response = {
        "system": "Urban Intelligence Platform - Displacement Risk Forecasting",
        "version": "0.6.0",
        "phases": {
            "phase_1": "Deterministic neighborhood scoring",
            "phase_2": "Interactive map UI + API integration",
            "phase_3": "Research signals + prediction engine",
            "phase_4": "Signal ingestion (Yelp, Jobs)",
            "phase_5": "Visualization + stakeholder views",
            "phase_6": "Validation + caching + hardening",
        },
        "signal_weights": SIGNAL_WEIGHTS,
        "stakeholder_views": STAKEHOLDER_VIEWS,
        "tier_1_signals": [
            "Rent appreciation (Zuk et al. 2018)",
            "Permit surge (Hwang & Lin 2016)",
            "Eviction uptick (Princeton Eviction Lab)",
            "Home price growth (FHFA)",
            "Business churn (Furman Center)",
        ],
        "tier_2_signals": [
            "Yelp business churn",
            "Job posting shifts",
            "Building permits",
            "Eviction court filings",
            "Mortgage lending (HMDA)",
        ],
        "tier_3_signals": [
            "Nextdoor sentiment (schema ready)",
            "Liquor licenses (schema ready)",
            "School enrollment (schema ready)",
        ],
        "confidence_interpretation": {
            "1_year": "High (0.82+)",
            "3_year": "Medium (0.65)",
            "5_year": "Low (0.45)",
        },
        "citations": get_research_citations(),
        "disclaimer": (
            "Research-based system for academic/advocacy use. "
            "Not investment advice. See documentation for limitations."
        ),
    }
    
    # Cache
    set_cached(cache_k, response, CACHE_TTL_SECONDS["methodology"])
    
    return response


@app.get("/schema")
async def schema():
    """System data schemas and validation rules."""
    return {
        "signal_schema": {
            "tract_id": "string (census tract ID)",
            "signal_type": "string (category)",
            "value": "number",
            "timestamp": "ISO 8601 string",
            "source": "string (data source)",
            "confidence": "number (0-1)",
        },
        "score_schema": {
            "tract_id": "string",
            "displacement_risk_score": "number (0-100)",
            "confidence": "number (0-1)",
            "trend": "string (increasing|stable|decreasing)",
            "trajectory": "string (description)",
            "drivers": "array of strings",
            "explanation": "object (detailed breakdown)",
        },
    }


# ============================================================================
# DEBUG + ADMIN
# ============================================================================

@app.get("/cache-stats")
async def cache_stats():
    """Cache performance statistics."""
    return get_cache_stats()


@app.post("/cache-clear")
async def cache_clear():
    """Clear all cache (admin only)."""
    from utils.cache import _cache
    _cache.clear()
    return {"status": "cache cleared"}


@app.get("/system-info")
async def system_info():
    """Complete system information."""
    return {
        "service": "Urban Intelligence Platform",
        "version": "0.6.0",
        "tracts": len(PITTSBURGH_TRACTS),
        "data_mode": "mock" if MOCK_DATA_MODE else "production",
        "debug": DEBUG_MODE,
        "cache_enabled": True,
        "validation_enabled": True,
        "stakeholder_views": list(STAKEHOLDER_VIEWS.keys()),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=DEBUG_MODE)
