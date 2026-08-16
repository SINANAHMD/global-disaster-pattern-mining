import React, { useState, useMemo, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Tooltip,
  useMap,
} from "react-leaflet";
import { RotateCcw, Maximize2, Brain, Globe2 } from "lucide-react";
import "leaflet/dist/leaflet.css";
import { getGeographicContext } from "../utils/geoUtils";

export function getProbabilityColor(probPct) {
  if (probPct >= 70) return "#ef4444"; // Very High (Coral/Red)
  if (probPct >= 50) return "#f59e0b"; // High (Amber)
  if (probPct >= 30) return "#eab308"; // Moderate (Gold)
  if (probPct >= 15) return "#14b8a6"; // Low (Teal)
  return "#475569"; // Very Low (Muted Slate)
}

function MapController({ resetTrigger, fitTrigger, bounds, targetBounds }) {
  const map = useMap();

  useEffect(() => {
    if (resetTrigger > 0) {
      map.setView([20, 0], 2, { animate: true });
    }
  }, [resetTrigger, map]);

  useEffect(() => {
    if (fitTrigger > 0 && bounds && bounds.length > 0) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 7, animate: true });
    }
  }, [fitTrigger, bounds, map]);

  useEffect(() => {
    if (targetBounds) {
      map.fitBounds(targetBounds, { padding: [50, 50], maxZoom: 6, animate: true });
    }
  }, [targetBounds, map]);

  return null;
}

export default function PredictionMap({ predictions = [], onSelectRegion }) {
  const [activeBand, setActiveBand] = useState(null);
  const [resetTrigger, setResetTrigger] = useState(0);
  const [fitTrigger, setFitTrigger] = useState(0);
  const [targetBounds, setTargetBounds] = useState(null);

  // Filter valid grid coordinates
  const validPredictions = useMemo(() => {
    return predictions.filter((p) => {
      const lat = p.grid_lat ?? p.latitude;
      const lng = p.grid_lon ?? p.longitude;
      return (
        typeof lat === "number" &&
        !isNaN(lat) &&
        typeof lng === "number" &&
        !isNaN(lng) &&
        lat >= -90 &&
        lat <= 90 &&
        lng >= -180 &&
        lng <= 180
      );
    });
  }, [predictions]);

  // Compute map bounds
  const mapBounds = useMemo(() => {
    return validPredictions.map((p) => [
      p.grid_lat ?? p.latitude,
      p.grid_lon ?? p.longitude,
    ]);
  }, [validPredictions]);

  const handleReset = () => {
    setActiveBand(null);
    setTargetBounds(null);
    setResetTrigger((prev) => prev + 1);
  };

  const handleFit = () => {
    setFitTrigger((prev) => prev + 1);
  };

  return (
    <div className="panel global-map-panel">
      <div className="map-view-header" style={{ paddingBottom: "12px" }}>
        <div className="view-switcher-title">
          <span className="panel-kicker">GEOSPATIAL PREDICTION MAP</span>
          <div className="view-header-main">
            <h2>Next-Month Event Likelihood Map</h2>
          </div>
          <p className="view-subtitle">
            Spatial distribution of regional prediction grid points colored by calibrated event likelihood.
          </p>
        </div>
      </div>

      <div className="map-wrapper">
        <MapContainer
          center={[20, 0]}
          zoom={2}
          minZoom={2}
          maxZoom={12}
          scrollWheelZoom={true}
          className="leaflet-map-canvas"
          zoomControl={false}
        >
          <MapController
            resetTrigger={resetTrigger}
            fitTrigger={fitTrigger}
            bounds={mapBounds}
            targetBounds={targetBounds}
          />

          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            subdomains="abcd"
            maxZoom={19}
          />

          {validPredictions.map((item, idx) => {
            const lat = item.grid_lat ?? item.latitude;
            const lng = item.grid_lon ?? item.longitude;
            const probPct = item.calibrated_probability_percent ?? (item.calibrated_probability * 100) ?? 0;
            const color = getProbabilityColor(probPct);
            const level = item.activity_level || (probPct >= 70 ? "VERY HIGH" : probPct >= 50 ? "HIGH" : probPct >= 30 ? "MODERATE" : probPct >= 15 ? "LOW" : "VERY LOW");

            const isMatched = activeBand === null || activeBand === level;
            if (!isMatched) return null;

            const radius = Math.max(4, Math.min(12, 4 + (probPct / 100) * 8));
            const geoCtx = getGeographicContext(lat, lng, item.region_id);

            return (
              <CircleMarker
                key={item.region_id + "-" + idx}
                center={[lat, lng]}
                radius={radius}
                pathOptions={{
                  fillColor: color,
                  fillOpacity: 0.8,
                  color: "#ffffff",
                  weight: 1,
                }}
                eventHandlers={{
                  click: () => {
                    if (onSelectRegion) onSelectRegion(item);
                  },
                }}
              >
                <Tooltip direction="top" offset={[0, -radius]} opacity={0.95}>
                  <div className="map-tooltip">
                    <strong>{item.region_id}</strong>
                    <div style={{ fontSize: "11px", color: "var(--accent)", fontWeight: 600, margin: "2px 0" }}>
                      {geoCtx.geoLabel}
                    </div>
                    <div style={{ color: color, fontWeight: 700 }}>
                      {Number(probPct).toFixed(1)}% Est. Probability ({level})
                    </div>
                    <small>{geoCtx.formattedCoords} · Month {item.month} ({item.year})</small>
                  </div>
                </Tooltip>
              </CircleMarker>
            );
          })}
        </MapContainer>

        {/* FLOATING CONTROLS */}
        <div className="map-floating-controls">
          <button className="map-control-btn" onClick={handleReset} title="Reset View">
            <RotateCcw size={14} />
            <span>Reset View</span>
          </button>
          <button className="map-control-btn" onClick={handleFit} title="Fit Regions">
            <Maximize2 size={14} />
            <span>Fit Regions</span>
          </button>
        </div>

        {/* FLOATING LEGEND */}
        <div className="map-legend-card">
          <div className="legend-header">
            <div className="legend-title">
              <Brain size={13} />
              <span>PROBABILITY BANDS</span>
            </div>
            {activeBand !== null && (
              <button className="legend-clear-btn" onClick={() => setActiveBand(null)}>
                Clear
              </button>
            )}
          </div>

          <div className="legend-items" style={{ gridTemplateColumns: "1fr 1fr" }}>
            {[
              { level: "VERY HIGH", label: "Very High (70%+)", color: "#ef4444" },
              { level: "HIGH", label: "High (50–69%)", color: "#f59e0b" },
              { level: "MODERATE", label: "Moderate (30–49%)", color: "#eab308" },
              { level: "LOW", label: "Low (15–29%)", color: "#14b8a6" },
              { level: "VERY LOW", label: "Very Low (<15%)", color: "#475569" },
            ].map((band) => (
              <button
                key={band.level}
                className={`legend-item ${activeBand === band.level ? "selected" : ""}`}
                onClick={() => setActiveBand(activeBand === band.level ? null : band.level)}
              >
                <span className="legend-dot" style={{ backgroundColor: band.color }} />
                <span className="legend-label" style={{ fontSize: "9px" }}>{band.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
