import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Activity,
  BarChart3,
  Globe2,
  Layers3,
  Map,
  Search,
  Settings,
  Waves,
  Info,
  Menu,
  X,
  HelpCircle,
  Layers,
  ChevronRight,
  ShieldAlert,
  Moon,
  Sun,
  Check,
  Brain,
} from "lucide-react";

import GlobalMap, { getClusterColor } from "./components/GlobalMap";
import InfoTooltip from "./components/InfoTooltip";
import HelpModal from "./components/HelpModal";
import RegionDrawer from "./components/RegionDrawer";
import MethodologyFlow from "./components/MethodologyFlow";
import PredictionPage from "./components/PredictionPage";
import "./App.css";

const API = "http://127.0.0.1:8000";

// ============================================================
// SIDEBAR ITEM
// ============================================================
function SidebarItem({ icon: Icon, label, active, onClick }) {
  return (
    <button
      className={`sidebar-item ${active ? "active" : ""}`}
      onClick={onClick}
    >
      <Icon size={17} />
      <span>{label}</span>
    </button>
  );
}

// ============================================================
// STAT CARD WITH EDUCATIONAL TOOLTIP
// ============================================================
function StatCard({ icon: Icon, label, value, description, tooltipTerm }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">
        <Icon size={22} />
      </div>

      <div className="stat-content">
        <div className="stat-header-row">
          <span className="stat-label">{label}</span>
          {tooltipTerm && <InfoTooltip term={tooltipTerm} />}
        </div>

        <strong className="stat-value">{value}</strong>

        <span className="stat-description">{description}</span>
      </div>
    </div>
  );
}

// ============================================================
// MAIN APP COMPONENT
// ============================================================
function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [page, setPage] = useState("Overview");

  // THEME & PERSISTENCE STATE
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("theme") || "dark";
  });

  const [reducedMotion, setReducedMotion] = useState(() => {
    return localStorage.getItem("reducedMotion") === "true";
  });

  // API Data State
  const [summary, setSummary] = useState(null);
  const [clusters, setClusters] = useState([]);
  const [regions, setRegions] = useState([]);
  const [trends, setTrends] = useState([]);
  const [categories, setCategories] = useState([]);
  const [countries, setCountries] = useState([]);

  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState(false);

  // UI Interactive Drawer & Modal State
  const [selectedDrawerData, setSelectedDrawerData] = useState(null);
  const [helpModalOpen, setHelpModalOpen] = useState(false);

  // Synchronize Theme & Motion Preference to HTML Document
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    document.documentElement.setAttribute("data-reduced-motion", reducedMotion ? "true" : "false");
    localStorage.setItem("reducedMotion", reducedMotion ? "true" : "false");
  }, [reducedMotion]);

  // Load API Data
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setApiError(false);

        const [
          summaryResponse,
          clustersResponse,
          regionsResponse,
          trendsResponse,
          categoriesResponse,
          countriesResponse,
        ] = await Promise.all([
          axios.get(`${API}/api/summary`),
          axios.get(`${API}/api/clusters`),
          axios.get(`${API}/api/regions`),
          axios.get(`${API}/api/trends`),
          axios.get(`${API}/api/categories`),
          axios.get(`${API}/api/countries`).catch(() => ({ data: { countries: [] } })),
        ]);

        setSummary(summaryResponse.data);
        setClusters(
          clustersResponse.data.clusters ||
          clustersResponse.data ||
          []
        );
        setRegions(
          regionsResponse.data.regions ||
          regionsResponse.data ||
          []
        );
        setTrends(
          trendsResponse.data.trends ||
          trendsResponse.data ||
          []
        );
        setCategories(
          categoriesResponse.data.categories ||
          categoriesResponse.data ||
          []
        );
        setCountries(
          countriesResponse.data.countries ||
          countriesResponse.data ||
          []
        );
      } catch (error) {
        console.error("API loading error:", error);
        setApiError(true);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  function navigate(target) {
    setPage(target);
    setSidebarOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Summary Metrics Values
  const eventCount =
    summary?.total_event_observations ??
    summary?.total_events ??
    35497;

  const regionCount = summary?.total_regions ?? 383;
  const clusterCount = summary?.total_clusters ?? 9;
  const silhouette = summary?.silhouette_score ?? 0.4682;

  const pageDescriptions = {
    Overview: "Global natural-event observations and regional profiles discovered by K-Means pattern mining.",
    "Global Map": "Geospatial visualization of 383 regional profiles and country hazard analysis.",
    "Prediction Intelligence": "Calibrated next-month EONET event likelihood estimates derived from regional patterns.",
    Clusters: "Analyze the nine regional disaster-event profiles discovered by K-Means clustering.",
    Trends: "Temporal analysis of NASA EONET event observations from 2015 to 2025.",
    Categories: "Distribution of natural event categories across global observations.",
    "Region Explorer": "Search and inspect individual spatial regions and country profiles.",
    "About Project": "Project methodology, NASA EONET dataset, machine learning pipeline, and technology stack.",
    Settings: "Dashboard visual theme options, animation preferences, and API connection information.",
  };

  return (
    <div className="app">
      {/* =====================================================
          SIDEBAR NAVIGATION
      ====================================================== */}
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        {/* BRAND */}
        <div className="brand">
          <div className="brand-logo">
            <Globe2 size={24} />
          </div>
          <div>
            <div className="brand-title">GLOBAL DISASTER</div>
            <div className="brand-subtitle">PATTERN MINING PLATFORM</div>
          </div>
        </div>

        {/* ANALYTICS SECTION */}
        <div className="sidebar-section">
          <span className="section-title">ANALYTICS</span>
          <SidebarItem
            icon={Activity}
            label="Overview"
            active={page === "Overview"}
            onClick={() => navigate("Overview")}
          />
          <SidebarItem
            icon={Map}
            label="Global Map"
            active={page === "Global Map"}
            onClick={() => navigate("Global Map")}
          />
          <SidebarItem
            icon={Brain}
            label="Prediction Intelligence"
            active={page === "Prediction Intelligence"}
            onClick={() => navigate("Prediction Intelligence")}
          />
          <SidebarItem
            icon={Layers3}
            label="Clusters"
            active={page === "Clusters"}
            onClick={() => navigate("Clusters")}
          />
          <SidebarItem
            icon={BarChart3}
            label="Trends"
            active={page === "Trends"}
            onClick={() => navigate("Trends")}
          />
          <SidebarItem
            icon={Waves}
            label="Categories"
            active={page === "Categories"}
            onClick={() => navigate("Categories")}
          />
        </div>

        {/* EXPLORE SECTION */}
        <div className="sidebar-section">
          <span className="section-title">EXPLORE</span>
          <SidebarItem
            icon={Search}
            label="Region Explorer"
            active={page === "Region Explorer"}
            onClick={() => navigate("Region Explorer")}
          />
        </div>

        {/* SYSTEM BOTTOM SECTION */}
        <div className="sidebar-bottom">
          <SidebarItem
            icon={Info}
            label="About Project"
            active={page === "About Project"}
            onClick={() => navigate("About Project")}
          />
          <SidebarItem
            icon={Settings}
            label="Settings"
            active={page === "Settings"}
            onClick={() => navigate("Settings")}
          />
        </div>
      </aside>

      {/* =====================================================
          MAIN DASHBOARD AREA
      ====================================================== */}
      <main className="main">
        {/* TOPBAR HEADER */}
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle navigation drawer"
          >
            {sidebarOpen ? <X size={22} /> : <Menu size={22} />}
          </button>

          <div className="page-heading">
            <div className="eyebrow">NASA EONET • DATA MINING PLATFORM</div>
            <h1>{page === "Overview" ? "Global Disaster Intelligence" : page}</h1>
            <p>{pageDescriptions[page]}</p>
          </div>

          <div className="topbar-right-controls">
            <div className="period-badge">
              <span className="status-dot"></span>
              Data Connected (2015–2025)
            </div>

            <button
              className="topbar-help-btn"
              onClick={() => setHelpModalOpen(true)}
              title="Dashboard Guide"
            >
              <HelpCircle size={15} />
              <span>Guide</span>
            </button>
          </div>
        </header>

        {/* CONTENT AREA */}
        <section className="content">
          {loading && (
            <div className="panel" style={{ padding: "30px", textAlign: "center", color: "var(--accent)" }}>
              Loading NASA EONET data mining analytical dataset...
            </div>
          )}

          {apiError && (
            <div className="panel" style={{ padding: "24px", borderColor: "rgba(239, 68, 68, 0.3)", marginBottom: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--danger)", marginBottom: "8px" }}>
                <ShieldAlert size={20} />
                <strong>Backend Connection Notice</strong>
              </div>
              <p style={{ margin: 0, fontSize: "13px", color: "var(--text-secondary)" }}>
                Make sure the FastAPI backend is running at <code>http://127.0.0.1:8000</code>.
              </p>
            </div>
          )}

          {/* =================================================
              OVERVIEW PAGE
          ================================================== */}
          {page === "Overview" && (
            <>
              {/* KPI STAT CARDS GRID */}
              <div className="stats-grid">
                <StatCard
                  icon={Activity}
                  label="EVENT OBSERVATIONS"
                  value={Number(eventCount).toLocaleString()}
                  description="Coordinate-based natural hazard records"
                  tooltipTerm="Event Observation"
                />
                <StatCard
                  icon={Globe2}
                  label="ACTIVE REGIONS"
                  value={Number(regionCount).toLocaleString()}
                  description="Geographical analysis spatial units"
                  tooltipTerm="Region"
                />
                <StatCard
                  icon={Layers3}
                  label="DISCOVERED CLUSTERS"
                  value={Number(clusterCount).toLocaleString()}
                  description="Regional event profiles by K-Means"
                  tooltipTerm="Cluster"
                />
                <StatCard
                  icon={BarChart3}
                  label="SILHOUETTE SCORE"
                  value={Number(silhouette).toFixed(4)}
                  description="Cluster cohesion & separation quality"
                  tooltipTerm="Silhouette Score"
                />
              </div>

              {/* INTERACTIVE METHODOLOGY PIPELINE FLOW */}
              <MethodologyFlow />

              {/* GLOBAL MAP PREVIEW PANEL */}
              <section className="panel map-panel">
                <div className="panel-header">
                  <div>
                    <span className="panel-kicker">GEOGRAPHIC INTELLIGENCE</span>
                    <h2>Global Regional Activity Map</h2>
                    <p>Geospatial distribution of 383 regional profiles and country event densities.</p>
                  </div>
                  <button className="panel-action" onClick={() => navigate("Global Map")}>
                    <Map size={16} />
                    Explore Map View
                  </button>
                </div>

                <div style={{ padding: "30px", textAlign: "center" }}>
                  <Globe2 size={48} style={{ color: "var(--accent)", marginBottom: "12px" }} />
                  <h3 style={{ margin: "0 0 6px 0", color: "var(--text-primary)" }}>
                    Interactive Geospatial Map Ready
                  </h3>
                  <p style={{ margin: "0 0 18px 0", color: "var(--text-secondary)", fontSize: "13px" }}>
                    Explore 383 spatial regions, country choropleths, and 5 analytical map views.
                  </p>
                  <button className="primary-button" onClick={() => navigate("Global Map")}>
                    Open Global Map Page
                  </button>
                </div>
              </section>

              {/* LOWER ANALYTICS PREVIEW GRID */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "18px" }}>
                {/* TEMPORAL TREND PREVIEW */}
                <section className="panel">
                  <div className="panel-header compact">
                    <div>
                      <span className="panel-kicker">TEMPORAL ANALYSIS</span>
                      <h2>Yearly Event Trend</h2>
                    </div>
                    <span className="period-badge">2015–2025</span>
                  </div>
                  <MiniTrend data={trends} />
                </section>

                {/* CLUSTER DISTRIBUTION PREVIEW */}
                <section className="panel">
                  <div className="panel-header compact">
                    <div>
                      <span className="panel-kicker">MACHINE LEARNING</span>
                      <h2>Cluster Distribution</h2>
                    </div>
                    <span className="period-badge">K = {clusterCount}</span>
                  </div>

                  <div style={{ padding: "20px" }}>
                    {clusters
                      .slice()
                      .sort((a, b) => (b.region_count || 0) - (a.region_count || 0))
                      .slice(0, 5)
                      .map((cluster) => (
                        <ClusterBar
                          key={cluster.cluster}
                          label={`Cluster ${cluster.cluster}`}
                          value={cluster.region_count || 0}
                          percentage={cluster.region_percentage || 0}
                          clusterId={cluster.cluster}
                          onClick={() => setSelectedDrawerData({ cluster: cluster.cluster, total_events: cluster.total_events || 0, active_years: "2015–2025" })}
                        />
                      ))}
                  </div>
                </section>
              </div>
            </>
          )}

          {/* =================================================
              GLOBAL MAP PAGE
          ================================================== */}
          {page === "Global Map" && (
            <GlobalMap
              regions={regions}
              summary={summary}
              clusters={clusters}
              countries={countries}
              loading={loading}
              apiError={apiError}
              onSelectDrawer={(data) => setSelectedDrawerData(data)}
            />
          )}

          {/* =================================================
              PREDICTION INTELLIGENCE PAGE
          ================================================== */}
          {page === "Prediction Intelligence" && <PredictionPage />}

          {/* =================================================
              CLUSTERS PAGE
          ================================================== */}
          {page === "Clusters" && (
            <ClustersPage
              clusters={clusters}
              onSelectCluster={(cluster) => setSelectedDrawerData({ cluster: cluster.cluster, total_events: cluster.total_events || 0, active_years: "2015–2025" })}
            />
          )}

          {/* =================================================
              TRENDS PAGE
          ================================================== */}
          {page === "Trends" && <TrendsPage trends={trends} />}

          {/* =================================================
              CATEGORIES PAGE
          ================================================== */}
          {page === "Categories" && <CategoriesPage categories={categories} />}

          {/* =================================================
              REGION EXPLORER PAGE
          ================================================== */}
          {page === "Region Explorer" && (
            <RegionExplorer
              regions={regions}
              onSelectRegion={(reg) => setSelectedDrawerData(reg)}
            />
          )}

          {/* =================================================
              ABOUT PROJECT PAGE
          ================================================== */}
          {page === "About Project" && <AboutPage />}

          {/* =================================================
              SETTINGS PAGE
          ================================================== */}
          {page === "Settings" && (
            <SettingsPage
              apiError={apiError}
              theme={theme}
              onThemeChange={setTheme}
              reducedMotion={reducedMotion}
              onReducedMotionChange={setReducedMotion}
            />
          )}

          {/* DASHBOARD FOOTER */}
          <footer className="dashboard-footer">
            <div>
              <span className="footer-status"></span>
              NASA EONET Analytical Pipeline Operational
            </div>
            <span>Global Disaster Intelligence • K-Means (K=9) • FastAPI • React Leaflet</span>
          </footer>
        </section>
      </main>

      {/* REUSABLE INTERACTIVE OVERLAYS */}
      <HelpModal isOpen={helpModalOpen} onClose={() => setHelpModalOpen(false)} />
      <RegionDrawer
        isOpen={selectedDrawerData !== null}
        onClose={() => setSelectedDrawerData(null)}
        data={selectedDrawerData}
      />
    </div>
  );
}

// ============================================================
// MINI TREND CHART
// ============================================================
function MiniTrend({ data }) {
  const values = data.map((item) => item.event_observations ?? item.events ?? item.count ?? 0);
  const max = Math.max(...values, 1);

  return (
    <div style={{ height: "150px", display: "flex", alignItems: "flex-end", gap: "8px", padding: "20px" }}>
      {values.map((value, index) => {
        const height = Math.max((value / max) * 100, 4);
        return (
          <div
            key={index}
            title={`${data[index]?.year || 2015 + index}: ${value.toLocaleString()} events`}
            style={{
              flex: 1,
              height: `${height}%`,
              background: "linear-gradient(180deg, var(--accent), var(--border))",
              borderRadius: "4px 4px 0 0",
              minWidth: "5px",
            }}
          />
        );
      })}
    </div>
  );
}

// ============================================================
// CLUSTER BAR COMPONENT
// ============================================================
function ClusterBar({ label, value, percentage, clusterId, onClick }) {
  const color = getClusterColor(clusterId);
  return (
    <div
      onClick={onClick}
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "10px 12px",
        marginBottom: "8px",
        borderRadius: "8px",
        background: "var(--surface-elevated)",
        border: "1px solid var(--border)",
        cursor: "pointer",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px" }}>
        <span style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: color }} />
        <strong style={{ color: "var(--text-primary)" }}>{label}</strong>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>{value} regions</span>
        <span style={{ fontSize: "12px", fontWeight: 700, color: color }}>{Number(percentage).toFixed(1)}%</span>
      </div>
    </div>
  );
}

// ============================================================
// CLUSTERS PAGE
// ============================================================
function ClustersPage({ clusters, onSelectCluster }) {
  const sorted = clusters.slice().sort((a, b) => (b.region_count || 0) - (a.region_count || 0));

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">MACHINE LEARNING DISCOVERY</span>
          <h2>Discovered Regional Cluster Profiles</h2>
          <p>K-Means clustering partitioning 383 spatial regions into K=9 similarity profiles.</p>
        </div>
        <InfoTooltip term="Cluster" />
      </div>

      <div className="clusters-cards-grid">
        {sorted.map((cluster) => {
          const cid = cluster.cluster;
          const color = getClusterColor(cid);
          const regionCount = cluster.region_count || 0;
          const pct = cluster.region_percentage || 0;

          return (
            <div
              key={cid}
              className="cluster-card"
              onClick={() => onSelectCluster(cluster)}
            >
              <div className="cluster-card-header">
                <span
                  className="cluster-badge-pill"
                  style={{ backgroundColor: `${color}22`, color: color, borderColor: `${color}55` }}
                >
                  <Layers size={13} />
                  Cluster {cid}
                </span>
                <span style={{ fontSize: "12px", fontWeight: 800, color: color }}>
                  {Number(pct).toFixed(1)}% share
                </span>
              </div>

              <h3 className="cluster-card-title">Regional Profile Cluster {cid}</h3>

              <div className="cluster-card-metrics">
                <span><strong>{regionCount}</strong> Spatial Regions</span>
                <span>Model Profile {cid}</span>
              </div>

              <div className="cluster-track">
                <div className="cluster-fill" style={{ width: `${Math.min(pct, 100)}%`, backgroundColor: color }} />
              </div>

              <div className="cluster-card-action">
                <span>View cluster details</span>
                <ChevronRight size={14} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

// ============================================================
// TRENDS PAGE
// ============================================================
function TrendsPage({ trends }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">TEMPORAL ANALYSIS</span>
          <h2>Global Event Observation Trend</h2>
          <p>NASA EONET natural hazard observations recorded between 2015 and 2025.</p>
        </div>
        <InfoTooltip term="Recent Activity" />
      </div>

      <div style={{ padding: "24px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "15px" }}>
          {trends.map((item) => {
            const value = item.event_observations ?? item.events ?? item.count ?? 0;
            return (
              <div className="stat-card" key={item.year} style={{ minHeight: "110px", padding: "16px" }}>
                <div className="stat-content">
                  <span className="stat-label">{item.year}</span>
                  <strong className="stat-value" style={{ fontSize: "22px" }}>
                    {Number(value).toLocaleString()}
                  </strong>
                  <span className="stat-description">Observations</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

// ============================================================
// CATEGORIES PAGE
// ============================================================
function CategoriesPage({ categories }) {
  const sorted = categories
    .slice()
    .sort((a, b) => (b.event_observations || b.count || 0) - (a.event_observations || a.count || 0));

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">HAZARD CATEGORIES</span>
          <h2>Disaster Event Categories</h2>
          <p>Distribution of NASA EONET hazard event classifications in the dataset.</p>
        </div>
        <InfoTooltip term="Dominant Disaster Type" />
      </div>

      <div style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "14px" }}>
        {sorted.map((category, index) => {
          const catName = category.category || category.name || "Unknown Category";
          const value = category.event_observations ?? category.count ?? category.total ?? 0;
          const max = sorted.length > 0 ? Math.max(...sorted.map((x) => x.event_observations ?? x.count ?? 0), 1) : 1;
          const percentage = (value / max) * 100;

          return (
            <div key={catName || index} style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                <strong style={{ color: "var(--text-primary)" }}>{catName}</strong>
                <span style={{ color: "var(--accent)", fontWeight: 700 }}>{Number(value).toLocaleString()} observations</span>
              </div>
              <div className="cluster-track" style={{ height: "8px" }}>
                <div className="cluster-fill" style={{ width: `${percentage}%`, background: "linear-gradient(90deg, var(--accent), var(--info))" }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

// ============================================================
// REGION EXPLORER PAGE
// ============================================================
function RegionExplorer({ regions, onSelectRegion }) {
  const [search, setSearch] = useState("");

  const filtered = regions.filter((region) => {
    const text = `${region.region_id || ""} ${region.cluster ?? ""} ${region.region_name || ""} ${region.country || ""}`.toLowerCase();
    return text.includes(search.toLowerCase());
  });

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">REGION EXPLORER</span>
          <h2>Search & Inspect Regional Profiles</h2>
          <p>Explore all 383 spatial regions used by the K-Means clustering model.</p>
        </div>
        <InfoTooltip term="Region" />
      </div>

      <div style={{ padding: "24px" }}>
        <div style={{ marginBottom: "20px" }}>
          <div className="country-search-box" style={{ width: "100%", maxWidth: "450px" }}>
            <Search size={16} className="search-icon" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search region by ID, cluster, or country..."
              className="country-search-input"
            />
            {search && (
              <button className="search-clear" onClick={() => setSearch("")}>
                <X size={14} />
              </button>
            )}
          </div>
        </div>

        {filtered.length === 0 ? (
          <div style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
            No spatial region found matching "{search}".
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--text-muted)", textAlign: "left" }}>
                  <th style={{ padding: "12px" }}>Region ID</th>
                  <th style={{ padding: "12px" }}>Cluster</th>
                  <th style={{ padding: "12px" }}>Total Events</th>
                  <th style={{ padding: "12px" }}>Events / Active Year</th>
                  <th style={{ padding: "12px" }}>Latitude</th>
                  <th style={{ padding: "12px" }}>Longitude</th>
                  <th style={{ padding: "12px" }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {filtered.slice(0, 50).map((region, index) => {
                  const color = getClusterColor(region.cluster);
                  return (
                    <tr
                      key={region.region_id || index}
                      style={{ borderBottom: "1px solid var(--border-subtle)", cursor: "pointer" }}
                      onClick={() => onSelectRegion(region)}
                    >
                      <td style={{ padding: "12px", fontWeight: 700, color: "var(--text-primary)" }}>
                        {region.region_id || "-"}
                      </td>
                      <td style={{ padding: "12px" }}>
                        <span className="popup-cluster-pill" style={{ backgroundColor: `${color}22`, color: color, borderColor: `${color}55` }}>
                          Cluster {region.cluster ?? "-"}
                        </span>
                      </td>
                      <td style={{ padding: "12px", color: "var(--accent)", fontWeight: 700 }}>
                        {Number(region.total_events || 0).toLocaleString()}
                      </td>
                      <td style={{ padding: "12px" }}>
                        {region.events_per_active_year != null ? Number(region.events_per_active_year).toFixed(2) : "-"}
                      </td>
                      <td style={{ padding: "12px", color: "var(--text-secondary)" }}>
                        {region.region_latitude ?? region.latitude ?? "-"}
                      </td>
                      <td style={{ padding: "12px", color: "var(--text-secondary)" }}>
                        {region.region_longitude ?? region.longitude ?? "-"}
                      </td>
                      <td style={{ padding: "12px" }}>
                        <span style={{ color: "var(--accent)", fontWeight: 600 }}>Inspect →</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}

// ============================================================
// ABOUT PROJECT PAGE
// ============================================================
function AboutPage() {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">PROJECT METHODOLOGY</span>
          <h2>Global Disaster Pattern Mining</h2>
          <p>NASA EONET natural hazard analysis, machine learning architecture, and technology stack.</p>
        </div>
        <InfoTooltip term="NASA EONET" />
      </div>

      <div style={{ padding: "26px", maxWidth: "950px", lineHeight: "1.7" }}>
        <h3 style={{ color: "var(--accent)", fontSize: "16px", marginTop: 0 }}>Project Architecture & Objective</h3>
        <p style={{ color: "var(--text-secondary)" }}>
          This project processes historical natural hazard observations from <strong>NASA EONET (Earth Observatory Natural Event Tracker)</strong> spanning 2015 to 2025.
          Raw spatial coordinates are mapped into geographical analysis regions and standardized before fitting an unsupervised <strong>K-Means clustering algorithm (K=9)</strong>.
        </p>

        <h3 style={{ color: "var(--accent)", fontSize: "16px", marginTop: "25px" }}>Technology Stack</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "14px", marginTop: "12px" }}>
          <div className="drawer-metric-card">
            <span className="metric-lbl">DATASET</span>
            <strong className="metric-val accent">NASA EONET</strong>
            <span className="metric-sub">Global satellite hazard telemetry</span>
          </div>

          <div className="drawer-metric-card">
            <span className="metric-lbl">DATA PROCESSING</span>
            <strong className="metric-val accent">Python & Pandas</strong>
            <span className="metric-sub">Feature engineering & spatial aggregation</span>
          </div>

          <div className="drawer-metric-card">
            <span className="metric-lbl">MACHINE LEARNING</span>
            <strong className="metric-val accent">Scikit-learn K-Means</strong>
            <span className="metric-sub">StandardScaler & K=9 clustering</span>
          </div>

          <div className="drawer-metric-card">
            <span className="metric-lbl">BACKEND API</span>
            <strong className="metric-val accent">FastAPI</strong>
            <span className="metric-sub">High-performance REST service</span>
          </div>

          <div className="drawer-metric-card">
            <span className="metric-lbl">FRONTEND UI</span>
            <strong className="metric-val accent">React & Vite</strong>
            <span className="metric-sub">Component architecture & state</span>
          </div>

          <div className="drawer-metric-card">
            <span className="metric-lbl">GEOSPATIAL MAP</span>
            <strong className="metric-val accent">React Leaflet</strong>
            <span className="metric-sub">Interactive GeoJSON vector mapping</span>
          </div>
        </div>

        <h3 style={{ color: "var(--accent)", fontSize: "16px", marginTop: "25px" }}>Model Validation & Metrics</h3>
        <p style={{ color: "var(--text-secondary)" }}>
          The final model utilizes <strong>K = 9 regional profiles</strong> evaluated with a <strong>Silhouette Score of 0.4682</strong>, demonstrating well-defined cluster separation across spatial feature vectors.
        </p>

        <div className="drawer-safety-notice" style={{ marginTop: "20px" }}>
          <Info size={16} style={{ color: "var(--accent)" }} />
          <p>
            <strong>Scientific Disclaimer:</strong> This dashboard identifies mathematical similarity patterns in historical event observations. Cluster numbers are labels and do not constitute official risk scores or danger predictions.
          </p>
        </div>
      </div>
    </section>
  );
}

// ============================================================
// SETTINGS PAGE WITH LIGHT/DARK MODE SWITCHER
// ============================================================
function SettingsPage({ apiError, theme, onThemeChange, reducedMotion, onReducedMotionChange }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">PREFERENCES & SYSTEM</span>
          <h2>Dashboard Settings</h2>
          <p>Choose visual themes, animation preferences, and view system status.</p>
        </div>
        <InfoTooltip term="API" />
      </div>

      <div style={{ padding: "26px" }}>
        {/* APPEARANCE SECTION */}
        <div className="settings-section">
          <div className="settings-heading">APPEARANCE THEME</div>
          <p style={{ margin: "0 0 16px 0", fontSize: "13px", color: "var(--text-secondary)" }}>
            Choose how Global Disaster Intelligence looks on your device. Selected preference is saved automatically.
          </p>

          <div className="theme-switcher-grid">
            <button
              className={`theme-card-btn ${theme === "dark" ? "active" : ""}`}
              onClick={() => onThemeChange("dark")}
            >
              <div className="theme-card-icon">
                <Moon size={20} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span className="theme-card-title">Dark Mode</span>
                  {theme === "dark" && <Check size={16} style={{ color: "var(--accent)" }} />}
                </div>
                <span className="theme-card-sub">Charcoal & Teal scientific layout</span>
              </div>
            </button>

            <button
              className={`theme-card-btn ${theme === "light" ? "active" : ""}`}
              onClick={() => onThemeChange("light")}
            >
              <div className="theme-card-icon">
                <Sun size={20} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span className="theme-card-title">Light Mode</span>
                  {theme === "light" && <Check size={16} style={{ color: "var(--accent)" }} />}
                </div>
                <span className="theme-card-sub">Clean neutral analytics layout</span>
              </div>
            </button>
          </div>
        </div>

        {/* ACCESSIBILITY & ANIMATION PREFERENCES */}
        <div className="settings-section" style={{ marginTop: "32px" }}>
          <div className="settings-heading">ACCESSIBILITY</div>
          <label style={{ display: "flex", alignItems: "center", gap: "12px", cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={reducedMotion}
              onChange={(e) => onReducedMotionChange(e.target.checked)}
              style={{ width: "16px", height: "16px", accentColor: "var(--accent)" }}
            />
            <div>
              <strong style={{ display: "block", fontSize: "13px", color: "var(--text-primary)" }}>
                Reduce Motion & Decorative Animations
              </strong>
              <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                Disables decorative UI transitions for reduced visual strain.
              </span>
            </div>
          </label>
        </div>

        {/* SYSTEM STATUS */}
        <div className="settings-section" style={{ marginTop: "32px" }}>
          <div className="settings-heading">SYSTEM CONNECTION</div>
          <div className="drawer-metrics-grid" style={{ marginTop: "12px" }}>
            <div className="drawer-metric-card">
              <span className="metric-lbl">BACKEND SERVICE</span>
              <strong className="metric-val" style={{ color: apiError ? "var(--danger)" : "var(--success)" }}>
                {apiError ? "Offline" : "Connected (8000)"}
              </strong>
            </div>

            <div className="drawer-metric-card">
              <span className="metric-lbl">DATASET</span>
              <strong className="metric-val">NASA EONET</strong>
            </div>

            <div className="drawer-metric-card">
              <span className="metric-lbl">MODEL PROFILE</span>
              <strong className="metric-val">K-Means (K=9)</strong>
            </div>

            <div className="drawer-metric-card">
              <span className="metric-lbl">SPATIAL UNITS</span>
              <strong className="metric-val">383 Regions</strong>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default App;