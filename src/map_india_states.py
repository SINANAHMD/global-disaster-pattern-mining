"""
STEP 3F - MAP EONET EVENTS TO INDIAN STATES / UNION TERRITORIES

ADD-ON MODULE ONLY

This script:
1. Loads the existing cleaned EONET dataset.
2. Selects events with valid coordinates.
3. Filters coordinates approximately to India's geographic extent.
4. Converts coordinates into geographic points.
5. Performs a spatial join with India's ADM1 boundaries.
6. Saves a NEW state-level event dataset.

IMPORTANT:
This script does NOT modify the existing EONET dataset,
K-Means model, regional features, or dashboard data.
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

EONET_FILE = (
    ROOT
    / "data"
    / "processed"
    / "eonet_events_final.csv"
)

BOUNDARY_FILE = (
    ROOT
    / "data"
    / "prediction"
    / "boundaries"
    / "india_adm1.geojson"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "prediction"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "eonet_india_state_events.csv"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "india_state_mapping_report.txt"
)


# ============================================================
# SETTINGS
# ============================================================

# Approximate geographic bounding box used only to reduce
# unnecessary global spatial-join calculations.

INDIA_MIN_LAT = 6.0
INDIA_MAX_LAT = 37.5

INDIA_MIN_LON = 68.0
INDIA_MAX_LON = 97.5


# ============================================================
# START
# ============================================================

print("=" * 70)
print("STEP 3F - EONET → INDIA STATE MAPPING")
print("=" * 70)


# ============================================================
# LOAD EONET
# ============================================================

print("\nLoading existing EONET dataset...")

df = pd.read_csv(EONET_FILE)

print(
    f"Total EONET observations: {len(df):,}"
)


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "event_id",
    "latitude",
    "longitude",
    "event_date",
    "categories",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "Missing required columns: "
        + ", ".join(missing_columns)
    )


# ============================================================
# VALID COORDINATES
# ============================================================

coordinate_df = df[
    df["latitude"].notna()
    & df["longitude"].notna()
].copy()

print(
    f"Observations with coordinates: "
    f"{len(coordinate_df):,}"
)


# ============================================================
# APPROXIMATE INDIA FILTER
# ============================================================

india_area_df = coordinate_df[
    coordinate_df["latitude"].between(
        INDIA_MIN_LAT,
        INDIA_MAX_LAT
    )
    &
    coordinate_df["longitude"].between(
        INDIA_MIN_LON,
        INDIA_MAX_LON
    )
].copy()

print(
    f"Observations inside approximate India extent: "
    f"{len(india_area_df):,}"
)


# ============================================================
# CREATE GEOGRAPHIC POINTS
# ============================================================

print("\nCreating geographic points...")

points = gpd.GeoDataFrame(
    india_area_df,
    geometry=gpd.points_from_xy(
        india_area_df["longitude"],
        india_area_df["latitude"]
    ),
    crs="EPSG:4326",
)


# ============================================================
# LOAD INDIA ADM1
# ============================================================

print(
    "\nLoading India ADM1 boundaries..."
)

boundaries = gpd.read_file(
    BOUNDARY_FILE
)

print(
    f"State / UT boundaries loaded: "
    f"{len(boundaries):,}"
)


# ============================================================
# CHECK CRS
# ============================================================

print(
    f"Boundary CRS: {boundaries.crs}"
)

if boundaries.crs is None:
    boundaries = boundaries.set_crs(
        "EPSG:4326"
    )

elif boundaries.crs.to_string() != "EPSG:4326":
    boundaries = boundaries.to_crs(
        "EPSG:4326"
    )


# ============================================================
# KEEP REQUIRED BOUNDARY COLUMNS
# ============================================================

boundaries = boundaries[
    [
        "shapeName",
        "shapeISO",
        "geometry",
    ]
].copy()


boundaries = boundaries.rename(
    columns={
        "shapeName": "state_name",
        "shapeISO": "state_iso",
    }
)


# ============================================================
# SPATIAL JOIN
# ============================================================

print(
    "\nPerforming point-in-polygon spatial join..."
)

mapped = gpd.sjoin(
    points,
    boundaries,
    how="left",
    predicate="within",
)


# ============================================================
# REMOVE SPATIAL JOIN INDEX
# ============================================================

if "index_right" in mapped.columns:
    mapped = mapped.drop(
        columns=["index_right"]
    )


# ============================================================
# MAPPING RESULTS
# ============================================================

mapped_count = (
    mapped["state_name"]
    .notna()
    .sum()
)

unmapped_count = (
    mapped["state_name"]
    .isna()
    .sum()
)

print(
    f"\nSuccessfully mapped to state/UT: "
    f"{mapped_count:,}"
)

print(
    f"Not mapped to a state/UT: "
    f"{unmapped_count:,}"
)


# ============================================================
# REMOVE GEOMETRY BEFORE CSV
# ============================================================

output_df = pd.DataFrame(
    mapped.drop(
        columns=["geometry"],
        errors="ignore"
    )
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

output_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# STATE SUMMARY
# ============================================================

state_summary = (
    output_df[
        output_df["state_name"].notna()
    ]
    .groupby(
        "state_name"
    )
    .agg(
        event_observations=(
            "event_id",
            "count"
        )
    )
    .sort_values(
        "event_observations",
        ascending=False
    )
)


# ============================================================
# REPORT
# ============================================================

report = []

report.append(
    "INDIA STATE MAPPING REPORT"
)

report.append(
    "=" * 70
)

report.append(
    f"Original EONET observations: {len(df):,}"
)

report.append(
    f"Observations with coordinates: "
    f"{len(coordinate_df):,}"
)

report.append(
    f"Observations inside India bounding box: "
    f"{len(india_area_df):,}"
)

report.append(
    f"Mapped to state/UT: {mapped_count:,}"
)

report.append(
    f"Unmapped: {unmapped_count:,}"
)

report.append(
    f"State/UT boundaries: {len(boundaries):,}"
)

report.append(
    "\nState event counts:"
)

report.append(
    state_summary.to_string()
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
print("STEP 3F COMPLETE")
print("=" * 70)

print(
    "\nNew state-level dataset:"
)

print(
    OUTPUT_FILE
)

print(
    "\nMapping report:"
)

print(
    REPORT_FILE
)

print(
    "\nTop 15 states/UTs:"
)

print(
    state_summary.head(15).to_string()
)

print(
    "\nIMPORTANT:"
)

print(
    "Existing EONET data and K-Means files were not modified."
)

print(
    "\nNext:"
)

print(
    "Validate the India state mapping before building risk features."
)
