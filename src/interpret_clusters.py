from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PROCESSED = ROOT / "data" / "processed"

PROFILE_FILE = (
    PROCESSED /
    "final_cluster_profiles.csv"
)

OUTPUT_FILE = (
    PROCESSED /
    "cluster_interpretation_report.txt"
)


# ============================================================
# LOAD PROFILE DATA
# ============================================================

df = pd.read_csv(PROFILE_FILE)


# ============================================================
# CATEGORY FEATURES
# ============================================================

category_columns = [
    column
    for column in df.columns
    if (
        column.startswith("cat_")
        and column.endswith("_proportion")
    )
]


# ============================================================
# CATEGORY DISPLAY NAMES
# ============================================================

category_names = {
    "cat_drought_proportion": "Drought",
    "cat_dust_and_haze_proportion": "Dust and Haze",
    "cat_earthquakes_proportion": "Earthquakes",
    "cat_floods_proportion": "Floods",
    "cat_landslides_proportion": "Landslides",
    "cat_sea_and_lake_ice_proportion": "Sea and Lake Ice",
    "cat_severe_storms_proportion": "Severe Storms",
    "cat_volcanoes_proportion": "Volcanoes",
    "cat_water_color_proportion": "Water Color",
    "cat_wildfires_proportion": "Wildfires",
}


# ============================================================
# CREATE REPORT
# ============================================================

report = []

report.append(
    "GLOBAL DISASTER / CLIMATE PATTERN MINING"
)

report.append(
    "CLUSTER INTERPRETATION REPORT"
)

report.append("=" * 70)

report.append(
    f"Number of clusters: {len(df)}"
)

report.append(
    f"Number of regions: {df['region_count'].sum()}"
)

report.append("")


# ============================================================
# INTERPRET EACH CLUSTER
# ============================================================

for _, row in df.iterrows():

    cluster = int(row["cluster"])

    region_count = int(
        row["region_count"]
    )

    average_events = float(
        row["average_events"]
    )

    average_rate = float(
        row[
            "average_events_per_active_year"
        ]
    )

    recent_events = float(
        row[
            "average_recent_events"
        ]
    )

    # Sort category proportions
    category_values = []

    for column in category_columns:

        value = float(
            row[column]
        )

        category_values.append(
            (
                column,
                value
            )
        )

    category_values.sort(
        key=lambda x: x[1],
        reverse=True
    )

    top_categories = (
        category_values[:3]
    )

    report.append(
        "=" * 70
    )

    report.append(
        f"CLUSTER {cluster}"
    )

    report.append(
        f"Regions: {region_count}"
    )

    report.append(
        f"Average total events: "
        f"{average_events:.2f}"
    )

    report.append(
        f"Average events per active year: "
        f"{average_rate:.2f}"
    )

    report.append(
        f"Average recent events "
        f"(2023-2025): "
        f"{recent_events:.2f}"
    )

    report.append(
        "\nDominant categories:"
    )

    for column, value in top_categories:

        name = category_names.get(
            column,
            column
        )

        report.append(
            f"  - {name}: "
            f"{value * 100:.2f}%"
        )

    report.append("")

    # Basic profile interpretation

    dominant_column = (
        top_categories[0][0]
    )

    dominant_value = (
        top_categories[0][1]
    )

    dominant_name = category_names.get(
        dominant_column,
        dominant_column
    )

    if dominant_value >= 0.75:

        interpretation = (
            f"{dominant_name}-dominant "
            "regional event profile."
        )

    elif dominant_value >= 0.50:

        interpretation = (
            f"Primarily {dominant_name}-"
            "associated regional event profile "
            "with secondary hazards."
        )

    else:

        interpretation = (
            "Mixed multi-hazard regional "
            "event profile."
        )

    report.append(
        "Interpretation:"
    )

    report.append(
        f"  {interpretation}"
    )

    if region_count <= 3:

        report.append(
            "  Note: This is a very small "
            "cluster and should be interpreted "
            "as a rare/specialized profile."
        )


# ============================================================
# FINAL NOTES
# ============================================================

report.append("")
report.append("=" * 70)

report.append(
    "IMPORTANT INTERPRETATION NOTE"
)

report.append(
    "Cluster numbers are identifiers and "
    "do not represent inherent risk levels."
)

report.append(
    "The analysis describes EONET event "
    "observation patterns rather than "
    "official disaster-risk scores."
)

report.append(
    "Event frequency should not be interpreted "
    "as direct evidence of population, economic, "
    "or infrastructure risk."
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)


print("=" * 70)
print("STEP 15 - CLUSTER INTERPRETATION")
print("=" * 70)

print(
    "\nCluster interpretation report created:"
)

print(
    OUTPUT_FILE
)

print(
    "\nClusters analyzed:"
    f" {len(df)}"
)

print(
    "\nNext:"
)

print(
    "Review the cluster interpretation before "
    "creating the final global cluster map."
)   