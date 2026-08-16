"""
STEP 12 - K-MEANS CLUSTERING EXPERIMENT

Tests multiple K values and calculates:

1. Inertia
2. Silhouette Score

Input:
    data/processed/ml_features_scaled.csv

Outputs:
    data/processed/kmeans_experiments.csv
    data/processed/eda/07_elbow_method.png
    data/processed/eda/08_silhouette_scores.png
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


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
    / "ml_features_scaled.csv"
)

EDA_DIR = (
    PROCESSED
    / "eda"
)

EDA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    PROCESSED
    / "kmeans_experiments.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("STEP 12 - K-MEANS CLUSTERING EXPERIMENT")
print("=" * 70)

print(
    "\nLoading scaled ML features..."
)

df = pd.read_csv(
    INPUT_FILE
)

region_ids = df["region_id"]

X = df.drop(
    columns=["region_id"]
)

print(
    f"Regions: {len(X):,}"
)

print(
    f"Features: {X.shape[1]:,}"
)


# ============================================================
# TEST DIFFERENT K VALUES
# ============================================================

k_values = range(
    2,
    11
)

results = []


print(
    "\nTesting K values:"
)

for k in k_values:

    print(
        f"  Running K = {k}..."
    )

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=20
    )

    labels = model.fit_predict(
        X
    )

    inertia = (
        model.inertia_
    )

    silhouette = (
        silhouette_score(
            X,
            labels
        )
    )

    results.append({

        "k": k,

        "inertia": inertia,

        "silhouette_score":
            silhouette

    })


# ============================================================
# CREATE RESULTS DATAFRAME
# ============================================================

results_df = pd.DataFrame(
    results
)


print()
print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# BEST SILHOUETTE
# ============================================================

best_row = (
    results_df
    .loc[
        results_df[
            "silhouette_score"
        ].idxmax()
    ]
)

best_k_silhouette = int(
    best_row["k"]
)

best_silhouette = (
    best_row[
        "silhouette_score"
    ]
)


print()
print(
    f"Best silhouette K: "
    f"{best_k_silhouette}"
)

print(
    f"Best silhouette score: "
    f"{best_silhouette:.4f}"
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# ELBOW PLOT
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    results_df["k"],
    results_df["inertia"],
    marker="o"
)

plt.title(
    "K-Means Elbow Method"
)

plt.xlabel(
    "Number of Clusters (K)"
)

plt.ylabel(
    "Inertia"
)

plt.xticks(
    list(k_values)
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    EDA_DIR
    /
    "07_elbow_method.png",
    dpi=200
)

plt.close()


# ============================================================
# SILHOUETTE PLOT
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    results_df["k"],
    results_df["silhouette_score"],
    marker="o"
)

plt.title(
    "K-Means Silhouette Score by K"
)

plt.xlabel(
    "Number of Clusters (K)"
)

plt.ylabel(
    "Silhouette Score"
)

plt.xticks(
    list(k_values)
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    EDA_DIR
    /
    "08_silhouette_scores.png",
    dpi=200
)

plt.close()


# ============================================================
# REPORT
# ============================================================

report = []

report.append(
    "K-MEANS EXPERIMENT REPORT"
)

report.append(
    "=" * 70
)

report.append(
    f"Regions: {len(X):,}"
)

report.append(
    f"Features: {X.shape[1]:,}"
)

report.append(
    "\nK evaluation:"
)

report.append(
    results_df.to_string(
        index=False
    )
)

report.append(
    "\nBest silhouette K:"
)

report.append(
    str(
        best_k_silhouette
    )
)

report.append(
    "\nBest silhouette score:"
)

report.append(
    f"{best_silhouette:.4f}"
)

report.append(
    "\nImportant:"
)

report.append(
    "The best silhouette K is not automatically "
    "the final K. The elbow curve and cluster "
    "interpretability must also be considered."
)


(
    PROCESSED
    /
    "kmeans_experiment_report.txt"
).write_text(
    "\n".join(report),
    encoding="utf-8"
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("STEP 12 COMPLETE")
print("=" * 70)

print(
    "\nExperiment results:"
)

print(
    OUTPUT_FILE
)

print(
    "\nElbow graph:"
)

print(
    EDA_DIR
    /
    "07_elbow_method.png"
)

print(
    "\nSilhouette graph:"
)

print(
    EDA_DIR
    /
    "08_silhouette_scores.png"
)

print(
    "\nNext:"
)

print(
    "Inspect the K results and select the final "
    "number of clusters based on evidence."
)