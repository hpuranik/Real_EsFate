'use client';

import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import styles from './page_phase5.module.css';
import pittsburghTracts from '../data/pittsburgh-tracts.json';

interface ScoreData {
  tract_id: string;
  displacement_risk_score: number;
  views: {
    researcher: any;
    resident: any;
    investor: any;
    city: any;
  };
}

export default function Home() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [selectedTract, setSelectedTract] = useState<ScoreData | null>(null);
  const [selectedView, setSelectedView] = useState<'researcher' | 'resident' | 'investor' | 'city'>('researcher');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [allScores, setAllScores] = useState<any[]>([]);
  const [timeSlider, setTimeSlider] = useState(0);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

  useEffect(() => {
    if (!MAPBOX_TOKEN) {
      setError('Mapbox token not configured');
      return;
    }

    mapboxgl.accessToken = MAPBOX_TOKEN;

    if (map.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current!,
      style: 'mapbox://styles/mapbox/light-v11',
      center: [-80.009, 40.4406],
      zoom: 10.5,
    });

    map.current.on('load', () => {
      if (!map.current) return;

      map.current.addSource('pittsburgh-tracts', {
        type: 'geojson',
        data: pittsburghTracts as any,
      });

      map.current.addLayer({
        id: 'tracts-fill',
        type: 'fill',
        source: 'pittsburgh-tracts',
        paint: {
          'fill-color': '#888',
          'fill-opacity': 0.5,
        },
      });

      map.current.addLayer({
        id: 'tracts-outline',
        type: 'line',
        source: 'pittsburgh-tracts',
        paint: {
          'line-color': '#000',
          'line-width': 2,
        },
      });

      map.current.on('click', 'tracts-fill', async (e) => {
        const feature = e.features?.[0];
        if (!feature?.properties) return;

        const tractId = feature.properties.tract_id;
        setLoading(true);
        setError(null);

        try {
          const response = await fetch(`${API_URL}/tract-score/${tractId}`);
          if (!response.ok) throw new Error('Failed to fetch');
          const data = await response.json();
          setSelectedTract(data);
          setSelectedView('researcher');
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Error');
        } finally {
          setLoading(false);
        }
      });
    });

    // Load all scores for heatmap
    fetch(`${API_URL}/all-tracts`)
      .then(r => r.json())
      .then(d => setAllScores(d.tracts))
      .catch(e => console.error(e));
  }, [MAPBOX_TOKEN]);

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#e74c3c';
    if (score >= 70) return '#e67e22';
    if (score >= 60) return '#f39c12';
    if (score >= 50) return '#f1c40f';
    if (score >= 40) return '#2ecc71';
    return '#27ae60';
  };

  const getConfidenceOpacity = (confidence: number) => {
    return 0.4 + confidence * 0.5;
  };

  const currentView = selectedTract?.views[selectedView];

  return (
    <div className={styles.container}>
      <div ref={mapContainer} className={styles.map} />

      <div className={styles.controls}>
        <label className={styles.sliderLabel}>Timeline: {timeSlider} months</label>
        <input
          type="range"
          min="0"
          max="36"
          value={timeSlider}
          onChange={(e) => setTimeSlider(Number(e.target.value))}
          className={styles.slider}
        />
      </div>

      {selectedTract && (
        <div className={styles.panel}>
          <button className={styles.closeBtn} onClick={() => setSelectedTract(null)}>✕</button>

          <h2>{selectedTract.tract_id}</h2>

          <div className={styles.viewSelector}>
            {(['researcher', 'resident', 'investor', 'city'] as const).map(view => (
              <button
                key={view}
                className={`${styles.viewBtn} ${selectedView === view ? styles.active : ''}`}
                onClick={() => setSelectedView(view)}
              >
                {view.charAt(0).toUpperCase() + view.slice(1)}
              </button>
            ))}
          </div>

          {currentView && (
            <div className={styles.content}>
              {selectedView === 'researcher' && (
                <div>
                  <div className={styles.scoreCard}>
                    <div className={styles.scoreValue}>
                      {currentView.displacement_risk_score || 'N/A'}
                    </div>
                    <div className={styles.scoreLabel}>Displacement Risk</div>
                    <div className={styles.confidence}>
                      Confidence: {Math.round((currentView.confidence_intervals?.['1_year'] || 0) * 100)}%
                    </div>
                  </div>
                  <p className={styles.trajectory}>{currentView.trajectory}</p>
                  <div className={styles.section}>
                    <h3>Early Stage (0-2 years)</h3>
                    <p>Risk: {currentView.early_stage?.risk_score}/100</p>
                    <p>Signals: {currentView.early_stage?.signals_active?.join(', ') || 'None'}</p>
                  </div>
                  <div className={styles.section}>
                    <h3>Mid Stage (2-5 years)</h3>
                    <p>Risk: {currentView.mid_stage?.risk_score}/100</p>
                    <p>Signals: {currentView.mid_stage?.signals_active?.join(', ') || 'None'}</p>
                  </div>
                </div>
              )}

              {selectedView === 'resident' && (
                <div>
                  <div className={styles.riskBadge}>{currentView.risk_level}</div>
                  <p>{currentView.what_it_means}</p>
                  <div className={styles.section}>
                    <h3>Tenant Resources</h3>
                    <ul>
                      {currentView.tenant_resources?.map((r: string, i: number) => (
                        <li key={i}>{r}</li>
                      ))}
                    </ul>
                  </div>
                  <div className={styles.section}>
                    <h3>What You Can Do</h3>
                    <ul>
                      {currentView.recommendations?.map((r: string, i: number) => (
                        <li key={i}>✓ {r}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {selectedView === 'investor' && (
                <div>
                  <div className={styles.opportunityScore}>
                    Opportunity: {currentView.opportunity_score?.toFixed(0)}/100
                  </div>
                  <div className={styles.riskDisclosure}>
                    <strong>Community Impact Disclosure:</strong>
                    <p>{currentView.community_impact_acknowledgment}</p>
                  </div>
                  <div className={styles.section}>
                    <h3>Market Signals</h3>
                    {currentView.market_signals && (
                      <ul>
                        <li>{currentView.market_signals.early_stage_capital_inflow ? '✓' : '✗'} Early stage capital</li>
                        <li>{currentView.market_signals.rent_appreciation_trajectory ? '✓' : '✗'} Rent appreciation</li>
                      </ul>
                    )}
                  </div>
                </div>
              )}

              {selectedView === 'city' && (
                <div>
                  <div className={styles.section}>
                    <h3>Policy Intervention Window</h3>
                    <p className={styles.urgent}>{currentView.policy_intervention_window}</p>
                  </div>
                  <div className={styles.section}>
                    <h3>Warning Signals</h3>
                    <ul>
                      {currentView.early_warning_signals?.map((signal: string, i: number) => (
                        <li key={i}>⚠️ {signal}</li>
                      ))}
                    </ul>
                  </div>
                  <div className={styles.section}>
                    <h3>Recommended Tools</h3>
                    <ul>
                      {currentView.tools?.map((tool: string, i: number) => (
                        <li key={i}>• {tool}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {error && <div className={styles.error}>{error}</div>}
      {loading && <div className={styles.loading}>Loading...</div>}
    </div>
  );
}
