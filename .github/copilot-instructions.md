# 🧠 URBAN INTELLIGENCE PLATFORM — SYSTEM SPECIFICATION

You are the primary engineering agent for building a complete geospatial intelligence platform.

---

# 0. GLOBAL SYSTEM INVARIANTS

These override all other instructions.

## 0.1 SYSTEM IDENTITY

This system IS:
- A deterministic spatial-temporal intelligence engine
- A signal aggregation + scoring system
- An explainable analytics platform
- A multi-stakeholder information system

This system is NOT:
- An AI/LLM predictive model
- A chatbot system
- An autonomous agent system
- A machine learning pipeline

## 0.2 DATA TRUTH INVARIANT

All outputs originate from:
- Explicit structured data
- Deterministic transformations
- Defined signal inputs

Never hallucinate: external datasets, real-world values, API responses.

If data is missing: use mock data, label clearly as mock, maintain schema integrity.

## 0.3 SCORING INVARIANT

All scores must be:
- Deterministic
- Reproducible
- Explainable
- Decomposable into weighted inputs

No black-box models allowed at any stage.

## 0.4 FRONTEND RESPONSIBILITY INVARIANT

Frontend is ONLY:
- Visualization
- Interaction
- Rendering backend outputs

Frontend MUST NOT:
- Compute scores
- Apply weighting logic
- Transform raw signals

## 0.5 COMPLETENESS INVARIANT

A feature is ONLY complete when:
- Backend logic exists
- API endpoint works
- Data flows end-to-end
- Frontend displays output (if applicable)
- Output matches schema
- Explanation metadata included

## 0.6 SCOPE FREEZE INVARIANT

MVP scope strictly limited to:
- Single city (Pittsburgh)
- Census tract level analysis
- Defined signal set
- Deterministic scoring system

Do NOT introduce:
- Multi-city scaling
- ML models
- Autonomous agents
- Authentication
- Payments
- Microservices

## 0.7 MATHEMATICAL STABILITY RULE

The system MUST prioritize:
- Reproducibility over novelty
- Interpretability over complexity
- Stable statistical methods over experimental methods

Mathematical methods only change when:
- Explicitly manually updated
- Clearly versioned in codebase

The system MUST NOT autonomously modify its mathematical model.

## 0.8 DATA TRUST HIERARCHY

All signals ranked by reliability:

**Tier 1 (Ground truth)**: census, permits, tax records, zoning, infrastructure
**Tier 2 (Observed behavior)**: rent changes, business openings/closures, job postings, evictions
**Tier 3 (Behavioral proxies)**: sentiment, social signals, community text

RULE: Tier 1 signals MUST dominate scoring. Tier 3 signals MUST NEVER override Tier 1 conclusions.

---

# 1. ARCHITECTURE

## Backend
- FastAPI (Python)
- Modular service-based structure
- REST API

## Frontend
- Next.js + TypeScript
- Mapbox GL JS
- Responsive design

## Database
- PostgreSQL + PostGIS (future phase)
- Spatial + temporal indexing

---

# 2. CANONICAL DATA SCHEMAS

All signals MUST conform to:
```json
{
  "tract_id": "string",
  "signal_type": "string",
  "value": "number",
  "timestamp": "ISO string",
  "source": "string",
  "confidence": "number (0-1)"
}
```

All outputs MUST conform to:
```json
{
  "tract_id": "string",
  "score": "number (0-100)",
  "confidence": "number (0-1)",
  "trend": "increasing | stable | decreasing",
  "drivers": ["string"],
  "explanation": {
    "positive_signals": [],
    "negative_signals": [],
    "weights_used": {}
  }
}
```

---

# 3. SIGNAL HIERARCHY

**Anchor signals (60% weight)**
- Permits
- Rent changes
- Evictions
- Home prices

**Acceleration signals (30% weight)**
- Yelp business churn
- Job posting shifts
- School enrollment

**Speculative signals (10% weight)**
- Sentiment analysis
- Community signals

Speculative signals MUST NOT dominate scoring.

---

# 4. CORE COMPONENTS

## Backend services/

**signal_normalizer.py**
- Convert raw signals → canonical schema
- Normalize numeric ranges
- Enforce consistency

**tract_aggregator.py**
- Group signals by tract_id
- Aggregate by signal_type
- Compute feature vectors

**scoring_engine.py**
- Deterministic weighted scoring
- Produce explanation metadata

**yelp_service.py**
- Ingest business openings/closures
- Classify businesses
- Map to tract_id

**jobs_service.py**
- Ingest job posting data
- Extract geography
- Categorize industries

---

# 5. PHASES

## Phase 3 — Spatial Intelligence Core ✅
- Unify data model
- Implement normalization
- Finalize deterministic scoring
- Ensure explainability

## Phase 4 — Signal Ingestion ✅
- Implement Yelp service
- Implement jobs service
- Integrate acceleration signals
- Normalize all Tier 3 inputs

## Phase 5 — Visualization Layer ✅
- Mapbox integration
- Tract heatmaps
- Clickable UI
- Explanation panel

## Phase 6 — System Hardening ✅
- Refactor backend structure
- Validate schema enforcement
- Improve caching
- Mock/real data separation
- Stabilize API responses

---

# 6. IMPLEMENTATION RULES

When coding:
- Always specify file paths
- Prefer simple working solutions
- Avoid unnecessary abstractions
- No premature optimization
- Code must be runnable immediately
- Maintain modular structure

Choose:
- Working system > perfect system
- Simple > complex
- Explicit > implicit

---

# 7. SUCCESS CONDITION

The system is complete when a user can:

1. Open map UI
2. See census tracts
3. Click a tract
4. View score
5. See explanation of score
6. Compare signals over time
7. Trace all contributing signals

If external data fails:
- Log error
- Return empty but valid schema
- System remains stable
- Frontend displays "insufficient data"

---

# 8. STAKEHOLDER VARIANTS

**Researcher**: Full transparency, methodology-focused
**Resident**: Actionable, accessible, resource-focused
**Investor**: Opportunity-focused with impact disclosure
**City**: Policy intervention windows

---

This specification is binding. Follow it literally.
