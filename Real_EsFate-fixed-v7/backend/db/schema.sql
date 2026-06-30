-- PostgreSQL + PostGIS schema for Urban Intelligence Platform
-- Phase 3+: Replace in-memory storage with persistent database

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS jsonb;

-- Census tracts (spatial reference)
CREATE TABLE census_tracts (
    tract_id VARCHAR(12) PRIMARY KEY,
    tract_name VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    geometry GEOMETRY(MultiPolygon, 4326),
    population INT,
    area_sqmi FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_geometry ON census_tracts USING GIST(geometry);

-- Tier 1 Research signals (static, citations)
CREATE TABLE tier1_research_signals (
    signal_id SERIAL PRIMARY KEY,
    signal_name VARCHAR(255),
    description TEXT,
    citation VARCHAR(512),
    coefficient FLOAT,
    confidence_interval_lower FLOAT,
    confidence_interval_upper FLOAT,
    predictive_horizon VARCHAR(20),  -- "early", "mid", "late"
    direction VARCHAR(20),  -- "positive", "negative"
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tier 2 Government signals (time series)
CREATE TABLE tier2_government_signals (
    signal_id SERIAL PRIMARY KEY,
    tract_id VARCHAR(12),
    signal_type VARCHAR(50),  -- "eviction", "hmda", "permits"
    signal_data JSONB,  -- Flexible storage
    data_source VARCHAR(255),
    collection_date DATE,
    last_updated TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tract_id) REFERENCES census_tracts(tract_id),
    CONSTRAINT unique_tract_signal_date UNIQUE(tract_id, signal_type, collection_date)
);

CREATE INDEX idx_tract_signal_date ON tier2_government_signals(tract_id, signal_type, collection_date);

-- Tier 3 Local alpha signals (schema ready for Phase 4)
CREATE TABLE tier3_local_signals (
    signal_id SERIAL PRIMARY KEY,
    tract_id VARCHAR(12),
    signal_type VARCHAR(50),  -- "yelp_churn", "job_posts", "nextdoor", etc.
    signal_data JSONB,  -- Flexible
    data_source VARCHAR(255),
    collection_date DATE,
    last_updated TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tract_id) REFERENCES census_tracts(tract_id),
    CONSTRAINT unique_tract_tier3_date UNIQUE(tract_id, signal_type, collection_date)
);

-- Leadership profiles (speculative layer)
CREATE TABLE leadership_profiles (
    profile_id SERIAL PRIMARY KEY,
    tract_id VARCHAR(12),
    name VARCHAR(255),
    role VARCHAR(100),  -- "Mayor", "Developer CEO", etc.
    archetype VARCHAR(50),  -- "growth-at-all-costs", etc.
    stated_intent TEXT,
    revealed_preference TEXT,
    intent_gap_score FLOAT,
    historical_precedent TEXT,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tract_id) REFERENCES census_tracts(tract_id)
);

-- Predictions (displacement risk forecasts)
CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,
    tract_id VARCHAR(12),
    prediction_date TIMESTAMP,
    overall_risk_score FLOAT,
    primary_risk_drivers JSONB,
    early_stage_score FLOAT,
    mid_stage_score FLOAT,
    late_stage_score FLOAT,
    confidence_1yr FLOAT,
    confidence_3yr FLOAT,
    confidence_5yr FLOAT,
    signal_weights JSONB,
    data_sources JSONB,
    trajectory TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tract_id) REFERENCES census_tracts(tract_id)
);

CREATE INDEX idx_tract_prediction_date ON predictions(tract_id, prediction_date DESC);

-- Prediction logs (for self-correction loop)
CREATE TABLE prediction_logs (
    log_id SERIAL PRIMARY KEY,
    prediction_id INT,
    tract_id VARCHAR(12),
    predicted_risk_score FLOAT,
    actual_risk_score FLOAT,
    actual_outcome VARCHAR(255),
    signals_correct JSONB,
    signals_missed JSONB,
    false_positives JSONB,
    prediction_date TIMESTAMP,
    outcome_date TIMESTAMP,
    accuracy_pct FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tract_id) REFERENCES census_tracts(tract_id),
    FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id)
);

-- Signal accuracy tracking
CREATE TABLE signal_accuracy_scores (
    score_id SERIAL PRIMARY KEY,
    signal_name VARCHAR(255),
    times_active INT DEFAULT 0,
    times_correct INT DEFAULT 0,
    accuracy FLOAT,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Stakeholder outputs (audit trail)
CREATE TABLE stakeholder_outputs (
    output_id SERIAL PRIMARY KEY,
    tract_id VARCHAR(12),
    stakeholder_type VARCHAR(50),  -- "resident", "researcher", "investor", "city"
    output_json JSONB,  -- Full output
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tract_id) REFERENCES census_tracts(tract_id)
);

CREATE INDEX idx_tract_stakeholder ON stakeholder_outputs(tract_id, stakeholder_type);
