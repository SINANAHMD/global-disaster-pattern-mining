import React, { useState, useMemo, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  GeoJSON,
  Popup,
  Tooltip,
  useMap,
} from "react-leaflet";
import {
  RotateCcw,
  Maximize2,
  Activity,
  Layers,
  Search,
  HelpCircle,
  X,
  Flame,
  Globe2,
  TrendingUp,
  BarChart2,
  Info,
} from "lucide-react";
import "leaflet/dist/leaflet.css";

// ============================================================
// CLUSTER COLOR PALETTE (K = 9)
// ============================================================
export const CLUSTER_COLORS = {
  0: "#38bdf8", // Sky Blue
  1: "#f43f5e", // Rose Red
  2: "#fbbf24", // Amber Yellow
  3: "#a855f7", // Purple
  4: "#34d399", // Emerald Green
  5: "#f97316", // Orange
  6: "#06b6d4", // Cyan
  7: "#ec4899", // Pink
  8: "#6366f1", // Indigo
};

export const getClusterColor = (clusterId) => {
  if (clusterId === null || clusterId === undefined) return "#94a3b8";
  return CLUSTER_COLORS[clusterId] || "#38bdf8";
};

// ============================================================
// CATEGORY COLOR PALETTE
// ============================================================
export const CATEGORY_COLORS = {
  Wildfires: "#f97316",
  "Severe Storms": "#38bdf8",
  Floods: "#3b82f6",
  Volcanoes: "#ef4444",
  Earthquakes: "#eab308",
  "Sea and Lake Ice": "#06b6d4",
  "Dust and Haze": "#94a3b8",
  Landslides: "#a855f7",
  Drought: "#d97706",
  "Water Color": "#14b8a6",
};

export const getCategoryColor = (category) => {
  if (!category) return "#64748b";
  return CATEGORY_COLORS[category] || "#64748b";
};

// Density color generator (Dark Navy to Bright Cyan)
export const getDensityColor = (val, maxVal) => {
  if (!val || val <= 0) return "#111f30"; // Neutral dim slate
  const ratio = val / (maxVal || 1);
  if (ratio < 0.03) return "#143a5e";
  if (ratio < 0.1) return "#0284c7";
  if (ratio < 0.25) return "#0369a1";
  if (ratio < 0.5) return "#0284c7";
  if (ratio < 0.8) return "#38bdf8";
  return "#7dd3fc";
};

// ============================================================
// MAP CONTROLLER (RESET VIEW, FIT BOUNDS, TARGET COUNTRY ZOOM)
// ============================================================
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

// ============================================================
// MAIN GLOBAL MAP COMPONENT
// ============================================================
export default function GlobalMap({
  regions = [],
  summary = null,
  clusters = [],
  countries = [],
  loading = false,
  apiError = false,
  onSelectDrawer = null,
}) {
  // MAP VIEW MODES:
  // 1: K-Means Clusters (Default)
  // 2: Country Event Density
  // 3: Dominant Disaster Type
  // 4: Recent Activity
  // 5: Cluster Distribution
  const [mapView, setMapView] = useState("clusters");

  const [activeCluster, setActiveCluster] = useState(null);
  const [resetTrigger, setResetTrigger] = useState(0);
  const [fitTrigger, setFitTrigger] = useState(0);
  const [targetBounds, setTargetBounds] = useState(null);

  // GeoJSON state
  const [geoJsonData, setGeoJsonData] = useState(null);

  // Country search state
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCountry, setSelectedCountry] = useState(null);

  // Modal state
  const [showExplanation, setShowExplanation] = useState(false);

  // Fetch GeoJSON world countries
  useEffect(() => {
    fetch("/world-countries.json")
      .then((res) => res.json())
      .then((data) => setGeoJsonData(data))
      .catch((err) => console.error("Error loading world GeoJSON:", err));
  }, []);

  // Compute dataset statistics
  const totalRegionsCount = regions.length || summary?.total_regions || 383;

  const totalEventsCount = useMemo(() => {
    if (summary?.total_event_observations || summary?.total_events) {
      return summary.total_event_observations || summary.total_events;
    }
    if (regions.length > 0) {
      return regions.reduce((acc, r) => acc + (r.total_events || 0), 0);
    }
    return 35497;
  }, [summary, regions]);

  const clusterCount = summary?.total_clusters || clusters.length || 9;

  // Filter valid geographic coordinate regions for View 1
  const validRegions = useMemo(() => {
    return regions.filter((r) => {
      const lat = r.region_latitude ?? r.latitude;
      const lng = r.region_longitude ?? r.longitude;
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
  }, [regions]);

  // Compute min/max total_events for radius scaling
  const { minEvents, maxEvents } = useMemo(() => {
    if (validRegions.length === 0) return { minEvents: 1, maxEvents: 1000 };
    let min = Infinity;
    let max = -Infinity;
    validRegions.forEach((r) => {
      const events = r.total_events || 1;
      if (events < min) min = events;
      if (events > max) max = events;
    });
    return {
      minEvents: min === Infinity ? 1 : min,
      maxEvents: max === -Infinity ? 1000 : max,
    };
  }, [validRegions]);

  // Radius sizing function
  const getMarkerRadius = (eventsCount) => {
    const val = eventsCount || 1;
    const minRadius = 4;
    const maxRadius = 14;
    const logMin = Math.log(Math.max(1, minEvents));
    const logMax = Math.log(Math.max(logMin + 1, maxEvents));
    const logVal = Math.log(Math.max(1, val));
    const norm = (logVal - logMin) / (logMax - logMin || 1);
    return Math.max(minRadius, Math.min(maxRadius, minRadius + norm * (maxRadius - minRadius)));
  };

  // Bounds for region fit
  const mapBounds = useMemo(() => {
    return validRegions.map((r) => [
      r.region_latitude ?? r.latitude,
      r.region_longitude ?? r.longitude,
    ]);
  }, [validRegions]);

  // Country Data Map (keyed by uppercase country name and ISO3)
  const countryMap = useMemo(() => {
    const map = new Map();
    countries.forEach((c) => {
      if (c.country) map.set(c.country.toUpperCase(), c);
      if (c.country_iso3) map.set(c.country_iso3.toUpperCase(), c);
    });
    return map;
  }, [countries]);

  // Max country total events & max recent events for choropleth scale
  const maxCountryEvents = useMemo(() => {
    return countries.reduce((max, c) => Math.max(max, c.total_events || 0), 1);
  }, [countries]);

  const maxCountryRecentEvents = useMemo(() => {
    return countries.reduce((max, c) => Math.max(max, c.recent_events || 0), 1);
  }, [countries]);

  // Top 5 Countries sorted by events
  const topCountries = useMemo(() => {
    return [...countries]
      .sort((a, b) => (b.total_events || 0) - (a.total_events || 0))
      .slice(0, 5);
  }, [countries]);

  // Active categories present in dataset
  const activeCategories = useMemo(() => {
    const set = new Set();
    countries.forEach((c) => {
      if (c.dominant_category) set.add(c.dominant_category);
    });
    return Array.from(set);
  }, [countries]);

  // Search filtered countries
  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const q = searchQuery.toLowerCase().trim();
    return countries
      .filter((c) => c.country && c.country.toLowerCase().includes(q))
      .slice(0, 6);
  }, [countries, searchQuery]);

  // Helper to locate country feature in GeoJSON and zoom
  const handleSelectCountry = (countryObj) => {
    setSelectedCountry(countryObj);
    setSearchQuery("");

    if (!geoJsonData || !countryObj) return;

    // Find matching GeoJSON feature
    const feature = geoJsonData.features.find((f) => {
      const p = f.properties || {};
      const name = p.name || p.NAME || p.NAME_LONG || "";
      const iso3 = p["ISO3166-1-Alpha-3"] || p.ISO_A3 || p.country_iso3 || "";
      return (
        name.toUpperCase() === countryObj.country.toUpperCase() ||
        (countryObj.country_iso3 &&
          iso3.toUpperCase() === countryObj.country_iso3.toUpperCase())
      );
    });

    if (feature && feature.geometry) {
      // Calculate simple bounds from coordinates
      const coords = feature.geometry.coordinates;
      const flatCoords = [];
      const extract = (arr) => {
        if (typeof arr[0] === "number" && typeof arr[1] === "number") {
          flatCoords.push([arr[1], arr[0]]);
        } else if (Array.isArray(arr)) {
          arr.forEach(extract);
        }
      };
      extract(coords);

      if (flatCoords.length > 0) {
        let minLat = 90,
          maxLat = -90,
          minLng = 180,
          maxLng = -180;
        flatCoords.forEach(([lat, lng]) => {
          if (lat < minLat) minLat = lat;
          if (lat > maxLat) maxLat = lat;
          if (lng < minLng) minLng = lng;
          if (lng > maxLng) maxLng = lng;
        });
        setTargetBounds([
          [minLat, minLng],
          [maxLat, maxLng],
        ]);
      }
    }
  };

  const handleResetView = () => {
    setActiveCluster(null);
    setSelectedCountry(null);
    setTargetBounds(null);
    setResetTrigger((prev) => prev + 1);
  };

  const handleFitRegions = () => {
    setFitTrigger((prev) => prev + 1);
  };

  // Helper to look up country stats for a GeoJSON feature
  const getCountryForFeature = (feature) => {
    const p = feature.properties || {};
    const name = (p.name || p.NAME || p.NAME_LONG || "").toUpperCase();
    const iso3 = (p["ISO3166-1-Alpha-3"] || p.ISO_A3 || "").toUpperCase();
    return countryMap.get(name) || countryMap.get(iso3) || null;
  };

  // GeoJSON style handler for choropleth views
  const getGeoJsonStyle = (feature) => {
    const countryObj = getCountryForFeature(feature);

    if (mapView === "clusters") {
      return {
        fillColor: "transparent",
        fillOpacity: 0,
        color: "rgba(148, 163, 184, 0.15)",
        weight: 0.8,
      };
    }

    if (!countryObj) {
      return {
        fillColor: "#0b1929",
        fillOpacity: 0.3,
        color: "rgba(148, 163, 184, 0.12)",
        weight: 0.6,
      };
    }

    if (mapView === "density") {
      const color = getDensityColor(countryObj.total_events, maxCountryEvents);
      return {
        fillColor: color,
        fillOpacity: countryObj.total_events > 0 ? 0.75 : 0.2,
        color: "rgba(255, 255, 255, 0.2)",
        weight: 0.8,
      };
    }

    if (mapView === "disaster") {
      const color = getCategoryColor(countryObj.dominant_category);
      return {
        fillColor: color,
        fillOpacity: 0.75,
        color: "rgba(255, 255, 255, 0.25)",
        weight: 0.8,
      };
    }

    if (mapView === "recent") {
      const color = getDensityColor(countryObj.recent_events, maxCountryRecentEvents);
      return {
        fillColor: color,
        fillOpacity: countryObj.recent_events > 0 ? 0.8 : 0.2,
        color: "rgba(255, 255, 255, 0.2)",
        weight: 0.8,
      };
    }

    if (mapView === "cluster_dist") {
      const color = getClusterColor(countryObj.dominant_cluster);
      return {
        fillColor: color,
        fillOpacity: 0.75,
        color: "rgba(255, 255, 255, 0.25)",
        weight: 0.8,
      };
    }

    return {
      fillColor: "#1e293b",
      fillOpacity: 0.4,
      color: "rgba(255, 255, 255, 0.15)",
      weight: 0.8,
    };
  };

  // GeoJSON interactive event handler
  const onEachCountryFeature = (feature, layer) => {
    const countryObj = getCountryForFeature(feature);

    layer.on({
      mouseover: (e) => {
        if (mapView !== "clusters") {
          e.target.setStyle({
            fillOpacity: 0.95,
            weight: 2,
            color: "#ffffff",
          });
        }
      },
      mouseout: (e) => {
        if (mapView !== "clusters") {
          const style = getGeoJsonStyle(feature);
          e.target.setStyle(style);
        }
      },
      click: () => {
        if (countryObj) {
          handleSelectCountry(countryObj);
        }
      },
    });
  };

  return (
    <section className="panel global-map-panel">
      {/* VIEW SWITCHER CONTROL HEADER */}
      <div className="map-view-header">
        <div className="view-switcher-title">
          <span className="panel-kicker">MAP ANALYSIS VIEW</span>
          <div className="view-header-main">
            <h2>
              {mapView === "clusters" && "K-Means Regional Profiles"}
              {mapView === "density" && "Country Event Density"}
              {mapView === "disaster" && "Dominant Disaster Type"}
              {mapView === "recent" && "Recent Event Activity (2023–2025)"}
              {mapView === "cluster_dist" && "Country Cluster Distribution"}
            </h2>

            <button
              className="explanation-btn"
              onClick={() => setShowExplanation(true)}
            >
              <HelpCircle size={14} />
              <span>How to read this map</span>
            </button>
          </div>

          <p className="view-subtitle">
            {mapView === "clusters" &&
              "Regions grouped by similarity in disaster-event activity and category composition."}
            {mapView === "density" &&
              "Total NASA EONET event observations aggregated per country."}
            {mapView === "disaster" &&
              "Most frequent disaster-event category observed in each country."}
            {mapView === "recent" &&
              "Recent NASA EONET event observations from 2023 to 2025."}
            {mapView === "cluster_dist" &&
              "Main K-Means cluster profile associated with each country."}
          </p>
        </div>

        {/* MAP VIEW BUTTONS */}
        <div className="map-view-tabs">
          <button
            className={`view-tab ${mapView === "clusters" ? "active" : ""}`}
            onClick={() => setMapView("clusters")}
          >
            <Layers size={14} />
            <span>K-Means Clusters</span>
          </button>

          <button
            className={`view-tab ${mapView === "density" ? "active" : ""}`}
            onClick={() => setMapView("density")}
          >
            <Globe2 size={14} />
            <span>Country Event Density</span>
          </button>

          <button
            className={`view-tab ${mapView === "disaster" ? "active" : ""}`}
            onClick={() => setMapView("disaster")}
          >
            <Flame size={14} />
            <span>Dominant Disaster Type</span>
          </button>

          <button
            className={`view-tab ${mapView === "recent" ? "active" : ""}`}
            onClick={() => setMapView("recent")}
          >
            <TrendingUp size={14} />
            <span>Recent Activity</span>
          </button>

          <button
            className={`view-tab ${mapView === "cluster_dist" ? "active" : ""}`}
            onClick={() => setMapView("cluster_dist")}
          >
            <BarChart2 size={14} />
            <span>Cluster Distribution</span>
          </button>
        </div>
      </div>

      {/* SEARCH & LIVE STATUS BAR */}
      <div className="map-subhead-bar">
        <div className="country-search-box">
          <Search size={15} className="search-icon" />
          <input
            type="text"
            placeholder="Search country..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="country-search-input"
          />
          {searchQuery && (
            <button
              className="search-clear"
              onClick={() => setSearchQuery("")}
            >
              <X size={14} />
            </button>
          )}

          {/* SEARCH DROPDOWN RESULTS */}
          {searchResults.length > 0 && (
            <div className="search-dropdown">
              {searchResults.map((c) => (
                <button
                  key={c.country}
                  className="search-item"
                  onClick={() => handleSelectCountry(c)}
                >
                  <div className="search-item-title">{c.country}</div>
                  <div className="search-item-meta">
                    <span>{c.total_events.toLocaleString()} events</span>
                    <span>• {c.dominant_category}</span>
                    <span>• Cluster {c.dominant_cluster}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="map-header-status">
          {!loading && !apiError && validRegions.length > 0 ? (
            <span className="live-badge connected">
              <span className="status-dot"></span>
              API CONNECTED
            </span>
          ) : (
            <span className="live-badge loading">
              <span className="status-dot warning"></span>
              LOADING DATA...
            </span>
          )}
        </div>
      </div>

      {/* MAP CANVAS CONTAINER */}
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

          {/* DARK MAP TILES */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            subdomains="abcd"
            maxZoom={19}
          />

          {/* COUNTRY GEOJSON CHOROPLETH LAYER */}
          {geoJsonData && (
            <GeoJSON
              key={`geojson-${mapView}`}
              data={geoJsonData}
              style={getGeoJsonStyle}
              onEachFeature={onEachCountryFeature}
            />
          )}

          {/* VIEW 1 — REGIONAL CIRCLE MARKERS */}
          {mapView === "clusters" &&
            validRegions.map((region, idx) => {
              const lat = region.region_latitude ?? region.latitude;
              const lng = region.region_longitude ?? region.longitude;
              const cluster = region.cluster;
              const totalEvents = region.total_events || 0;
              const color = getClusterColor(cluster);
              const radius = getMarkerRadius(totalEvents);

              const isHighlighted =
                activeCluster === null || activeCluster === cluster;
              const markerOpacity = isHighlighted ? 0.85 : 0.15;
              const strokeOpacity = isHighlighted ? 0.95 : 0.2;

              return (
                <CircleMarker
                  key={region.region_id || `region-${idx}`}
                  center={[lat, lng]}
                  radius={radius}
                  pathOptions={{
                    fillColor: color,
                    fillOpacity: markerOpacity,
                    color: isHighlighted ? "#ffffff" : color,
                    weight: isHighlighted ? 1.5 : 0.5,
                    opacity: strokeOpacity,
                  }}
                  eventHandlers={{
                    mouseover: (e) => {
                      const layer = e.target;
                      layer.setStyle({
                        fillOpacity: 1,
                        weight: 3,
                        color: "#ffffff",
                      });
                    },
                    mouseout: (e) => {
                      const layer = e.target;
                      layer.setStyle({
                        fillOpacity: markerOpacity,
                        weight: isHighlighted ? 1.5 : 0.5,
                        color: isHighlighted ? "#ffffff" : color,
                      });
                    },
                  }}
                >
                  {/* TOOLTIP */}
                  <Tooltip direction="top" offset={[0, -radius]} opacity={0.95}>
                    <div className="map-tooltip">
                      <strong>Region {region.region_id}</strong>
                      <div style={{ color }}>
                        K-Means Cluster {cluster ?? "N/A"}
                      </div>
                      <small>{totalEvents.toLocaleString()} total events</small>
                    </div>
                  </Tooltip>

                  {/* POPUP */}
                  <Popup className="custom-dark-popup">
                    <div className="popup-card">
                      <div
                        className="popup-header"
                        style={{ borderLeftColor: color }}
                      >
                        <div className="popup-subtitle">REGION</div>
                        <h3 className="popup-title">
                          Region {region.region_id}
                        </h3>
                      </div>

                      <div className="popup-body">
                        <div className="popup-row">
                          <span className="popup-label">K-MEANS CLUSTER</span>
                          <span
                            className="popup-cluster-pill"
                            style={{
                              backgroundColor: `${color}22`,
                              color: color,
                              borderColor: `${color}55`,
                            }}
                          >
                            Cluster {cluster ?? "N/A"}
                          </span>
                        </div>

                        <div className="popup-grid">
                          <div className="popup-metric">
                            <span className="popup-label">TOTAL EVENTS</span>
                            <span className="popup-val">
                              {totalEvents.toLocaleString()}
                            </span>
                          </div>

                          {region.events_per_active_year !== undefined &&
                            region.events_per_active_year !== null && (
                              <div className="popup-metric">
                                <span className="popup-label">
                                  EVENTS / ACTIVE YEAR
                                </span>
                                <span className="popup-val">
                                  {Number(
                                    region.events_per_active_year
                                  ).toFixed(2)}
                                </span>
                              </div>
                            )}

                          {(region.events_2023_2025 !== undefined ||
                            region.recent_events !== undefined) && (
                            <div className="popup-metric">
                              <span className="popup-label">RECENT EVENTS</span>
                              <span className="popup-val">
                                {Number(
                                  region.events_2023_2025 ??
                                    region.recent_events ??
                                    0
                                ).toLocaleString()}
                              </span>
                            </div>
                          )}
                        </div>

                        <div className="popup-coords">
                          <div>
                            <span className="popup-label">LAT:</span>{" "}
                            {Number(lat).toFixed(4)}
                          </div>
                          <div>
                            <span className="popup-label">LNG:</span>{" "}
                            {Number(lng).toFixed(4)}
                          </div>
                        </div>
                      </div>
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
        </MapContainer>

        {/* FLOATING MAP CONTROLS */}
        <div className="map-floating-controls">
          <button
            className="map-control-btn"
            onClick={handleResetView}
            title="Reset View to World [20, 0] Zoom 2"
          >
            <RotateCcw size={14} />
            <span>Reset View</span>
          </button>

          <button
            className="map-control-btn"
            onClick={handleFitRegions}
            title="Fit Bounds to all Regional Coordinates"
          >
            <Maximize2 size={14} />
            <span>Fit Regions</span>
          </button>
        </div>

        {/* FLOATING OVERLAY CARD */}
        <div className="map-overlay-card">
          <div className="overlay-header">
            <Activity size={14} className="overlay-icon" />
            <span>GLOBAL ANALYSIS</span>
          </div>

          <div className="overlay-metrics-grid">
            <div className="overlay-stat">
              <strong className="overlay-num">
                {totalRegionsCount.toLocaleString()}
              </strong>
              <span className="overlay-lbl">Regions</span>
            </div>

            <div className="overlay-stat">
              <strong className="overlay-num">{clusterCount}</strong>
              <span className="overlay-lbl">Clusters</span>
            </div>

            <div className="overlay-stat">
              <strong className="overlay-num">
                {Number(totalEventsCount).toLocaleString()}
              </strong>
              <span className="overlay-lbl">Events</span>
            </div>

            <div className="overlay-stat">
              <strong className="overlay-num">K = {clusterCount}</strong>
              <span className="overlay-lbl">Algorithm</span>
            </div>
          </div>
        </div>

        {/* FLOATING TOP COUNTRIES PANEL */}
        {topCountries.length > 0 && (
          <div className="map-top-countries-card">
            <div className="top-card-header">
              <Globe2 size={13} />
              <span>TOP COUNTRIES BY EVENTS</span>
            </div>

            <div className="top-countries-list">
              {topCountries.map((c, i) => (
                <button
                  key={c.country}
                  className="top-country-row"
                  onClick={() => handleSelectCountry(c)}
                  title={`Focus on ${c.country}`}
                >
                  <span className="rank-num">{i + 1}.</span>
                  <span className="country-name">{c.country}</span>
                  <strong className="country-count">
                    {c.total_events.toLocaleString()}
                  </strong>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* DYNAMIC VIEW LEGEND */}
        <div className="map-legend-card">
          {/* VIEW 1 & VIEW 5: CLUSTERS LEGEND */}
          {(mapView === "clusters" || mapView === "cluster_dist") && (
            <>
              <div className="legend-header">
                <div className="legend-title">
                  <Layers size={13} />
                  <span>
                    {mapView === "clusters"
                      ? "K-MEANS CLUSTERS"
                      : "K-MEANS CLUSTER DISTRIBUTION"}
                  </span>
                </div>

                {activeCluster !== null && (
                  <button
                    className="legend-clear-btn"
                    onClick={() => setActiveCluster(null)}
                  >
                    Clear Filter
                  </button>
                )}
              </div>

              <div className="legend-items">
                {Array.from({ length: clusterCount }).map((_, cid) => {
                  const color = getClusterColor(cid);
                  const isSelected = activeCluster === cid;

                  return (
                    <button
                      key={cid}
                      className={`legend-item ${isSelected ? "selected" : ""} ${
                        activeCluster !== null && !isSelected ? "dimmed" : ""
                      }`}
                      onClick={() =>
                        setActiveCluster(activeCluster === cid ? null : cid)
                      }
                    >
                      <span
                        className="legend-dot"
                        style={{ backgroundColor: color }}
                      />
                      <span className="legend-label">Cluster {cid}</span>
                    </button>
                  );
                })}
              </div>
              <div style={{ fontSize: "9px", color: "#64748b", marginTop: "8px", borderTop: "1px dashed rgba(148,163,184,0.12)", paddingTop: "6px" }}>
                Cluster colors are visual identifiers only. They do not represent risk severity.
              </div>
            </>
          )}

          {/* VIEW 2: EVENT DENSITY LEGEND */}
          {mapView === "density" && (
            <>
              <div className="legend-title" style={{ marginBottom: "8px" }}>
                <span>OBSERVED EONET EVENT DENSITY</span>
              </div>
              <div className="density-gradient-bar" />
              <div className="gradient-labels">
                <span>Low (1)</span>
                <span>High ({maxCountryEvents.toLocaleString()})</span>
              </div>
            </>
          )}

          {/* VIEW 3: DOMINANT DISASTER CATEGORY LEGEND */}
          {mapView === "disaster" && (
            <>
              <div className="legend-title" style={{ marginBottom: "8px" }}>
                <span>DOMINANT DISASTER CATEGORY</span>
              </div>
              <div className="category-legend-grid">
                {activeCategories.slice(0, 6).map((cat) => (
                  <div key={cat} className="category-legend-item">
                    <span
                      className="legend-dot"
                      style={{ backgroundColor: getCategoryColor(cat) }}
                    />
                    <span className="legend-label">{cat}</span>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* VIEW 4: RECENT ACTIVITY LEGEND */}
          {mapView === "recent" && (
            <>
              <div className="legend-title" style={{ marginBottom: "8px" }}>
                <span>RECENT ACTIVITY (2023–2025)</span>
              </div>
              <div className="density-gradient-bar" />
              <div className="gradient-labels">
                <span>Low (1)</span>
                <span>High ({maxCountryRecentEvents.toLocaleString()})</span>
              </div>
            </>
          )}
        </div>

        {/* SELECTED COUNTRY POPUP / CARD OVERLAY */}
        {selectedCountry && (
          <div className="selected-country-overlay">
            <div className="country-card-header">
              <div>
                <span className="country-eyebrow">COUNTRY ANALYSIS</span>
                <h3>{selectedCountry.country}</h3>
              </div>
              <button
                className="country-close"
                onClick={() => setSelectedCountry(null)}
              >
                <X size={16} />
              </button>
            </div>

            <div className="country-card-grid">
              <div className="country-metric">
                <span className="metric-lbl">EVENT OBSERVATIONS</span>
                <strong className="metric-val">
                  {selectedCountry.total_events?.toLocaleString() ?? "-"}
                </strong>
              </div>

              <div className="country-metric">
                <span className="metric-lbl">RECENT ACTIVITY (2023-2025)</span>
                <strong className="metric-val">
                  {selectedCountry.recent_events?.toLocaleString() ?? "-"}
                </strong>
              </div>

              <div className="country-metric">
                <span className="metric-lbl">DOMINANT CATEGORY</span>
                <strong
                  className="metric-val"
                  style={{
                    color: getCategoryColor(selectedCountry.dominant_category),
                  }}
                >
                  {selectedCountry.dominant_category ?? "-"}
                </strong>
              </div>

              <div className="country-metric">
                <span className="metric-lbl">CATEGORY SHARE</span>
                <strong className="metric-val">
                  {selectedCountry.dominant_category_proportion != null
                    ? `${selectedCountry.dominant_category_proportion}%`
                    : "-"}
                </strong>
              </div>

              <div className="country-metric">
                <span className="metric-lbl">REGIONS ANALYZED</span>
                <strong className="metric-val">
                  {selectedCountry.region_count ?? "-"}
                </strong>
              </div>

              <div className="country-metric" style={{ gridColumn: "span 2" }}>
                <button
                  className="primary-button"
                  style={{ width: "100%", marginTop: "4px", padding: "8px", fontSize: "11px" }}
                  onClick={() => {
                    if (onSelectDrawer) onSelectDrawer(selectedCountry);
                  }}
                >
                  Inspect Complete Country Profile →
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* EXPLANATION MODAL */}
      {showExplanation && (
        <div className="modal-backdrop" onClick={() => setShowExplanation(false)}>
          <div
            className="explanation-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <div className="modal-title">
                <Info size={18} />
                <h3>How to Read This Map</h3>
              </div>
              <button
                className="modal-close"
                onClick={() => setShowExplanation(false)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              <div className="explanation-section">
                <h4>1. K-Means Clusters</h4>
                <p>
                  Shows regional profiles discovered by the machine-learning
                  model. Regions are grouped by similarity in disaster-event
                  frequency and category composition.
                </p>
              </div>

              <div className="explanation-section">
                <h4>2. Country Event Density</h4>
                <p>
                  Displays country choropleth shading corresponding to total
                  observed NASA EONET event observations.
                </p>
              </div>

              <div className="explanation-section">
                <h4>3. Dominant Disaster Type</h4>
                <p>
                  Highlights the most common event category associated with
                  each country (e.g. Wildfires, Severe Storms, Floods).
                </p>
              </div>

              <div className="explanation-section">
                <h4>4. Recent Activity (2023–2025)</h4>
                <p>
                  Shows event observations recorded during the recent 2023–2025
                  period.
                </p>
              </div>

              <div className="explanation-section">
                <h4>5. Cluster Distribution</h4>
                <p>
                  Displays each country colored by its dominant K-Means cluster
                  profile.
                </p>
              </div>

              <div className="explanation-disclaimer">
                <strong>IMPORTANT NOTICE:</strong>
                <p>
                  These visualizations describe observed NASA EONET event
                  patterns. They are NOT official disaster-risk scores or risk
                  predictions.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
