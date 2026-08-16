import React from "react";
import InfoTooltip from "./InfoTooltip";

export const PROBABILITY_BANDS = [
  { key: "very_high_count", label: "Very High (70%+)", color: "#ef4444", text: "VERY HIGH" },
  { key: "high_count", label: "High (50–69%)", color: "#f59e0b", text: "HIGH" },
  { key: "moderate_count", label: "Moderate (30–49%)", color: "#eab308", text: "MODERATE" },
  { key: "low_count", label: "Low (15–29%)", color: "#14b8a6", text: "LOW" },
  { key: "very_low_count", label: "Very Low (<15%)", color: "#64748b", text: "VERY LOW" },
];

export default function PredictionProbabilityChart({ summary }) {
  if (!summary) return null;

  const total = summary.prediction_rows || 3487;

  const counts = {
    very_high_count: summary.very_high_count || 0,
    high_count: summary.high_count || 0,
    moderate_count: summary.moderate_count || 0,
    low_count: summary.low_count || 0,
    very_low_count: summary.very_low_count || 0,
  };

  const maxVal = Math.max(...Object.values(counts), 1);

  return (
    <div className="panel prediction-chart-panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">PROBABILITY DISTRIBUTION</span>
          <h2>Prediction Probability Distribution</h2>
          <p>Distribution of prediction records across calibrated event likelihood bands.</p>
        </div>
        <InfoTooltip term="Probability Distribution" customTitle="Probability Distribution">
          Shows how estimated event probabilities are distributed across all analyzed spatial regions and prediction months.
        </InfoTooltip>
      </div>

      <div style={{ padding: "24px" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {PROBABILITY_BANDS.map((band) => {
            const count = counts[band.key] || 0;
            const pct = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
            const barWidth = (count / maxVal) * 100;

            return (
              <div key={band.key} style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ width: 10, height: 10, borderRadius: "3px", backgroundColor: band.color }} />
                    <strong style={{ color: "var(--text-primary)" }}>{band.label}</strong>
                  </div>
                  <div style={{ display: "flex", gap: "12px", fontSize: "12px" }}>
                    <span style={{ color: "var(--text-secondary)" }}>{count.toLocaleString()} regions</span>
                    <strong style={{ color: band.color }}>{pct}%</strong>
                  </div>
                </div>

                <div className="cluster-track" style={{ height: "10px" }}>
                  <div
                    className="cluster-fill"
                    style={{
                      width: `${Math.max(barWidth, 2)}%`,
                      backgroundColor: band.color,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
