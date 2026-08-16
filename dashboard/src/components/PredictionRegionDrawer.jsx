import React, { useEffect } from "react";
import { X, MapPin, Activity, Brain, ShieldCheck, Info, Globe2, Compass } from "lucide-react";
import InfoTooltip from "./InfoTooltip";
import { getActivityLevelBadge } from "./PredictionRanking";
import { getGeographicContext } from "../utils/geoUtils";

export default function PredictionRegionDrawer({ isOpen, onClose, data }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden"; // Prevent background scroll on mobile
    }
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "auto";
    };
  }, [isOpen, onClose]);

  if (!isOpen || !data) return null;

  const regionId = data.region_id || "Profile";
  const probPct = data.calibrated_probability_percent ?? (data.calibrated_probability * 100) ?? 0;
  const formattedProb = Number(probPct).toFixed(1);
  const activityLevel = data.activity_level || (probPct >= 70 ? "VERY HIGH" : probPct >= 50 ? "HIGH" : probPct >= 30 ? "MODERATE" : probPct >= 15 ? "LOW" : "VERY LOW");

  const month = data.month || 1;
  const year = data.year || 2025;

  // Geographic Context Engine
  const geoCtx = getGeographicContext(data.grid_lat, data.grid_lon, regionId);

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside className="region-drawer-panel mobile-bottom-sheet" onClick={(e) => e.stopPropagation()}>
        {/* MOBILE DRAG HANDLE */}
        <div className="mobile-sheet-drag-handle" />

        {/* HEADER */}
        <div className="drawer-header">
          <div>
            <div className="drawer-eyebrow">
              <Brain size={12} />
              <span>PREDICTION INTELLIGENCE PROFILE</span>
            </div>
            <h2 className="drawer-title">{regionId}</h2>
            <div className="drawer-geo-subtitle">
              <Globe2 size={13} />
              <span>{geoCtx.geoLabel}</span>
            </div>
          </div>

          <button className="drawer-close" onClick={onClose} aria-label="Close detail panel">
            <X size={18} />
          </button>
        </div>

        {/* BODY CONTENT */}
        <div className="drawer-body">
          {/* LIKELIHOOD BANNER */}
          <div className="drawer-cluster-banner" style={{ background: "var(--accent-glow)", borderColor: "var(--accent)" }}>
            <div className="banner-cluster-icon" style={{ backgroundColor: "var(--accent)", color: "#ffffff" }}>
              <Activity size={20} />
            </div>
            <div>
              <div className="banner-lbl">
                NEXT-MONTH EVENT LIKELIHOOD{" "}
                <InfoTooltip term="Event Probability" customTitle="Calibrated Event Probability">
                  The statistically estimated likelihood of at least one EONET hazard event observation occurring in this region during the target month.
                </InfoTooltip>
              </div>
              <strong className="banner-val" style={{ color: probPct >= 50 ? "var(--warning)" : "var(--accent)" }}>
                {formattedProb}% Est. Probability
              </strong>
            </div>
          </div>

          {/* GEOGRAPHIC CONTEXT CARD */}
          <div className="drawer-section">
            <h3 className="section-title-sm">
              <Compass size={14} /> GEOGRAPHIC CONTEXT
            </h3>
            <div className="model-explanation-card" style={{ background: "var(--surface-elevated)" }}>
              <div className="drawer-metrics-grid" style={{ marginBottom: "10px" }}>
                <div className="drawer-metric-card">
                  <span className="metric-lbl">CONTINENT</span>
                  <strong className="metric-val">{geoCtx.continent}</strong>
                </div>

                <div className="drawer-metric-card">
                  <span className="metric-lbl">SUB-REGION</span>
                  <strong className="metric-val accent">{geoCtx.subregion}</strong>
                </div>

                <div className="drawer-metric-card" style={{ gridColumn: "span 2" }}>
                  <span className="metric-lbl">APPROXIMATE COORDINATES</span>
                  <strong className="metric-val" style={{ fontSize: "13px" }}>{geoCtx.formattedCoords}</strong>
                </div>
              </div>

              {geoCtx.nearbyCountries && geoCtx.nearbyCountries.length > 0 && (
                <div style={{ marginTop: "10px" }}>
                  <span className="metric-lbl" style={{ display: "block", marginBottom: "6px" }}>NEARBY COUNTRIES / REGIONS</span>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                    {geoCtx.nearbyCountries.map((c, i) => (
                      <span key={i} className="popup-cluster-pill" style={{ background: "var(--bg-secondary)", color: "var(--text-primary)" }}>
                        {c}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* OVERVIEW METRICS */}
          <div className="drawer-section">
            <h3 className="section-title-sm">
              <Activity size={14} /> PREDICTION METRICS
            </h3>

            <div className="drawer-metrics-grid">
              <div className="drawer-metric-card">
                <span className="metric-lbl">ACTIVITY BAND</span>
                <div style={{ marginTop: "4px" }}>
                  {getActivityLevelBadge(activityLevel, probPct)}
                </div>
                <span className="metric-sub">Calibrated scale</span>
              </div>

              <div className="drawer-metric-card">
                <span className="metric-lbl">PREDICTION PERIOD</span>
                <strong className="metric-val">Month {month} ({year})</strong>
                <span className="metric-sub">Target period</span>
              </div>
            </div>
          </div>

          {/* WHAT DOES THIS MEAN */}
          <div className="drawer-section">
            <h3 className="section-title-sm">
              <Info size={14} /> WHAT DOES THIS MEAN?
            </h3>
            <div className="model-explanation-card">
              <p>
                The calibrated model estimates a <strong>{formattedProb}% probability</strong> of at least one EONET event observation in {regionId} ({geoCtx.geoLabel}) during Month {month}.
              </p>
              <p style={{ marginTop: "8px", fontSize: "11px", color: "var(--text-muted)" }}>
                This is a statistical estimate based on historical EONET observations and recent regional patterns. It does not mean that a natural disaster will definitely occur.
              </p>
            </div>
          </div>

          {/* SAFETY NOTICE */}
          <div className="drawer-safety-notice">
            <ShieldCheck size={14} className="safety-icon" />
            <p>
              <strong>Statistical Model Notice:</strong> Prediction outputs are for research analysis only and are not official emergency warnings or disaster forecasts.
            </p>
          </div>
        </div>
      </aside>
    </div>
  );
}
