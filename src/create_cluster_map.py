"""
STEP 16 - GLOBAL K-MEANS CLUSTER MAP

Creates a global visualization of the 9 regional
disaster-event clusters.

Input:
    data/processed/final_region_clusters.csv

Output:
    data/processed/eda/09_global_cluster_map.png
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PROCESSED = ROOT / "data" / "processed"

INPUT_FILE = (
    PROCESSED /
    "final_region_clusters.csv"
)

EDA_DIR = (
    PROCESSED /
    "eda"
)

EDA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    EDA_DIR /
    "09_global_cluster_map.png"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("STEP 16 - GLOBAL CLUSTER MAP")
print("=" * 70)

print(
    "\nLoading final cluster dataset..."
)

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"Regions loaded: {len(df):,}"
)


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "region_id",
    "region_latitude",
    "region_longitude",
    "cluster",
    "total_events"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        "Missing required columns: "
        + str(missing_columns)
    )


# ============================================================
# REMOVE INVALID COORDINATES
# ============================================================

map_df = df.dropna(
    subset=[
        "region_latitude",
        "region_longitude"
    ]
).copy()


print(
    f"Regions with coordinates: "
    f"{len(map_df):,}"
)


# ============================================================
# CREATE MAP
# ============================================================

print(
    "\nCreating global cluster map..."
)

plt.figure(
    figsize=(16, 9)
)

clusters = sorted(
    map_df["cluster"].unique()
)


# ============================================================
# PLOT EACH CLUSTER
# ============================================================

for cluster in clusters:

    subset = map_df[
        map_df["cluster"] == cluster
    ]

    plt.scatter(
        subset["region_longitude"],
        subset["region_latitude"],
        s=(
            subset["total_events"]
            .clip(lower=1)
            ** 0.5
            * 8
        ),
        alpha=0.70,
        label=f"Cluster {cluster}"
    )


# ============================================================
# MAP FORMATTING
# ============================================================

plt.title(
    "Global Regional Disaster-Event Profiles "
    "from K-Means Clustering",
    fontsize=16
)

plt.xlabel(
    "Longitude"
)

plt.ylabel(
    "Latitude"
)

plt.xlim(
    -180,
    180
)

plt.ylim(
    -90,
    90
)

plt.grid(
    alpha=0.25
)

plt.legend(
    title="K-Means Cluster",
    bbox_to_anchor=(
        1.02,
        1
    ),
    loc="upper left"
)

plt.tight_layout()


# ============================================================
# SAVE
# ============================================================

plt.savefig(
    OUTPUT_FILE,
    dpi=250,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("STEP 16 COMPLETE")
print("=" * 70)

print(
    "\nGlobal cluster map:"
)

print(
    OUTPUT_FILE
)

print(
    "\nNext:"
)

print(
    "Inspect the map before creating the enhanced "
    "geographic visualization."
)