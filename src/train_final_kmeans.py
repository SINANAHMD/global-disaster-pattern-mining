"""
STEP 14 - FINAL K-MEANS MODEL

Final model:
    K = 9

Input:
    data/processed/ml_features_scaled.csv
    data/processed/ml_features.csv
    data/processed/regional_features.csv

Outputs:
    final_region_clusters.csv
    final_cluster_profiles.csv
    final_cluster_centroids.csv
    final_kmeans_report.txt
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PROCESSED = ROOT / "data" / "processed"

SCALED_FILE = (
    PROCESSED
    / "ml_features_scaled.csv"
)

RAW_FEATURE_FILE = (
    PROCESSED
    / "ml_features.csv"
)

REGIONAL_FILE = (
    PROCESSED
    / "regional_features.csv"
)


# ============================================================
# FINAL MODEL SETTINGS
# ============================================================

# IMPORTANT:
# Final model selected after comparing K = 8, 9 and 10.
FINAL_K = 9

RANDOM_STATE = 42

N_INIT = 20


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("STEP 14 - FINAL K-MEANS MODEL")
print("=" * 70)

print("\nLoading ML features...")

scaled_df = pd.read_csv(
    SCALED_FILE
)

raw_ml_df = pd.read_csv(
    RAW_FEATURE_FILE
)

regional_df = pd.read_csv(
    REGIONAL_FILE
)


# ============================================================
# PREPARE ML INPUT
# ============================================================

region_ids = scaled_df["region_id"]

X = scaled_df.drop(
    columns=["region_id"]
)


print(
    f"Regions: {len(X):,}"
)

print(
    f"Features: {X.shape[1]:,}"
)

print(
    f"Final K: {FINAL_K}"
)


# ============================================================
# VALIDATION CHECK
# ============================================================

if len(X) != len(raw_ml_df):
    raise ValueError(
        "Mismatch between scaled and raw ML datasets."
    )

if len(X) != len(regional_df):
    raise ValueError(
        "Mismatch between ML dataset and regional dataset."
    )


if X.isna().sum().sum() > 0:
    raise ValueError(
        "Missing values detected in scaled ML features."
    )


if np.isinf(X).sum().sum() > 0:
    raise ValueError(
        "Infinite values detected in scaled ML features."
    )


# ============================================================
# TRAIN FINAL K-MEANS MODEL
# ============================================================

print(
    "\nTraining final K-Means model..."
)

model = KMeans(
    n_clusters=FINAL_K,
    random_state=RANDOM_STATE,
    n_init=N_INIT
)

labels = model.fit_predict(
    X
)


# ============================================================
# MODEL METRICS
# ============================================================

inertia = model.inertia_

silhouette = silhouette_score(
    X,
    labels
)


print(
    f"\nInertia: {inertia:.4f}"
)

print(
    f"Silhouette score: {silhouette:.4f}"
)


# ============================================================
# CREATE REGION CLUSTER DATASET
# ============================================================

cluster_df = raw_ml_df.copy()

cluster_df["cluster"] = labels


# ============================================================
# ADD REGIONAL INFORMATION
# ============================================================

regional_columns = [
    "region_id",
    "total_events",
    "region_latitude",
    "region_longitude",
    "first_event_year",
    "last_event_year",
    "active_years",
    "events_per_active_year",
    "events_2023_2025"
]


available_regional_columns = [
    column
    for column in regional_columns
    if column in regional_df.columns
]


regional_info = regional_df[
    available_regional_columns
].copy()


# Avoid duplicate columns before merge.

columns_to_drop = [
    column
    for column in available_regional_columns
    if column != "region_id"
]

cluster_df = cluster_df.drop(
    columns=columns_to_drop,
    errors="ignore"
)


# ============================================================
# MERGE REGIONAL INFORMATION
# ============================================================

cluster_df = cluster_df.merge(
    regional_info,
    on="region_id",
    how="left"
)


# ============================================================
# CHECK MERGE
# ============================================================

if len(cluster_df) != len(X):
    raise ValueError(
        "Region count changed after merging regional information."
    )


if cluster_df["cluster"].isna().any():
    raise ValueError(
        "Some regions do not have a cluster assignment."
    )


# ============================================================
# SORT DATA
# ============================================================

cluster_df = cluster_df.sort_values(
    [
        "cluster",
        "total_events"
    ],
    ascending=[
        True,
        False
    ]
)


# ============================================================
# SAVE FINAL REGION CLUSTERS
# ============================================================

cluster_output = (
    PROCESSED
    /
    "final_region_clusters.csv"
)

cluster_df.to_csv(
    cluster_output,
    index=False
)


# ============================================================
# CLUSTER SIZE SUMMARY
# ============================================================

cluster_sizes = (
    cluster_df
    .groupby("cluster")
    .agg(
        region_count=(
            "region_id",
            "count"
        ),

        total_events_sum=(
            "total_events",
            "sum"
        ),

        average_events=(
            "total_events",
            "mean"
        ),

        median_events=(
            "total_events",
            "median"
        ),

        average_events_per_active_year=(
            "events_per_active_year",
            "mean"
        ),

        average_recent_events=(
            "events_2023_2025",
            "mean"
        )
    )
    .reset_index()
)


cluster_sizes["region_percentage"] = (
    cluster_sizes["region_count"]
    /
    len(cluster_df)
    *
    100
)


# ============================================================
# VERIFY ALL CLUSTERS EXIST
# ============================================================

expected_clusters = set(
    range(FINAL_K)
)

actual_clusters = set(
    cluster_sizes["cluster"]
)

if expected_clusters != actual_clusters:

    raise ValueError(
        "Unexpected cluster labels detected."
    )


# ============================================================
# CATEGORY PROFILE
# ============================================================

profile_features = [
    column
    for column in raw_ml_df.columns
    if (
        column.startswith("cat_")
        and column.endswith("_proportion")
    )
]


cluster_category_profile = (
    cluster_df
    .groupby("cluster")
    [profile_features]
    .mean()
    .reset_index()
)


# ============================================================
# COMPLETE CLUSTER PROFILE
# ============================================================

cluster_profiles = (
    cluster_sizes
    .merge(
        cluster_category_profile,
        on="cluster",
        how="left"
    )
)


profile_output = (
    PROCESSED
    /
    "final_cluster_profiles.csv"
)

cluster_profiles.to_csv(
    profile_output,
    index=False
)


# ============================================================
# K-MEANS CENTROIDS
# ============================================================

centroids = pd.DataFrame(
    model.cluster_centers_,
    columns=X.columns
)

centroids.insert(
    0,
    "cluster",
    range(FINAL_K)
)


centroid_output = (
    PROCESSED
    /
    "final_cluster_centroids.csv"
)

centroids.to_csv(
    centroid_output,
    index=False
)


# ============================================================
# PRINT CLUSTER SIZES
# ============================================================

print(
    "\nCluster sizes:"
)

print(
    cluster_sizes[
        [
            "cluster",
            "region_count",
            "region_percentage",
            "average_events"
        ]
    ]
    .to_string(
        index=False
    )
)


# ============================================================
# PRINT CATEGORY PROFILES
# ============================================================

print(
    "\nAverage category proportions by cluster:"
)

print(
    cluster_category_profile
    .to_string(
        index=False
    )
)


# ============================================================
# REPORT
# ============================================================

report = []

report.append(
    "FINAL K-MEANS MODEL REPORT"
)

report.append(
    "=" * 70
)

report.append(
    f"Final K: {FINAL_K}"
)

report.append(
    f"Number of regions: {len(X):,}"
)

report.append(
    f"Number of ML features: {X.shape[1]:,}"
)

report.append(
    f"Inertia: {inertia:.4f}"
)

report.append(
    f"Silhouette score: {silhouette:.4f}"
)

report.append(
    "\nModel configuration:"
)

report.append(
    f"Random state: {RANDOM_STATE}"
)

report.append(
    f"n_init: {N_INIT}"
)

report.append(
    "\nCluster sizes:"
)

report.append(
    cluster_sizes.to_string(
        index=False
    )
)

report.append(
    "\nCategory profiles:"
)

report.append(
    cluster_category_profile.to_string(
        index=False
    )
)

report.append(
    "\nInterpretation:"
)

report.append(
    "Cluster labels are numerical identifiers."
)

report.append(
    "They do not inherently represent low, "
    "medium, or high risk."
)

report.append(
    "Cluster meanings must be determined from "
    "the observed disaster-event profiles."
)

report.append(
    "\nFinal model selection:"
)

report.append(
    "K=9 was selected after comparing K=8, "
    "K=9 and K=10 using silhouette score, "
    "cluster stability and cluster-size "
    "interpretability."
)

report.append(
    "K=9 provided a strong silhouette score "
    "and high stability while avoiding the "
    "excessive fragmentation observed with K=10."
)


report_output = (
    PROCESSED
    /
    "final_kmeans_report.txt"
)

report_output.write_text(
    "\n".join(report),
    encoding="utf-8"
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("STEP 14 COMPLETE")
print("=" * 70)

print(
    "\nFinal model: K = 9"
)

print(
    "\nFinal region clusters:"
)

print(
    cluster_output
)

print(
    "\nCluster profiles:"
)

print(
    profile_output
)

print(
    "\nCluster centroids:"
)

print(
    centroid_output
)

print(
    "\nFinal model report:"
)

print(
    report_output
)

print(
    "\nNext:"
)

print(
    "Interpret the 9 discovered regional event profiles."
)