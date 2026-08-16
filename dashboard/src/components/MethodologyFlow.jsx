import React, { useState } from "react";
import { Database, Filter, MapPin, Cpu, Sliders, Layers, Award, Monitor, ChevronRight } from "lucide-react";

export const PIPELINE_STEPS = [
  {
    id: "eonet",
    icon: Database,
    title: "NASA EONET Data",
    short: "Raw Event Stream",
    description: "Inbound satellite-tracked natural hazard event observations captured from 2015 to 2025.",
  },
  {
    id: "cleaning",
    icon: Filter,
    title: "Data Cleaning",
    short: "Validation & Deduplication",
    description: "Removal of invalid coordinates, null timestamps, and duplicate event geometries.",
  },
  {
    id: "mapping",
    icon: MapPin,
    title: "Geographic Mapping",
    short: "Country & Spatial Grid",
    description: "Associating raw coordinates with spatial grid regions and sovereign country boundaries.",
  },
  {
    id: "features",
    icon: Cpu,
    title: "Feature Engineering",
    short: "Regional Aggregation",
    description: "Computing total event counts, yearly rates, recent shares, and disaster category proportions.",
  },
  {
    id: "scaling",
    icon: Sliders,
    title: "Standardization",
    short: "StandardScaler Transformation",
    description: "Transforming numerical features to zero mean and unit variance for distance-based clustering.",
  },
  {
    id: "kmeans",
    icon: Layers,
    title: "K-Means Model",
    short: "K = 9 Clustering",
    description: "Grouping regions into 9 similarity profiles using Euclidean distance optimization.",
  },
  {
    id: "eval",
    icon: Award,
    title: "Cluster Evaluation",
    short: "Silhouette Score = 0.4682",
    description: "Validating cluster separation and cohesion using Elbow curves and Silhouette metrics.",
  },
  {
    id: "viz",
    icon: Monitor,
    title: "Data Intelligence",
    short: "Interactive Dashboard",
    description: "Delivering real-time multi-view geospatial maps, temporal trends, and region detail drawers.",
  },
];

export default function MethodologyFlow() {
  const [activeStep, setActiveStep] = useState(PIPELINE_STEPS[5]);

  return (
    <div className="methodology-flow-card">
      <div className="flow-header">
        <div className="flow-title-group">
          <span className="panel-kicker">DATA MINING PIPELINE</span>
          <h3>End-to-End Analytical Architecture</h3>
        </div>
        <p className="flow-subtitle">
          Click any stage in the pipeline below to inspect its data processing methodology.
        </p>
      </div>

      {/* PIPELINE STEPS CAROUSEL / GRID */}
      <div className="pipeline-steps-wrapper">
        {PIPELINE_STEPS.map((step, idx) => {
          const Icon = step.icon;
          const isSelected = activeStep.id === step.id;

          return (
            <React.Fragment key={step.id}>
              <button
                type="button"
                className={`pipeline-step-btn ${isSelected ? "selected" : ""}`}
                onClick={() => setActiveStep(step)}
              >
                <div className="step-num">{idx + 1}</div>
                <div className="step-icon-wrap">
                  <Icon size={16} />
                </div>
                <span className="step-btn-title">{step.title}</span>
                <span className="step-btn-short">{step.short}</span>
              </button>

              {idx < PIPELINE_STEPS.length - 1 && (
                <div className="pipeline-arrow">
                  <ChevronRight size={14} />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* ACTIVE STEP DETAIL DISPLAY */}
      {activeStep && (
        <div className="active-step-detail-card">
          <div className="detail-header">
            <div className="detail-icon-badge">
              <activeStep.icon size={18} />
            </div>
            <div>
              <span className="detail-stage-tag">STAGE METHODOLOGY</span>
              <h4>{activeStep.title}</h4>
            </div>
          </div>
          <p className="detail-description">{activeStep.description}</p>
        </div>
      )}
    </div>
  );
}
