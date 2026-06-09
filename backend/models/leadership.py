"""Leadership layer - speculative research-only signals."""

def get_archetype_forecast(tract_id: str) -> dict:
    """Get speculative leadership layer forecast (RESEARCH ONLY)."""
    return {
        "status": "SPECULATIVE",
        "note": "Leadership layer not enabled for production use"
    }

def leadership_layer_disclaimer() -> str:
    """Return leadership layer disclaimer."""
    return (
        "This layer is research-only and speculative. "
        "It attempts to model community leadership dynamics which are inherently unpredictable. "
        "Use at academic/advocacy level only, not for policy."
    )
