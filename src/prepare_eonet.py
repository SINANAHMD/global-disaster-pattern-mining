"""
STEP 5
Prepare the raw NASA EONET dataset for analysis.

Input:
    data/raw/eonet_events_2015_2025.json

Output:
    data/processed/eonet_events_2015_2025_clean.csv
    data/processed/eonet_data_quality_report.txt
"""

from pathlib import Path
import json
import pandas as pd


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = ROOT / "data" / "raw" / "eonet_events_2015_2025.json"

PROCESSED_DIR = ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

START_DATE = pd.Timestamp("2015-01-01", tz="UTC")

END_DATE = pd.Timestamp(
    "2025-12-31 23:59:59",
    tz="UTC"
)


# ------------------------------------------------------------
# LOAD RAW DATA
# ------------------------------------------------------------

print("=" * 70)
print("NASA EONET DATA PREPARATION")
print("=" * 70)

print("\nLoading raw NASA JSON...")

with open(
    RAW_FILE,
    "r",
    encoding="utf-8"
) as file:

    payload = json.load(file)

events = payload.get(
    "events",
    []
)

print(
    f"Raw unique events loaded: {len(events):,}"
)


# ------------------------------------------------------------
# FLATTEN EVENTS
# ------------------------------------------------------------

rows = []

for event in events:

    categories = event.get(
        "categories"
    ) or []

    sources = event.get(
        "sources"
    ) or []

    geometry = event.get(
        "geometry"
    ) or []

    # --------------------------------------------------------
    # IMPORTANT:
    # EONET events can contain multiple geometry records.
    #
    # We create ONE row per geometry because each geometry
    # can have a different date/location.
    # --------------------------------------------------------

    for geo in geometry:

        coordinates = geo.get(
            "coordinates"
        )

        longitude = None
        latitude = None

        if (
            isinstance(coordinates, list)
            and len(coordinates) >= 2
        ):

            if (
                isinstance(
                    coordinates[0],
                    (int, float)
                )
                and
                isinstance(
                    coordinates[1],
                    (int, float)
                )
            ):

                # GeoJSON = [longitude, latitude]

                longitude = coordinates[0]
                latitude = coordinates[1]

        category_ids = [
            str(c.get("id"))
            for c in categories
            if c.get("id") is not None
        ]

        category_names = [
            c.get("title")
            for c in categories
            if c.get("title")
        ]

        source_ids = [
            str(s.get("id"))
            for s in sources
            if s.get("id") is not None
        ]

        source_names = [
            s.get("title")
            for s in sources
            if s.get("title")
        ]

        source_urls = [
            s.get("source")
            for s in sources
            if s.get("source")
        ]

        rows.append({

            "event_id":
                event.get("id"),

            "title":
                event.get("title"),

            "description":
                event.get("description"),

            "closed":
                event.get("closed"),

            "category_ids":
                "|".join(category_ids),

            "categories":
                "|".join(category_names),

            "source_ids":
                "|".join(source_ids),

            "source_names":
                "|".join(source_names),

            "source_urls":
                "|".join(source_urls),

            "event_date":
                geo.get("date"),

            "geometry_type":
                geo.get("type"),

            "longitude":
                longitude,

            "latitude":
                latitude,

            "magnitude_value":
                geo.get("magnitudeValue"),

            "magnitude_unit":
                geo.get("magnitudeUnit"),

            "magnitude_description":
                geo.get("magnitudeDescription"),

            "source_count":
                len(sources),

            "geometry_count":
                len(geometry),

            "event_link":
                event.get("link"),
        })


df = pd.DataFrame(rows)


print(
    f"Rows after geometry expansion: {len(df):,}"
)


# ------------------------------------------------------------
# DATE CONVERSION
# ------------------------------------------------------------

df["event_date"] = pd.to_datetime(
    df["event_date"],
    errors="coerce",
    utc=True
)


before_date_filter = len(df)


df = df[
    (df["event_date"] >= START_DATE)
    &
    (df["event_date"] <= END_DATE)
].copy()


removed_date = (
    before_date_filter - len(df)
)


print(
    f"Rows removed outside 2015-2025: "
    f"{removed_date:,}"
)


# ------------------------------------------------------------
# COORDINATE VALIDATION
# ------------------------------------------------------------

invalid_latitude = (
    df["latitude"].notna()
    &
    ~df["latitude"].between(-90, 90)
)

invalid_longitude = (
    df["longitude"].notna()
    &
    ~df["longitude"].between(-180, 180)
)

invalid_coordinates = (
    invalid_latitude
    |
    invalid_longitude
)

print(
    f"Invalid coordinate rows: "
    f"{invalid_coordinates.sum():,}"
)


# Replace invalid coordinates with missing

df.loc[
    invalid_latitude,
    "latitude"
] = pd.NA

df.loc[
    invalid_longitude,
    "longitude"
] = pd.NA


# ------------------------------------------------------------
# REMOVE DUPLICATE EVENT + DATE + LOCATION
# ------------------------------------------------------------

before_duplicates = len(df)

df = df.drop_duplicates(
    subset=[
        "event_id",
        "event_date",
        "latitude",
        "longitude"
    ]
).copy()

duplicates_removed = (
    before_duplicates - len(df)
)


print(
    f"Duplicate geometry rows removed: "
    f"{duplicates_removed:,}"
)


# ------------------------------------------------------------
# CREATE TIME FEATURES
# ------------------------------------------------------------

df["year"] = (
    df["event_date"]
    .dt.year
)

df["month"] = (
    df["event_date"]
    .dt.month
)

df["month_name"] = (
    df["event_date"]
    .dt.month_name()
)


# ------------------------------------------------------------
# COORDINATE QUALITY FLAG
# ------------------------------------------------------------

df["has_coordinates"] = (
    df["latitude"].notna()
    &
    df["longitude"].notna()
)


# ------------------------------------------------------------
# SORT
# ------------------------------------------------------------

df = df.sort_values(
    "event_date"
).reset_index(
    drop=True
)


# ------------------------------------------------------------
# SAVE CLEAN DATASET
# ------------------------------------------------------------

output_file = (
    PROCESSED_DIR
    /
    "eonet_events_2015_2025_clean.csv"
)


df.to_csv(
    output_file,
    index=False
)


# ------------------------------------------------------------
# QUALITY REPORT
# ------------------------------------------------------------

quality_report = []

quality_report.append(
    "NASA EONET DATA QUALITY REPORT"
)

quality_report.append(
    "=" * 60
)

quality_report.append(
    f"Raw event objects: {len(events):,}"
)

quality_report.append(
    f"Rows after geometry expansion: "
    f"{len(rows):,}"
)

quality_report.append(
    f"Rows after date filtering: "
    f"{len(df):,}"
)

quality_report.append(
    f"Rows removed outside 2015-2025: "
    f"{removed_date:,}"
)

quality_report.append(
    f"Duplicate geometry rows removed: "
    f"{duplicates_removed:,}"
)

quality_report.append(
    f"Rows with coordinates: "
    f"{df['has_coordinates'].sum():,}"
)

quality_report.append(
    f"Rows without coordinates: "
    f"{(~df['has_coordinates']).sum():,}"
)

quality_report.append(
    f"Final columns: {len(df.columns)}"
)

quality_report.append(
    f"Final date range: "
    f"{df['event_date'].min()} "
    f"to "
    f"{df['event_date'].max()}"
)

quality_report.append(
    "\nMissing values:"
)

quality_report.append(
    df.isna()
    .sum()
    .sort_values(
        ascending=False
    )
    .to_string()
)

quality_report.append(
    "\n\nTop categories:"
)

quality_report.append(
    df["categories"]
    .value_counts()
    .head(20)
    .to_string()
)


report_file = (
    PROCESSED_DIR
    /
    "eonet_data_quality_report.txt"
)


report_file.write_text(
    "\n".join(quality_report),
    encoding="utf-8"
)


# ------------------------------------------------------------
# FINAL OUTPUT
# ------------------------------------------------------------

print()
print("=" * 70)
print("STEP 5 COMPLETE")
print("=" * 70)

print(
    f"\nFinal clean rows: {len(df):,}"
)

print(
    f"Final date range: "
    f"{df['event_date'].min()} "
    f"→ "
    f"{df['event_date'].max()}"
)

print(
    f"\nClean dataset:\n{output_file}"
)

print(
    f"\nQuality report:\n{report_file}"
)

print(
    "\nNext step: inspect the quality report."
)