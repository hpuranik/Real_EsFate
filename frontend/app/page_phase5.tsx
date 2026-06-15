'use client';

import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import styles from './page_phase5.module.css';
import pittsburghTracts from '../data/pittsburgh-tracts.json';

interface ScoreData {
  tract_id: string;
  displacement_risk_score: number;
  views: any;
}

export default function Home() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  const [selectedTract, setSelectedTract] = useState<ScoreData | null>(null);
  const [selectedView, setSelectedView] = useState<'researcher' | 'resident' | 'investor' | 'city'>('researcher');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

    map.current.on('load', () => {
      if (!map.current) return;

      // Add tracts
      map.current.addSource('tracts', {
        type: 'geojson',
        data: pittsburghTracts as any,
      });

      map.current.addLayer({
        id: 'tracts-fill',
        type: 'fill',
        source: 'tracts',
        paint: {
          'fill-color': '#888',
          'fill-opacity': 0.6,
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
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, [MAPBOX_TOKEN]);

  const currentView = selectedTract?.views?.[selectedView];

  return (
    <div className={styles.container}>
      <div ref={mapContainer} className={styles.map} />

      {/* SIMPLE DEBUG PANEL */}
      {error && (
        <div className={styles.error}>
          {error}
        </div>
      )}

      {loading && (
        <div className={styles.loading}>
          Loading tract data...
        </div>
      )}

      {selectedTract && currentView && (
        <div className={styles.panel}>
          <h2>{selectedTract.tract_id}</h2>

          <div className={styles.scoreCard}>
            <div className={styles.scoreValue}>
              {currentView.displacement_risk_score ?? 'N/A'}
            </div>
            <div>Risk Score</div>
          </div>

          <p>
            <strong>Trajectory:</strong> {currentView.trajectory ?? 'N/A'}
          </p>
        </div>
      )}
    </div>
  );
}
