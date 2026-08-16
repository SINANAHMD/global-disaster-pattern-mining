"""
NASA EONET v3 - Complete Historical Dataset Collector

Project:
Global Disaster Pattern Mining and Regional Risk Profile Clustering

Collection period:
2015-01-01 to 2025-12-31

Method:
Monthly API requests -> combine -> remove duplicate event IDs
-> save raw JSON -> create flat CSV
"""

from pathlib import Path
from datetime import datetime, timezone
import json
import time

import requests
import pandas as pd


# ============================================================
# PROJECT SETTINGS
# ============================================================

BASE_URL = "https://eonet.gsfc.nasa.gov/api/v3"

START_YEAR = 2015
END_YEAR = 2025

STATUS = "all"

# Small monthly windows prevent the 5000-event API limit
# from cutting off our historical dataset.
REQUEST_LIMIT = 5000

# Small delay between requests
REQUEST_DELAY = 0.2


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# API REQUEST FUNCTION
# ============================================================

def get_json(url, params=None):

    response = requests.get(
        url,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# FLATTEN EVENT DATA
# ============================================================

def flatten_events(events):

    rows = []

    for event in events:

        categories = event.get("categories") or []
        sources = event.get("sources") or []
        geometry = event.get("geometry") or []

        # Use the first geometry for the flat CSV.
        # Full geometry information remains preserved
        # inside the raw JSON snapshot.

        first_geometry = geometry[0] if geometry else {}

        coordinates = first_geometry.get(
            "coordinates"
        ) if isinstance(first_geometry, dict) else None

        latitude = None
        longitude = None

        if (
            isinstance(coordinates, list)
            and len(coordinates) >= 2
        ):

            if (
                isinstance(coordinates[0], (int, float))
                and isinstance(coordinates[1], (int, float))
            ):

                # GeoJSON uses [longitude, latitude]

                longitude = coordinates[0]
                latitude = coordinates[1]

        # Category information

        category_ids = [
            str(c.get("id"))
            for c in categories
            if c.get("id") is not None
        ]

        category_titles = [
            c.get("title")
            for c in categories
            if c.get("title")
        ]

        # Source information

        source_ids = [
            str(s.get("id"))
            for s in sources
            if s.get("id") is not None
        ]

        source_titles = [
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
                "|".join(category_titles),

            "source_ids":
                "|".join(source_ids),

            "source_names":
                "|".join(source_titles),

            "source_urls":
                "|".join(source_urls),

            "event_date":
                first_geometry.get("date"),

            "geometry_type":
                first_geometry.get("type"),

            "longitude":
                longitude,

            "latitude":
                latitude,

            "magnitude_value":
                first_geometry.get(
                    "magnitudeValue"
                ),

            "magnitude_unit":
                first_geometry.get(
                    "magnitudeUnit"
                ),

            "magnitude_description":
                first_geometry.get(
                    "magnitudeDescription"
                ),

            "source_count":
                len(sources),

            "geometry_count":
                len(geometry),

            "event_link":
                event.get("link"),
        })

    return rows


# ============================================================
# MONTHLY DATE GENERATOR
# ============================================================

def generate_months():

    periods = []

    for year in range(
        START_YEAR,
        END_YEAR + 1
    ):

        for month in range(1, 13):

            start_date = (
                f"{year:04d}-{month:02d}-01"
            )

            if month == 12:

                next_year = year + 1
                next_month = 1

            else:

                next_year = year
                next_month = month + 1

            end_date = (
                f"{next_year:04d}-"
                f"{next_month:02d}-01"
            )

            periods.append(
                (
                    start_date,
                    end_date
                )
            )

    return periods


# ============================================================
# MAIN COLLECTION
# ============================================================

def main():

    print("=" * 70)
    print("NASA EONET HISTORICAL DATA COLLECTION")
    print("=" * 70)

    print()
    print(
        f"Collection period: "
        f"{START_YEAR}-01-01 → "
        f"{END_YEAR}-12-31"
    )

    print(f"Status: {STATUS}")
    print(f"Monthly requests: {12 * (END_YEAR - START_YEAR + 1)}")
    print()

    all_events = []

    periods = generate_months()

    for index, (start_date, end_date) in enumerate(
        periods,
        start=1
    ):

        print(
            f"[{index:03d}/{len(periods)}] "
            f"{start_date} → {end_date}"
        )

        params = {

            "status": STATUS,

            "start": start_date,

            "end": end_date,

            "limit": REQUEST_LIMIT,
        }

        try:

            payload = get_json(
                f"{BASE_URL}/events",
                params=params
            )

            events = payload.get(
                "events",
                []
            )

            print(
                f"       Events received: "
                f"{len(events):,}"
            )

            all_events.extend(events)

        except Exception as error:

            print(
                f"       ERROR: {error}"
            )

        time.sleep(
            REQUEST_DELAY
        )

    print()
    print("=" * 70)
    print("COMBINING EVENTS")
    print("=" * 70)

    print(
        f"Events before duplicate removal: "
        f"{len(all_events):,}"
    )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique_events = {}

    for event in all_events:

        event_id = event.get("id")

        if event_id:

            unique_events[event_id] = event

    all_events = list(
        unique_events.values()
    )

    print(
        f"Unique events: "
        f"{len(all_events):,}"
    )

    # ========================================================
    # SAVE RAW JSON
    # ========================================================

    raw_json_path = (
        RAW_DIR /
        f"eonet_events_{START_YEAR}_{END_YEAR}.json"
    )

    raw_payload = {

        "metadata": {

            "api": BASE_URL,

            "api_version": "v3",

            "start_year": START_YEAR,

            "end_year": END_YEAR,

            "status": STATUS,

            "collection_utc":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "collection_method":
                "monthly date-range requests",

            "event_count":
                len(all_events),
        },

        "events":
            all_events,
    }

    raw_json_path.write_text(
        json.dumps(
            raw_payload,
            indent=2
        ),
        encoding="utf-8"
    )

    # ========================================================
    # CREATE FLAT CSV
    # ========================================================

    rows = flatten_events(
        all_events
    )

    df = pd.DataFrame(
        rows
    )

    csv_path = (
        RAW_DIR /
        f"eonet_events_{START_YEAR}_{END_YEAR}_flat.csv"
    )

    df.to_csv(
        csv_path,
        index=False
    )

    # ========================================================
    # CATEGORY METADATA
    # ========================================================

    print()
    print(
        "Downloading category metadata..."
    )

    categories = get_json(
        f"{BASE_URL}/categories"
    )

    categories_path = (
        RAW_DIR /
        "eonet_categories.json"
    )

    categories_path.write_text(
        json.dumps(
            categories,
            indent=2
        ),
        encoding="utf-8"
    )

    # ========================================================
    # COLLECTION METADATA
    # ========================================================

    metadata_path = (
        RAW_DIR /
        "collection_metadata.txt"
    )

    metadata_lines = [

        f"collection_utc="
        f"{datetime.now(timezone.utc).isoformat()}",

        f"api_base={BASE_URL}",

        "api_version=v3",

        f"start="
        f"{START_YEAR}-01-01",

        f"end="
        f"{END_YEAR}-12-31",

        f"status={STATUS}",

        "collection_method="
        "monthly_date_range_requests",

        f"raw_unique_event_count="
        f"{len(all_events)}",

        f"flat_csv_row_count="
        f"{len(df)}",

        f"flat_csv_columns="
        f"{','.join(df.columns)}",
    ]

    metadata_path.write_text(
        "\n".join(metadata_lines),
        encoding="utf-8"
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)

    print(
        f"Unique events: "
        f"{len(all_events):,}"
    )

    print(
        f"CSV rows: "
        f"{len(df):,}"
    )

    print()
    print(
        f"Raw JSON:\n{raw_json_path}"
    )

    print()
    print(
        f"Flat CSV:\n{csv_path}"
    )

    print()
    print(
        "Next step: run the data audit."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()