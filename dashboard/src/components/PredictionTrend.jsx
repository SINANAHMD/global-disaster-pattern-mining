import React, { useEffect, useState } from "react";
import axios from "axios";
import { TrendingUp, Calendar, Info } from "lucide-react";
import InfoTooltip from "./InfoTooltip";

const API = "http://127.0.0.1:8000";

export default function PredictionTrend({ selectedRegionId }) {
  const [trendData, setTrendData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!selectedRegionId) return;

    async function fetchTrend() {
      try {
        setLoading(true);
        setError(false);
        const res = await axios.get(`${API}/api/prediction/region/${selectedRegionId}`);
        setTrendData(res.data.predictions || []);
      } catch (err) {
        console.error("Error fetching region trend:", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    }

    fetchTrend();
  }, [selectedRegionId]);

  if (!selectedRegionId) {
    return (
      <div className="panel" style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)" }}>
        Select a region from the map or top list to inspect its 2025 monthly probability trend.
      </div>
    );
  }

  return (
    <div className="panel prediction-trend-panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">MONTHLY PROBABILITY PROFILE</span>
          <h2>Region Prediction Trend — {selectedRegionId}</h2>
          <p>Estimated probability of natural event observations across prediction months in 2025.</p>
        </div>
        <InfoTooltip term="Probability Trend" customTitle="Monthly Probability Trend">
          Shows how estimated event probabilities vary month-by-month for the selected region throughout the prediction year.
        </InfoTooltip>
      </div>

      <div style={{ padding: "24px" }}>
        {loading && (
          <div style={{ padding: "30px", textAlign: "center", color: "var(--accent)" }}>
            Loading monthly trend data for {selectedRegionId}...
          </div>
        )}

        {error && (
          <div style={{ padding: "20px", color: "var(--danger)", textAlign: "center" }}>
            Unable to load prediction trend for {selectedRegionId}.
          </div>
        )}

        {!loading && !error && trendData.length === 0 && (
          <div style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)" }}>
            No monthly trend observations available for {selectedRegionId}.
          </div>
        )}

        {!loading && !error && trendData.length > 0 && (
          <div>
            <div style={{ height: "180px", display: "flex", alignItems: "flex-end", gap: "10px", padding: "10px 0" }}>
              {trendData.map((item, idx) => {
                const pct = item.calibrated_probability_percent ?? (item.calibrated_probability * 100) ?? 0;
                const height = Math.max(pct, 4);
                let color = "var(--accent)";
                if (pct >= 70) color = "#ef4444";
                else if (pct >= 50) color = "#f59e0b";
                else if (pct >= 30) color = "#eab308";

                return (
                  <div
                    key={item.month || idx}
                    style={{
                      flex: 1,
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      height: "100%",
                      justifyContent: "flex-end",
                    }}
                  >
                    <span style={{ fontSize: "10px", fontWeight: 700, color: color, marginBottom: "4px" }}>
                      {Number(pct).toFixed(0)}%
                    </span>
                    <div
                      title={`Month ${item.month}: ${Number(pct).toFixed(1)}% probability`}
                      style={{
                        width: "100%",
                        height: `${height}%`,
                        backgroundColor: color,
                        borderRadius: "4px 4px 0 0",
                        transition: "height 0.3s ease",
                      }}
                    />
                    <span style={{ fontSize: "10px", color: "var(--text-muted)", marginTop: "6px" }}>
                      M{item.month}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
