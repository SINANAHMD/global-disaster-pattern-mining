import React from "react";
import { Info, ShieldCheck } from "lucide-react";

export default function PredictionDisclaimer() {
  return (
    <div className="prediction-disclaimer-card">
      <div className="disclaimer-icon-wrap">
        <ShieldCheck size={20} className="disclaimer-icon" />
      </div>
      <div className="disclaimer-content">
        <h4>STATISTICAL MODEL INTEGRITY & SAFETY NOTICE</h4>
        <p>
          Prediction estimates are statistical outputs derived from historical NASA EONET event observations using calibrated Logistic Regression. They represent calculated probabilities for historical analysis and research purposes. They are <strong>not official disaster warnings, real-time emergency alerts, or guarantees of future events</strong>.
        </p>
      </div>
    </div>
  );
}
