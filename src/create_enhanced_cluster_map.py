"""
STEP 17 - ENHANCED GLOBAL K-MEANS CLUSTER MAP

Purpose:
    Create a presentation-quality geographic visualization
    of the final K-Means regional disaster-event profiles.

Input:
    data/processed/final_region_clusters.csv

Output:
    data/processed/eda/10_enhanced_global_cluster_map.png
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
    "10_enhanced_global_cluster_map.png"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("STEP 17 - ENHANCED GLOBAL CLUSTER MAP")
print("=" * 70)

print("\nLoading final K-Means results...")

df = pd.read_csv(INPUT_FILE)

print(
    f"Total regions: {len(df):,}"
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "region_id",
    "region_latitude",
    "region_longitude",
    "cluster",
    "total_events"
]

missing = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing:
    raise ValueError(
        "Missing required columns: "
        + str(missing)
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
# CLUSTER PROFILE NAMES
# ============================================================

cluster_names = {
    0: "Flood–Wildfire Mixed",
    1: "Volcanic Dominant",
    2: "Severe Storm Dominant",
    3: "Sea/Lake Ice Dominant",
    4: "Wildfire Dominant",
    5: "Dust/Haze Specialized",
    6: "Multi-Hazard Specialized",
    7: "Water-Color Specialized",
    8: "Mixed Hydro-Climate"
}


# ============================================================
# PLOT
# ============================================================

print(
    "\nCreating enhanced global map..."
)

fig, ax = plt.subplots(
    figsize=(18, 10)
)


# ============================================================
# WORLD-LIKE BACKGROUND
# ============================================================

# Create a simple geographic background using
# longitude/latitude reference lines.

ax.set_facecolor(
    "#F4F7FA"
)


# ============================================================
# GRID
# ============================================================

ax.set_xticks(
    range(-180, 181, 30)
)

ax.set_yticks(
    range(-90, 91, 15)
)

ax.grid(
    True,
    linestyle="--",
    linewidth=0.5,
    alpha=0.35
)


# ============================================================
# CLUSTER COLORS
# ============================================================

clusters = sorted(
    map_df["cluster"].unique()
)

# Matplotlib automatically provides a categorical
# colour sequence.

colors = plt.cm.tab10(
    range(len(clusters))
)


# ============================================================
# PLOT CLUSTERS
# ============================================================

for cluster, color in zip(
    clusters,
    colors
):

    subset = map_df[
        map_df["cluster"] == cluster
    ]

    # Point size represents event activity.

    sizes = (
        subset["total_events"]
        .clip(lower=1)
        .pow(0.5)
        * 12
    )

    ax.scatter(
        subset["region_longitude"],
        subset["region_latitude"],
        s=sizes,
        alpha=0.72,
        color=color,
        edgecolors="black",
        linewidths=0.35,
        label=(
            f"Cluster {cluster}: "
            f"{cluster_names.get(cluster, 'Unknown')}"
        )
    )


# ============================================================
# AXIS LIMITS
# ============================================================

ax.set_xlim(
    -180,
    180
)

ax.set_ylim(
    -90,
    90
)


# ============================================================
# TITLES
# ============================================================

ax.set_title(
    "Global Disaster-Event Profiles "
    "Identified by K-Means Clustering",
    fontsize=20,
    fontweight="bold",
    pad=18
)

ax.set_xlabel(
    "Longitude",
    fontsize=12
)

ax.set_ylabel(
    "Latitude",
    fontsize=12
)


# ============================================================
# LEGEND
# ============================================================

legend = ax.legend(
    title="Regional Event Profiles",
    bbox_to_anchor=(
        1.02,
        1
    ),
    loc="upper left",
    fontsize=9,
    title_fontsize=10
)


# ============================================================
# FOOTNOTE
# ============================================================

fig.text(
    0.5,
    0.015,
    "Point size represents event-observation activity. "
    "Cluster labels describe observed EONET event patterns "
    "and are not official disaster-risk scores.",
    ha="center",
    fontsize=9
)


# ============================================================
# LAYOUT
# ============================================================

plt.tight_layout(
    rect=[
        0,
        0.04,
        0.84,
        1
    ]
)


# ============================================================
# SAVE
# ============================================================

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("STEP 17 COMPLETE")
print("=" * 70)

print(
    "\nEnhanced cluster map:"
)

print(
    OUTPUT_FILE
)

print(
    "\nClusters displayed:"
)

for cluster in clusters:

    count = (
        map_df["cluster"] == cluster
    ).sum()

    print(
        f"  Cluster {cluster}: "
        f"{cluster_names.get(cluster, 'Unknown')} "
        f"({count} regions)"
    )

print(
    "\nNext:"
)

print(
    "Inspect the enhanced map before building "
    "the interactive dashboard."
)