"""
STEP 3P - FINAL PREDICTION MODEL

ADD-ON MODULE ONLY

Purpose:
    Train the selected Logistic Regression model using the
    chronological training + validation period and generate
    next-month event probabilities for the 2025 test period.

IMPORTANT:
    This is an activity-probability estimator, NOT a guaranteed
    disaster prediction system.

Existing K-Means files are NOT modified.
Existing dashboard/backend files are NOT modified.
All outputs are written under data/prediction/.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
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

INPUT_FILE = (
    PREDICTION_DIR
    / "monthly_prediction_dataset.csv"
)

MODEL_FILE = (
    PREDICTION_DIR
    / "final_prediction_model.joblib"
)

SCORES_FILE = (
    PREDICTION_DIR
    / "prediction_scores.csv"
)

REPORT_FILE = (
    PREDICTION_DIR
    / "final_prediction_report.txt"
)


# ============================================================
# SETTINGS
# ============================================================

RANDOM_STATE = 42

# Use historical data through 2024 to train the final model.
# 2025 remains the chronological evaluation period.
TRAIN_END_YEAR = 2024

TEST_YEAR = 2025


# ============================================================
# START
# ============================================================

print("=" * 70)
print("STEP 3P - FINAL PREDICTION MODEL")
print("=" * 70)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading prediction dataset...")

df = pd.read_csv(
    INPUT_FILE
)

df["date"] = pd.to_datetime(
    df["date"]
)

print(
    f"Rows: {len(df):,}"
)


# ============================================================
# TARGET
# ============================================================

TARGET = "next_month_event"


if TARGET not in df.columns:
    raise ValueError(
        f"Target column '{TARGET}' not found."
    )


# ============================================================
# FEATURES
# ============================================================

# These are identifiers, target columns, or future-information
# columns and therefore must not enter the model.

excluded_columns = [
    "region_id",
    "date",
    "next_month_event_count",
    TARGET,
]


feature_columns = [
    column
    for column in df.columns
    if column not in excluded_columns
]


print(
    "\nFeatures used by final model:"
)

for column in feature_columns:
    print(
        f"  - {column}"
    )

print(
    f"\nTotal features: {len(feature_columns)}"
)


# ============================================================
# CHRONOLOGICAL TRAINING DATA
# ============================================================

train_df = df[
    df["year"] <= TRAIN_END_YEAR
].copy()

test_df = df[
    df["year"] == TEST_YEAR
].copy()


print(
    f"\nTraining period: 2015-{TRAIN_END_YEAR}"
)

print(
    f"Training rows: {len(train_df):,}"
)

print(
    f"Test period: {TEST_YEAR}"
)

print(
    f"Test rows: {len(test_df):,}"
)


# ============================================================
# PREPARE X / y
# ============================================================

X_train = train_df[
    feature_columns
]

y_train = train_df[
    TARGET
]

X_test = test_df[
    feature_columns
]

y_test = test_df[
    TARGET
]


# ============================================================
# MODEL
# ============================================================

print(
    "\nTraining Logistic Regression..."
)

model = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            ),
        ),
        (
            "scaler",
            StandardScaler(),
        ),
        (
            "model",
            LogisticRegression(
                class_weight="balanced",
                max_iter=2000,
                random_state=RANDOM_STATE,
            ),
        ),
    ]
)


model.fit(
    X_train,
    y_train
)


# ============================================================
# TEST PROBABILITIES
# ============================================================

print(
    "Generating 2025 probability estimates..."
)

probabilities = model.predict_proba(
    X_test
)[:, 1]

predictions = (
    probabilities >= 0.50
).astype(int)


# ============================================================
# ACTIVITY LEVEL
# ============================================================

def activity_level(probability):
    """
    Convert probability into an easy-to-understand
    activity level.

    These are presentation categories, not official
    disaster warning levels.
    """

    if probability < 0.20:
        return "LOW"

    if probability < 0.40:
        return "MODERATE"

    if probability < 0.60:
        return "ELEVATED"

    if probability < 0.80:
        return "HIGH"

    return "VERY HIGH"


# ============================================================
# CREATE SCORES
# ============================================================

scores = test_df[
    [
        "region_id",
        "grid_lat",
        "grid_lon",
        "year",
        "month",
        "date",
        "current_event_count",
        "previous_month_events",
        "previous_3_month_events",
        "previous_6_month_events",
        "previous_12_month_events",
        "same_month_historical_events",
        "historical_total_events",
        "historical_active_months",
        "recent_activity_share",
    ]
].copy()


scores["event_probability"] = (
    probabilities
)

scores["event_probability_percent"] = (
    probabilities * 100
)

scores["predicted_event"] = (
    predictions
)

scores["activity_level"] = [
    activity_level(probability)
    for probability in probabilities
]


# ============================================================
# ROUND VALUES
# ============================================================

scores["event_probability"] = (
    scores["event_probability"]
    .round(4)
)

scores["event_probability_percent"] = (
    scores["event_probability_percent"]
    .round(2)
)

scores["recent_activity_share"] = (
    scores["recent_activity_share"]
    .round(4)
)


# ============================================================
# SORT
# ============================================================

scores = scores.sort_values(
    [
        "event_probability",
        "region_id",
        "date",
    ],
    ascending=[
        False,
        True,
        True,
    ]
).reset_index(
    drop=True
)


# ============================================================
# SAVE SCORES
# ============================================================

scores.to_csv(
    SCORES_FILE,
    index=False
)


# ============================================================
# TEST SUMMARY
# ============================================================

actual_positive = int(
    y_test.sum()
)

predicted_positive = int(
    predictions.sum()
)

average_probability = float(
    probabilities.mean()
)

maximum_probability = float(
    probabilities.max()
)

minimum_probability = float(
    probabilities.min()
)


# ============================================================
# TOP REGIONS
# ============================================================

top_scores = (
    scores[
        [
            "region_id",
            "month",
            "event_probability_percent",
            "activity_level",
        ]
    ]
    .head(20)
)


# ============================================================
# SAVE MODEL METADATA
# ============================================================

model_package = {
    "model": model,
    "feature_columns": feature_columns,
    "excluded_columns": excluded_columns,
    "training_period": (
        "2015-01 through 2024-12"
    ),
    "test_period": "2025",
    "target": TARGET,
    "random_state": RANDOM_STATE,
    "probability_interpretation": (
        "Estimated probability of at least one "
        "EONET event in the following month."
    ),
    "activity_levels": {
        "LOW": "<20%",
        "MODERATE": "20-39.99%",
        "ELEVATED": "40-59.99%",
        "HIGH": "60-79.99%",
        "VERY HIGH": "80%+",
    },
}

joblib.dump(
    model_package,
    MODEL_FILE
)


# ============================================================
# REPORT
# ============================================================

report = []

report.append(
    "FINAL PREDICTION MODEL REPORT"
)

report.append(
    "=" * 70
)

report.append(
    "Model: Logistic Regression"
)

report.append(
    "Target: next_month_event"
)

report.append(
    "0 = no EONET event in following month"
)

report.append(
    "1 = at least one EONET event in following month"
)

report.append(
    "\nTraining period:"
)

report.append(
    "2015-2024"
)

report.append(
    "\nTest period:"
)

report.append(
    "2025"
)

report.append(
    f"\nTraining rows: {len(train_df):,}"
)

report.append(
    f"Test rows: {len(test_df):,}"
)

report.append(
    f"Actual positive test rows: {actual_positive:,}"
)

report.append(
    f"Predicted positive test rows: {predicted_positive:,}"
)

report.append(
    f"Average predicted probability: "
    f"{average_probability:.4f}"
)

report.append(
    f"Minimum predicted probability: "
    f"{minimum_probability:.4f}"
)

report.append(
    f"Maximum predicted probability: "
    f"{maximum_probability:.4f}"
)

report.append(
    "\nFeatures:"
)

for column in feature_columns:
    report.append(
        f" - {column}"
    )

report.append(
    "\nExcluded:"
)

for column in excluded_columns:
    report.append(
        f" - {column}"
    )

report.append(
    "\nActivity-level interpretation:"
)

report.append(
    "LOW       = probability below 20%"
)

report.append(
    "MODERATE  = probability 20-39.99%"
)

report.append(
    "ELEVATED  = probability 40-59.99%"
)

report.append(
    "HIGH      = probability 60-79.99%"
)

report.append(
    "VERY HIGH = probability 80% or above"
)

report.append(
    "\nImportant:"
)

report.append(
    "These activity levels are analytical categories "
    "created for dashboard interpretation. They are "
    "not official disaster warnings."
)

report.append(
    "\nTop 20 probability scores:"
)

report.append(
    top_scores.to_string(
        index=False
    )
)

report.append(
    "\nLimitation:"
)

report.append(
    "The model estimates historical EONET event activity. "
    "It does not establish causation or guarantee that a "
    "disaster will occur."
)

report.append(
    "\nExisting system:"
)

report.append(
    "Existing K-Means clustering, regional features, "
    "FastAPI backend, and React dashboard were not modified."
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
print("STEP 3P COMPLETE")
print("=" * 70)

print(
    f"\nModel: Logistic Regression"
)

print(
    f"Training rows: {len(train_df):,}"
)

print(
    f"Test rows: {len(test_df):,}"
)

print(
    f"Average probability: "
    f"{average_probability:.4f}"
)

print(
    f"Minimum probability: "
    f"{minimum_probability:.4f}"
)

print(
    f"Maximum probability: "
    f"{maximum_probability:.4f}"
)

print(
    "\nTop probability regions:"
)

print(
    top_scores.to_string(
        index=False
    )
)

print(
    "\nSaved model:"
)

print(
    MODEL_FILE
)

print(
    "\nPrediction scores:"
)

print(
    SCORES_FILE
)

print(
    "\nReport:"
)

print(
    REPORT_FILE
)

print(
    "\nIMPORTANT:"
)

print(
    "This is an analytical activity-probability estimate, "
    "not an official disaster warning."
)

print(
    "\nExisting K-Means system was not modified."
)