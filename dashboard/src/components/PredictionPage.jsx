import React, { useEffect, useState } from "react";
import axios from "axios";
import { Brain, Activity, Globe2, BarChart3, Search, RefreshCw, X, ShieldAlert, Compass, Flag } from "lucide-react";
import PredictionModelInfo from "./PredictionModelInfo";
import PredictionMap from "./PredictionMap";
import PredictionProbabilityChart from "./PredictionProbabilityChart";
import PredictionRanking from "./PredictionRanking";
import PredictionTrend from "./PredictionTrend";
import PredictionRegionDrawer from "./PredictionRegionDrawer";
import PredictionDisclaimer from "./PredictionDisclaimer";
import InfoTooltip from "./InfoTooltip";
import { getGeographicContext } from "../utils/geoUtils";

const API = "http://127.0.0.1:8000";

export default function PredictionPage() {
  const [viewScope, setViewScope] = useState("global"); // 'global' | 'india'
  const [summary, setSummary] = useState(null);
  const [topPredictions, setTopPredictions] = useState([]);
  const [regionsPredictions, setRegionsPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedBandFilter, setSelectedBandFilter] = useState("ALL");

  // Selected Region for Drawer & Trend
  const [selectedRegionData, setSelectedRegionData] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(false);

      const [summaryRes, topRes, regionsRes] = await Promise.all([
        axios.get(`${API}/api/prediction/summary`),
        axios.get(`${API}/api/prediction/top`),
        axios.get(`${API}/api/prediction/regions`),
      ]);

      setSummary(summaryRes.data);
      setTopPredictions(topRes.data.predictions || []);
      setRegionsPredictions(regionsRes.data.predictions || []);

      if (topRes.data.predictions && topRes.data.predictions.length > 0) {
        setSelectedRegionData(topRes.data.predictions[0]);
      }
    } catch (err) {
      console.error("Error fetching prediction API data:", err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Filter regions based on search query and probability band
  const filteredPredictions = regionsPredictions.filter((item) => {
    const probPct = item.calibrated_probability_percent ?? (item.calibrated_probability * 100) ?? 0;
    const band = item.activity_level || (probPct >= 70 ? "VERY HIGH" : probPct >= 50 ? "HIGH" : probPct >= 30 ? "MODERATE" : probPct >= 15 ? "LOW" : "VERY LOW");

    const geoCtx = getGeographicContext(item.grid_lat, item.grid_lon, item.region_id);
    const textSearch = `${item.region_id} ${geoCtx.geoLabel} ${geoCtx.continent} ${geoCtx.subregion}`.toLowerCase();

    const matchesSearch = searchQuery.trim() === "" || textSearch.includes(searchQuery.toLowerCase().trim());
    const matchesBand = selectedBandFilter === "ALL" || band === selectedBandFilter;

    return matchesSearch && matchesBand;
  });

  const avgProb = summary ? (summary.average_probability * 100).toFixed(1) : "15.1";
  const maxProb = summary ? (summary.maximum_probability * 100).toFixed(1) : "100.0";
  const regionCount = summary?.regions || 317;
  const targetYear = summary?.prediction_year || 2025;

  return (
    <div className="prediction-page-container">
      {/* SCOPE TOGGLE TABS & STATUS */}
      <div className="prediction-scope-bar">
        <div className="scope-tabs-group">
          <button
            className={`scope-tab-btn ${viewScope === "global" ? "active" : ""}`}
            onClick={() => setViewScope("global")}
          >
            <Globe2 size={15} />
            <span>Global Grid Predictions</span>
          </button>
          <button
            className={`scope-tab-btn ${viewScope === "india" ? "active" : ""}`}
            onClick={() => setViewScope("india")}
          >
            <Flag size={15} />
            <span>India State Intelligence</span>
          </button>
        </div>

        <div className="status-badge-group">
          <span className="live-badge connected">
            <span className="status-dot"></span>
            PREDICTION MODEL ACTIVE
          </span>
          <span className="period-badge" style={{ fontSize: "11px" }}>
            Target Period: {targetYear}
          </span>
        </div>
      </div>

      {loading && (
        <div className="panel" style={{ padding: "40px", textAlign: "center", color: "var(--accent)" }}>
          Loading Prediction Intelligence datasets and model metrics...
        </div>
      )}

      {error && (
        <div className="panel" style={{ padding: "24px", borderColor: "rgba(239, 68, 68, 0.3)", marginBottom: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--danger)" }}>
              <ShieldAlert size={20} />
              <strong>Prediction Data Unavailable</strong>
            </div>
            <button className="primary-button" onClick={fetchData}>
              <RefreshCw size={14} /> Retry
            </button>
          </div>
          <p style={{ margin: "8px 0 0 0", fontSize: "13px", color: "var(--text-secondary)" }}>
            Make sure the FastAPI backend is running at <code>http://127.0.0.1:8000</code>.
          </p>
        </div>
      )}

      {!loading && !error && viewScope === "global" && (
        <>
          {/* HERO KPI SUMMARY CARDS */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">
                <Brain size={22} />
              </div>
              <div className="stat-content">
                <div className="stat-header-row">
                  <span className="stat-label">AVERAGE PROBABILITY</span>
                  <InfoTooltip term="Average Probability" customTitle="Average Event Probability">
                    The mean predicted next-month event likelihood across all analyzed spatial regions.
                  </InfoTooltip>
                </div>
                <strong className="stat-value">{avgProb}%</strong>
                <span className="stat-description">Mean regional likelihood</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <Activity size={22} />
              </div>
              <div className="stat-content">
                <div className="stat-header-row">
                  <span className="stat-label">MAX ESTIMATED PROBABILITY</span>
                  <InfoTooltip term="Highest Likelihood" customTitle="Highest Estimated Probability">
                    The maximum predicted next-month likelihood observed across target regions.
                  </InfoTooltip>
                </div>
                <strong className="stat-value" style={{ color: "var(--warning)" }}>{maxProb}%</strong>
                <span className="stat-description">Peak regional likelihood</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <Globe2 size={22} />
              </div>
              <div className="stat-content">
                <div className="stat-header-row">
                  <span className="stat-label">REGIONS ANALYZED</span>
                  <InfoTooltip term="Region" inline />
                </div>
                <strong className="stat-value">{regionCount}</strong>
                <span className="stat-description">Spatial prediction grid units</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <BarChart3 size={22} />
              </div>
              <div className="stat-content">
                <div className="stat-header-row">
                  <span className="stat-label">PREDICTION PERIOD</span>
                </div>
                <strong className="stat-value">{targetYear}</strong>
                <span className="stat-description">Target monthly evaluation</span>
              </div>
            </div>
          </div>

          {/* MODEL EXPLANATION CARD */}
          <PredictionModelInfo />

          {/* GEOSPATIAL PREDICTION MAP */}
          <PredictionMap
            predictions={filteredPredictions}
            onSelectRegion={(reg) => setSelectedRegionData(reg)}
          />

          {/* SEARCH & FILTERS BAR */}
          <div className="panel" style={{ padding: "16px 24px", marginBottom: "24px" }}>
            <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: "14px" }}>
              <div className="country-search-box" style={{ width: "100%", maxWidth: "340px" }}>
                <Search size={15} className="search-icon" />
                <input
                  type="text"
                  placeholder="Search region ID, continent, location..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="country-search-input"
                />
                {searchQuery && (
                  <button className="search-clear" onClick={() => setSearchQuery("")}>
                    <X size={14} />
                  </button>
                )}
              </div>

              {/* PROBABILITY BAND FILTER CHIPS */}
              <div className="mobile-scrollable-chips" style={{ display: "flex", alignItems: "center", gap: "8px", overflowX: "auto", maxWidth: "100%" }}>
                <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.08em", whiteSpace: "nowrap" }}>
                  BAND:
                </span>
                {["ALL", "VERY HIGH", "HIGH", "MODERATE", "LOW", "VERY LOW"].map((band) => (
                  <button
                    key={band}
                    className={`view-tab ${selectedBandFilter === band ? "active" : ""}`}
                    onClick={() => setSelectedBandFilter(band)}
                    style={{ padding: "6px 10px", fontSize: "11px", whiteSpace: "nowrap" }}
                  >
                    {band}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* MIDDLE ANALYTICS GRID: PROBABILITY CHART & MONTHLY TREND */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "20px", marginBottom: "24px" }}>
            <PredictionProbabilityChart summary={summary} />
            <PredictionTrend selectedRegionId={selectedRegionData?.region_id} />
          </div>

          {/* TOP PREDICTED REGIONS RANKING TABLE */}
          <PredictionRanking
            predictions={topPredictions}
            onSelectRegion={(reg) => setSelectedRegionData(reg)}
          />

          {/* MANDATORY SAFETY DISCLAIMER */}
          <PredictionDisclaimer />
        </>
      )}

      {/* INDIA STATE INTELLIGENCE VIEW */}
      {!loading && !error && viewScope === "india" && (
        <section className="panel" style={{ padding: "24px" }}>
          <div className="panel-header" style={{ paddingBottom: "16px", marginBottom: "20px" }}>
            <div>
              <span className="panel-kicker">INDIA STATE-LEVEL ANALYTICS</span>
              <h2>India State Prediction Intelligence</h2>
              <p>State-level event probability models evaluated across 20 Indian States/UTs.</p>
            </div>
          </div>

          <div className="drawer-metrics-grid" style={{ marginBottom: "24px" }}>
            <div className="drawer-metric-card">
              <span className="metric-lbl">TOTAL STATE OBSERVATIONS</span>
              <strong className="metric-val accent">2,380 Rows</strong>
              <span className="metric-sub">Monthly state timeline (2016–2025)</span>
            </div>

            <div className="drawer-metric-card">
              <span className="metric-lbl">REPRESENTED STATES</span>
              <strong className="metric-val">20 States/UTs</strong>
              <span className="metric-sub">ADM1 spatial boundaries</span>
            </div>

            <div className="drawer-metric-card">
              <span className="metric-lbl">POSITIVE EVENT RATE</span>
              <strong className="metric-val" style={{ color: "var(--warning)" }}>1.58% (49 Events)</strong>
              <span className="metric-sub">Low-sample regime</span>
            </div>

            <div className="drawer-metric-card">
              <span className="metric-lbl">BEST MODEL (STEP 3T)</span>
              <strong className="metric-val" style={{ color: "var(--success)" }}>Gradient Boosting</strong>
              <span className="metric-sub">PR-AUC: 0.2412 | Brier: 0.0914</span>
            </div>
          </div>

          <div className="drawer-safety-notice" style={{ marginBottom: "20px" }}>
            <Compass size={16} style={{ color: "var(--accent)" }} />
            <div>
              <strong style={{ color: "var(--text-primary)", fontSize: "13px" }}>Limited Historical Data Coverage Notice:</strong>
              <p style={{ margin: "4px 0 0 0", fontSize: "12px", color: "var(--text-secondary)" }}>
                Because historical EONET observations inside specific state polygons are sparse (49 positive event-months across 2,380 state-month records), state-level outputs are presented for research analysis only and should not be used as official warnings.
              </p>
            </div>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--text-muted)", textAlign: "left" }}>
                  <th style={{ padding: "10px" }}>State Name</th>
                  <th style={{ padding: "10px" }}>Historical Unique Events</th>
                  <th style={{ padding: "10px" }}>Category Focus</th>
                  <th style={{ padding: "10px" }}>2025 Test Max Prob</th>
                  <th style={{ padding: "10px" }}>Model Status</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: "Madhya Pradesh", events: 10, cat: "Wildfires", maxProb: "0.23%", status: "Calibrated" },
                  { name: "Chhattisgarh", events: 8, cat: "Wildfires", maxProb: "1.58%", status: "Calibrated" },
                  { name: "Mizoram", events: 7, cat: "Wildfires / Landslides", maxProb: "0.71%", status: "Calibrated" },
                  { name: "Andhra Pradesh", events: 6, cat: "Severe Storms / Floods", maxProb: "25.63%", status: "Calibrated" },
                  { name: "Maharashtra", events: 4, cat: "Wildfires / Cyclones", maxProb: "2.09%", status: "Calibrated" },
                  { name: "Odisha", events: 4, cat: "Severe Storms", maxProb: "9.64%", status: "Calibrated" },
                  { name: "Gujarat", events: 4, cat: "Wildfires / Cyclones", maxProb: "3.07%", status: "Calibrated" },
                  { name: "Kerala", events: 4, cat: "Floods / Storms", maxProb: "9.12%", status: "Calibrated" },
                  { name: "Tamil Nadu", events: 4, cat: "Severe Storms", maxProb: "17.78%", status: "Calibrated" },
                  { name: "Bihar", events: 3, cat: "Floods", maxProb: "90.34%", status: "Calibrated" },
                  { name: "West Bengal", events: 3, cat: "Floods / Cyclones", maxProb: "86.21%", status: "Calibrated" },
                  { name: "Karnataka", events: 3, cat: "Floods", maxProb: "0.99%", status: "Calibrated" },
                  { name: "Meghalaya", events: 3, cat: "Landslides", maxProb: "1.51%", status: "Calibrated" },
                ].map((s, idx) => (
                  <tr key={s.name || idx} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                    <td style={{ padding: "10px", fontWeight: 700, color: "var(--text-primary)" }}>{s.name}</td>
                    <td style={{ padding: "10px", color: "var(--accent)", fontWeight: 700 }}>{s.events} events</td>
                    <td style={{ padding: "10px", color: "var(--text-secondary)" }}>{s.cat}</td>
                    <td style={{ padding: "10px", fontWeight: 700, color: parseFloat(s.maxProb) >= 20 ? "var(--warning)" : "var(--text-primary)" }}>{s.maxProb}</td>
                    <td style={{ padding: "10px" }}>
                      <span className="popup-cluster-pill" style={{ background: "rgba(20, 184, 166, 0.15)", color: "var(--accent)" }}>
                        {s.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* REGION DETAIL DRAWER OVERLAY */}
      <PredictionRegionDrawer
        isOpen={selectedRegionData !== null}
        onClose={() => setSelectedRegionData(null)}
        data={selectedRegionData}
      />
    </div>
  );
}
