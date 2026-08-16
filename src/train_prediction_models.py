"""
STEP 3O - PREDICTION MODEL COMPARISON

ADD-ON MODULE ONLY

Models:
    1. Logistic Regression
    2. Random Forest
    3. Gradient Boosting

Target:
    next_month_event

Important:
    next_month_event_count is excluded because it contains
    future information and would cause data leakage.

Existing K-Means files are NOT modified.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
)

from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
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

INPUT_FILE = (
    PREDICTION_DIR
    / "monthly_prediction_dataset.csv"
)

RESULT_FILE = (
    PREDICTION_DIR
    / "prediction_model_comparison.csv"
)

REPORT_FILE = (
    PREDICTION_DIR
    / "prediction_model_report.txt"
)


# ============================================================
# SETTINGS
# ============================================================

RANDOM_STATE = 42

# Chronological split
TRAIN_END_YEAR = 2022
VALIDATION_END_YEAR = 2024

# Final test period = 2025


# ============================================================
# START
# ============================================================

print("=" * 70)
print("STEP 3O - PREDICTION MODEL COMPARISON")
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
# REMOVE LEAKAGE / IDENTIFIERS
# ============================================================

excluded_columns = [
    "region_id",
    "date",

    # Future information — MUST NOT be used
    "next_month_event_count",

    # Target itself
    TARGET,
]


# ============================================================
# FEATURE SELECTION
# ============================================================

feature_columns = [
    column
    for column in df.columns
    if column not in excluded_columns
]


print(
    "\nSelected features:"
)

for column in feature_columns:
    print(
        f"  - {column}"
    )


print(
    f"\nTotal features: {len(feature_columns)}"
)


# ============================================================
# TEMPORAL SPLIT
# ============================================================

print(
    "\nCreating chronological train/validation/test split..."
)

train_df = df[
    df["year"] <= TRAIN_END_YEAR
].copy()

validation_df = df[
    (
        df["year"] > TRAIN_END_YEAR
    )
    &
    (
        df["year"] <= VALIDATION_END_YEAR
    )
].copy()

test_df = df[
    df["year"] > VALIDATION_END_YEAR
].copy()


print(
    f"Training rows:   {len(train_df):,}"
)

print(
    f"Validation rows: {len(validation_df):,}"
)

print(
    f"Test rows:       {len(test_df):,}"
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

X_validation = validation_df[
    feature_columns
]

y_validation = validation_df[
    TARGET
]

X_test = test_df[
    feature_columns
]

y_test = test_df[
    TARGET
]


# ============================================================
# TARGET BALANCE
# ============================================================

print(
    "\nTarget distribution:"
)

print(
    "\nTRAIN:"
)

print(
    y_train.value_counts(
        normalize=True
    )
    .mul(100)
    .round(2)
    .to_string()
)

print(
    "\nVALIDATION:"
)

print(
    y_validation.value_counts(
        normalize=True
    )
    .mul(100)
    .round(2)
    .to_string()
)

print(
    "\nTEST:"
)

print(
    y_test.value_counts(
        normalize=True
    )
    .mul(100)
    .round(2)
    .to_string()
)


# ============================================================
# MODELS
# ============================================================

models = {

    "Logistic Regression": Pipeline(
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
    ),

    "Random Forest": Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=12,
                    min_samples_leaf=3,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    ),

    "Gradient Boosting": Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "model",
                GradientBoostingClassifier(
                    n_estimators=200,
                    learning_rate=0.05,
                    max_depth=3,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    ),
}


# ============================================================
# EVALUATION FUNCTION
# ============================================================

def evaluate_model(
    model,
    X,
    y,
    dataset_name,
):
    """
    Evaluate a binary classification model.
    """

    predictions = model.predict(
        X
    )

    probabilities = model.predict_proba(
        X
    )[:, 1]

    accuracy = accuracy_score(
        y,
        predictions
    )

    precision = precision_score(
        y,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y,
        predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y,
        probabilities
    )

    pr_auc = average_precision_score(
        y,
        probabilities
    )

    return {
        "dataset": dataset_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
    }


# ============================================================
# TRAIN + EVALUATE
# ============================================================

results = []

trained_models = {}


for model_name, model in models.items():

    print()
    print("-" * 70)
    print(
        f"Training: {model_name}"
    )
    print("-" * 70)

    model.fit(
        X_train,
        y_train
    )

    trained_models[
        model_name
    ] = model

    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    train_result = evaluate_model(
        model,
        X_train,
        y_train,
        "train",
    )

    train_result[
        "model"
    ] = model_name

    results.append(
        train_result
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    validation_result = evaluate_model(
        model,
        X_validation,
        y_validation,
        "validation",
    )

    validation_result[
        "model"
    ] = model_name

    results.append(
        validation_result
    )

    # --------------------------------------------------------
    # TEST
    # --------------------------------------------------------

    test_result = evaluate_model(
        model,
        X_test,
        y_test,
        "test",
    )

    test_result[
        "model"
    ] = model_name

    results.append(
        test_result
    )

    # --------------------------------------------------------
    # PRINT
    # --------------------------------------------------------

    print(
        "\nValidation:"
    )

    print(
        f"  Accuracy : "
        f"{validation_result['accuracy']:.4f}"
    )

    print(
        f"  Precision: "
        f"{validation_result['precision']:.4f}"
    )

    print(
        f"  Recall   : "
        f"{validation_result['recall']:.4f}"
    )

    print(
        f"  F1       : "
        f"{validation_result['f1']:.4f}"
    )

    print(
        f"  ROC-AUC  : "
        f"{validation_result['roc_auc']:.4f}"
    )

    print(
        f"  PR-AUC   : "
        f"{validation_result['pr_auc']:.4f}"
    )

    print(
        "\nTest:"
    )

    print(
        f"  Accuracy : "
        f"{test_result['accuracy']:.4f}"
    )

    print(
        f"  Precision: "
        f"{test_result['precision']:.4f}"
    )

    print(
        f"  Recall   : "
        f"{test_result['recall']:.4f}"
    )

    print(
        f"  F1       : "
        f"{test_result['f1']:.4f}"
    )

    print(
        f"  ROC-AUC  : "
        f"{test_result['roc_auc']:.4f}"
    )

    print(
        f"  PR-AUC   : "
        f"{test_result['pr_auc']:.4f}"
    )


# ============================================================
# RESULTS DATAFRAME
# ============================================================

results_df = pd.DataFrame(
    results
)

results_df = results_df[
    [
        "model",
        "dataset",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "pr_auc",
    ]
]


# ============================================================
# BEST MODEL
# ============================================================

validation_results = results_df[
    results_df["dataset"]
    == "validation"
].copy()

validation_results = (
    validation_results
    .sort_values(
        "pr_auc",
        ascending=False
    )
)

best_model_name = (
    validation_results
    .iloc[0]["model"]
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_df.to_csv(
    RESULT_FILE,
    index=False
)


# ============================================================
# REPORT
# ============================================================

report = []

report.append(
    "PREDICTION MODEL COMPARISON REPORT"
)

report.append(
    "=" * 70
)

report.append(
    "Target: next_month_event"
)

report.append(
    "0 = no event in following month"
)

report.append(
    "1 = at least one event in following month"
)

report.append(
    "\nTemporal split:"
)

report.append(
    "Training: 2015-2022"
)

report.append(
    "Validation: 2023-2024"
)

report.append(
    "Test: 2025"
)

report.append(
    "\nExcluded columns:"
)

for column in excluded_columns:
    report.append(
        f" - {column}"
    )

report.append(
    "\nReason for excluding next_month_event_count:"
)

report.append(
    "It contains information from the prediction month "
    "and would cause data leakage."
)

report.append(
    "\nModel comparison:"
)

report.append(
    results_df.to_string(
        index=False
    )
)

report.append(
    "\nBest validation model:"
)

report.append(
    best_model_name
)

report.append(
    "\nModel selection metric:"
)

report.append(
    "PR-AUC was used as the primary selection metric "
    "because the positive class represents only a "
    "minority of observations."
)

report.append(
    "\nImportant limitation:"
)

report.append(
    "The EONET dataset shows substantial changes in "
    "event reporting volume across years, particularly "
    "in 2024-2025. Model predictions should therefore "
    "be interpreted as historical activity-based estimates, "
    "not guaranteed disaster forecasts."
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
print("STEP 3O COMPLETE")
print("=" * 70)

print(
    "\nModel comparison:"
)

print(
    results_df.to_string(
        index=False
    )
)

print(
    "\nBest validation model:"
)

print(
    best_model_name
)

print(
    "\nResults:"
)

print(
    RESULT_FILE
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
    "Existing K-Means model and dashboard were not modified."
)

print(
    "\nNext:"
)

print(
    "Review model results before selecting the final prediction model."
)