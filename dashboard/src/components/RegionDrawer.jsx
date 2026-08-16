import React, { useEffect } from "react";
import { X, MapPin, Activity, Layers, Info, ShieldCheck } from "lucide-react";
import { getClusterColor } from "./GlobalMap";
import InfoTooltip from "./InfoTooltip";

export default function RegionDrawer({ isOpen, onClose, data }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !data) return null;

  const isCountry = data.country !== undefined;
  const name = isCountry ? data.country : `Region ${data.region_id || "Profile"}`;
  const totalEvents = data.total_events || data.events || 0;
  const recentEvents = data.recent_events ?? data.events_2023_2025 ?? 0;
  const cluster = data.cluster ?? data.dominant_cluster ?? 0;
  const clusterColor = getClusterColor(cluster);
  const dominantCategory = data.dominant_category || data.dominant_type || "Wildfires / Storms";
  const dominantShare = data.dominant_category_proportion;
  const activeYears = data.active_years ?? "2015–2025";
  const eventsPerYear = data.events_per_active_year != null ? Number(data.events_per_active_year).toFixed(2) : "-";
  const lat = data.region_latitude ?? data.latitude;
  // FIX: Line below previously threw ReferenceError: region_longitude is not defined
  const lng = data.region_longitude ?? data.longitude;

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside className="region-drawer-panel" onClick={(e) => e.stopPropagation()}>
        {/* HEADER */}
        <div className="drawer-header">
          <div>
            <div className="drawer-eyebrow">
              <MapPin size={12} />
              <span>{isCountry ? "COUNTRY INTELLIGENCE PROFILE" : "REGIONAL CLUSTER PROFILE"}</span>
            </div>
            <h2 className="drawer-title">{name}</h2>
          </div>

          <button className="drawer-close" onClick={onClose} aria-label="Close detail panel">
            <X size={18} />
          </button>
        </div>

        {/* BODY CONTENT */}
        <div className="drawer-body">
          {/* CLUSTER BADGE SUMMARY */}
          <div className="drawer-cluster-banner" style={{ borderColor: `${clusterColor}44`, background: `${clusterColor}15` }}>
            <div className="banner-cluster-icon" style={{ backgroundColor: `${clusterColor}25`, color: clusterColor }}>
              <Layers size={20} />
            </div>
            <div>
              <div className="banner-lbl">
                K-MEANS CLUSTER ASSIGNMENT <InfoTooltip term="Cluster" inline />
              </div>
              <strong className="banner-val" style={{ color: clusterColor }}>
                Cluster {cluster} Profile
              </strong>
            </div>
          </div>

          {/* OVERVIEW METRICS */}
          <div className="drawer-section">
            <h3 className="section-title-sm">
              <Activity size={14} /> HISTORICAL EVENT METRICS
            </h3>

            <div className="drawer-metrics-grid">
              <div className="drawer-metric-card">
                <span className="metric-lbl">TOTAL EVENTS <InfoTooltip term="Event Observation" inline /></span>
                <strong className="metric-val">{Number(totalEvents).toLocaleString()}</strong>
                <span className="metric-sub">Recorded observations</span>
              </div>

              <div className="drawer-metric-card">
                <span className="metric-lbl">RECENT ACTIVITY <InfoTooltip term="Recent Activity" inline /></span>
                <strong className="metric-val">{Number(recentEvents).toLocaleString()}</strong>
                <span className="metric-sub">2023–2025 observations</span>
              </div>

              <div className="drawer-metric-card">
                <span className="metric-lbl">DOMINANT HAZARD <InfoTooltip term="Dominant Disaster Type" inline /></span>
                <strong className="metric-val accent">{dominantCategory}</strong>
                <span className="metric-sub">
                  {dominantShare != null ? `${dominantShare}% category share` : "Primary hazard driver"}
                </span>
              </div>

              <div className="drawer-metric-card">
                <span className="metric-lbl">ACTIVE DURATION</span>
                <strong className="metric-val">{activeYears}</strong>
                <span className="metric-sub">{eventsPerYear !== "-" ? `${eventsPerYear} events / year` : "Tracked period"}</span>
              </div>
            </div>
          </div>

          {/* COORDINATES IF AVAILABLE */}
          {lat != null && lng != null && (
            <div className="drawer-coords-box">
              <span><strong>Latitude:</strong> {Number(lat).toFixed(4)}</span>
              <span><strong>Longitude:</strong> {Number(lng).toFixed(4)}</span>
            </div>
          )}

          {/* MODEL EXPLANATION SECTION */}
          <div className="drawer-section">
            <h3 className="section-title-sm">
              <Info size={14} /> WHY THIS LOCATION IS IN CLUSTER {cluster}
            </h3>
            <div className="model-explanation-card">
              <p>
                This location is assigned to <strong>Cluster {cluster}</strong> because its numerical feature vector (total event count, yearly frequency, and hazard category distribution) shares maximum mathematical similarity with other regions in Cluster {cluster} compared to alternative cluster centers.
              </p>
            </div>
          </div>

          {/* SAFE LANGUAGE NOTICE */}
          <div className="drawer-safety-notice">
            <ShieldCheck size={14} className="safety-icon" />
            <p>
              <strong>Scientific Notice:</strong> This profile describes observed historical EONET event activity. Cluster numbers represent model-generated statistical groups, not official administrative danger or risk rankings.
            </p>
          </div>
        </div>
      </aside>
    </div>
  );
}
