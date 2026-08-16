"""
STEP 3Q - PREDICTION PROBABILITY VALIDATION

Validates the probability outputs produced by the final
Logistic Regression prediction model.

IMPORTANT:
- Does NOT retrain the model.
- Does NOT modify the K-Means model.
- Does NOT modify existing processed datasets.
- Only creates validation reports under data/prediction/.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import (
    brier_score_loss,
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

SCORES_FILE = (
    PREDICTION_DIR
    / "prediction_scores.csv"
)

DATASET_FILE = (
    PREDICTION_DIR
    / "monthly_prediction_dataset.csv"
)

OUTPUT_FILE = (
    PREDICTION_DIR
    / "prediction_probability_validation.csv"
)

REPORT_FILE = (
    PREDICTION_DIR
    / "prediction_probability_validation_report.txt"
)


# ============================================================
# START
# ============================================================

print("=" * 70)
print("STEP 3Q - PREDICTION PROBABILITY VALIDATION")
print("=" * 70)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading prediction scores...")

scores = pd.read_csv(
    SCORES_FILE
)

dataset = pd.read_csv(
    DATASET_FILE
)


print(
    f"Prediction rows: {len(scores):,}"
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_score_columns = [
    "region_id",
    "month",
    "event_probability",
    "event_probability_percent",
    "predicted_event",
]

required_dataset_columns = [
    "region_id",
    "year",
    "month",
    "next_month_event",
]


missing_scores = [
    column
    for column in required_score_columns
    if column not in scores.columns
]

missing_dataset = [
    column
    for column in required_dataset_columns
    if column not in dataset.columns
]

if missing_scores:
    raise ValueError(
        "Missing score columns: "
        + ", ".join(missing_scores)
    )

if missing_dataset:
    raise ValueError(
        "Missing dataset columns: "
        + ", ".join(missing_dataset)
    )


# ============================================================
# ALIGN ACTUAL TARGET
# ============================================================

print(
    "\nAligning actual 2025 outcomes..."
)

# The prediction_scores file represents the 2025 test period.
# Match actual outcomes using region + year + month.

actual = dataset[
    dataset["year"] == 2025
][
    [
        "region_id",
        "year",
        "month",
        "next_month_event",
    ]
].copy()


validation = scores.merge(
    actual,
    on=[
        "region_id",
        "month",
    ],
    how="left"
)


# ============================================================
# CHECK ALIGNMENT
# ============================================================

missing_targets = (
    validation["next_month_event"]
    .isna()
    .sum()
)

if missing_targets > 0:

    print(
        f"WARNING: {missing_targets:,} "
        "rows have no matching target."
    )

    validation = validation[
        validation["next_month_event"]
        .notna()
    ].copy()


validation[
    "next_month_event"
] = validation[
    "next_month_event"
].astype(int)


# ============================================================
# BASIC PROBABILITY CHECK
# ============================================================

probabilities = (
    validation["event_probability"]
)

actual_target = (
    validation["next_month_event"]
)


print(
    "\nProbability statistics:"
)

print(
    probabilities.describe().to_string()
)


# ============================================================
# PROBABILITY THRESHOLD COUNTS
# ============================================================

thresholds = [
    0.90,
    0.80,
    0.70,
    0.60,
    0.50,
    0.40,
    0.30,
    0.20,
    0.10,
]

print(
    "\nProbability threshold distribution:"
)

threshold_rows = []

for threshold in thresholds:

    count = int(
        (
            probabilities
            >= threshold
        ).sum()
    )

    percentage = (
        count
        / len(validation)
        * 100
    )

    threshold_rows.append(
        {
            "threshold": threshold,
            "rows": count,
            "percentage": percentage,
        }
    )

    print(
        f"  >= {threshold:.0%}: "
        f"{count:,} rows "
        f"({percentage:.2f}%)"
    )


# ============================================================
# CALIBRATION BINS
# ============================================================

print(
    "\nCreating probability calibration bins..."
)

# 10 equal-width probability bins.

bins = [
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

labels = [
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

validation["probability_bin"] = pd.cut(
    probabilities,
    bins=bins,
    labels=labels,
    include_lowest=True,
)


calibration = (
    validation
    .groupby(
        "probability_bin",
        observed=False
    )
    .agg(
        observations=(
            "next_month_event",
            "size",
        ),
        average_predicted_probability=(
            "event_probability",
            "mean",
        ),
        actual_event_rate=(
            "next_month_event",
            "mean",
        ),
        actual_events=(
            "next_month_event",
            "sum",
        ),
    )
    .reset_index()
)


calibration[
    "average_predicted_probability"
] = (
    calibration[
        "average_predicted_probability"
    ]
    .round(4)
)

calibration[
    "actual_event_rate"
] = (
    calibration[
        "actual_event_rate"
    ]
    .round(4)
)

calibration[
    "calibration_error"
] = (
    calibration[
        "average_predicted_probability"
    ]
    -
    calibration[
        "actual_event_rate"
    ]
).abs().round(4)


print(
    "\nCalibration table:"
)

print(
    calibration.to_string(
        index=False
    )
)


# ============================================================
# GLOBAL METRICS
# ============================================================

print(
    "\nCalculating probability metrics..."
)

try:

    roc_auc = roc_auc_score(
        actual_target,
        probabilities
    )

except ValueError:

    roc_auc = np.nan


brier = brier_score_loss(
    actual_target,
    probabilities
)


# ============================================================
# EXTREME PROBABILITIES
# ============================================================

very_high = validation[
    validation["event_probability"]
    >= 0.90
]

very_low = validation[
    validation["event_probability"]
    <= 0.10
]


print(
    "\nExtreme probability analysis:"
)

print(
    f"Probability >= 90%: "
    f"{len(very_high):,}"
)

print(
    f"Probability <= 10%: "
    f"{len(very_low):,}"
)


if len(very_high) > 0:

    high_actual_rate = (
        very_high[
            "next_month_event"
        ]
        .mean()
    )

else:

    high_actual_rate = np.nan


if len(very_low) > 0:

    low_actual_rate = (
        very_low[
            "next_month_event"
        ]
        .mean()
    )

else:

    low_actual_rate = np.nan


# ============================================================
# TOP / BOTTOM REGIONS
# ============================================================

top_regions = (
    validation[
        [
            "region_id",
            "month",
            "event_probability",
            "next_month_event",
        ]
    ]
    .sort_values(
        "event_probability",
        ascending=False
    )
    .head(20)
)


bottom_regions = (
    validation[
        [
            "region_id",
            "month",
            "event_probability",
            "next_month_event",
        ]
    ]
    .sort_values(
        "event_probability",
        ascending=True
    )
    .head(20)
)


# ============================================================
# SAVE CALIBRATION
# ============================================================

calibration.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# REPORT
# ============================================================

report = []

report.append(
    "PREDICTION PROBABILITY VALIDATION REPORT"
)

report.append(
    "=" * 70
)

report.append(
    f"Validation rows: {len(validation):,}"
)

report.append(
    f"Actual positive rows: "
    f"{int(actual_target.sum()):,}"
)

report.append(
    f"Actual positive rate: "
    f"{actual_target.mean() * 100:.2f}%"
)

report.append(
    "\nProbability statistics:"
)

report.append(
    probabilities.describe().to_string()
)

report.append(
    "\nGlobal probability metrics:"
)

report.append(
    f"ROC-AUC: {roc_auc:.4f}"
)

report.append(
    f"Brier score: {brier:.4f}"
)

report.append(
    "\nExtreme probability analysis:"
)

report.append(
    f"Rows >= 90%: {len(very_high):,}"
)

report.append(
    f"Actual event rate among >= 90%: "
    f"{high_actual_rate * 100:.2f}%"
    if not np.isnan(high_actual_rate)
    else "Actual event rate among >= 90%: N/A"
)

report.append(
    f"Rows <= 10%: {len(very_low):,}"
)

report.append(
    f"Actual event rate among <= 10%: "
    f"{low_actual_rate * 100:.2f}%"
    if not np.isnan(low_actual_rate)
    else "Actual event rate among <= 10%: N/A"
)

report.append(
    "\nCalibration table:"
)

report.append(
    calibration.to_string(
        index=False
    )
)

report.append(
    "\nTop 20 predicted probabilities:"
)

report.append(
    top_regions.to_string(
        index=False
    )
)

report.append(
    "\nBottom 20 predicted probabilities:"
)

report.append(
    bottom_regions.to_string(
        index=False
    )
)

report.append(
    "\nInterpretation:"
)

report.append(
    "Probability values represent model-estimated "
    "likelihood of at least one EONET event occurring "
    "in the following month."
)

report.append(
    "\nImportant limitation:"
)

report.append(
    "These probabilities are statistical estimates based "
    "on historical EONET observations. They are not official "
    "warnings and should not be interpreted as certainty."
)

report.append(
    "\nExisting system:"
)

report.append(
    "Existing K-Means clustering and dashboard logic "
    "were not modified."
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
print("STEP 3Q COMPLETE")
print("=" * 70)

print(
    f"\nValidation rows: "
    f"{len(validation):,}"
)

print(
    f"ROC-AUC: "
    f"{roc_auc:.4f}"
)

print(
    f"Brier score: "
    f"{brier:.4f}"
)

print(
    f"\nRows >= 90% probability: "
    f"{len(very_high):,}"
)

if not np.isnan(high_actual_rate):

    print(
        f"Actual event rate among >= 90%: "
        f"{high_actual_rate * 100:.2f}%"
    )

print(
    f"\nRows <= 10% probability: "
    f"{len(very_low):,}"
)

if not np.isnan(low_actual_rate):

    print(
        f"Actual event rate among <= 10%: "
        f"{low_actual_rate * 100:.2f}%"
    )

print(
    "\nCalibration file:"
)

print(
    OUTPUT_FILE
)

print(
    "\nValidation report:"
)

print(
    REPORT_FILE
)

print(
    "\nNext:"
)

print(
    "Review probability calibration before connecting "
    "prediction results to the dashboard."
)