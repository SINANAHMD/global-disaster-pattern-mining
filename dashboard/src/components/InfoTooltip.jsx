import React, { useState } from "react";
import { Info, HelpCircle } from "lucide-react";

export const GLOSSARY_TERMS = {
  "K-Means": {
    term: "K-Means Clustering",
    definition:
      "An unsupervised machine-learning algorithm that groups regions into clusters based on similarity in their numerical event features.",
    whyItMatters:
      "Helps discover natural regional groupings without needing human labels or predefined boundaries.",
  },
  Cluster: {
    term: "Disaster Event Cluster",
    definition:
      "A group of geographical regions that exhibit similar historical natural-event activity and category compositions.",
    whyItMatters:
      "Allows comparing regions with similar risk profiles regardless of political borders.",
  },
  "Silhouette Score": {
    term: "Silhouette Score Quality Metric",
    definition:
      "A validation metric (from -1 to +1) measuring how well-separated and cohesive clusters are.",
    whyItMatters:
      "Scores above 0.40 indicate robust, well-defined cluster separation in the data.",
  },
  "Elbow Method": {
    term: "Elbow Method Optimization",
    definition:
      "A heuristic technique used to determine the optimal number of clusters (K=9) by analyzing within-cluster variation.",
    whyItMatters:
      "Ensures the model selects the ideal number of clusters without overfitting.",
  },
  Feature: {
    term: "Regional Feature Vector",
    definition:
      "Numerical properties extracted from raw EONET events (such as total count, yearly frequency, and category proportions).",
    whyItMatters:
      "Serves as the input data used by the algorithm to evaluate similarity.",
  },
  Standardization: {
    term: "Feature Standardization (StandardScaler)",
    definition:
      "Transforming feature values to a uniform scale (mean=0, std=1) before distance calculations.",
    whyItMatters:
      "Prevents large numbers (like total events) from overwhelming smaller percentage features.",
  },
  PCA: {
    term: "Principal Component Analysis (PCA)",
    definition:
      "A dimensionality reduction method that compresses multi-dimensional feature data into principal visual components.",
    whyItMatters:
      "Allows visualizing complex multi-feature cluster structures in 2D and 3D space.",
  },
  Region: {
    term: "Spatial Analysis Region",
    definition:
      "A grid-based geographic analysis unit created from event coordinates in the dataset.",
    whyItMatters:
      "Standardizes spatial units for objective machine-learning comparison.",
  },
  "Event Observation": {
    term: "EONET Event Observation",
    definition:
      "A coordinate-based natural hazard record (wildfire, severe storm, flood, volcano, etc.) from NASA EONET.",
    whyItMatters:
      "Forms the underlying raw empirical data for all dashboard statistics.",
  },
  "Dominant Disaster Type": {
    term: "Dominant Disaster Category",
    definition:
      "The single most frequent event category recorded within a specific region or country.",
    whyItMatters:
      "Identifies the primary natural driver influencing local environmental activity.",
  },
  "Event Density": {
    term: "Observed Event Density",
    definition:
      "The concentration of recorded natural event observations per geographic area.",
    whyItMatters:
      "Highlights areas with high historical frequency of tracked natural occurrences.",
  },
  "Recent Activity": {
    term: "Recent Activity (2023–2025)",
    definition:
      "Observed natural events recorded during the recent 2023 to 2025 analysis period.",
    whyItMatters:
      "Helps detect recent shifts in hazard frequency compared to earlier years.",
  },
  "Cluster Distribution": {
    term: "Geographic Cluster Distribution",
    definition:
      "The spatial layout showing which model-generated cluster profile is dominant in each country.",
    whyItMatters:
      "Visualizes how regional disaster profiles span across global continents.",
  },
  "Regional Profile": {
    term: "Regional Event Profile",
    definition:
      "The complete numerical summary of event frequencies, trends, and category shares for a region.",
    whyItMatters:
      "Defines the unique signature used to assign a region to its K-Means cluster.",
  },
  API: {
    term: "FastAPI Backend Connection",
    definition:
      "High-performance REST API backend serving processed data, statistics, and model parameters.",
    whyItMatters:
      "Connects the React interactive interface directly to backend analytical datasets.",
  },
  "NASA EONET": {
    term: "NASA Earth Observatory Natural Event Tracker",
    definition:
      "NASA's global metadata repository continuously tracking natural hazards across Earth.",
    whyItMatters:
      "Provides trusted, verified satellite-derived data for scientific intelligence.",
  },
};

export default function InfoTooltip({ term, customTitle, children, inline = false }) {
  const [showPopover, setShowPopover] = useState(false);
  const info = GLOSSARY_TERMS[term] || {
    term: customTitle || term,
    definition: children || "Technical analytical concept used in dashboard calculations.",
    whyItMatters: "Helps interpret data-mining and regional pattern results.",
  };

  return (
    <span className={`info-tooltip-wrapper ${inline ? "inline" : ""}`}>
      <button
        type="button"
        className="info-tooltip-trigger"
        onClick={() => setShowPopover(!showPopover)}
        onMouseEnter={() => setShowPopover(true)}
        onMouseLeave={() => setShowPopover(false)}
        aria-label={`Learn about ${info.term}`}
      >
        <HelpCircle size={13} className="info-icon" />
      </button>

      {showPopover && (
        <span className="info-popover-card">
          <span className="info-popover-header">
            <Info size={13} className="popover-icon" />
            <strong className="info-popover-title">{info.term}</strong>
          </span>
          <span className="info-popover-body">{info.definition}</span>
          {info.whyItMatters && (
            <span className="info-popover-why">
              <strong>Why it matters:</strong> {info.whyItMatters}
            </span>
          )}
        </span>
      )}
    </span>
  );
}
