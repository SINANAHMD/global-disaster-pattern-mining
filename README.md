# 🌍 Global Disaster Pattern Mining & Prediction Platform

> An end-to-end data science and geospatial intelligence platform for analyzing NASA EONET disaster events, discovering global spatial patterns, and estimating next-month disaster-event likelihood.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![React](https://img.shields.io/badge/React-Frontend-61DAFB)
![Machine Learning](https://img.shields.io/badge/ML-scikit--learn-orange)
![Geospatial](https://img.shields.io/badge/Geospatial-Leaflet-green)
![Data Source](https://img.shields.io/badge/Data-NASA%20EONET-red)

---

## 🚀 Project Overview

Global Disaster Pattern Mining is an end-to-end analytical platform built around NASA EONET disaster-event data.

The system combines:

- Data collection and cleaning
- Exploratory data analysis
- Geospatial analysis
- Regional feature engineering
- K-Means clustering
- Disaster-category analysis
- Probability calibration
- Next-month event prediction
- India state-level disaster analysis
- Interactive geospatial visualization
- FastAPI backend services
- React-based analytical dashboard

The goal is to transform large-scale disaster-event observations into an interactive research and decision-support interface.

---

## 🎯 Key Objectives

### 1. Global Disaster Analysis

Analyze historical disaster-event activity across countries and regions.

### 2. Geospatial Pattern Discovery

Identify geographic regions with similar disaster-event characteristics using clustering.

### 3. Disaster Trend Analysis

Study temporal patterns including:

- Yearly activity
- Monthly activity
- Disaster categories
- Regional activity
- Event density

### 4. Predictive Intelligence

Estimate the statistical likelihood of an event occurring in the following month based on historical patterns.

### 5. India State-Level Analysis

Provide a dedicated state-level analytical pipeline for India using administrative boundaries and spatial event mapping.

---

# 🧠 Machine Learning Pipeline

```text
NASA EONET
     │
     ▼
Data Collection
     │
     ▼
Data Cleaning & Validation
     │
     ▼
Feature Engineering
     │
     ├───────────────┐
     ▼               ▼
Global Analysis   India State Mapping
     │               │
     ▼               ▼
K-Means Clustering  State Features
     │               │
     ▼               ▼
Cluster Analysis   State Prediction
     │               │
     └───────┬───────┘
             ▼
      Prediction Layer
             │
             ▼
    Probability Calibration
             │
             ▼
      FastAPI Backend
             │
             ▼
      React Dashboard

🌎 Global Analytics

The platform provides interactive global analysis including:

Country event density
Dominant disaster category
Recent disaster activity
Regional profiles
K-Means clusters
Cluster distribution
Historical trends

The dashboard uses interactive maps to provide geographic context to the analytical results.

🔮 Prediction Intelligence

The prediction module estimates:

Next-Month Event Likelihood

using historical temporal features such as:

Current event activity
Previous-month activity
Previous 3-month activity
Previous 6-month activity
Previous 12-month activity
Historical event activity
Seasonal features
Time progression

Probability calibration is applied to improve the reliability of predicted probabilities.

Calibration Results

The final global calibrated model achieved approximately:

Metric	Result
ROC-AUC	0.81
Brier Score	0.13

The calibrated model substantially improves probability quality compared with the raw model.

🇮🇳 India State-Level Intelligence

A separate India-focused pipeline maps EONET event geometries to Indian state/UT administrative boundaries.

Current pipeline:

EONET Event Geometry
        │
        ▼
India ADM1 Boundaries
        │
        ▼
Spatial Join
        │
        ▼
State ↔ Event Association
        │
        ▼
Monthly State Timeline
        │
        ▼
Prediction Features
        │
        ▼
State-Level Risk Engine

The current dataset contains:

20 represented Indian states
66 unique events affecting India
71 state-event associations
2 multi-state events
2,380 prediction rows

The India state pipeline also provides data-confidence indicators because the available historical state-level observations are limited.

🗺️ Interactive Dashboard

The React dashboard provides:

Global Map

Interactive global disaster-event density and regional analysis.

Prediction Intelligence

Interactive next-month likelihood visualization.

Clusters

Geospatial K-Means cluster exploration.

Trends

Historical disaster-event trends.

Categories

Disaster-category distribution and analysis.

Region Explorer

Detailed regional profiles.

India State Intelligence

State-level disaster activity and prediction analysis.

🛠️ Technology Stack
Backend
Python
FastAPI
Pandas
NumPy
Scikit-learn
Joblib
Shapely
Frontend
React
Vite
JavaScript
CSS
Leaflet
Machine Learning
Logistic Regression
Random Forest
Histogram Gradient Boosting
K-Means Clustering
StandardScaler
Probability Calibration
Geospatial
Shapely
GeoJSON
Leaflet
Administrative boundary datasets
Data
NASA EONET disaster-event observations
📁 Project Structure
global-disaster-pattern-mining/
│
├── backend/
│   ├── main.py
│   └── prediction_api.py
│
├── dashboard/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── scripts/
│   ├── build_india_state_dataset.py
│   └── validate_india_state_mapping.py
│
├── src/
│   ├── collect_eonet.py
│   ├── clean_eonet.py
│   ├── prepare_eonet.py
│   ├── eda.py
│   ├── regional_features.py
│   ├── train_final_kmeans.py
│   ├── train_prediction_models.py
│   ├── calibrate_prediction_model.py
│   ├── final_calibrated_prediction.py
│   ├── train_india_state_models.py
│   └── build_india_state_risk_engine.py
│
├── data/
│   └── prediction/
│
├── requirements.txt
├── README.md
└── .gitignore
⚙️ Local Development
1. Clone
git clone https://github.com/SINANAHMD/global-disaster-pattern-mining.git
cd global-disaster-pattern-mining
2. Create virtual environment
python -m venv .venv
Windows
.venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Start backend
uvicorn backend.main:app --reload

Backend:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs
5. Start dashboard
cd dashboard
npm install
npm run dev
📊 Model Evaluation

Because disaster events are highly imbalanced, evaluation should not rely on accuracy alone.

The project considers:

Precision
Recall
F1-score
ROC-AUC
PR-AUC
Brier Score
Probability calibration

This is especially important when evaluating rare-event prediction.

⚠️ Important Limitations

This project is a research and analytical prediction system.

Its predictions are statistical estimates derived from historical EONET observations.

The system is NOT:

An official disaster warning system
A government emergency alert system
A guaranteed disaster forecast
A real-time emergency notification service
A replacement for official meteorological or disaster-management authorities

A high predicted probability should be interpreted as:

Historical patterns indicate an increased statistical likelihood of an EONET-type event being observed in the target period.

It does not mean that a disaster is guaranteed to occur.

India state-level predictions should also be interpreted carefully because the available state-level event observations are limited.

🔬 Research Focus

This project demonstrates an end-to-end workflow combining:

Data Engineering → Exploratory Analysis → Geospatial Analytics → Machine Learning → Probability Calibration → Prediction → API Development → Interactive Visualization

It is designed as a portfolio/research project demonstrating practical application of data science and machine learning to geospatial disaster-event data.

👨‍💻 Author

Sinan Ahmd

B.Sc. Computer Science