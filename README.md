# 🌍 Global Disaster Pattern Mining & Prediction Platform

> An end-to-end **Data Science, Machine Learning, and Geospatial Intelligence platform** for analyzing NASA EONET disaster-event observations, discovering spatial patterns, and estimating next-month event likelihood.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-Build%20Tool-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Scikit-learn](https://img.shields.io/badge/ML-scikit--learn-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Leaflet](https://img.shields.io/badge/Maps-Leaflet-199900?logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![NASA EONET](https://img.shields.io/badge/Data-NASA%20EONET-EF3B2D)](https://eonet.gsfc.nasa.gov/)

---

## 📌 Overview

**Global Disaster Pattern Mining & Prediction Platform** is a full-stack analytical system built around disaster-event observations from **NASA EONET**.

The project combines:

- Data collection and preprocessing
- Data quality validation
- Exploratory Data Analysis
- Geospatial analysis
- Country-level aggregation
- Regional feature engineering
- K-Means clustering
- Disaster-category analysis
- Temporal trend analysis
- Probability calibration
- Next-month event likelihood estimation
- India state-level spatial analysis
- FastAPI backend services
- Interactive React dashboard
- Leaflet-based geospatial visualization

The objective is to transform historical disaster-event observations into an interactive **research and decision-support platform**.

---

# ✨ Key Highlights

| Area | Capability |
|------|------------|
| 🌎 Global Analysis | Country and regional disaster-event analysis |
| 🗺️ Geospatial Intelligence | Interactive global and regional maps |
| 🧠 Machine Learning | K-Means, Logistic Regression, Random Forest, Gradient Boosting |
| 📈 Prediction | Next-month event likelihood estimation |
| 🎯 Calibration | Probability calibration and reliability evaluation |
| 🇮🇳 India Intelligence | State-level spatial event mapping and risk analysis |
| ⚡ Backend | FastAPI REST services |
| 💻 Frontend | React + Vite analytical dashboard |
| 📊 Visualization | Interactive maps, rankings, trends and charts |
| 🔬 Research | End-to-end data science and ML workflow |

---

# 🎯 Project Objectives

## 1. Global Disaster Analysis

Analyze historical disaster-event activity across countries and geographic regions.

The platform provides insights into:

- Event density
- Disaster categories
- Regional activity
- Recent activity
- Historical trends
- Country-level comparisons

---

## 2. Geospatial Pattern Discovery

Use geospatial features and **K-Means clustering** to discover regions with similar disaster-event characteristics.

The clustering workflow includes:

```text
Regional Event Data
        │
        ▼
Feature Engineering
        │
        ▼
Feature Scaling
        │
        ▼
K-Means Experiments
        │
        ▼
Cluster Validation
        │
        ▼
Final Regional Clusters
        │
        ▼
Interactive Cluster Map

<img width="1920" height="1020" alt="Screenshot 2026-08-16 132903" src="https://github.com/user-attachments/assets/1e333461-e239-4a2b-9bda-98657ef8312d" />

3. Disaster Trend Analysis

The platform analyzes temporal patterns across the available EONET observations.

Key dimensions include:

Yearly activity
Monthly activity
Disaster categories
Regional activity
Recent activity
Event density
4. Predictive Intelligence

The prediction system estimates the statistical likelihood of an EONET-type event being observed during the following month.

The prediction pipeline uses historical temporal features including:

Current event activity
Previous-month activity
Previous 3-month activity
Previous 6-month activity
Previous 12-month activity
Historical event activity
Historical active periods
Seasonal features
Time progression
🧠 Machine Learning Architecture
                    NASA EONET
                        │
                        ▼
                Data Collection
                        │
                        ▼
              Data Cleaning & QA
                        │
                        ▼
                Feature Engineering
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
       Global Analysis      India State Mapping
              │                   │
              ▼                   ▼
      Regional Features      State Features
              │                   │
              ▼                   ▼
       K-Means Clustering    State Prediction
              │                   │
              └─────────┬─────────┘
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
🔮 Prediction Intelligence
Prediction Target

The primary prediction target is:

Next-Month Event Likelihood

The system estimates the probability of at least one relevant EONET event being observed in the target region during the following month.

Feature Engineering

The prediction dataset contains temporal and historical features such as:

Current Event Count
Previous Month Events
Previous 3-Month Events
Previous 6-Month Events
Previous 12-Month Events
Same-Month Historical Events
Historical Total Events
Historical Active Months
Recent Activity Share
Month Sin
Month Cos
Years Since 2015

Seasonality is represented using cyclic transformations:

month_sin
month_cos

This allows the model to represent the cyclical nature of calendar months.

📊 Model Evaluation

Because disaster-event prediction is a rare-event classification problem, accuracy alone is not sufficient.

The project evaluates models using:

Precision
Recall
F1-score
ROC-AUC
PR-AUC
Brier Score
Probability calibration
Global Calibrated Model

The final global calibrated prediction model achieved approximately:

Metric	Result
ROC-AUC	0.81
Brier Score	0.13

These metrics are used to evaluate both discrimination and probability quality.

🇮🇳 India State-Level Intelligence

The project contains a dedicated India state-level analytical pipeline.

Historical EONET event geometries are spatially matched against Indian administrative boundaries.

Spatial Processing Pipeline
EONET Event Geometry
        │
        ▼
India ADM1 Boundaries
        │
        ▼
Spatial Intersection
        │
        ▼
State ↔ Event Association
        │
        ▼
Monthly State Timeline
        │
        ▼
State Prediction Features
        │
        ▼
State-Level Risk Engine
        │
        ▼
Interactive Dashboard
Current Dataset

The current India state-level pipeline contains:

Metric	Value
Represented States	20
Unique Events Affecting India	66
State-Event Associations	71
Multi-State Events	2
Prediction Rows	2,380

The state-level pipeline also reports data-confidence indicators because state-level historical observations are considerably more limited than the global dataset.

🗺️ Interactive Dashboard

The React dashboard provides multiple analytical modules.

🌎 Global Map

Interactive global disaster-event visualization with:

Country event density
Dominant disaster type
Recent activity
Cluster information
Regional profiles
Country-level analysis
🔮 Prediction Intelligence

Interactive next-month likelihood visualization with:

Prediction probability map
Probability bands
Regional ranking
Prediction metrics
Historical prediction trends
Regional prediction details
Statistical interpretation
Prediction disclaimer
🧩 Clusters

Explore geographic regions discovered through K-Means clustering.

Includes:

Cluster distribution
Cluster characteristics
Geographic visualization
Regional comparisons
📈 Trends

Analyze historical disaster activity over time.

Includes:

Yearly trends
Monthly patterns
Regional activity
Event frequency
🏷️ Categories

Explore disaster-event categories and their distribution across the dataset.

🌐 Region Explorer

Detailed regional profiles providing geographic and historical context.

🇮🇳 India State Intelligence

Dedicated state-level analytical capabilities including:

State event history
State prediction scores
Risk levels
Data-confidence indicators
State-level rankings
Geographic visualization
🛠️ Technology Stack
Backend
Python
FastAPI
Pandas
NumPy
Joblib
Shapely
Frontend
React
Vite
JavaScript
CSS
Leaflet
Machine Learning
Scikit-learn
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
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
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
│   ├── prepare_ml_features.py
│   ├── eda.py
│   ├── regional_features.py
│   ├── train_final_kmeans.py
│   ├── validate_kmeans.py
│   ├── train_prediction_models.py
│   ├── calibrate_prediction_model.py
│   ├── final_calibrated_prediction.py
│   ├── train_india_state_models.py
│   └── build_india_state_risk_engine.py
│
├── data/
│   ├── processed/
│   └── prediction/
│
├── requirements.txt
├── README.md
└── .gitignore
⚙️ Local Development
1. Clone the Repository
git clone https://github.com/SINANAHMD/global-disaster-pattern-mining.git


cd global-disaster-pattern-mining
2. Create a Python Virtual Environment
Windows
python -m venv .venv


.venv\Scripts\activate
Linux / macOS
python3 -m venv .venv


source .venv/bin/activate
3. Install Python Dependencies
pip install -r requirements.txt
🚀 Run the Backend

Start the FastAPI backend:

uvicorn backend.main:app --reload

Backend:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs
💻 Run the Dashboard

Open another terminal:

cd dashboard

Install frontend dependencies:

npm install

Start the development server:

npm run dev

The Vite development server will provide the local dashboard URL.

🔬 Data Science Workflow

The overall research workflow follows:

Data Collection
      ↓
Data Quality Audit
      ↓
Data Cleaning
      ↓
Data Preparation
      ↓
Exploratory Data Analysis
      ↓
Regional Feature Engineering
      ↓
Geospatial Analysis
      ↓
K-Means Clustering
      ↓
Prediction Dataset Creation
      ↓
Model Training
      ↓
Model Evaluation
      ↓
Probability Calibration
      ↓
India State-Level Analysis
      ↓
FastAPI Services
      ↓
Interactive React Dashboard
📈 Rare-Event Prediction

The prediction problem is highly imbalanced.

Therefore, the project does not rely on accuracy alone.

For example, a model could achieve high accuracy simply by predicting that an event will not occur most of the time.

Instead, the project emphasizes:

Precision
Recall
F1
ROC-AUC
PR-AUC
Brier Score
Calibration

This provides a more meaningful evaluation of rare-event prediction performance.

⚠️ Important Limitations

This project is a research and analytical prediction system.

Predictions are statistical estimates derived from historical NASA EONET observations.

The system is NOT:

An official disaster warning system
A government emergency alert system
A guaranteed disaster forecast
A real-time emergency notification service
A replacement for official meteorological authorities
A replacement for disaster-management authorities

A high predicted probability should be interpreted as:

Historical patterns indicate an increased statistical likelihood of an EONET-type event being observed during the target period.

It does not mean that a disaster is guaranteed to occur.

India State-Level Limitation

India state-level predictions should be interpreted particularly carefully because the available state-level historical observations are limited.

The dashboard therefore includes data-confidence indicators alongside prediction outputs.

🔐 Research & Responsible Interpretation

The platform is designed for:

Educational research
Data science experimentation
Geospatial analysis
Machine learning research
Historical disaster-pattern analysis
Portfolio demonstration
Decision-support research

Prediction outputs should not be used as the sole basis for emergency response or public safety decisions.

Official disaster-management and meteorological sources should always be consulted for real-world warnings and emergency decisions.

🔮 Future Improvements

Potential future development areas include:

More comprehensive historical disaster datasets
Additional geospatial features
Weather and climate variables
Population and infrastructure exposure data
Improved rare-event modelling
Additional calibration techniques
Temporal cross-validation
More granular administrative-level analysis
Real-time data updates
Cloud deployment
Automated model retraining
Advanced spatial-temporal models
🎓 Research Focus

This project demonstrates an end-to-end application of:

Data Engineering
        ↓
Exploratory Data Analysis
        ↓
Geospatial Analytics
        ↓
Feature Engineering
        ↓
Machine Learning
        ↓
Model Evaluation
        ↓
Probability Calibration
        ↓
Prediction
        ↓
API Development
        ↓
Interactive Visualization

The project demonstrates how historical geospatial event data can be transformed into an interactive analytical and machine-learning platform.

👨‍💻 Author
Sinan Ahmd

B.Sc. Computer Science

Data Science • Machine Learning • Geospatial Analytics • Full-Stack Development







