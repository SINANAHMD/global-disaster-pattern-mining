/**
 * Geographic Context Engine
 * Maps spatial grid coordinates to human-readable Continents, Sub-regions,
 * formatted coordinate strings, and nearby country descriptions.
 */

// Known Grid ID specific geographical mappings for high precision
const KNOWN_GRID_LOCATIONS = {
  GRID_N00_E020: {
    continent: "Africa",
    subregion: "Central Africa",
    nearbyCountries: ["Democratic Republic of the Congo", "Republic of the Congo", "Central African Republic", "Cameroon", "Gabon"],
    geoLabel: "Central Africa",
  },
  GRID_N10_E076: {
    continent: "Asia",
    subregion: "South Asia",
    nearbyCountries: ["India (Kerala / Tamil Nadu)"],
    geoLabel: "South Asia · India",
  },
  GRID_N20_E078: {
    continent: "Asia",
    subregion: "South Asia",
    nearbyCountries: ["India (Maharashtra / Madhya Pradesh)"],
    geoLabel: "South Asia · India",
  },
  GRID_N20_E090: {
    continent: "Asia",
    subregion: "South Asia / Bay of Bengal",
    nearbyCountries: ["India (West Bengal)", "Bangladesh", "Myanmar"],
    geoLabel: "South Asia · Bay of Bengal",
  },
  GRID_N15_E078: {
    continent: "Asia",
    subregion: "South Asia",
    nearbyCountries: ["India (Andhra Pradesh / Karnataka)"],
    geoLabel: "South Asia · India",
  },
  GRID_N35_W118: {
    continent: "North America",
    subregion: "North America",
    nearbyCountries: ["United States (California)"],
    geoLabel: "North America · USA",
  },
};

/**
 * Format latitude and longitude into 0.0°N/S, 0.0°E/W format
 */
export function formatCoordinates(lat, lon) {
  if (lat == null || lon == null || isNaN(lat) || isNaN(lon)) {
    return "Coordinates N/A";
  }
  const latStr = `${Math.abs(lat).toFixed(1)}°${lat >= 0 ? "N" : "S"}`;
  const lonStr = `${Math.abs(lon).toFixed(1)}°${lon >= 0 ? "E" : "W"}`;
  return `${latStr}, ${lonStr}`;
}

/**
 * Extract lat and lon numbers from a grid ID string like GRID_N20_E090 or GRID_S10_W050
 */
export function parseGridId(gridId) {
  if (!gridId || typeof gridId !== "string") return null;
  const match = gridId.match(/GRID_([NS])(\d+)_([EW])(\d+)/i);
  if (!match) return null;

  const latSign = match[1].toUpperCase() === "S" ? -1 : 1;
  const latVal = parseFloat(match[2]) * latSign;

  const lonSign = match[3].toUpperCase() === "W" ? -1 : 1;
  const lonVal = parseFloat(match[4]) * lonSign;

  return { lat: latVal, lon: lonVal };
}

/**
 * Get comprehensive geographic context object for a region or coordinate pair
 */
export function getGeographicContext(lat, lon, gridId = "") {
  let finalLat = lat;
  let finalLon = lon;

  if ((finalLat == null || finalLon == null) && gridId) {
    const parsed = parseGridId(gridId);
    if (parsed) {
      finalLat = parsed.lat;
      finalLon = parsed.lon;
    }
  }

  // Check known explicit grid lookup first
  if (gridId && KNOWN_GRID_LOCATIONS[gridId.toUpperCase()]) {
    const known = KNOWN_GRID_LOCATIONS[gridId.toUpperCase()];
    return {
      continent: known.continent,
      subregion: known.subregion,
      nearbyCountries: known.nearbyCountries,
      geoLabel: known.geoLabel,
      formattedCoords: formatCoordinates(finalLat, finalLon),
      isApproximate: false,
    };
  }

  if (finalLat == null || finalLon == null || isNaN(finalLat) || isNaN(finalLon)) {
    return {
      continent: "Global",
      subregion: "Spatial Grid Unit",
      nearbyCountries: ["Geographic context unavailable"],
      geoLabel: "Spatial Region",
      formattedCoords: "Coordinates N/A",
      isApproximate: true,
    };
  }

  // Determine Continent & Sub-region based on spatial coordinates
  let continent = "Global";
  let subregion = "Spatial Unit";
  let nearbyCountries = [];

  if (finalLat < -60) {
    continent = "Antarctica";
    subregion = "Antarctic Ocean";
  } else if (finalLat >= -35 && finalLat <= 38 && finalLon >= -20 && finalLon <= 52) {
    continent = "Africa";
    if (finalLat > 15) subregion = "North Africa";
    else if (finalLat > 5 && finalLon < 15) subregion = "West Africa";
    else if (finalLat >= -10 && finalLat <= 10 && finalLon >= 10 && finalLon <= 32) subregion = "Central Africa";
    else if (finalLat >= -15 && finalLon > 30) subregion = "East Africa";
    else subregion = "Southern Africa";
  } else if (finalLat >= -10 && finalLat <= 80 && finalLon >= 45 && finalLon <= 180) {
    continent = "Asia";
    if (finalLat >= 5 && finalLat <= 38 && finalLon >= 68 && finalLon <= 98) {
      subregion = "South Asia (India Region)";
      nearbyCountries = ["India", "Pakistan", "Bangladesh", "Nepal", "Sri Lanka"];
    } else if (finalLat > 12 && finalLat <= 45 && finalLon >= 98 && finalLon <= 145) {
      subregion = "East Asia";
      nearbyCountries = ["China", "Japan", "South Korea", "Taiwan"];
    } else if (finalLat >= -10 && finalLat <= 20 && finalLon >= 95 && finalLon <= 140) {
      subregion = "Southeast Asia";
      nearbyCountries = ["Indonesia", "Philippines", "Vietnam", "Thailand", "Malaysia"];
    } else if (finalLat >= 12 && finalLat <= 45 && finalLon >= 35 && finalLon <= 65) {
      subregion = "Middle East";
      nearbyCountries = ["Saudi Arabia", "UAE", "Iran", "Iraq", "Oman"];
    } else {
      subregion = "Central / North Asia";
    }
  } else if (finalLat >= 35 && finalLat <= 72 && finalLon >= -25 && finalLon <= 45) {
    continent = "Europe";
    if (finalLat > 55) subregion = "Northern Europe";
    else if (finalLon < 10) subregion = "Western Europe";
    else if (finalLat < 45) subregion = "Southern Europe";
    else subregion = "Eastern Europe";
  } else if (finalLat >= 15 && finalLat <= 85 && finalLon >= -170 && finalLon <= -30) {
    continent = "North America";
    if (finalLat < 25) subregion = "Central America & Caribbean";
    else subregion = "North America";
  } else if (finalLat >= -58 && finalLat < 15 && finalLon >= -90 && finalLon <= -30) {
    continent = "South America";
    if (finalLat > 0) subregion = "Northern South America";
    else if (finalLat > -20) subregion = "Amazonia / Central South America";
    else subregion = "Southern Cone";
  } else if (finalLat >= -50 && finalLat <= 0 && finalLon >= 110 && finalLon <= 180) {
    continent = "Oceania";
    subregion = "Australia & Pacific Islands";
    nearbyCountries = ["Australia", "New Zealand", "Papua New Guinea"];
  }

  if (nearbyCountries.length === 0) {
    nearbyCountries = [`Region around ${formatCoordinates(finalLat, finalLon)}`];
  }

  const geoLabel = `${continent} · ${subregion}`;

  return {
    continent,
    subregion,
    nearbyCountries,
    geoLabel,
    formattedCoords: formatCoordinates(finalLat, finalLon),
    isApproximate: true,
  };
}
