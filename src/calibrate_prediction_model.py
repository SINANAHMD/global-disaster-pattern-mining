"""
STEP 3R - CALIBRATED PREDICTION MODEL

Purpose:
    Improve the reliability of Logistic Regression probability
    estimates using probability calibration.

Important:
    - Existing K-Means model is NOT modified.
    - Existing dashboard is NOT modified.
    - Existing prediction dataset is NOT modified.
    - Existing prediction_scores.csv is NOT modified.
    - This creates separate calibrated-model outputs.

Method:
    Logistic Regression + Sigmoid (Platt) Calibration

Evaluation:
    2025 is kept as the final unseen test period.
    Calibration is fitted using only the 2015-2024 training period.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)


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
    / "calibrated_prediction_model.joblib"
)

SCORES_FILE = (
    PREDICTION_DIR
    / "calibrated_prediction_scores.csv"
)

COMPARISON_FILE = (
    PREDICTION_DIR
    / "raw_vs_calibrated_comparison.csv"
)

REPORT_FILE = (
    PREDICTION_DIR
    / "calibrated_prediction_report.txt"
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
# ACTIVITY LABEL
# ============================================================

def activity_level(probability):
    """
    Convert calibrated probability into an easy-to-understand
    activity level.

    These are analytical categories, NOT official warnings.
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
# START
# ============================================================

print("=" * 70)
print("STEP 3R - CALIBRATED PREDICTION MODEL")
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
# CHECK FEATURES
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
    "\nCreating chronological split..."
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
    f"Training period: 2015-2024"
)

print(
    f"Training rows: {len(train_df):,}"
)

print(
    f"Test period: 2025"
)

print(
    f"Test rows: {len(test_df):,}"
)


# ============================================================
# BASE LOGISTIC REGRESSION
# ============================================================

print(
    "\nTraining base Logistic Regression..."
)

base_model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=RANDOM_STATE,
)

base_model.fit(
    X_train,
    y_train
)


# ============================================================
# RAW TEST PROBABILITIES
# ============================================================

print(
    "\nGenerating raw probabilities..."
)

raw_probability = (
    base_model
    .predict_proba(X_test)[:, 1]
)


raw_prediction = (
    raw_probability >= 0.50
).astype(int)


# ============================================================
# CALIBRATION
# ============================================================

print(
    "\nApplying sigmoid probability calibration..."
)

calibrated_model = CalibratedClassifierCV(
    estimator=LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    ),
    method="sigmoid",
    cv=5,
)

calibrated_model.fit(
    X_train,
    y_train
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
# METRIC FUNCTION
# ============================================================

def calculate_metrics(
    y_true,
    probabilities,
    predictions,
):

    return {
        "accuracy": accuracy_score(
            y_true,
            predictions
        ),

        "precision": precision_score(
            y_true,
            predictions,
            zero_division=0
        ),

        "recall": recall_score(
            y_true,
            predictions,
            zero_division=0
        ),

        "f1": f1_score(
            y_true,
            predictions,
            zero_division=0
        ),

        "roc_auc": roc_auc_score(
            y_true,
            probabilities
        ),

        "brier_score": brier_score_loss(
            y_true,
            probabilities
        ),
    }


# ============================================================
# CALCULATE METRICS
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
    "\nRAW LOGISTIC REGRESSION:"
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
    f"Raw minimum: "
    f"{raw_probability.min():.4f}"
)

print(
    f"Raw maximum: "
    f"{raw_probability.max():.4f}"
)

print(
    f"Raw average: "
    f"{raw_probability.mean():.4f}"
)

print(
    f"Calibrated minimum: "
    f"{calibrated_probability.min():.4f}"
)

print(
    f"Calibrated maximum: "
    f"{calibrated_probability.max():.4f}"
)

print(
    f"Calibrated average: "
    f"{calibrated_probability.mean():.4f}"
)


# ============================================================
# EXTREME PROBABILITY CHECK
# ============================================================

raw_90 = (
    raw_probability >= 0.90
).sum()

calibrated_90 = (
    calibrated_probability >= 0.90
).sum()

raw_10 = (
    raw_probability <= 0.10
).sum()

calibrated_10 = (
    calibrated_probability <= 0.10
).sum()


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
# CREATE SCORE DATASET
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
] = y_test.values


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
    index=False
)


# ============================================================
# COMPARISON DATAFRAME
# ============================================================

comparison_rows = []

for model_name, metrics in [
    (
        "Logistic Regression - Raw",
        raw_metrics,
    ),
    (
        "Logistic Regression - Calibrated",
        calibrated_metrics,
    ),
]:

    row = {
        "model": model_name,
    }

    row.update(metrics)

    comparison_rows.append(
        row
    )


comparison_df = pd.DataFrame(
    comparison_rows
)


comparison_df.to_csv(
    COMPARISON_FILE,
    index=False
)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    calibrated_model,
    MODEL_FILE
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
# REPORT
# ============================================================

report = []

report.append(
    "CALIBRATED PREDICTION MODEL REPORT"
)

report.append(
    "=" * 70
)

report.append(
    "Model: Logistic Regression + Sigmoid Calibration"
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
    f"Number of features: {len(FEATURES)}"
)

report.append(
    "\nRAW MODEL METRICS:"
)

for key, value in raw_metrics.items():

    report.append(
        f"{key}: {value:.4f}"
    )


report.append(
    "\nCALIBRATED MODEL METRICS:"
)

for key, value in calibrated_metrics.items():

    report.append(
        f"{key}: {value:.4f}"
    )


report.append(
    "\nPROBABILITY RANGE:"
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
    f"Calibrated minimum: "
    f"{calibrated_probability.min():.4f}"
)

report.append(
    f"Calibrated maximum: "
    f"{calibrated_probability.max():.4f}"
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
    "Calibration adjusts the raw model probabilities "
    "so that probability values better correspond to "
    "observed event frequencies."
)

report.append(
    "\nIMPORTANT LIMITATION:"
)

report.append(
    "The prediction represents a statistical estimate "
    "of the likelihood of at least one EONET event in "
    "the following month. It is not an official disaster "
    "warning, forecast, or certainty."
)

report.append(
    "\nSYSTEM SAFETY:"
)

report.append(
    "Existing K-Means clustering, existing prediction "
    "dataset, backend API, and dashboard logic were "
    "not modified."
)


REPORT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("STEP 3R COMPLETE")
print("=" * 70)

print(
    "\nRaw Brier score: "
    f"{raw_metrics['brier_score']:.4f}"
)

print(
    "Calibrated Brier score: "
    f"{calibrated_metrics['brier_score']:.4f}"
)

print(
    "\nRaw ROC-AUC: "
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
    "\nCalibrated prediction scores:"
)

print(
    SCORES_FILE
)

print(
    "\nComparison:"
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
    "Review raw vs calibrated metrics before dashboard integration."
)   