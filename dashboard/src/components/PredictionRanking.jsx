import React, { useState } from "react";
import { ChevronRight, ArrowUpDown, ArrowUp, ArrowDown, MapPin } from "lucide-react";
import { getGeographicContext } from "../utils/geoUtils";

export function getActivityLevelBadge(level, probPct) {
  let color = "#475569";
  let bg = "rgba(71, 85, 105, 0.15)";
  const label = level || (probPct >= 70 ? "VERY HIGH" : probPct >= 50 ? "HIGH" : probPct >= 30 ? "MODERATE" : probPct >= 15 ? "LOW" : "VERY LOW");

  if (label === "VERY HIGH") {
    color = "#ef4444";
    bg = "rgba(239, 68, 68, 0.15)";
  } else if (label === "HIGH") {
    color = "#f59e0b";
    bg = "rgba(245, 158, 11, 0.15)";
  } else if (label === "MODERATE") {
    color = "#eab308";
    bg = "rgba(234, 179, 8, 0.15)";
  } else if (label === "LOW") {
    color = "#14b8a6";
    bg = "rgba(20, 184, 166, 0.15)";
  } else {
    color = "#6f7d89";
    bg = "rgba(111, 125, 137, 0.15)";
  }

  return (
    <span
      className="popup-cluster-pill"
      style={{
        backgroundColor: bg,
        color: color,
        borderColor: `${color}44`,
      }}
    >
      {label}
    </span>
  );
}

export default function PredictionRanking({ predictions = [], onSelectRegion }) {
  const [sortField, setSortField] = useState("probability"); // probability | region | month | level
  const [sortDir, setSortDir] = useState("desc");

  if (!predictions || predictions.length === 0) {
    return (
      <div className="panel" style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)" }}>
        No top predicted regions available.
      </div>
    );
  }

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDir("desc");
    }
  };

  const sortedPredictions = [...predictions].sort((a, b) => {
    const pA = a.calibrated_probability_percent ?? (a.calibrated_probability * 100) ?? 0;
    const pB = b.calibrated_probability_percent ?? (b.calibrated_probability * 100) ?? 0;

    let res = 0;
    if (sortField === "probability") {
      res = pA - pB;
    } else if (sortField === "region") {
      res = (a.region_id || "").localeCompare(b.region_id || "");
    } else if (sortField === "month") {
      res = (a.month || 0) - (b.month || 0);
    } else if (sortField === "level") {
      res = pA - pB;
    }

    return sortDir === "asc" ? res : -res;
  });

  const getSortIcon = (field) => {
    if (sortField !== field) return <ArrowUpDown size={12} style={{ opacity: 0.4 }} />;
    return sortDir === "asc" ? <ArrowUp size={12} style={{ color: "var(--accent)" }} /> : <ArrowDown size={12} style={{ color: "var(--accent)" }} />;
  };

  return (
    <div className="panel prediction-ranking-panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">HIGHEST ESTIMATED LIKELIHOOD</span>
          <h2>Top Predicted Spatial Regions</h2>
          <p>Regions with highest calculated next-month EONET event probabilities.</p>
        </div>
      </div>

      <div style={{ padding: "20px" }}>
        {/* DESKTOP TABLE VIEW */}
        <div className="desktop-table-container" style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--text-muted)", textAlign: "left" }}>
                <th style={{ padding: "12px 10px" }}>Rank</th>
                <th style={{ padding: "12px 10px", cursor: "pointer" }} onClick={() => handleSort("region")}>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span>Region ID</span>
                    {getSortIcon("region")}
                  </div>
                </th>
                <th style={{ padding: "12px 10px" }}>Geographic Area</th>
                <th style={{ padding: "12px 10px" }}>Coordinates</th>
                <th style={{ padding: "12px 10px", cursor: "pointer" }} onClick={() => handleSort("probability")}>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span>Est. Probability</span>
                    {getSortIcon("probability")}
                  </div>
                </th>
                <th style={{ padding: "12px 10px", cursor: "pointer" }} onClick={() => handleSort("level")}>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span>Activity Band</span>
                    {getSortIcon("level")}
                  </div>
                </th>
                <th style={{ padding: "12px 10px", cursor: "pointer" }} onClick={() => handleSort("month")}>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span>Month</span>
                    {getSortIcon("month")}
                  </div>
                </th>
                <th style={{ padding: "12px 10px" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {sortedPredictions.map((item, idx) => {
                const probPct = item.calibrated_probability_percent ?? (item.calibrated_probability * 100) ?? 0;
                const formattedProb = Number(probPct).toFixed(1);
                const geoCtx = getGeographicContext(item.grid_lat, item.grid_lon, item.region_id);

                return (
                  <tr
                    key={item.region_id + "-" + idx}
                    style={{ borderBottom: "1px solid var(--border-subtle)", cursor: "pointer" }}
                    onClick={() => onSelectRegion && onSelectRegion(item)}
                  >
                    <td style={{ padding: "12px 10px", fontWeight: 800, color: "var(--text-muted)" }}>
                      {String(idx + 1).padStart(2, "0")}
                    </td>
                    <td style={{ padding: "12px 10px", fontWeight: 700, color: "var(--text-primary)" }}>
                      {item.region_id}
                    </td>
                    <td style={{ padding: "12px 10px", color: "var(--accent)", fontWeight: 600 }}>
                      {geoCtx.geoLabel}
                    </td>
                    <td style={{ padding: "12px 10px", color: "var(--text-secondary)", fontSize: "12px" }}>
                      {geoCtx.formattedCoords}
                    </td>
                    <td style={{ padding: "12px 10px" }}>
                      <strong style={{ fontSize: "14px", color: probPct >= 50 ? "var(--warning)" : "var(--accent)" }}>
                        {formattedProb}%
                      </strong>
                    </td>
                    <td style={{ padding: "12px 10px" }}>
                      {getActivityLevelBadge(item.activity_level, probPct)}
                    </td>
                    <td style={{ padding: "12px 10px", color: "var(--text-secondary)" }}>
                      Month {item.month} ({item.year})
                    </td>
                    <td style={{ padding: "12px 10px" }}>
                      <span style={{ color: "var(--accent)", fontWeight: 600, display: "inline-flex", alignItems: "center", gap: "4px" }}>
                        Inspect <ChevronRight size={14} />
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* MOBILE CARDS VIEW (<768px) */}
        <div className="mobile-cards-container">
          {sortedPredictions.map((item, idx) => {
            const probPct = item.calibrated_probability_percent ?? (item.calibrated_probability * 100) ?? 0;
            const formattedProb = Number(probPct).toFixed(1);
            const geoCtx = getGeographicContext(item.grid_lat, item.grid_lon, item.region_id);

            return (
              <div
                key={"mob-" + item.region_id + "-" + idx}
                className="mobile-prediction-card"
                onClick={() => onSelectRegion && onSelectRegion(item)}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <span style={{ fontSize: "11px", fontWeight: 800, color: "var(--text-muted)" }}>
                    #{String(idx + 1).padStart(2, "0")}
                  </span>
                  {getActivityLevelBadge(item.activity_level, probPct)}
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                  <div>
                    <h3 style={{ margin: "0 0 2px 0", fontSize: "15px", color: "var(--text-primary)" }}>{item.region_id}</h3>
                    <div style={{ fontSize: "12px", color: "var(--accent)", fontWeight: 600 }}>{geoCtx.geoLabel}</div>
                    <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "2px" }}>{geoCtx.formattedCoords}</div>
                  </div>

                  <div style={{ textAlign: "right" }}>
                    <strong style={{ fontSize: "18px", color: probPct >= 50 ? "var(--warning)" : "var(--accent)" }}>
                      {formattedProb}%
                    </strong>
                    <div style={{ fontSize: "10px", color: "var(--text-muted)" }}>Est. Probability</div>
                  </div>
                </div>

                <div style={{ marginTop: "12px", paddingTop: "8px", borderTop: "1px solid var(--border-subtle)", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "12px" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Month {item.month} ({item.year})</span>
                  <span style={{ color: "var(--accent)", fontWeight: 600, display: "inline-flex", alignItems: "center", gap: "2px" }}>
                    Inspect profile <ChevronRight size={14} />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
