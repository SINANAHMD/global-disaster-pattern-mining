"""
STEP 11 - ML FEATURE PREPARATION

Purpose:
Prepare the regional feature matrix for K-Means clustering.

Input:
    data/processed/regional_features.csv

Outputs:
    data/processed/ml_features.csv
    data/processed/ml_features_scaled.csv
    data/processed/ml_feature_report.txt
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PROCESSED = (
    ROOT
    / "data"
    / "processed"
)

INPUT_FILE = (
    PROCESSED
    / "regional_features.csv"
)

OUTPUT_RAW = (
    PROCESSED
    / "ml_features.csv"
)

OUTPUT_SCALED = (
    PROCESSED
    / "ml_features_scaled.csv"
)

OUTPUT_REPORT = (
    PROCESSED
    / "ml_feature_report.txt"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("STEP 11 - ML FEATURE PREPARATION")
print("=" * 70)

print("\nLoading regional feature matrix...")

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"Regions loaded: {len(df):,}"
)


# ============================================================
# CREATE TRANSFORMED INTENSITY FEATURES
# ============================================================

print(
    "\nCreating event-intensity features..."
)

# Log transformation reduces the influence
# of extremely large regions.

df["log_total_events"] = np.log1p(
    df["total_events"]
)

df["log_events_per_active_year"] = np.log1p(
    df["events_per_active_year"]
)


# ============================================================
# RECENT ACTIVITY FEATURE
# ============================================================

print(
    "Creating recent activity feature..."
)

df["recent_event_share"] = np.where(
    df["total_events"] > 0,
    df["events_2023_2025"]
    /
    df["total_events"],
    0
)


# Keep values safely inside [0, 1].

df["recent_event_share"] = (
    df["recent_event_share"]
    .clip(0, 1)
)


# ============================================================
# CATEGORY PROPORTION FEATURES
# ============================================================

print(
    "Selecting category proportion features..."
)

proportion_columns = [
    column
    for column in df.columns
    if (
        column.startswith("cat_")
        and column.endswith("_proportion")
    )
]


# Remove categories whose proportions
# are zero across every region.

useful_proportions = []

removed_zero_columns = []

for column in proportion_columns:

    if df[column].sum() > 0:

        useful_proportions.append(
            column
        )

    else:

        removed_zero_columns.append(
            column
        )


print(
    f"Category proportion features found: "
    f"{len(proportion_columns)}"
)

print(
    f"Useful category proportion features: "
    f"{len(useful_proportions)}"
)

print(
    f"Zero-only features removed: "
    f"{len(removed_zero_columns)}"
)


# ============================================================
# FINAL FEATURE LIST
# ============================================================

selected_features = [
    "log_total_events",
    "log_events_per_active_year",
    "recent_event_share"
]

selected_features += useful_proportions


print(
    "\nSelected ML features:"
)

for feature in selected_features:

    print(
        f"  - {feature}"
    )


# ============================================================
# CREATE ML DATAFRAME
# ============================================================

ml_df = df[
    [
        "region_id"
    ]
    +
    selected_features
].copy()


# ============================================================
# CHECK MISSING VALUES
# ============================================================

print(
    "\nChecking missing values..."
)

missing = (
    ml_df[selected_features]
    .isna()
    .sum()
)

missing_total = (
    missing.sum()
)

print(
    f"Total missing feature values: "
    f"{missing_total}"
)


# ============================================================
# HANDLE MISSING VALUES
# ============================================================

if missing_total > 0:

    print(
        "Missing values found. "
        "Replacing with feature medians..."
    )

    for column in selected_features:

        if ml_df[column].isna().any():

            median_value = (
                ml_df[column]
                .median()
            )

            ml_df[column] = (
                ml_df[column]
                .fillna(
                    median_value
                )
            )


# ============================================================
# CHECK INFINITE VALUES
# ============================================================

print(
    "Checking infinite values..."
)

numeric_values = (
    ml_df[selected_features]
)

infinite_count = (
    np.isinf(
        numeric_values
    )
    .sum()
    .sum()
)

print(
    f"Infinite values: "
    f"{infinite_count}"
)


if infinite_count > 0:

    print(
        "Replacing infinite values "
        "with NaN and then median..."
    )

    ml_df[selected_features] = (
        ml_df[selected_features]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
    )

    for column in selected_features:

        if ml_df[column].isna().any():

            ml_df[column] = (
                ml_df[column]
                .fillna(
                    ml_df[column].median()
                )
            )


# ============================================================
# CHECK CONSTANT FEATURES
# ============================================================

print(
    "\nChecking constant features..."
)

constant_features = []

for column in selected_features:

    if (
        ml_df[column].nunique()
        <= 1
    ):

        constant_features.append(
            column
        )


if constant_features:

    print(
        "Constant features found:"
    )

    for feature in constant_features:

        print(
            f"  - {feature}"
        )

    ml_df = ml_df.drop(
        columns=constant_features
    )

    selected_features = [
        feature
        for feature in selected_features
        if feature
        not in constant_features
    ]

else:

    print(
        "No constant features found."
    )


# ============================================================
# SAVE UN-SCALED ML FEATURES
# ============================================================

ml_df.to_csv(
    OUTPUT_RAW,
    index=False
)


# ============================================================
# STANDARDIZATION
# ============================================================

print(
    "\nStandardizing ML features..."
)

scaler = StandardScaler()

scaled_values = scaler.fit_transform(
    ml_df[selected_features]
)

scaled_df = pd.DataFrame(
    scaled_values,
    columns=selected_features
)

scaled_df.insert(
    0,
    "region_id",
    ml_df["region_id"].values
)


# ============================================================
# SAVE SCALED DATA
# ============================================================

scaled_df.to_csv(
    OUTPUT_SCALED,
    index=False
)


# ============================================================
# FEATURE STATISTICS
# ============================================================

feature_statistics = (
    ml_df[selected_features]
    .describe()
    .T
)

feature_statistics.to_csv(
    PROCESSED
    /
    "ml_feature_statistics.csv"
)


# ============================================================
# REPORT
# ============================================================

report = []

report.append(
    "ML FEATURE PREPARATION REPORT"
)

report.append(
    "=" * 70
)

report.append(
    f"Number of regions: "
    f"{len(ml_df):,}"
)

report.append(
    f"Number of final features: "
    f"{len(selected_features):,}"
)

report.append(
    "\nFinal features:"
)

for feature in selected_features:

    report.append(
        f"  - {feature}"
    )


report.append(
    "\nRemoved zero-only features:"
)

if removed_zero_columns:

    for feature in removed_zero_columns:

        report.append(
            f"  - {feature}"
        )

else:

    report.append(
        "  None"
    )


report.append(
    "\nRemoved constant features:"
)

if constant_features:

    for feature in constant_features:

        report.append(
            f"  - {feature}"
        )

else:

    report.append(
        "  None"
    )


report.append(
    f"\nMissing values after cleaning: "
    f"{ml_df[selected_features].isna().sum().sum()}"
)

report.append(
    f"Infinite values after cleaning: "
    f"{np.isinf(ml_df[selected_features]).sum().sum()}"
)

report.append(
    "\nStandardization:"
)

report.append(
    "StandardScaler applied to all final ML features."
)


OUTPUT_REPORT.write_text(
    "\n".join(report),
    encoding="utf-8"
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("STEP 11 COMPLETE")
print("=" * 70)

print(
    f"\nRegions: "
    f"{len(ml_df):,}"
)

print(
    f"Final ML features: "
    f"{len(selected_features):,}"
)

print(
    "\nUnscaled ML dataset:"
)

print(
    OUTPUT_RAW
)

print(
    "\nScaled ML dataset:"
)

print(
    OUTPUT_SCALED
)

print(
    "\nFeature statistics:"
)

print(
    PROCESSED
    /
    "ml_feature_statistics.csv"
)

print(
    "\nFeature report:"
)

print(
    OUTPUT_REPORT
)

print(
    "\nNext step:"
)

print(
    "Run K-Means experiments using the scaled "
    "feature matrix."
)