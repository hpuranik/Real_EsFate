'use client';

import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import styles from './page_phase5.module.css';
import pittsburghTracts from '../data/pittsburgh-tracts.json';
import pittsburghBlockGroups from '../data/pittsburgh-block-groups.json';
import InvestmentSimulator from './InvestmentSimulator';

type Resolution = 'neighborhood' | 'block-group';

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
  const hoverPopup = useRef<mapboxgl.Popup | null>(null);
  const hoveredIdRef = useRef<string | null>(null);

  const [selectedTract, setSelectedTract] = useState<ScoreData | null>(null);
  const [selectedTractName, setSelectedTractName] = useState<string | null>(null);
  const [selectedBlockGroupId, setSelectedBlockGroupId] = useState<string | null>(null);
  const [selectedView, setSelectedView] = useState<ViewKey>('researcher');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scoresLoaded, setScoresLoaded] = useState(false);
  const [backendUnreachable, setBackendUnreachable] = useState(false);
  const [resolution, setResolution] = useState<Resolution>('neighborhood');
  const resolutionRef = useRef<Resolution>('neighborhood');

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
      // Bounding box of the 9 real neighborhood polygons below (computed
      // from the actual geometry, not eyeballed) -- fitBounds frames them
      // properly regardless of how the underlying shapes change later.
      bounds: [
        [-80.0181, 40.3982], // southwest
        [-79.9124, 40.4900], // northeast
      ],
      fitBoundsOptions: { padding: 60 },
    });

    hoverPopup.current = new mapboxgl.Popup({
      closeButton: false,
      closeOnClick: false,
      className: styles.hoverPopup,
      offset: 8,
    });

    map.current.on('load', async () => {
      if (!map.current) return;

      // Start with neighborhood boundaries (no scores yet, so render neutral
      // gray immediately rather than waiting on the network for first paint).
      // promoteId lets Mapbox track hover state per-tract via feature-state.
      map.current.addSource('tracts', {
        type: 'geojson',
        data: pittsburghTracts as any,
        promoteId: 'tract_id',
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
          'fill-opacity': [
            'case',
            ['boolean', ['feature-state', 'hover'], false],
            0.85,
            0.65,
          ],
          'fill-opacity-transition': { duration: 150 },
        },
      });

      map.current.addLayer({
        id: 'tracts-outline',
        type: 'line',
        source: 'tracts',
        paint: {
          'line-color': [
            'case',
            ['boolean', ['feature-state', 'hover'], false],
            '#111',
            '#000',
          ],
          'line-width': [
            'case',
            ['boolean', ['feature-state', 'hover'], false],
            2.5,
            1,
          ],
        },
      });

      // Name labels so people know what they're looking at before they even
      // click. At block-group resolution this still shows the parent
      // neighborhood name (each block group inherits it), which reads better
      // than 12-digit GEOIDs plastered across a dense map.
      map.current.addLayer({
        id: 'tracts-labels',
        type: 'symbol',
        source: 'tracts',
        layout: {
          'text-field': ['get', 'name'],
          'text-size': 12,
          'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
          'text-allow-overlap': false,
        },
        paint: {
          'text-color': '#1a1a1a',
          'text-halo-color': '#ffffff',
          'text-halo-width': 1.4,
        },
      });

      map.current.on('mouseenter', 'tracts-fill', () => {
        if (map.current) map.current.getCanvas().style.cursor = 'pointer';
      });

      map.current.on('mousemove', 'tracts-fill', (e) => {
        if (!map.current) return;
        const feature = e.features?.[0];
        if (!feature) return;

        const tractId = feature.properties?.tract_id;
        const name = feature.properties?.name ?? tractId;

        if (hoveredIdRef.current !== null && hoveredIdRef.current !== tractId) {
          map.current.setFeatureState({ source: 'tracts', id: hoveredIdRef.current }, { hover: false });
        }
        if (tractId != null) {
          map.current.setFeatureState({ source: 'tracts', id: tractId }, { hover: true });
          hoveredIdRef.current = tractId;
        }

        hoverPopup.current
          ?.setLngLat(e.lngLat)
          .setHTML(`<strong>${name}</strong>`)
          .addTo(map.current);
      });

      map.current.on('mouseleave', 'tracts-fill', () => {
        if (!map.current) return;
        map.current.getCanvas().style.cursor = '';
        if (hoveredIdRef.current !== null) {
          map.current.setFeatureState({ source: 'tracts', id: hoveredIdRef.current }, { hover: false });
          hoveredIdRef.current = null;
        }
        hoverPopup.current?.remove();
      });

      map.current.on('click', 'tracts-fill', async (e) => {
        const feature = e.features?.[0];
        const clickedId = feature?.properties?.tract_id;
        const clickedName = feature?.properties?.name ?? null;

        if (!clickedId) {
          setError('No tract ID found');
          return;
        }

        // At block-group resolution, the clicked feature's tract_id is a
        // 12-digit block-group GEOID, which has no /tract-score entry of its
        // own (the rich researcher/resident/investor/city views only exist
        // at the neighborhood level -- see backend/models/block_group_scoring.py).
        // Fetch the PARENT neighborhood's full views instead, and surface
        // the block group's own id/score alongside it so it's clear which
        // resolution the detail panel is actually describing.
        const isBlockGroup = resolutionRef.current === 'block-group';
        const parentTractId = isBlockGroup ? feature?.properties?.parent_tract : null;

        setSelectedTractName(clickedName);
        setSelectedBlockGroupId(isBlockGroup ? clickedId : null);
        setLoading(true);
        setError(null);

        const fetchTractId = isBlockGroup ? parentTractId : clickedId;

        try {
          const res = await fetch(`${API_URL}/tract-score/${fetchTractId}`);

          if (!res.ok) {
            throw new Error(`Backend returned ${res.status}`);
          }

          const data = await res.json();
          setSelectedTract(data);
        } catch (err: any) {
          setError(`Can't reach the backend at ${API_URL} (${err.message}).`);
          setBackendUnreachable(true);
        } finally {
          setLoading(false);
        }
      });

      await loadScores('neighborhood');
    });

    return () => {
      hoverPopup.current?.remove();
      map.current?.remove();
      map.current = null;
    };
  }, [MAPBOX_TOKEN]);

  /** Swaps the map's source data + score coloring between neighborhood (9
   * real polygons) and block-group (76 real Census block groups) resolution.
   * Both are real geography -- this is a resolution change, not mock-vs-real. */
  async function loadScores(res: Resolution) {
    if (!map.current) return;
    resolutionRef.current = res;

    const geojson = res === 'neighborhood' ? pittsburghTracts : pittsburghBlockGroups;
    const endpoint = res === 'neighborhood' ? '/all-tracts' : '/block-groups';

    // Swap geometry immediately (no network needed), gray until scores load.
    (map.current.getSource('tracts') as mapboxgl.GeoJSONSource)?.setData(geojson as any);
    setScoresLoaded(false);

    try {
      const apiRes = await fetch(`${API_URL}${endpoint}`);
      if (!apiRes.ok) throw new Error(`Backend returned ${apiRes.status}`);
      const data = await apiRes.json();

      const scoreById: Record<string, number> = {};
      if (res === 'neighborhood') {
        for (const t of data.tracts ?? []) {
          if (t?.tract_id != null && typeof t.displacement_risk_score === 'number') {
            scoreById[t.tract_id] = t.displacement_risk_score;
          }
        }
      } else {
        for (const bg of data.block_groups ?? []) {
          if (bg?.geoid != null && typeof bg.displacement_risk_score === 'number') {
            scoreById[bg.geoid] = bg.displacement_risk_score;
          }
        }
      }

      const merged = {
        ...(geojson as any),
        features: (geojson as any).features.map((f: any) => ({
          ...f,
          properties: {
            ...f.properties,
            score: scoreById[f.properties.tract_id] ?? null,
          },
        })),
      };

      (map.current.getSource('tracts') as mapboxgl.GeoJSONSource)?.setData(merged);
      setScoresLoaded(true);
      setBackendUnreachable(false);
      setError(null);
    } catch (err: any) {
      setError(
        `Can't reach the backend at ${API_URL} (${err.message}). ` +
        `Is it running? Check NEXT_PUBLIC_API_URL in .env.local.`
      );
      setBackendUnreachable(true);
    }
  }

  function handleResolutionChange(res: Resolution) {
    setResolution(res);
    loadScores(res);
  }

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
      {backendUnreachable && (
        <div className={styles.bannerError}>
          ⚠ Can't reach the backend at {API_URL}. The map will stay gray and clicks won't
          work until it's running. Start it with <code>uvicorn main:app</code> in the
          backend folder, or check <code>NEXT_PUBLIC_API_URL</code> in <code>.env.local</code>.
        </div>
      )}
      <div ref={mapContainer} className={styles.map} />

      <div className={styles.resolutionToggle}>
        <button
          className={`${styles.resBtn} ${resolution === 'neighborhood' ? styles.resActive : ''}`}
          onClick={() => handleResolutionChange('neighborhood')}
        >
          Neighborhoods (9)
        </button>
        <button
          className={`${styles.resBtn} ${resolution === 'block-group' ? styles.resActive : ''}`}
          onClick={() => handleResolutionChange('block-group')}
        >
          Block Groups (76)
        </button>
      </div>

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

          <h2>{selectedTractName ?? selectedTract.tract_id}</h2>
          <p className={styles.tractIdSubtitle}>Census Tract {selectedTract.tract_id}</p>
          {selectedBlockGroupId && (
            <p className={styles.blockGroupNote}>
              Block group {selectedBlockGroupId} -- detail below reflects the parent
              neighborhood's full data (block-group-level signals aren't independently
              measured yet, see /block-groups in the API for how its map color is derived).
            </p>
          )}

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
                <InvestmentSimulator tractName={selectedTractName ?? selectedTract.tract_id} />
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
