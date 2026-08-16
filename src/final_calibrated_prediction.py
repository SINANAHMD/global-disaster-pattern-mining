"""
STEP 3S - FINAL CALIBRATED PREDICTION MODEL

Pipeline:
    StandardScaler
        ↓
    Logistic Regression
        ↓
    Sigmoid (Platt) Calibration

Purpose:
    Produce better-calibrated monthly EONET event probabilities.

IMPORTANT:
    - Existing K-Means model is NOT modified.
    - Existing dashboard is NOT modified.
    - Existing EONET dataset is NOT modified.
    - Existing prediction dataset is NOT modified.
    - Existing prediction_scores.csv is NOT modified.

Output:
    calibrated final prediction model
    calibrated 2025 prediction scores
    model comparison
    validation report
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    brier_score_loss,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PREDICTION_DIR = (
    ROOT
    / "data"
    / "prediction"
)

DATASET_FILE = (
    PREDICTION_DIR
    / "monthly_prediction_dataset.csv"
)

MODEL_FILE = (
    PREDICTION_DIR
    / "final_calibrated_prediction_model.joblib"
)

SCORES_FILE = (
    PREDICTION_DIR
    / "final_calibrated_prediction_scores.csv"
)

COMPARISON_FILE = (
    PREDICTION_DIR
    / "final_prediction_model_comparison.csv"
)

REPORT_FILE = (
    PREDICTION_DIR
    / "final_calibrated_prediction_report.txt"
)


# ============================================================
# SETTINGS
# ============================================================

RANDOM_STATE = 42

FEATURES = [
    "grid_lat",
    "grid_lon",
    "year",
    "month",
    "current_event_count",
    "previous_month_events",
    "previous_3_month_events",
    "previous_6_month_events",
    "previous_12_month_events",
    "same_month_historical_events",
    "historical_total_events",
    "historical_active_months",
    "recent_activity_share",
    "month_sin",
    "month_cos",
    "years_since_2015",
]

TARGET = "next_month_event"


# ============================================================
# ACTIVITY LEVEL
# ============================================================

def activity_level(probability):
    """
    Convert calibrated probability into a simple
    user-friendly activity level.

    These labels are analytical categories only.
    They are NOT official disaster warnings.
    """

    if probability >= 0.70:
        return "VERY HIGH"

    if probability >= 0.50:
        return "HIGH"

    if probability >= 0.30:
        return "MODERATE"

    if probability >= 0.15:
        return "LOW"

    return "VERY LOW"


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    y_true,
    probability,
    prediction,
):

    return {
        "accuracy": accuracy_score(
            y_true,
            prediction,
        ),

        "precision": precision_score(
            y_true,
            prediction,
            zero_division=0,
        ),

        "recall": recall_score(
            y_true,
            prediction,
            zero_division=0,
        ),

        "f1": f1_score(
            y_true,
            prediction,
            zero_division=0,
        ),

        "roc_auc": roc_auc_score(
            y_true,
            probability,
        ),

        "brier_score": brier_score_loss(
            y_true,
            probability,
        ),
    }


# ============================================================
# START
# ============================================================

print("=" * 70)
print("STEP 3S - FINAL CALIBRATED PREDICTION MODEL")
print("=" * 70)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading prediction dataset...")

df = pd.read_csv(
    DATASET_FILE
)

print(
    f"Rows: {len(df):,}"
)


# ============================================================
# VALIDATE COLUMNS
# ============================================================

missing_features = [
    column
    for column in FEATURES
    if column not in df.columns
]

if missing_features:

    raise ValueError(
        "Missing required features: "
        + ", ".join(missing_features)
    )

if TARGET not in df.columns:

    raise ValueError(
        f"Missing target column: {TARGET}"
    )


# ============================================================
# CHRONOLOGICAL SPLIT
# ============================================================

print(
    "\nCreating chronological train/test split..."
)

train_df = df[
    df["year"] <= 2024
].copy()

test_df = df[
    df["year"] == 2025
].copy()


X_train = train_df[
    FEATURES
]

y_train = train_df[
    TARGET
]

X_test = test_df[
    FEATURES
]

y_test = test_df[
    TARGET
]


print(
    "Training period: 2015-2024"
)

print(
    f"Training rows: {len(train_df):,}"
)

print(
    "Test period: 2025"
)

print(
    f"Test rows: {len(test_df):,}"
)


# ============================================================
# TRAINING DISTRIBUTION
# ============================================================

print(
    "\nTraining target distribution:"
)

print(
    (
        y_train
        .value_counts(
            normalize=True
        )
        * 100
    )
    .round(2)
    .to_string()
)


# ============================================================
# BASE SCALED LOGISTIC REGRESSION
# ============================================================

print(
    "\nBuilding scaled Logistic Regression pipeline..."
)

base_pipeline = Pipeline(
    steps=[
        (
            "scaler",
            StandardScaler(),
        ),
        (
            "logistic_regression",
            LogisticRegression(
                max_iter=5000,
                class_weight="balanced",
                solver="lbfgs",
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)


# ============================================================
# RAW MODEL
# ============================================================

print(
    "\nTraining scaled Logistic Regression..."
)

base_pipeline.fit(
    X_train,
    y_train,
)


print(
    "Generating raw 2025 probabilities..."
)

raw_probability = (
    base_pipeline
    .predict_proba(X_test)[:, 1]
)

raw_prediction = (
    raw_probability >= 0.50
).astype(int)


# ============================================================
# CALIBRATED MODEL
# ============================================================

print(
    "\nTraining calibrated Logistic Regression..."
)

calibrated_model = CalibratedClassifierCV(
    estimator=Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "logistic_regression",
                LogisticRegression(
                    max_iter=5000,
                    class_weight="balanced",
                    solver="lbfgs",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    ),
    method="sigmoid",
    cv=5,
)

calibrated_model.fit(
    X_train,
    y_train,
)


# ============================================================
# CALIBRATED PROBABILITIES
# ============================================================

print(
    "\nGenerating calibrated probabilities..."
)

calibrated_probability = (
    calibrated_model
    .predict_proba(X_test)[:, 1]
)

calibrated_prediction = (
    calibrated_probability >= 0.50
).astype(int)


# ============================================================
# METRICS
# ============================================================

raw_metrics = calculate_metrics(
    y_test,
    raw_probability,
    raw_prediction,
)

calibrated_metrics = calculate_metrics(
    y_test,
    calibrated_probability,
    calibrated_prediction,
)


# ============================================================
# PRINT COMPARISON
# ============================================================

print()
print("-" * 70)
print("RAW VS CALIBRATED")
print("-" * 70)

print(
    "\nSCALED LOGISTIC REGRESSION:"
)

for key, value in raw_metrics.items():

    print(
        f"  {key.upper():12}: "
        f"{value:.4f}"
    )


print(
    "\nCALIBRATED LOGISTIC REGRESSION:"
)

for key, value in calibrated_metrics.items():

    print(
        f"  {key.upper():12}: "
        f"{value:.4f}"
    )


# ============================================================
# PROBABILITY STATISTICS
# ============================================================

print(
    "\nProbability distribution:"
)

print(
    f"Raw minimum:       "
    f"{raw_probability.min():.4f}"
)

print(
    f"Raw maximum:       "
    f"{raw_probability.max():.4f}"
)

print(
    f"Raw average:       "
    f"{raw_probability.mean():.4f}"
)

print(
    f"Calibrated minimum:"
    f" {calibrated_probability.min():.4f}"
)

print(
    f"Calibrated maximum:"
    f" {calibrated_probability.max():.4f}"
)

print(
    f"Calibrated average:"
    f" {calibrated_probability.mean():.4f}"
)


# ============================================================
# EXTREME PROBABILITY COUNTS
# ============================================================

raw_90 = int(
    (
        raw_probability >= 0.90
    ).sum()
)

calibrated_90 = int(
    (
        calibrated_probability >= 0.90
    ).sum()
)

raw_10 = int(
    (
        raw_probability <= 0.10
    ).sum()
)

calibrated_10 = int(
    (
        calibrated_probability <= 0.10
    ).sum()
)


print(
    "\nExtreme probability counts:"
)

print(
    f"Raw >= 90%: "
    f"{raw_90:,}"
)

print(
    f"Calibrated >= 90%: "
    f"{calibrated_90:,}"
)

print(
    f"Raw <= 10%: "
    f"{raw_10:,}"
)

print(
    f"Calibrated <= 10%: "
    f"{calibrated_10:,}"
)


# ============================================================
# CREATE FINAL SCORE DATASET
# ============================================================

scores = test_df[
    [
        "region_id",
        "grid_lat",
        "grid_lon",
        "year",
        "month",
        "date",
    ]
].copy()


scores[
    "raw_probability"
] = raw_probability


scores[
    "raw_probability_percent"
] = (
    raw_probability
    * 100
)


scores[
    "calibrated_probability"
] = calibrated_probability


scores[
    "calibrated_probability_percent"
] = (
    calibrated_probability
    * 100
)


scores[
    "predicted_event"
] = calibrated_prediction


scores[
    "activity_level"
] = [
    activity_level(
        probability
    )
    for probability
    in calibrated_probability
]


scores[
    "actual_next_month_event"
] = (
    y_test
    .to_numpy()
)


# ============================================================
# SORT
# ============================================================

scores = scores.sort_values(
    [
        "calibrated_probability",
        "region_id",
        "month",
    ],
    ascending=[
        False,
        True,
        True,
    ],
)


# ============================================================
# SAVE SCORES
# ============================================================

scores.to_csv(
    SCORES_FILE,
    index=False,
)


# ============================================================
# MODEL COMPARISON
# ============================================================

comparison = pd.DataFrame(
    [
        {
            "model":
                "Scaled Logistic Regression",
            **raw_metrics,
        },
        {
            "model":
                "Scaled Logistic Regression + Sigmoid Calibration",
            **calibrated_metrics,
        },
    ]
)


comparison.to_csv(
    COMPARISON_FILE,
    index=False,
)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    calibrated_model,
    MODEL_FILE,
)


# ============================================================
# TOP PREDICTIONS
# ============================================================

top_predictions = (
    scores[
        [
            "region_id",
            "month",
            "calibrated_probability_percent",
            "activity_level",
            "actual_next_month_event",
        ]
    ]
    .head(20)
)


# ============================================================
# CALIBRATION QUALITY
# ============================================================

calibration_bins = [
    0.0,
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    1.0,
]

calibration_labels = [
    "0-10%",
    "10-20%",
    "20-30%",
    "30-40%",
    "40-50%",
    "50-60%",
    "60-70%",
    "70-80%",
    "80-90%",
    "90-100%",
]


calibration_df = pd.DataFrame(
    {
        "probability":
            calibrated_probability,
        "actual":
            y_test.to_numpy(),
    }
)


calibration_df[
    "probability_bin"
] = pd.cut(
    calibration_df[
        "probability"
    ],
    bins=calibration_bins,
    labels=calibration_labels,
    include_lowest=True,
)


calibration_summary = (
    calibration_df
    .groupby(
        "probability_bin",
        observed=False,
    )
    .agg(
        observations=(
            "actual",
            "size",
        ),
        average_predicted_probability=(
            "probability",
            "mean",
        ),
        actual_event_rate=(
            "actual",
            "mean",
        ),
        actual_events=(
            "actual",
            "sum",
        ),
    )
    .reset_index()
)


calibration_summary[
    "calibration_error"
] = (
    calibration_summary[
        "average_predicted_probability"
    ]
    -
    calibration_summary[
        "actual_event_rate"
    ]
).abs()


# ============================================================
# REPORT
# ============================================================

report = []

report.append(
    "FINAL CALIBRATED PREDICTION MODEL REPORT"
)

report.append(
    "=" * 70
)

report.append(
    "Model: StandardScaler + Logistic Regression + "
    "Sigmoid (Platt) Calibration"
)

report.append(
    "Training period: 2015-2024"
)

report.append(
    "Test period: 2025"
)

report.append(
    f"Training rows: {len(train_df):,}"
)

report.append(
    f"Test rows: {len(test_df):,}"
)

report.append(
    f"Features: {len(FEATURES)}"
)

report.append(
    "\nRAW SCALED LOGISTIC REGRESSION:"
)

for key, value in raw_metrics.items():

    report.append(
        f"{key}: {value:.4f}"
    )


report.append(
    "\nCALIBRATED MODEL:"
)

for key, value in calibrated_metrics.items():

    report.append(
        f"{key}: {value:.4f}"
    )


report.append(
    "\nPROBABILITY DISTRIBUTION:"
)

report.append(
    f"Raw minimum: "
    f"{raw_probability.min():.4f}"
)

report.append(
    f"Raw maximum: "
    f"{raw_probability.max():.4f}"
)

report.append(
    f"Raw average: "
    f"{raw_probability.mean():.4f}"
)

report.append(
    f"Calibrated minimum: "
    f"{calibrated_probability.min():.4f}"
)

report.append(
    f"Calibrated maximum: "
    f"{calibrated_probability.max():.4f}"
)

report.append(
    f"Calibrated average: "
    f"{calibrated_probability.mean():.4f}"
)


report.append(
    "\nEXTREME PROBABILITIES:"
)

report.append(
    f"Raw >= 90%: {raw_90:,}"
)

report.append(
    f"Calibrated >= 90%: {calibrated_90:,}"
)

report.append(
    f"Raw <= 10%: {raw_10:,}"
)

report.append(
    f"Calibrated <= 10%: {calibrated_10:,}"
)


report.append(
    "\nCALIBRATION TABLE:"
)

report.append(
    calibration_summary.to_string(
        index=False
    )
)


report.append(
    "\nTOP 20 CALIBRATED PREDICTIONS:"
)

report.append(
    top_predictions.to_string(
        index=False
    )
)


report.append(
    "\nINTERPRETATION:"
)

report.append(
    "The calibrated probability represents the model's "
    "estimated likelihood of at least one EONET event "
    "occurring in the following month for a given "
    "geographic grid region."
)

report.append(
    "\nIMPORTANT LIMITATION:"
)

report.append(
    "These are statistical estimates derived from "
    "historical NASA EONET observations. They are not "
    "official disaster warnings, emergency alerts, or "
    "guarantees of future events."
)

report.append(
    "\nSYSTEM SAFETY:"
)

report.append(
    "Existing K-Means clustering, regional clustering "
    "files, original EONET data, FastAPI backend, and "
    "existing dashboard logic were not modified."
)


REPORT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8",
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("STEP 3S COMPLETE")
print("=" * 70)

print(
    "\nScaled raw Brier score: "
    f"{raw_metrics['brier_score']:.4f}"
)

print(
    "Calibrated Brier score: "
    f"{calibrated_metrics['brier_score']:.4f}"
)

print(
    "\nScaled raw ROC-AUC: "
    f"{raw_metrics['roc_auc']:.4f}"
)

print(
    "Calibrated ROC-AUC: "
    f"{calibrated_metrics['roc_auc']:.4f}"
)

print(
    "\nCalibrated model:"
)

print(
    MODEL_FILE
)

print(
    "\nFinal prediction scores:"
)

print(
    SCORES_FILE
)

print(
    "\nModel comparison:"
)

print(
    COMPARISON_FILE
)

print(
    "\nReport:"
)

print(
    REPORT_FILE
)

print(
    "\nNext:"
)

print(
    "Review STEP 3S results before integrating prediction "
    "into the dashboard."
)