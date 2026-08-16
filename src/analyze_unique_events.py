"""
STEP 3J - UNIQUE EONET EVENT DIAGNOSTIC

ADD-ON ONLY.

This script analyzes unique EONET event IDs before building
the predictive dataset.

It does NOT modify any existing dataset or ML model.
"""

from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
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
    / "prediction"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "unique_event_diagnostic.csv"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "unique_event_diagnostic_report.txt"
)


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("STEP 3J - UNIQUE EVENT DIAGNOSTIC")
print("=" * 70)

df = pd.read_csv(INPUT_FILE)

print(
    f"\nGeometry observations: {len(df):,}"
)

print(
    f"Unique event IDs: {df['event_id'].nunique():,}"
)


# ============================================================
# EVENT-LEVEL REPRESENTATION
# ============================================================

# One row per EONET event.
#
# For geographic prediction we retain:
# - first available coordinate
# - event date
# - category
#
# Geometry_count tells us how many geometry observations
# belonged to that event.

events = (
    df
    .sort_values(
        [
            "event_id",
            "event_date",
        ]
    )
    .groupby(
        "event_id",
        as_index=False
    )
    .agg(
        title=("title", "first"),
        categories=("categories", "first"),
        event_date=("event_date", "first"),
        year=("year", "first"),
        month=("month", "first"),
        latitude=("latitude", "first"),
        longitude=("longitude", "first"),
        geometry_observations=("event_id", "size"),
        has_any_coordinates=(
            "has_coordinates",
            "max"
        ),
    )
)


# ============================================================
# COORDINATE QUALITY
# ============================================================

events["has_valid_coordinates"] = (
    events["latitude"].notna()
    &
    events["longitude"].notna()
)


valid_coordinate_events = (
    events["has_valid_coordinates"].sum()
)

missing_coordinate_events = (
    (~events["has_valid_coordinates"]).sum()
)


print(
    f"\nUnique events with coordinates: "
    f"{valid_coordinate_events:,}"
)

print(
    f"Unique events without coordinates: "
    f"{missing_coordinate_events:,}"
)


# ============================================================
# CATEGORY SUMMARY
# ============================================================

category_summary = (
    events["categories"]
    .value_counts()
    .rename_axis("category")
    .reset_index(
        name="unique_event_count"
    )
)


# ============================================================
# GEOMETRY OBSERVATION SUMMARY
# ============================================================

geometry_summary = (
    events["geometry_observations"]
    .describe()
)


# ============================================================
# YEAR SUMMARY
# ============================================================

year_summary = (
    events
    .groupby("year")
    .size()
    .reset_index(
        name="unique_events"
    )
)


# ============================================================
# SAVE EVENT DATASET
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

events.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# REPORT
# ============================================================

report = []

report.append(
    "UNIQUE EONET EVENT DIAGNOSTIC REPORT"
)

report.append(
    "=" * 70
)

report.append(
    f"Geometry observations: {len(df):,}"
)

report.append(
    f"Unique events: {len(events):,}"
)

report.append(
    f"Unique events with coordinates: "
    f"{valid_coordinate_events:,}"
)

report.append(
    f"Unique events without coordinates: "
    f"{missing_coordinate_events:,}"
)

report.append(
    f"Average geometry observations per event: "
    f"{events['geometry_observations'].mean():.2f}"
)

report.append(
    f"Median geometry observations per event: "
    f"{events['geometry_observations'].median():.2f}"
)

report.append(
    f"Maximum geometry observations for one event: "
    f"{events['geometry_observations'].max():,}"
)

report.append(
    "\nUnique events by year:"
)

report.append(
    year_summary.to_string(
        index=False
    )
)

report.append(
    "\nTop disaster categories by unique event:"
)

report.append(
    category_summary.head(20).to_string(
        index=False
    )
)

report.append(
    "\nGeometry observations per unique event:"
)

report.append(
    geometry_summary.to_string()
)

REPORT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)


# ============================================================
# OUTPUT
# ============================================================

print()
print("=" * 70)
print("STEP 3J COMPLETE")
print("=" * 70)

print(
    "\nUnique-event diagnostic:"
)

print(
    OUTPUT_FILE
)

print(
    "\nDiagnostic report:"
)

print(
    REPORT_FILE
)

print(
    "\nTop categories:"
)

print(
    category_summary.head(10).to_string(
        index=False
    )
)

print(
    "\nIMPORTANT:"
)

print(
    "Existing EONET and K-Means files were not modified."
)

print(
    "\nNext:"
)

print(
    "Review unique-event statistics before building the global "
    "ADM1 prediction dataset."
)