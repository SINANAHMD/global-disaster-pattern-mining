"""
STEP 7 - Clean and prepare NASA EONET event data.

Input:
    data/processed/eonet_events_2015_2025_clean.csv

Output:
    data/processed/eonet_events_final.csv
    data/processed/cleaning_report.txt
    data/processed/category_summary.csv

Important decision:
    Records without coordinates are NOT deleted.
    They remain available for temporal/category analysis.

    Geographic analysis and regional clustering will later
    use only records with valid coordinates.
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
    / "eonet_events_2015_2025_clean.csv"
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
# LOAD DATA
# ============================================================

print("=" * 70)
print("STEP 7 - EONET DATA CLEANING")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"Input rows: {len(df):,}"
)

print(
    f"Input columns: {len(df.columns)}"
)


# ============================================================
# PRESERVE ORIGINAL CATEGORY INFORMATION
# ============================================================

# We keep the original categories field.
# This is important for traceability.

df["categories"] = (
    df["categories"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# NORMALIZE CATEGORY NAMES
# ============================================================

def normalize_category(value):

    if not value:
        return ""

    categories = []

    for category in value.split("|"):

        category = category.strip()

        if category:

            categories.append(
                category
            )

    # Remove duplicate category names
    # while preserving order.

    categories = list(
        dict.fromkeys(categories)
    )

    return "|".join(categories)


df["categories"] = (
    df["categories"]
    .apply(normalize_category)
)


# ============================================================
# DATE PROCESSING
# ============================================================

print("\nProcessing dates...")

df["event_date"] = pd.to_datetime(
    df["event_date"],
    errors="coerce",
    utc=True
)

invalid_dates = (
    df["event_date"].isna().sum()
)

print(
    f"Invalid dates: {invalid_dates:,}"
)


# ============================================================
# COORDINATE VALIDATION
# ============================================================

print("\nValidating coordinates...")

df["latitude"] = pd.to_numeric(
    df["latitude"],
    errors="coerce"
)

df["longitude"] = pd.to_numeric(
    df["longitude"],
    errors="coerce"
)


invalid_latitude = (
    df["latitude"].notna()
    &
    ~df["latitude"].between(
        -90,
        90
    )
)

invalid_longitude = (
    df["longitude"].notna()
    &
    ~df["longitude"].between(
        -180,
        180
    )
)

invalid_coordinate_count = (
    invalid_latitude
    |
    invalid_longitude
).sum()


# Convert invalid coordinates to missing

df.loc[
    invalid_latitude,
    "latitude"
] = pd.NA

df.loc[
    invalid_longitude,
    "longitude"
] = pd.NA


# ============================================================
# COORDINATE FLAG
# ============================================================

df["has_coordinates"] = (
    df["latitude"].notna()
    &
    df["longitude"].notna()
)


print(
    f"Rows with coordinates: "
    f"{df['has_coordinates'].sum():,}"
)

print(
    f"Rows without coordinates: "
    f"{(~df['has_coordinates']).sum():,}"
)


# ============================================================
# REMOVE UNNECESSARY HIGH-MISSING TEXT COLUMNS
# ============================================================

columns_to_remove = [
    "description",
    "magnitude_description"
]

existing_columns_to_remove = [
    column
    for column in columns_to_remove
    if column in df.columns
]

df = df.drop(
    columns=existing_columns_to_remove
)


print(
    "\nRemoved unnecessary columns:"
)

for column in existing_columns_to_remove:

    print(
        f"  - {column}"
    )


# ============================================================
# NUMERIC MAGNITUDE
# ============================================================

if "magnitude_value" in df.columns:

    df["magnitude_value"] = pd.to_numeric(
        df["magnitude_value"],
        errors="coerce"
    )


# ============================================================
# TIME FEATURES
# ============================================================

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


# ============================================================
# CATEGORY COUNT
# ============================================================

df["category_count"] = df[
    "categories"
].apply(
    lambda x:
    len(
        [
            c
            for c in x.split("|")
            if c
        ]
    )
)


# ============================================================
# MULTI-CATEGORY FLAG
# ============================================================

df["is_multi_category"] = (
    df["category_count"] > 1
)


# ============================================================
# CATEGORY INDICATOR COLUMNS
# ============================================================

print(
    "\nCreating category indicators..."
)

# Find all individual categories.

all_categories = set()

for value in df["categories"]:

    if not value:
        continue

    for category in value.split("|"):

        category = category.strip()

        if category:
            all_categories.add(
                category
            )


all_categories = sorted(
    all_categories
)


print(
    f"Unique category labels found: "
    f"{len(all_categories)}"
)


# Create binary columns.

for category in all_categories:

    # Convert category name to safe column name.

    column_name = (
        category
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )

    column_name = (
        "cat_"
        + column_name
    )

    df[column_name] = (
        df["categories"]
        .str.split("|")
        .apply(
            lambda values:
            int(
                category
                in values
            )
        )
    )


# ============================================================
# CATEGORY SUMMARY
# ============================================================

category_rows = []

for category in all_categories:

    count = (
        df["categories"]
        .str.split("|")
        .apply(
            lambda values:
            category
            in values
        )
        .sum()
    )

    percentage = (
        count
        /
        len(df)
        *
        100
    )

    category_rows.append({

        "category":
            category,

        "observation_count":
            int(count),

        "percentage":
            round(
                percentage,
                3
            )
    })


category_summary = pd.DataFrame(
    category_rows
)

category_summary = (
    category_summary
    .sort_values(
        "observation_count",
        ascending=False
    )
)


category_summary_file = (
    OUTPUT_DIR
    /
    "category_summary.csv"
)

category_summary.to_csv(
    category_summary_file,
    index=False
)


# ============================================================
# REMOVE EXACT DUPLICATE ROWS
# ============================================================

before_duplicates = len(df)

df = df.drop_duplicates()

duplicates_removed = (
    before_duplicates
    -
    len(df)
)


print(
    f"\nExact duplicate rows removed: "
    f"{duplicates_removed:,}"
)


# ============================================================
# SORT DATA
# ============================================================

df = df.sort_values(
    "event_date"
).reset_index(
    drop=True
)


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

preferred_columns = [

    "event_id",
    "title",

    "categories",
    "category_count",
    "is_multi_category",

    "event_date",
    "year",
    "month",
    "month_name",

    "latitude",
    "longitude",
    "has_coordinates",

    "geometry_type",

    "magnitude_value",
    "magnitude_unit",

    "source_ids",
    "source_names",
    "source_urls",

    "source_count",
    "geometry_count",

    "closed",
    "event_link"
]


# Add category indicator columns after
# the main fields.

category_columns = [
    column
    for column in df.columns
    if column.startswith("cat_")
]


final_columns = [
    column
    for column in preferred_columns
    if column in df.columns
]

final_columns += category_columns

# Add anything unexpected at the end
# so information isn't accidentally lost.

remaining_columns = [
    column
    for column in df.columns
    if column not in final_columns
]

final_columns += remaining_columns


df = df[
    final_columns
]


# ============================================================
# SAVE FINAL CLEAN DATASET
# ============================================================

OUTPUT_FILE = (
    OUTPUT_DIR
    /
    "eonet_events_final.csv"
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# CREATE CLEANING REPORT
# ============================================================

report = []

report.append(
    "NASA EONET FINAL CLEANING REPORT"
)

report.append(
    "=" * 70
)

report.append(
    f"Input rows: {before_duplicates:,}"
)

report.append(
    f"Final rows: {len(df):,}"
)

report.append(
    f"Exact duplicate rows removed: "
    f"{duplicates_removed:,}"
)

report.append(
    f"Invalid coordinate rows detected: "
    f"{invalid_coordinate_count:,}"
)

report.append(
    f"Rows with coordinates: "
    f"{df['has_coordinates'].sum():,}"
)

report.append(
    f"Rows without coordinates: "
    f"{(~df['has_coordinates']).sum():,}"
)

report.append(
    f"Invalid dates: {invalid_dates:,}"
)

report.append(
    f"Final columns: {len(df.columns)}"
)

report.append(
    "\nCategory labels:"
)

for category in all_categories:

    report.append(
        f"  - {category}"
    )

report.append(
    "\nMissing values:"
)

report.append(
    df.isna()
    .sum()
    .sort_values(
        ascending=False
    )
    .to_string()
)


report_file = (
    OUTPUT_DIR
    /
    "cleaning_report.txt"
)

report_file.write_text(
    "\n".join(report),
    encoding="utf-8"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("STEP 7 COMPLETE")
print("=" * 70)

print(
    f"\nFinal rows: {len(df):,}"
)

print(
    f"Final columns: {len(df.columns)}"
)

print(
    f"\nFinal dataset:"
    f"\n{OUTPUT_FILE}"
)

print(
    f"\nCategory summary:"
    f"\n{category_summary_file}"
)

print(
    f"\nCleaning report:"
    f"\n{report_file}"
)

print(
    "\nImportant:"
)

print(
    "Records without coordinates were KEPT."
)

print(
    "They will be excluded later only "
    "from geographic/regional analysis."
)

print(
    "\nNext step: inspect the cleaning results."
)