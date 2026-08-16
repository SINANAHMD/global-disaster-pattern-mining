"""
STEP 8 - Geographic Country Mapping

Converts:
    latitude + longitude
        ->
    country + ISO code + world region

Input:
    data/processed/eonet_events_final.csv

Country boundaries:
    Natural Earth Admin 0 Countries

Output:
    data/processed/eonet_events_with_country.csv
    data/processed/country_mapping_report.txt
"""

from pathlib import Path
import io
import zipfile
import requests

import pandas as pd
import geopandas as gpd


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
# NATURAL EARTH DATA
# ============================================================

NATURAL_EARTH_URL = (
    "https://naciscdn.org/naturalearth/"
    "110m/cultural/"
    "ne_110m_admin_0_countries.zip"
)


# ============================================================
# LOAD EVENT DATA
# ============================================================

print("=" * 70)
print("STEP 8 - GEOGRAPHIC COUNTRY MAPPING")
print("=" * 70)

print("\nLoading cleaned EONET dataset...")

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"Total observations: {len(df):,}"
)


# ============================================================
# SELECT EVENTS WITH VALID COORDINATES
# ============================================================

geo_df = df[
    df["latitude"].notna()
    &
    df["longitude"].notna()
].copy()

print(
    f"Observations with coordinates: "
    f"{len(geo_df):,}"
)

print(
    f"Observations without coordinates: "
    f"{len(df) - len(geo_df):,}"
)


# ============================================================
# CREATE POINT GEOMETRY
# ============================================================

print("\nCreating geographic points...")

geo_df["latitude"] = pd.to_numeric(
    geo_df["latitude"],
    errors="coerce"
)

geo_df["longitude"] = pd.to_numeric(
    geo_df["longitude"],
    errors="coerce"
)

# GeoPandas expects x = longitude
# and y = latitude.

points = gpd.GeoDataFrame(
    geo_df,
    geometry=gpd.points_from_xy(
        geo_df["longitude"],
        geo_df["latitude"]
    ),
    crs="EPSG:4326"
)


# ============================================================
# DOWNLOAD NATURAL EARTH COUNTRY BOUNDARIES
# ============================================================

print(
    "\nDownloading Natural Earth country boundaries..."
)

response = requests.get(
    NATURAL_EARTH_URL,
    timeout=60
)

response.raise_for_status()

zip_data = io.BytesIO(
    response.content
)


# ============================================================
# READ SHAPEFILE FROM ZIP
# ============================================================

with zipfile.ZipFile(
    zip_data
) as z:

    shapefile = [
        name
        for name in z.namelist()
        if name.endswith(".shp")
    ][0]

    # GeoPandas/Fiona can read from the
    # zip archive using the /vsizip/ mechanism,
    # but extracting to a temporary folder is
    # more reliable across Windows environments.

    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:

        z.extractall(
            temp_dir
        )

        country_file = (
            Path(temp_dir)
            /
            shapefile
        )

        countries = gpd.read_file(
            country_file
        )


# ============================================================
# DISPLAY COUNTRY DATA
# ============================================================

print(
    f"Country polygons loaded: "
    f"{len(countries):,}"
)

print(
    "\nCountry boundary columns:"
)

print(
    list(countries.columns)
)


# ============================================================
# SELECT USEFUL COUNTRY ATTRIBUTES
# ============================================================

# Natural Earth version 5.1.1 includes
# ISO codes and geographic region fields.

possible_columns = [
    "ADMIN",
    "NAME",
    "NAME_LONG",
    "ISO_A3",
    "ISO_A2",
    "SOVEREIGNT",
    "CONTINENT",
    "REGION_UN",
    "SUBREGION"
]

available_columns = [
    column
    for column in possible_columns
    if column in countries.columns
]


print(
    "\nAvailable country attributes:"
)

print(
    available_columns
)


# ============================================================
# KEEP COUNTRY GEOMETRY + ATTRIBUTES
# ============================================================

countries = countries[
    available_columns
    +
    ["geometry"]
].copy()


# ============================================================
# STANDARDIZE CRS
# ============================================================

countries = countries.to_crs(
    "EPSG:4326"
)


# ============================================================
# SPATIAL JOIN
# ============================================================

print(
    "\nPerforming spatial join..."
)

# Each event point is matched with the
# country polygon containing that point.

joined = gpd.sjoin(
    points,
    countries,
    how="left",
    predicate="within"
)


# ============================================================
# REMOVE SPATIAL INDEX COLUMN
# ============================================================

if "index_right" in joined.columns:

    joined = joined.drop(
        columns=["index_right"]
    )


# ============================================================
# RENAME COUNTRY FIELDS
# ============================================================

rename_map = {}

if "ADMIN" in joined.columns:

    rename_map["ADMIN"] = "country"

elif "NAME" in joined.columns:

    rename_map["NAME"] = "country"


if "ISO_A3" in joined.columns:

    rename_map["ISO_A3"] = "country_iso3"


if "CONTINENT" in joined.columns:

    rename_map["CONTINENT"] = "continent"


if "REGION_UN" in joined.columns:

    rename_map["REGION_UN"] = "world_region"


if "SUBREGION" in joined.columns:

    rename_map["SUBREGION"] = "subregion"


joined = joined.rename(
    columns=rename_map
)


# ============================================================
# REMOVE GEOMETRY BEFORE CSV
# ============================================================

if "geometry" in joined.columns:

    joined = pd.DataFrame(
        joined.drop(
            columns=["geometry"]
        )
    )


# ============================================================
# CHECK UNMAPPED EVENTS
# ============================================================

if "country" in joined.columns:

    mapped_count = (
        joined["country"]
        .notna()
        .sum()
    )

    unmapped_count = (
        joined["country"]
        .isna()
        .sum()
    )

else:

    mapped_count = 0
    unmapped_count = len(joined)


print(
    f"\nCountry-mapped observations: "
    f"{mapped_count:,}"
)

print(
    f"Unmapped observations: "
    f"{unmapped_count:,}"
)


# ============================================================
# SAVE COUNTRY-MAPPED DATA
# ============================================================

OUTPUT_FILE = (
    OUTPUT_DIR
    /
    "eonet_events_with_country.csv"
)

joined.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# COUNTRY SUMMARY
# ============================================================

if "country" in joined.columns:

    country_summary = (
        joined["country"]
        .value_counts()
        .reset_index()
    )

    country_summary.columns = [
        "country",
        "event_observations"
    ]

    country_summary_file = (
        OUTPUT_DIR
        /
        "country_event_summary.csv"
    )

    country_summary.to_csv(
        country_summary_file,
        index=False
    )


# ============================================================
# REPORT
# ============================================================

report = []

report.append(
    "NASA EONET COUNTRY MAPPING REPORT"
)

report.append(
    "=" * 70
)

report.append(
    f"Total cleaned observations: "
    f"{len(df):,}"
)

report.append(
    f"Observations with coordinates: "
    f"{len(geo_df):,}"
)

report.append(
    f"Country mapped: "
    f"{mapped_count:,}"
)

report.append(
    f"Unmapped: "
    f"{unmapped_count:,}"
)

if len(geo_df) > 0:

    mapping_percentage = (
        mapped_count
        /
        len(geo_df)
        *
        100
    )

    report.append(
        f"Mapping success rate: "
        f"{mapping_percentage:.2f}%"
    )


if "country" in joined.columns:

    report.append(
        "\nTop countries:"
    )

    report.append(
        joined["country"]
        .value_counts()
        .head(25)
        .to_string()
    )


report_file = (
    OUTPUT_DIR
    /
    "country_mapping_report.txt"
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
print("STEP 8 COMPLETE")
print("=" * 70)

print(
    f"\nCountry-mapped dataset:"
)

print(
    OUTPUT_FILE
)

print(
    "\nCountry summary:"
)

if "country_summary_file" in locals():

    print(
        country_summary_file
    )

print(
    "\nMapping report:"
)

print(
    report_file
)

print(
    "\nNext step:"
)

print(
    "Inspect country mapping results before "
    "building regional features."
)