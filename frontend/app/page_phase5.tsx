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
      const errorMsg = 'Mapbox token not configured. Please create frontend/.env.local with NEXT_PUBLIC_MAPBOX_TOKEN. See .env.local.template for instructions.';
      console.error('❌', errorMsg);
      setError(errorMsg);
      return;
    }

    mapboxgl.accessToken = MAPBOX_TOKEN;

    if (map.current) return;

    try {
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

        // Hover effect
        map.current.on('mouseenter', 'tracts-fill', () => {
          if (map.current) {
            map.current.getCanvas().style.cursor = 'pointer';
          }
        });

        map.current.on('mouseleave', 'tracts-fill', () => {
          if (map.current) {
            map.current.getCanvas().style.cursor = '';
          }
        });

        map.current.on('click', 'tracts-fill', async (e) => {
          const feature = e.features?.[0];
          if (!feature?.properties) {
            console.warn('⚠️ No properties found on clicked feature');
            setError('Unable to identify tract. Please try clicking again.');
            return;
          }

          const tractId = feature.properties.tract_id;
          console.log('📍 Clicked tract:', tractId);
          setLoading(true);
          setError(null);

          try {
            const response = await fetch(`${API_URL}/tract-score/${tractId}`);
            if (!response.ok) {
              throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            console.log('✅ Fetched score:', data);
            setSelectedTract(data);
            setSelectedView('researcher');
          } catch (err) {
            const errorMsg = err instanceof Error ? err.message : 'Unknown error fetching tract score';
            console.error('❌ Error:', errorMsg);
            setError(`Failed to load tract data: ${errorMsg}`);
          } finally {
            setLoading(false);
          }
        });
      });

      // Load all scores for heatmap coloring
      fetch(`${API_URL}/all-tracts`)
        .then(r => r.json())
        .then(d => {
          console.log('✅ Loaded all tract scores:', d.count, 'tracts');
          setAllScores(d.tracts);
          
          // Update heatmap colors based on scores
          if (map.current && d.tracts.length > 0) {
            const colorExpression: any[] = ['match', ['get', 'tract_id']];
            
            d.tracts.forEach((tract: any) => {
              const score = tract.displacement_risk_score || 0;
              const color = getScoreColor(score);
              colorExpression.push(tract.tract_id, color);
            });
            
            colorExpression.push('#888'); // default color
            
            map.current.setPaintProperty('tracts-fill', 'fill-color', colorExpression);
          }
        })
        .catch(e => {
          console.error('❌ Error loading all tracts:', e);
          setError('Failed to load tract scores for map coloring');
        });
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error initializing map';
      console.error('❌ Map initialization error:', errorMsg);
      setError(`Failed to initialize map: ${errorMsg}`);
    }

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [MAPBOX_TOKEN]);

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#e74c3c';  // Dark red
    if (score >= 70) return '#e67e22';  // Orange-red
    if (score >= 60) return '#f39c12';  // Orange
    if (score >= 50) return '#f1c40f';  // Yellow
    if (score >= 40) return '#2ecc71';  // Light green
    return '#27ae60';                   // Dark green
  };

  const getConfidenceOpacity = (confidence: number) => {
    return 0.4 + confidence * 0.5;
  };

  const currentView = selectedTract?.views[selectedView];

  return (
    <div className={styles.container}>
      <div ref={mapContainer} className={styles.map} />

      <div className={styles.controls}>
        <label className={styles.sliderLabel}>Timeline: {timeSlider} months ago</label>
        <input
          type="range"
          min="0"
          max="36"
          value={timeSlider}
          onChange={(e) => setTimeSlider(Number(e.target.value))}
          className={styles.slider}
        />
        <p className={styles.timelineNote}>(Historical data coming in Phase 7)</p>
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
                      {currentView.displacement_risk_score ? currentView.displacement_risk_score.toFixed(1) : 'N/A'}
                    </div>
                    <div className={styles.scoreLabel}>Displacement Risk (0-100)</div>
                    <div className={styles.confidence}>
                      1-Year Confidence: {Math.round((currentView.confidence_intervals?.['1_year'] || 0) * 100)}%
                    </div>
                  </div>
                  <p className={styles.trajectory}>
                    <strong>Trajectory:</strong> {currentView.trajectory}
                  </p>
                  
                  <div className={styles.section}>
                    <h3>Early Stage (0-2 years)</h3>
                    <p><strong>Risk Score:</strong> {currentView.early_stage?.risk_score}/100</p>
                    <p><strong>Confidence:</strong> {Math.round((currentView.early_stage?.confidence || 0) * 100)}%</p>
                    <p><strong>Active Signals:</strong> {currentView.early_stage?.signals_active?.join(', ') || 'None detected'}</p>
                    <p className={styles.interpretation}>{currentView.early_stage?.interpretation}</p>
                  </div>
                  
                  <div className={styles.section}>
                    <h3>Mid Stage (2-5 years)</h3>
                    <p><strong>Risk Score:</strong> {currentView.mid_stage?.risk_score}/100</p>
                    <p><strong>Confidence:</strong> {Math.round((currentView.mid_stage?.confidence || 0) * 100)}%</p>
                    <p><strong>Active Signals:</strong> {currentView.mid_stage?.signals_active?.join(', ') || 'None detected'}</p>
                    <p className={styles.interpretation}>{currentView.mid_stage?.interpretation}</p>
                  </div>

                  <div className={styles.section}>
                    <h3>Late Stage (5+ years)</h3>
                    <p><strong>Risk Score:</strong> {currentView.late_stage?.risk_score}/100</p>
                    <p><strong>Confidence:</strong> {Math.round((currentView.late_stage?.confidence || 0) * 100)}%</p>
                    <p><strong>Active Signals:</strong> {currentView.late_stage?.signals_active?.join(', ') || 'None detected'}</p>
                    <p className={styles.interpretation}>{currentView.late_stage?.interpretation}</p>
                  </div>

                  <div className={styles.section}>
                    <h3>Signal Methodology</h3>
                    <p><strong>Tier 1 Signals (60% weight):</strong></p>
                    <ul>
                      {currentView.methodology?.tier1_signals?.map((s: string) => (
                        <li key={s}>✓ {s}</li>
                      ))}
                    </ul>
                    <p><strong>Data Sources:</strong> {currentView.methodology?.tier2_sources?.join(', ')}</p>
                  </div>

                  {currentView.citations && currentView.citations.length > 0 && (
                    <div className={styles.section}>
                      <h3>Research Citations</h3>
                      {currentView.citations.map((c: any, i: number) => (
                        <div key={i} className={styles.citation}>
                          <p>
                            <strong>{c.authors.join(', ')} ({c.year})</strong>
                          </p>
                          <p>"{c.title}" — {c.source}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {selectedView === 'resident' && (
                <div>
                  <div className={styles.riskBadge}>{currentView.risk_level}</div>
                  <p><strong>What This Means:</strong> {currentView.what_it_means}</p>
                  
                  <div className={styles.section}>
                    <h3>Tenant Resources & Rights</h3>
                    <ul>
                      {currentView.tenant_resources?.map((r: string, i: number) => (
                        <li key={i}>📞 {r}</li>
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
                    Opportunity Score: {currentView.opportunity_score?.toFixed(0)}/100
                  </div>
                  
                  <div className={styles.riskDisclosure}>
                    <strong>⚠️ Community Impact Disclosure:</strong>
                    <p>{currentView.community_impact_acknowledgment}</p>
                  </div>
                  
                  <div className={styles.section}>
                    <h3>Market Signals</h3>
                    {currentView.market_signals && (
                      <ul>
                        <li>{currentView.market_signals.early_stage_capital_inflow ? '✓' : '✗'} Early stage capital inflows</li>
                        <li>{currentView.market_signals.rent_appreciation_trajectory ? '✓' : '✗'} Rent appreciation trajectory</li>
                      </ul>
                    )}
                  </div>

                  <div className={styles.section}>
                    <h3>Recommended Actions</h3>
                    <ul>
                      {currentView.recommendations?.map((r: string, i: number) => (
                        <li key={i}>→ {r}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {selectedView === 'city' && (
                <div>
                  <div className={styles.section}>
                    <h3>Policy Intervention Window</h3>
                    <p className={styles.urgent}><strong>{currentView.policy_intervention_window}</strong></p>
                  </div>
                  
                  <div className={styles.section}>
                    <h3>Early Warning Signals</h3>
                    <ul>
                      {currentView.early_warning_signals?.map((signal: string, i: number) => (
                        <li key={i}>⚠️ {signal}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className={styles.section}>
                    <h3>Recommended Policy Tools</h3>
                    <ul>
                      {currentView.tools?.map((tool: string, i: number) => (
                        <li key={i}>🛠️ {tool}</li>
                      ))}
                    </ul>
                  </div>

                  <div className={styles.section}>
                    <h3>Recommended Actions</h3>
                    <ul>
                      {currentView.recommendations?.map((r: string, i: number) => (
                        <li key={i}>→ {r}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {error && <div className={styles.error}>❌ {error}</div>}
      {loading && <div className={styles.loading}>⏳ Loading...</div>}
    </div>
  );
}
