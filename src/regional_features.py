"""
STEP 9 - Regional Feature Engineering

Purpose:
Convert individual EONET event observations into
geographic regional profiles for clustering.

Method:
10-degree latitude x 10-degree longitude grid.

Input:
    data/processed/eonet_events_final.csv

Output:
    data/processed/regional_features.csv
    data/processed/regional_event_summary.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "eonet_events_final.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SETTINGS
# ============================================================

GRID_SIZE = 10


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("STEP 9 - REGIONAL FEATURE ENGINEERING")
print("=" * 70)

print("\nLoading final EONET dataset...")

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"Total observations: {len(df):,}"
)


# ============================================================
# SELECT VALID COORDINATES
# ============================================================

geo_df = df[
    df["latitude"].notna()
    &
    df["longitude"].notna()
].copy()

print(
    f"Observations used for geographic features: "
    f"{len(geo_df):,}"
)

print(
    f"Observations excluded because coordinates "
    f"are missing: {len(df) - len(geo_df):,}"
)


# ============================================================
# DATE PROCESSING
# ============================================================

geo_df["event_date"] = pd.to_datetime(
    geo_df["event_date"],
    errors="coerce",
    utc=True
)

geo_df["year"] = (
    geo_df["event_date"]
    .dt.year
)


# ============================================================
# CREATE 10° x 10° GRID
# ============================================================

print(
    "\nCreating 10° x 10° geographic grid..."
)


# Latitude boundaries:
# -90, -80, -70, ... 80, 90

geo_df["lat_min"] = (
    np.floor(
        geo_df["latitude"]
        /
        GRID_SIZE
    )
    *
    GRID_SIZE
)


# Longitude boundaries:
# -180, -170, ... 170, 180

geo_df["lon_min"] = (
    np.floor(
        geo_df["longitude"]
        /
        GRID_SIZE
    )
    *
    GRID_SIZE
)


geo_df["lat_max"] = (
    geo_df["lat_min"]
    +
    GRID_SIZE
)

geo_df["lon_max"] = (
    geo_df["lon_min"]
    +
    GRID_SIZE
)


# ============================================================
# CREATE REGION ID
# ============================================================

def make_region_id(row):

    lat = int(row["lat_min"])
    lon = int(row["lon_min"])

    lat_direction = (
        "N"
        if lat >= 0
        else "S"
    )

    lon_direction = (
        "E"
        if lon >= 0
        else "W"
    )

    lat_value = abs(lat)
    lon_value = abs(lon)

    return (
        f"GRID_"
        f"{lat_direction}{lat_value:02d}_"
        f"{lon_direction}{lon_value:03d}"
    )


geo_df["region_id"] = (
    geo_df.apply(
        make_region_id,
        axis=1
    )
)


# ============================================================
# REGION CENTER
# ============================================================

geo_df["region_latitude"] = (
    geo_df["lat_min"]
    +
    GRID_SIZE / 2
)

geo_df["region_longitude"] = (
    geo_df["lon_min"]
    +
    GRID_SIZE / 2
)


# ============================================================
# BASIC REGIONAL STATISTICS
# ============================================================

print(
    "\nCalculating regional statistics..."
)

grouped = geo_df.groupby(
    "region_id"
)


regional = grouped.agg(

    total_events=(
        "event_id",
        "count"
    ),

    region_latitude=(
        "region_latitude",
        "first"
    ),

    region_longitude=(
        "region_longitude",
        "first"
    ),

    first_event_year=(
        "year",
        "min"
    ),

    last_event_year=(
        "year",
        "max"
    ),

    active_years=(
        "year",
        "nunique"
    )
).reset_index()


# ============================================================
# EVENTS PER ACTIVE YEAR
# ============================================================

regional["events_per_active_year"] = (
    regional["total_events"]
    /
    regional["active_years"]
)


# ============================================================
# CATEGORY FEATURES
# ============================================================

print(
    "Creating disaster-category features..."
)


# Get all individual category labels.

all_categories = set()

for value in geo_df["categories"].fillna(""):

    for category in str(value).split("|"):

        category = category.strip()

        if category:

            all_categories.add(
                category
            )


all_categories = sorted(
    all_categories
)


print(
    f"Category labels found: "
    f"{len(all_categories)}"
)


# Create a binary indicator for each category.

for category in all_categories:

    safe_name = (
        category
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )

    column_name = (
        "cat_"
        +
        safe_name
    )

    geo_df[column_name] = (
        geo_df["categories"]
        .fillna("")
        .str.split("|")
        .apply(
            lambda values:
            int(
                category
                in values
            )
        )
    )


# Aggregate category counts.

category_columns = [
    column
    for column in geo_df.columns
    if column.startswith("cat_")
]


category_counts = (
    geo_df
    .groupby("region_id")[category_columns]
    .sum()
    .reset_index()
)


regional = regional.merge(
    category_counts,
    on="region_id",
    how="left"
)


# ============================================================
# CATEGORY PROPORTIONS
# ============================================================

print(
    "Creating category proportions..."
)


for column in category_columns:

    proportion_name = (
        column
        +
        "_proportion"
    )

    regional[proportion_name] = (
        regional[column]
        /
        regional["total_events"]
    )


# ============================================================
# TEMPORAL FEATURES
# ============================================================

# Number of observations in the most recent
# three years of our study period.

recent_start_year = 2023

recent_events = geo_df[
    geo_df["year"]
    >=
    recent_start_year
]

recent_counts = (
    recent_events
    .groupby("region_id")
    .size()
    .rename(
        "events_2023_2025"
    )
    .reset_index()
)


regional = regional.merge(
    recent_counts,
    on="region_id",
    how="left"
)


regional["events_2023_2025"] = (
    regional["events_2023_2025"]
    .fillna(0)
)


# ============================================================
# MAGNITUDE FEATURES
# ============================================================

# Magnitude is not comparable across all event categories,
# so these are descriptive/experimental features.
# We will decide later whether they enter the final model.

if "magnitude_value" in geo_df.columns:

    geo_df["magnitude_value"] = pd.to_numeric(
        geo_df["magnitude_value"],
        errors="coerce"
    )

    magnitude_summary = (
        geo_df
        .groupby("region_id")
        ["magnitude_value"]
        .agg(
            magnitude_observations="count",
            magnitude_mean="mean",
            magnitude_median="median",
            magnitude_max="max"
        )
        .reset_index()
    )

    regional = regional.merge(
        magnitude_summary,
        on="region_id",
        how="left"
    )


# ============================================================
# FILL CATEGORY COUNTS
# ============================================================

for column in category_columns:

    if column in regional.columns:

        regional[column] = (
            regional[column]
            .fillna(0)
            .astype(int)
        )


# ============================================================
# SORT
# ============================================================

regional = regional.sort_values(
    "total_events",
    ascending=False
).reset_index(
    drop=True
)


# ============================================================
# SAVE REGIONAL FEATURE MATRIX
# ============================================================

output_file = (
    OUTPUT_DIR
    /
    "regional_features.csv"
)

regional.to_csv(
    output_file,
    index=False
)


# ============================================================
# CREATE SIMPLE REGION SUMMARY
# ============================================================

summary_columns = [
    "region_id",
    "region_latitude",
    "region_longitude",
    "total_events",
    "events_per_active_year",
    "active_years",
    "events_2023_2025"
]

summary_columns = [
    column
    for column in summary_columns
    if column in regional.columns
]

region_summary = regional[
    summary_columns
].copy()


summary_file = (
    OUTPUT_DIR
    /
    "regional_event_summary.csv"
)

region_summary.to_csv(
    summary_file,
    index=False
)


# ============================================================
# FINAL REPORT
# ============================================================

report_file = (
    OUTPUT_DIR
    /
    "regional_feature_report.txt"
)


report = []

report.append(
    "REGIONAL FEATURE ENGINEERING REPORT"
)

report.append(
    "=" * 70
)

report.append(
    f"Grid size: {GRID_SIZE}° x {GRID_SIZE}°"
)

report.append(
    f"Coordinate observations used: "
    f"{len(geo_df):,}"
)

report.append(
    f"Number of active regions: "
    f"{len(regional):,}"
)

report.append(
    f"Number of category features: "
    f"{len(category_columns):,}"
)

report.append(
    "\nTop regions by event count:"
)

report.append(
    regional[
        [
            "region_id",
            "total_events"
        ]
    ]
    .head(20)
    .to_string(index=False)
)

report.append(
    "\nRegional feature columns:"
)

report.append(
    "\n".join(
        regional.columns
    )
)


report_file.write_text(
    "\n".join(report),
    encoding="utf-8"
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print()
print("=" * 70)
print("STEP 9 COMPLETE")
print("=" * 70)

print(
    f"\nActive geographic regions: "
    f"{len(regional):,}"
)

print(
    f"Feature columns: "
    f"{len(regional.columns):,}"
)

print(
    f"\nRegional feature matrix:"
)

print(
    output_file
)

print(
    f"\nRegional summary:"
)

print(
    summary_file
)

print(
    f"\nFeature engineering report:"
)

print(
    report_file
)

print(
    "\nIMPORTANT:"
)

print(
    "Magnitude features were created for "
    "descriptive analysis but will NOT automatically "
    "be used in K-Means."
)

print(
    "\nNext step: inspect the regional feature matrix "
    "before EDA and model training."
)