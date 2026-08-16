"""
STEP 13 - K-MEANS MODEL VALIDATION

Compares K = 8, 9 and 10 using:

1. Silhouette score
2. Inertia
3. Cluster sizes
4. Multiple random seeds
5. Cluster feature profiles

Input:
    data/processed/ml_features_scaled.csv
    data/processed/ml_features.csv
    data/processed/regional_features.csv

Output:
    data/processed/kmeans_validation.csv
    data/processed/kmeans_cluster_profiles.csv
    data/processed/kmeans_validation_report.txt
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.metrics import adjusted_rand_score


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
# LOAD DATA
# ============================================================

print("=" * 70)
print("STEP 13 - K-MEANS MODEL VALIDATION")
print("=" * 70)

scaled_df = pd.read_csv(
    SCALED_FILE
)

raw_ml_df = pd.read_csv(
    RAW_FEATURE_FILE
)

regional_df = pd.read_csv(
    REGIONAL_FILE
)


region_ids = scaled_df["region_id"]

X = scaled_df.drop(
    columns=["region_id"]
)


# ============================================================
# TEST K VALUES
# ============================================================

k_values = [
    8,
    9,
    10
]

seeds = [
    42,
    100,
    200,
    500,
    1000
]


results = []

models = {}


print(
    "\nTesting cluster stability..."
)


for k in k_values:

    print(
        f"\nK = {k}"
    )

    seed_labels = []

    for seed in seeds:

        model = KMeans(
            n_clusters=k,
            random_state=seed,
            n_init=20
        )

        labels = model.fit_predict(
            X
        )

        score = silhouette_score(
            X,
            labels
        )

        inertia = model.inertia_

        seed_labels.append(
            labels
        )

        results.append({

            "k": k,

            "seed": seed,

            "inertia": inertia,

            "silhouette_score": score

        })

    # --------------------------------------------------------
    # Stability using Adjusted Rand Index
    # --------------------------------------------------------

    ari_scores = []

    for i in range(
        len(seed_labels)
    ):

        for j in range(
            i + 1,
            len(seed_labels)
        ):

            ari = adjusted_rand_score(
                seed_labels[i],
                seed_labels[j]
            )

            ari_scores.append(
                ari
            )

    print(
        f"Mean silhouette: "
        f"{np.mean([r['silhouette_score'] for r in results if r['k'] == k]):.4f}"
    )

    print(
        f"Mean ARI stability: "
        f"{np.mean(ari_scores):.4f}"
    )

    print(
        f"Minimum ARI: "
        f"{np.min(ari_scores):.4f}"
    )


# ============================================================
# SAVE VALIDATION RESULTS
# ============================================================

results_df = pd.DataFrame(
    results
)

validation_file = (
    PROCESSED
    /
    "kmeans_validation.csv"
)

results_df.to_csv(
    validation_file,
    index=False
)


# ============================================================
# SELECT REPRESENTATIVE MODEL
# ============================================================

# Use seed 42 as the reproducible representative model.

representative_models = {}

for k in k_values:

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=20
    )

    labels = model.fit_predict(
        X
    )

    representative_models[k] = (
        model,
        labels
    )


# ============================================================
# CLUSTER SIZE ANALYSIS
# ============================================================

cluster_size_rows = []

for k in k_values:

    model, labels = (
        representative_models[k]
    )

    counts = (
        pd.Series(labels)
        .value_counts()
        .sort_index()
    )

    for cluster, count in counts.items():

        cluster_size_rows.append({

            "k": k,

            "cluster": cluster,

            "region_count": count,

            "percentage": (
                count
                /
                len(labels)
                *
                100
            )

        })


cluster_sizes = pd.DataFrame(
    cluster_size_rows
)


# ============================================================
# CLUSTER PROFILES FOR K=9 AND K=10
# ============================================================

profile_rows = []

profile_features = [
    column
    for column in raw_ml_df.columns
    if column != "region_id"
]


for k in [9, 10]:

    model, labels = (
        representative_models[k]
    )

    temp = raw_ml_df.copy()

    temp["cluster"] = labels

    profile = (
        temp
        .groupby("cluster")
        [profile_features]
        .mean()
    )

    for cluster in profile.index:

        row = {

            "k": k,

            "cluster": cluster

        }

        for feature in profile_features:

            row[feature] = (
                profile
                .loc[
                    cluster,
                    feature
                ]
            )

        row["region_count"] = int(
            (
                labels
                ==
                cluster
            ).sum()
        )

        profile_rows.append(
            row
        )


profiles_df = pd.DataFrame(
    profile_rows
)

profiles_file = (
    PROCESSED
    /
    "kmeans_cluster_profiles.csv"
)

profiles_df.to_csv(
    profiles_file,
    index=False
)


# ============================================================
# REPORT
# ============================================================

report = []

report.append(
    "K-MEANS VALIDATION REPORT"
)

report.append(
    "=" * 70
)

report.append(
    "\nValidation summary:"
)

summary = (
    results_df
    .groupby("k")
    .agg(
        mean_silhouette=(
            "silhouette_score",
            "mean"
        ),
        std_silhouette=(
            "silhouette_score",
            "std"
        ),
        mean_inertia=(
            "inertia",
            "mean"
        )
    )
    .reset_index()
)

report.append(
    summary.to_string(
        index=False
    )
)

report.append(
    "\nCluster sizes:"
)

for k in k_values:

    sizes = (
        cluster_sizes[
            cluster_sizes["k"] == k
        ]
    )

    report.append(
        f"\nK = {k}"
    )

    report.append(
        sizes.to_string(
            index=False
        )
    )


report.append(
    "\nInterpretation note:"
)

report.append(
    "K=10 has the highest silhouette in the "
    "initial experiment, but K=9 is extremely close. "
    "Final selection should consider silhouette, "
    "stability, cluster sizes, and interpretability."
)


(
    PROCESSED
    /
    "kmeans_validation_report.txt"
).write_text(
    "\n".join(report),
    encoding="utf-8"
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("STEP 13 COMPLETE")
print("=" * 70)

print(
    "\nValidation results:"
)

print(
    validation_file
)

print(
    "\nCluster profiles:"
)

print(
    profiles_file
)

print(
    "\nValidation report:"
)

print(
    PROCESSED
    /
    "kmeans_validation_report.txt"
)

print(
    "\nNext:"
)

print(
    "Use the validation results to select the final K."
)