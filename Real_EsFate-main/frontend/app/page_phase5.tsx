'use client';

import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import styles from './page_phase5.module.css';
import pittsburghTracts from '../data/pittsburgh-tracts.json';

type ViewKey = 'researcher' | 'resident' | 'investor' | 'city';

interface ScoreData {
  tract_id: string;
  displacement_risk_score: number;
  views: Record<ViewKey, any>;
}

const VIEW_LABELS: Record<ViewKey, string> = {
  researcher: 'Researcher',
  resident: 'Resident',
  investor: 'Investor',
  city: 'City Planner',
};

export default function Home() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  const [selectedTract, setSelectedTract] = useState<ScoreData | null>(null);
  const [selectedView, setSelectedView] = useState<ViewKey>('researcher');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scoresLoaded, setScoresLoaded] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

  useEffect(() => {
    if (!MAPBOX_TOKEN) {
      setError('Missing Mapbox token (.env.local)');
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

    map.current.on('load', async () => {
      if (!map.current) return;

      // Start with the base tract boundaries (no scores yet, so render neutral
      // gray immediately rather than waiting on the network for first paint).
      map.current.addSource('tracts', {
        type: 'geojson',
        data: pittsburghTracts as any,
      });

      map.current.addLayer({
        id: 'tracts-fill',
        type: 'fill',
        source: 'tracts',
        paint: {
          // Step expression: gray = no score yet, then green/yellow/orange/red
          // bands matching the documented 0-40/40-60/60-80/80-100 risk scale.
          'fill-color': [
            'step',
            ['coalesce', ['get', 'score'], -1],
            '#9ca3af', // no data
            0, '#2ecc71', // low (0-40)
            40, '#f1c40f', // medium (40-60)
            60, '#e67e22', // high (60-80)
            80, '#e74c3c', // critical (80-100)
          ],
          'fill-opacity': 0.65,
        },
      });

      map.current.addLayer({
        id: 'tracts-outline',
        type: 'line',
        source: 'tracts',
        paint: {
          'line-color': '#000',
          'line-width': 1,
        },
      });

      map.current.on('mouseenter', 'tracts-fill', () => {
        if (map.current) map.current.getCanvas().style.cursor = 'pointer';
      });
      map.current.on('mouseleave', 'tracts-fill', () => {
        if (map.current) map.current.getCanvas().style.cursor = '';
      });

      map.current.on('click', 'tracts-fill', async (e) => {
        const feature = e.features?.[0];
        const tractId = feature?.properties?.tract_id;

        if (!tractId) {
          setError('No tract ID found');
          return;
        }

        setLoading(true);
        setError(null);

        try {
          const res = await fetch(`${API_URL}/tract-score/${tractId}`);

          if (!res.ok) {
            throw new Error(`Backend error ${res.status}`);
          }

          const data = await res.json();
          setSelectedTract(data);
        } catch (err: any) {
          setError(`Failed to load tract: ${err.message}`);
        } finally {
          setLoading(false);
        }
      });

      // Fetch all-tract scores and color the map. Done after the layers exist
      // so first paint is instant and this just upgrades the fill once data
      // arrives.
      try {
        const res = await fetch(`${API_URL}/all-tracts`);
        if (!res.ok) throw new Error(`Backend error ${res.status}`);
        const data = await res.json();

        const scoreByTract: Record<string, number> = {};
        for (const t of data.tracts ?? []) {
          if (t?.tract_id != null && typeof t.displacement_risk_score === 'number') {
            scoreByTract[t.tract_id] = t.displacement_risk_score;
          }
        }

        const merged = {
          ...(pittsburghTracts as any),
          features: (pittsburghTracts as any).features.map((f: any) => ({
            ...f,
            properties: {
              ...f.properties,
              score: scoreByTract[f.properties.tract_id] ?? null,
            },
          })),
        };

        (map.current.getSource('tracts') as mapboxgl.GeoJSONSource)?.setData(merged);
        setScoresLoaded(true);
      } catch (err: any) {
        setError(`Failed to load tract scores: ${err.message}`);
      }
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, [MAPBOX_TOKEN]);

  const currentView = selectedTract?.views?.[selectedView];

  const headline = (() => {
    if (!currentView) return null;
    switch (selectedView) {
      case 'researcher':
        return { value: currentView.displacement_risk_score, label: 'Displacement Risk Score' };
      case 'resident':
        return { value: currentView.displacement_risk, label: currentView.risk_level ?? 'Displacement Risk' };
      case 'investor':
        return { value: currentView.opportunity_score, label: 'Investment Opportunity Score' };
      case 'city':
        return { value: currentView.displacement_risk, label: 'Displacement Risk' };
      default:
        return null;
    }
  })();

  return (
    <div className={styles.container}>
      <div ref={mapContainer} className={styles.map} />

      {!selectedTract && (
        <div className={styles.legend}>
          <div className={styles.legendTitle}>Displacement Risk</div>
          <div className={styles.legendRow}><span className={styles.swatchGreen} /> Low (0-40)</div>
          <div className={styles.legendRow}><span className={styles.swatchYellow} /> Medium (40-60)</div>
          <div className={styles.legendRow}><span className={styles.swatchOrange} /> High (60-80)</div>
          <div className={styles.legendRow}><span className={styles.swatchRed} /> Critical (80-100)</div>
          {!scoresLoaded && <div className={styles.legendHint}>Loading scores...</div>}
          {scoresLoaded && <div className={styles.legendHint}>Click a tract to see details</div>}
        </div>
      )}

      {error && <div className={styles.error}>{error}</div>}
      {loading && <div className={styles.loading}>Loading tract data...</div>}

      {selectedTract && currentView && (
        <div className={styles.panel}>
          <button
            className={styles.closeBtn}
            onClick={() => setSelectedTract(null)}
            aria-label="Close panel"
          >
            &times;
          </button>

          <h2>{selectedTract.tract_id}</h2>

          <div className={styles.viewSelector}>
            {(Object.keys(VIEW_LABELS) as ViewKey[]).map((v) => (
              <button
                key={v}
                className={`${styles.viewBtn} ${selectedView === v ? styles.active : ''}`}
                onClick={() => setSelectedView(v)}
              >
                {VIEW_LABELS[v]}
              </button>
            ))}
          </div>

          <div className={styles.content}>
            {headline && (
              <div className={styles.scoreCard}>
                <div className={styles.scoreValue}>
                  {headline.value != null ? Math.round(headline.value) : 'N/A'}
                </div>
                <div className={styles.scoreLabel}>{headline.label}</div>
              </div>
            )}

            {/* RESEARCHER VIEW */}
            {selectedView === 'researcher' && (
              <>
                <p className={styles.trajectory}><strong>Trajectory:</strong> {currentView.trajectory ?? 'N/A'}</p>
                <div className={styles.section}>
                  <h3>Confidence Intervals</h3>
                  <p>1yr: {currentView.confidence_intervals?.['1_year']} &nbsp;|&nbsp;
                     3yr: {currentView.confidence_intervals?.['3_year']} &nbsp;|&nbsp;
                     5yr: {currentView.confidence_intervals?.['5_year']}</p>
                </div>
                <div className={styles.section}>
                  <h3>Tier 1 Signals</h3>
                  <p>{(currentView.methodology?.tier1_signals ?? []).join(', ')}</p>
                </div>
                <div className={styles.section}>
                  <h3>Citations</h3>
                  <ul>
                    {(currentView.citations ?? []).map((c: any, i: number) => (
                      <li key={i}>{(c.authors ?? []).join(' ')} ({c.year}) - {c.source}</li>
                    ))}
                  </ul>
                </div>
              </>
            )}

            {/* RESIDENT VIEW */}
            {selectedView === 'resident' && (
              <>
                <div className={styles.riskBadge}>{currentView.risk_level}</div>
                <p className={styles.trajectory}>{currentView.what_it_means}</p>
                <div className={styles.section}>
                  <h3>Tenant Resources</h3>
                  <ul>
                    {(currentView.tenant_resources ?? []).map((r: string, i: number) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
                <div className={styles.section}>
                  <h3>Recommendations</h3>
                  <ul>
                    {(currentView.recommendations ?? []).map((r: string, i: number) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              </>
            )}

            {/* INVESTOR VIEW */}
            {selectedView === 'investor' && (
              <>
                <div className={styles.riskDisclosure}>
                  <strong>Displacement Risk Disclosure</strong>
                  <p>{currentView.displacement_risk_disclosure}/100 — required transparency metric.</p>
                </div>
                <div className={styles.section}>
                  <h3>Community Impact</h3>
                  <p>{currentView.community_impact_acknowledgment}</p>
                </div>
                <div className={styles.section}>
                  <h3>Recommendations</h3>
                  <ul>
                    {(currentView.recommendations ?? []).map((r: string, i: number) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              </>
            )}

            {/* CITY VIEW */}
            {selectedView === 'city' && (
              <>
                <p className={styles.urgent}>{currentView.policy_intervention_window}</p>
                <div className={styles.section}>
                  <h3>Early Warning Signals</h3>
                  <ul>
                    {(currentView.early_warning_signals ?? []).map((s: string, i: number) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
                <div className={styles.section}>
                  <h3>Recommended Tools</h3>
                  <ul>
                    {(currentView.tools ?? []).map((t: string, i: number) => <li key={i}>{t}</li>)}
                  </ul>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
