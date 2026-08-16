import React from "react";
import { Cpu, Award, Sliders, CheckCircle2, Info } from "lucide-react";
import InfoTooltip from "./InfoTooltip";

export default function PredictionModelInfo() {
  return (
    <div className="panel prediction-model-info-panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">MODEL ARCHITECTURE & PERFORMANCE</span>
          <h2>Calibrated Logistic Regression Model</h2>
          <p>Statistical machine-learning pipeline estimating next-month natural event likelihood.</p>
        </div>
        <InfoTooltip term="Logistic Regression" customTitle="Logistic Regression Model">
          A statistical classification model that estimates the probability of a binary event outcome based on feature inputs.
        </InfoTooltip>
      </div>

      <div className="model-info-body" style={{ padding: "24px" }}>
        {/* 5-STEP VISUAL FLOW */}
        <div className="model-pipeline-flow">
          <div className="flow-step">
            <span className="flow-step-num">1</span>
            <span className="flow-step-text">Historical EONET Activity</span>
          </div>
          <span className="flow-divider">➔</span>

          <div className="flow-step">
            <span className="flow-step-num">2</span>
            <span className="flow-step-text">Recent Event Patterns</span>
          </div>
          <span className="flow-divider">➔</span>

          <div className="flow-step">
            <span className="flow-step-num">3</span>
            <span className="flow-step-text">Seasonal Trends</span>
          </div>
          <span className="flow-divider">➔</span>

          <div className="flow-step">
            <span className="flow-step-num">4</span>
            <span className="flow-step-text">Logistic Regression</span>
          </div>
          <span className="flow-divider">➔</span>

          <div className="flow-step active">
            <span className="flow-step-num">5</span>
            <span className="flow-step-text">Calibrated Probability</span>
          </div>
        </div>

        {/* VALIDATED PERFORMANCE METRICS GRID */}
        <div className="drawer-metrics-grid" style={{ marginTop: "24px" }}>
          <div className="drawer-metric-card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="metric-lbl">MODEL ARCHITECTURE</span>
              <InfoTooltip term="Logistic Regression" inline />
            </div>
            <strong className="metric-val accent">Calibrated Logistic Regression</strong>
            <span className="metric-sub">Sigmoid probability calibration</span>
          </div>

          <div className="drawer-metric-card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="metric-lbl">DISCRIMINATION (ROC-AUC)</span>
              <InfoTooltip term="ROC-AUC" customTitle="ROC-AUC Metric">
                Measures how well the model separates higher-probability cases from lower-probability cases. Scale 0.5 to 1.0.
              </InfoTooltip>
            </div>
            <strong className="metric-val" style={{ color: "var(--accent)" }}>0.81 (ROC-AUC)</strong>
            <span className="metric-sub">Strong regional discrimination</span>
          </div>

          <div className="drawer-metric-card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="metric-lbl">PROBABILITY ACCURACY (BRIER SCORE)</span>
              <InfoTooltip term="Brier Score" customTitle="Brier Score Metric">
                Measures how closely predicted probabilities match observed outcomes. Lower values indicate better calibration accuracy.
              </InfoTooltip>
            </div>
            <strong className="metric-val" style={{ color: "var(--success)" }}>0.13 (Brier Score)</strong>
            <span className="metric-sub">Calibrated probability alignment</span>
          </div>

          <div className="drawer-metric-card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="metric-lbl">PREDICTION TARGET</span>
            </div>
            <strong className="metric-val">Next-Month Event Likelihood</strong>
            <span className="metric-sub">Statistical probability estimate</span>
          </div>
        </div>
      </div>
    </div>
  );
}
