import React, { useEffect } from "react";
import { Info, X, Map, Layers, Search, BarChart2, ShieldAlert } from "lucide-react";

export default function HelpModal({ isOpen, onClose }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="explanation-modal help-modal-card" onClick={(e) => e.stopPropagation()}>
        {/* HEADER */}
        <div className="modal-header">
          <div className="modal-title">
            <Info size={18} />
            <h3>What Does This Dashboard Do?</h3>
          </div>
          <button className="modal-close" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        {/* BODY */}
        <div className="modal-body">
          <div className="help-intro-box">
            <p>
              This dashboard analyzes historical natural-event observations from <strong>NASA EONET</strong> (2015–2025) and groups geographical regions into similarity profiles using <strong>K-Means clustering</strong>.
            </p>
          </div>

          <h4 className="help-steps-heading">5-STEP GUIDE TO EXPLORING THE DATA</h4>

          <div className="help-steps-grid">
            <div className="help-step-item">
              <div className="step-badge">1</div>
              <div className="step-content">
                <div className="step-title">
                  <Map size={14} /> Explore the Global Map
                </div>
                <p>Switch between 5 analytical views (K-Means Clusters, Event Density, Disaster Category, Recent Activity, and Cluster Distribution).</p>
              </div>
            </div>

            <div className="help-step-item">
              <div className="step-badge">2</div>
              <div className="step-content">
                <div className="step-title">
                  <BarChart2 size={14} /> Check Trends & Categories
                </div>
                <p>Inspect yearly observation trends from 2015–2025 and compare dominant disaster event categories.</p>
              </div>
            </div>

            <div className="help-step-item">
              <div className="step-badge">3</div>
              <div className="step-content">
                <div className="step-title">
                  <Search size={14} /> Search Regions & Countries
                </div>
                <p>Use the Region Explorer or Country Search to open the slide-in detail drawer for any country or spatial region.</p>
              </div>
            </div>

            <div className="help-step-item">
              <div className="step-badge">4</div>
              <div className="step-content">
                <div className="step-title">
                  <Layers size={14} /> Inspect Discovered Clusters
                </div>
                <p>Examine the nine regional profiles discovered by K-Means and see why regions are grouped together.</p>
              </div>
            </div>

            <div className="help-step-item">
              <div className="step-badge">5</div>
              <div className="step-content">
                <div className="step-title">
                  <Info size={14} /> Learn Terminology As You Explore
                </div>
                <p>Hover over or click any <strong>ⓘ</strong> icon to read plain-English explanations of data-mining concepts.</p>
              </div>
            </div>
          </div>

          {/* SAFETY DISCLAIMER */}
          <div className="explanation-disclaimer">
            <div className="disclaimer-header">
              <ShieldAlert size={15} />
              <strong>IMPORTANT DATA INTEGRITY & SAFETY NOTICE</strong>
            </div>
            <p>
              This system describes mathematical patterns in historical NASA EONET event observations. Cluster labels and numbers represent model-generated groups, NOT official administrative disaster-risk predictions or emergency danger classifications.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
