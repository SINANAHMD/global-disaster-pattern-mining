"""
STEP 3M - MONTHLY PREDICTION DATASET

ADD-ON MODULE ONLY

Creates a time-aware monthly prediction dataset from the existing
EONET event data.

Prediction target:
    Did the region experience at least one EONET event
    in the following month?

IMPORTANT:
- Existing project files are NOT modified.
- Existing K-Means model is NOT modified.
- Existing regional features are NOT modified.
- This creates NEW files under data/prediction/.
"""

from pathlib import Path

import numpy as np
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
    / "monthly_prediction_dataset.csv"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "monthly_prediction_report.txt"
)


# ============================================================
# GRID SETTINGS
# ============================================================

# Same 10-degree geographic grid concept used by the existing
# regional analysis.

GRID_SIZE = 10


# ============================================================
# START
# ============================================================

print("=" * 70)
print("STEP 3M - MONTHLY PREDICTION DATASET")
print("=" * 70)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading EONET data...")

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"Total observations: {len(df):,}"
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "event_id",
    "event_date",
    "year",
    "month",
    "latitude",
    "longitude",
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
# UNIQUE EVENT REPRESENTATION
# ============================================================

print(
    "\nCreating unique-event representation..."
)

# One event should not be counted repeatedly simply because
# it has multiple geometry observations.
#
# We keep the first valid coordinate associated with each event.

df = df.sort_values(
    [
        "event_id",
        "event_date",
    ]
)

events = (
    df
    .groupby(
        "event_id",
        as_index=False
    )
    .agg(
        event_date=("event_date", "first"),
        year=("year", "first"),
        month=("month", "first"),
        latitude=("latitude", "first"),
        longitude=("longitude", "first"),
        categories=("categories", "first"),
    )
)


# ============================================================
# VALID COORDINATES
# ============================================================

events = events[
    events["latitude"].notna()
    &
    events["longitude"].notna()
].copy()

print(
    f"Unique events with coordinates: "
    f"{len(events):,}"
)


# ============================================================
# CREATE GRID
# ============================================================

print(
    "\nCreating geographic regions..."
)


def latitude_grid(value):
    return int(
        np.floor(
            value / GRID_SIZE
        )
        * GRID_SIZE
    )


def longitude_grid(value):
    return int(
        np.floor(
            value / GRID_SIZE
        )
        * GRID_SIZE
    )


events["grid_lat"] = (
    events["latitude"]
    .apply(latitude_grid)
)

events["grid_lon"] = (
    events["longitude"]
    .apply(longitude_grid)
)


def make_region_id(row):
    lat = row["grid_lat"]
    lon = row["grid_lon"]

    lat_prefix = "N" if lat >= 0 else "S"
    lon_prefix = "E" if lon >= 0 else "W"

    return (
        f"GRID_"
        f"{lat_prefix}{abs(lat):02d}_"
        f"{lon_prefix}{abs(lon):03d}"
    )


events["region_id"] = events.apply(
    make_region_id,
    axis=1
)


# ============================================================
# MONTHLY EVENT COUNTS
# ============================================================

print(
    "\nAggregating events by region and month..."
)

monthly = (
    events
    .groupby(
        [
            "region_id",
            "grid_lat",
            "grid_lon",
            "year",
            "month",
        ]
    )
    .agg(
        event_count=(
            "event_id",
            "nunique"
        )
    )
    .reset_index()
)


# ============================================================
# CREATE COMPLETE MONTH TIMELINE
# ============================================================

print(
    "Creating complete monthly timeline..."
)

regions = (
    monthly[
        [
            "region_id",
            "grid_lat",
            "grid_lon",
        ]
    ]
    .drop_duplicates()
)

dates = pd.date_range(
    start="2015-01-01",
    end="2025-12-01",
    freq="MS"
)

calendar = pd.DataFrame(
    {
        "date": dates
    }
)

calendar["year"] = (
    calendar["date"].dt.year
)

calendar["month"] = (
    calendar["date"].dt.month
)

regions["_key"] = 1
calendar["_key"] = 1

panel = regions.merge(
    calendar,
    on="_key"
).drop(
    columns="_key"
)


# ============================================================
# MERGE EVENT COUNTS
# ============================================================

panel = panel.merge(
    monthly,
    on=[
        "region_id",
        "grid_lat",
        "grid_lon",
        "year",
        "month",
    ],
    how="left"
)

panel["event_count"] = (
    panel["event_count"]
    .fillna(0)
    .astype(int)
)


# ============================================================
# SORT
# ============================================================

panel = panel.sort_values(
    [
        "region_id",
        "year",
        "month",
    ]
).reset_index(
    drop=True
)


# ============================================================
# BASIC FEATURES
# ============================================================

print(
    "\nCreating historical features..."
)

group = panel.groupby(
    "region_id"
)


# ------------------------------------------------------------
# Current activity
# ------------------------------------------------------------

panel["current_event_count"] = (
    panel["event_count"]
)


# ------------------------------------------------------------
# Previous month
# ------------------------------------------------------------

panel["previous_month_events"] = (
    group["event_count"]
    .shift(1)
    .fillna(0)
)


# ------------------------------------------------------------
# Previous 3 months
# ------------------------------------------------------------

panel["previous_3_month_events"] = (
    group["event_count"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            3,
            min_periods=1
        )
        .sum()
    )
    .fillna(0)
)


# ------------------------------------------------------------
# Previous 6 months
# ------------------------------------------------------------

panel["previous_6_month_events"] = (
    group["event_count"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            6,
            min_periods=1
        )
        .sum()
    )
    .fillna(0)
)


# ------------------------------------------------------------
# Previous 12 months
# ------------------------------------------------------------

panel["previous_12_month_events"] = (
    group["event_count"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            12,
            min_periods=1
        )
        .sum()
    )
    .fillna(0)
)


# ============================================================
# SEASONAL HISTORY
# ============================================================

print(
    "Creating seasonal features..."
)

# Historical activity for the same calendar month,
# excluding the current month.

panel["same_month_historical_events"] = (
    panel
    .groupby(
        [
            "region_id",
            "month",
        ]
    )["event_count"]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .mean()
    )
    .fillna(0)
)


# ============================================================
# LONG-TERM REGIONAL ACTIVITY
# ============================================================

panel["historical_total_events"] = (
    group["event_count"]
    .transform(
        lambda x:
        x.shift(1)
        .cumsum()
    )
    .fillna(0)
)


# ============================================================
# ACTIVE MONTHS
# ============================================================

panel["historical_active_months"] = (
    group["event_count"]
    .transform(
        lambda x:
        x.shift(1)
        .gt(0)
        .cumsum()
    )
    .fillna(0)
)


# ============================================================
# RECENT ACTIVITY SHARE
# ============================================================

panel["recent_activity_share"] = (
    panel["previous_3_month_events"]
    /
    (
        panel["previous_12_month_events"]
        + 1
    )
)


# ============================================================
# SEASONAL ENCODING
# ============================================================

panel["month_sin"] = np.sin(
    2
    * np.pi
    * panel["month"]
    / 12
)

panel["month_cos"] = np.cos(
    2
    * np.pi
    * panel["month"]
    / 12
)


# ============================================================
# YEAR TREND
# ============================================================

panel["years_since_2015"] = (
    panel["year"] - 2015
)


# ============================================================
# TARGET
# ============================================================

print(
    "\nCreating next-month target..."
)

group = panel.groupby(
    "region_id"
)

panel["next_month_event_count"] = (
    group["event_count"]
    .shift(-1)
)

panel["next_month_event"] = (
    panel["next_month_event_count"]
    .fillna(0)
    .gt(0)
    .astype(int)
)


# ============================================================
# REMOVE LAST MONTH
# ============================================================

# December 2025 has no January 2026 observation
# in our dataset, so it cannot have a valid target.

panel["date"] = pd.to_datetime(
    {
        "year": panel["year"],
        "month": panel["month"],
        "day": 1,
    }
)

panel = panel[
    panel["date"] < pd.Timestamp(
        "2025-12-01"
    )
].copy()


# ============================================================
# CLEAN NUMERIC VALUES
# ============================================================

numeric_columns = [
    column
    for column in panel.columns
    if panel[column].dtype
    in [
        "float64",
        "int64",
    ]
]

panel[numeric_columns] = (
    panel[numeric_columns]
    .replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan
    )
    .fillna(0)
)


# ============================================================
# SELECT OUTPUT COLUMNS
# ============================================================

output_columns = [
    "region_id",
    "grid_lat",
    "grid_lon",
    "year",
    "month",
    "date",

    # Current/historical activity
    "current_event_count",
    "previous_month_events",
    "previous_3_month_events",
    "previous_6_month_events",
    "previous_12_month_events",
    "same_month_historical_events",
    "historical_total_events",
    "historical_active_months",
    "recent_activity_share",

    # Seasonality
    "month_sin",
    "month_cos",
    "years_since_2015",

    # Target
    "next_month_event_count",
    "next_month_event",
]


prediction_df = panel[
    output_columns
].copy()


# ============================================================
# TARGET SUMMARY
# ============================================================

target_count = (
    prediction_df["next_month_event"]
    .value_counts()
    .sort_index()
)

positive = int(
    target_count.get(1, 0)
)

negative = int(
    target_count.get(0, 0)
)

total = len(
    prediction_df
)

positive_rate = (
    positive / total * 100
    if total > 0
    else 0
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

prediction_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# REPORT
# ============================================================

report = []

report.append(
    "MONTHLY PREDICTION DATASET REPORT"
)

report.append(
    "=" * 70
)

report.append(
    f"Unique events with coordinates: "
    f"{len(events):,}"
)

report.append(
    f"Prediction rows: {len(prediction_df):,}"
)

report.append(
    f"Regions: "
    f"{prediction_df['region_id'].nunique():,}"
)

report.append(
    "Time range: 2015-01 to 2025-11"
)

report.append(
    "\nTarget:"
)

report.append(
    "next_month_event = 1 when at least one "
    "event occurs in the following month."
)

report.append(
    f"\nPositive target rows: {positive:,}"
)

report.append(
    f"Negative target rows: {negative:,}"
)

report.append(
    f"Positive target rate: {positive_rate:.2f}%"
)

report.append(
    "\nFeature columns:"
)

for column in output_columns:
    report.append(
        f" - {column}"
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
print("STEP 3M COMPLETE")
print("=" * 70)

print(
    f"\nPrediction rows: "
    f"{len(prediction_df):,}"
)

print(
    f"Regions: "
    f"{prediction_df['region_id'].nunique():,}"
)

print(
    f"Positive next-month events: "
    f"{positive:,}"
)

print(
    f"Negative next-month events: "
    f"{negative:,}"
)

print(
    f"Positive rate: "
    f"{positive_rate:.2f}%"
)

print(
    "\nPrediction dataset:"
)

print(
    OUTPUT_FILE
)

print(
    "\nReport:"
)

print(
    REPORT_FILE
)

print(
    "\nIMPORTANT:"
)

print(
    "Existing project datasets and K-Means model were not modified."
)

print(
    "\nNext:"
)

print(
    "Inspect target balance and prediction features before training."
)