import os
import sys
import json
import unicodedata

import numpy as np
import pandas as pd
from shapely.geometry import shape, Point
from shapely.prepared import prep


sys.stdout.reconfigure(encoding="utf-8")


# ======================================================================
# PATHS
# ======================================================================

DATA_DIR = os.path.join("data", "prediction", "india")
os.makedirs(DATA_DIR, exist_ok=True)

CSV_PATH = os.path.join(
    "data",
    "processed",
    "eonet_events_final.csv"
)

GEOJSON_PATH = os.path.join(
    "data",
    "prediction",
    "boundaries",
    "india_adm1.geojson"
)

UNIQUE_EVENTS_OUTPUT = os.path.join(
    DATA_DIR,
    "india_state_unique_events.csv"
)

MONTHLY_EVENTS_OUTPUT = os.path.join(
    DATA_DIR,
    "india_state_monthly_events.csv"
)

PREDICTION_DATASET_OUTPUT = os.path.join(
    DATA_DIR,
    "india_state_prediction_dataset.csv"
)

REPORT_OUTPUT = os.path.join(
    DATA_DIR,
    "india_state_prediction_report.txt"
)


# ======================================================================
# STATE NAME NORMALIZATION
# ======================================================================

def normalize_state_name(raw_name):
    """
    Convert boundary names such as:

    Mahārāshtra -> Maharashtra
    Tamil Nādu   -> Tamil Nadu
    Karnātaka    -> Karnataka
    Gujarāt      -> Gujarat

    without manually assigning geographic locations.
    """

    if not raw_name:
        return ""

    normalized = unicodedata.normalize(
        "NFKD",
        str(raw_name)
    )

    normalized = (
        normalized
        .encode("ASCII", "ignore")
        .decode("utf-8")
        .strip()
    )

    return normalized


# ======================================================================
# MAIN
# ======================================================================

def main():

    print("=" * 70)
    print("BUILDING INDIA STATE-LEVEL PREDICTION DATASET")
    print("ALL GEOMETRY SPATIAL JOIN")
    print("=" * 70)

    # ==================================================================
    # 1. CHECK INPUT FILES
    # ==================================================================

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"EONET dataset not found: {CSV_PATH}"
        )

    if not os.path.exists(GEOJSON_PATH):
        raise FileNotFoundError(
            f"India ADM1 boundary file not found: {GEOJSON_PATH}"
        )

    # ==================================================================
    # 2. LOAD INDIA ADM1 BOUNDARIES
    # ==================================================================

    print("\nLoading India ADM1 boundaries...")

    with open(
        GEOJSON_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        gdata = json.load(f)

    prep_states = []

    for feature in gdata.get("features", []):

        properties = feature.get("properties", {})

        raw_name = properties.get(
            "shapeName",
            ""
        )

        normalized_name = normalize_state_name(
            raw_name
        )

        polygon = shape(
            feature["geometry"]
        )

        prep_states.append(
            {
                "raw_name": raw_name,
                "norm_name": normalized_name,
                "prep_poly": prep(polygon),
            }
        )

    print(
        f"State / UT boundaries loaded: {len(prep_states)}"
    )

    # ==================================================================
    # 3. LOAD EONET DATA
    # ==================================================================

    print("\nLoading EONET data...")

    df_raw = pd.read_csv(
        CSV_PATH
    )

    total_observations = len(df_raw)

    total_unique_events = (
        df_raw["event_id"].nunique()
    )

    print(
        f"Total EONET geometry observations: "
        f"{total_observations}"
    )

    print(
        f"Total unique event IDs: "
        f"{total_unique_events}"
    )

    # ==================================================================
    # 4. VALID COORDINATES
    # ==================================================================

    valid_mask = (
        df_raw["latitude"].notna()
        &
        df_raw["longitude"].notna()
        &
        (df_raw["latitude"] >= -90)
        &
        (df_raw["latitude"] <= 90)
        &
        (df_raw["longitude"] >= -180)
        &
        (df_raw["longitude"] <= 180)
    )

    df_valid = df_raw[
        valid_mask
    ].copy()

    print(
        f"Valid geometry observations: "
        f"{len(df_valid)}"
    )

    print(
        f"Unique events with valid coordinates: "
        f"{df_valid['event_id'].nunique()}"
    )

    # ==================================================================
    # 5. ALL-GEOMETRY SPATIAL JOIN
    # ==================================================================
    #
    # IMPORTANT:
    #
    # We intentionally DO NOT select only one coordinate per event.
    #
    # Every geometry observation belonging to an EONET event is tested.
    #
    # This allows tracked events such as storms/cyclones to be associated
    # with an Indian state when any part of their geometry enters that
    # state's boundary.
    #
    # No nearest-state assignment is performed.
    # ==================================================================

    print(
        "\nPerforming ALL-GEOMETRY spatial join..."
    )

    mapped_records = []

    for _, row in df_valid.iterrows():

        latitude = float(
            row["latitude"]
        )

        longitude = float(
            row["longitude"]
        )

        point = Point(
            longitude,
            latitude
        )

        for state in prep_states:

            if state["prep_poly"].intersects(point):

                mapped_records.append(
                    {
                        "event_id": row["event_id"],
                        "title": row["title"],
                        "categories": row["categories"],
                        "event_date": row["event_date"],
                        "year": int(row["year"]),
                        "month": int(row["month"]),
                        "latitude": latitude,
                        "longitude": longitude,
                        "state_name_raw": state["raw_name"],
                        "state_name": state["norm_name"],
                    }
                )

    # ==================================================================
    # 6. CREATE MAPPED OBSERVATION DATAFRAME
    # ==================================================================

    if mapped_records:

        df_mapped_obs = pd.DataFrame(
            mapped_records
        )

    else:

        df_mapped_obs = pd.DataFrame(
            columns=[
                "event_id",
                "title",
                "categories",
                "event_date",
                "year",
                "month",
                "latitude",
                "longitude",
                "state_name_raw",
                "state_name",
            ]
        )

    mapped_geometry_observations = len(
        df_mapped_obs
    )

    mapped_unique_events = (
        df_mapped_obs["event_id"].nunique()
        if len(df_mapped_obs) > 0
        else 0
    )

    print(
        f"Geometry observations intersecting India: "
        f"{mapped_geometry_observations}"
    )

    print(
        f"Unique events affecting India: "
        f"{mapped_unique_events}"
    )

    # ==================================================================
    # 7. STATE-EVENT DEDUPLICATION
    # ==================================================================
    #
    # IMPORTANT:
    #
    # Deduplicate by:
    #
    #     state_name + event_id
    #
    # NOT by event_id alone.
    #
    # This means an event can legitimately belong to multiple states.
    #
    # Example:
    #
    # EONET_5938
    #     Kerala
    #     Karnataka
    #     Tamil Nadu
    #
    # This remains three state-event associations but ONE unique event.
    # ==================================================================

    mapped_unique_rows = []

    if len(df_mapped_obs) > 0:

        grouped = df_mapped_obs.groupby(
            [
                "state_name",
                "event_id",
            ],
            sort=False
        )

        for (
            state_name,
            event_id
        ), group in grouped:

            first_row = group.iloc[0]

            mapped_unique_rows.append(
                {
                    "event_id": event_id,

                    "title": first_row["title"],

                    "categories": first_row[
                        "categories"
                    ],

                    "event_date": first_row[
                        "event_date"
                    ],

                    "year": int(
                        first_row["year"]
                    ),

                    "month": int(
                        first_row["month"]
                    ),

                    # Mean coordinate of all geometry
                    # points that intersect this state.
                    "latitude": round(
                        float(
                            group["latitude"].mean()
                        ),
                        6
                    ),

                    "longitude": round(
                        float(
                            group["longitude"].mean()
                        ),
                        6
                    ),

                    "state_name_raw": first_row[
                        "state_name_raw"
                    ],

                    "state_name": state_name,

                    "geometry_mapping_status": "mapped",
                }
            )

    df_state_events = pd.DataFrame(
        mapped_unique_rows
    )

    # ==================================================================
    # 8. SAFETY FILTER
    # ==================================================================
    #
    # THIS IS THE IMPORTANT FIX.
    #
    # Only mapped Indian state-event associations are written to:
    #
    # india_state_unique_events.csv
    #
    # Unmapped global events are NOT written into this India dataset.
    # ==================================================================

    if len(df_state_events) > 0:

        df_state_events = df_state_events[
            df_state_events["state_name"].notna()
            &
            (
                df_state_events["state_name"]
                .astype(str)
                .str.strip()
                != ""
            )
        ].copy()

    # ==================================================================
    # 9. VALIDATE STATE-EVENT PAIRS
    # ==================================================================

    duplicate_state_event_pairs = (
        df_state_events.duplicated(
            subset=[
                "event_id",
                "state_name",
            ]
        ).sum()
    )

    if duplicate_state_event_pairs > 0:

        print(
            "\nWARNING:"
        )

        print(
            f"Duplicate state-event pairs detected: "
            f"{duplicate_state_event_pairs}"
        )

        df_state_events = (
            df_state_events
            .drop_duplicates(
                subset=[
                    "event_id",
                    "state_name",
                ]
            )
            .copy()
        )

    # ==================================================================
    # 10. MULTI-STATE EVENT ANALYSIS
    # ==================================================================

    if len(df_state_events) > 0:

        event_state_counts = (
            df_state_events
            .groupby("event_id")["state_name"]
            .nunique()
        )

        multi_state_events = (
            event_state_counts[
                event_state_counts > 1
            ]
        )

    else:

        event_state_counts = pd.Series(
            dtype=int
        )

        multi_state_events = pd.Series(
            dtype=int
        )

    # ==================================================================
    # 11. SAVE CLEAN INDIA UNIQUE EVENT DATASET
    # ==================================================================

    df_state_events = (
        df_state_events
        .sort_values(
            [
                "state_name",
                "year",
                "month",
                "event_id",
            ]
        )
        .reset_index(drop=True)
    )

    df_state_events.to_csv(
        UNIQUE_EVENTS_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    # ==================================================================
    # 12. CREATE COMPLETE MONTHLY STATE TIMELINE
    # ==================================================================

    print(
        "\nCreating complete state-month timeline..."
    )

    if len(df_state_events) == 0:

        raise RuntimeError(
            "No EONET events were mapped to Indian states."
        )

    represented_states = sorted(
        df_state_events[
            "state_name"
        ].unique()
    )

    min_year = int(
        df_state_events["year"].min()
    )

    max_year = int(
        df_state_events["year"].max()
    )

    timeline_rows = []

    for state in represented_states:

        for year in range(
            min_year,
            max_year + 1
        ):

            for month in range(
                1,
                13
            ):

                timeline_rows.append(
                    {
                        "state_name": state,
                        "year": year,
                        "month": month,
                        "date": (
                            f"{year:04d}-"
                            f"{month:02d}-01"
                        ),
                    }
                )

    df_timeline = pd.DataFrame(
        timeline_rows
    )

    # Count unique events per state/month.
    df_events_grouped = (
        df_state_events
        .groupby(
            [
                "state_name",
                "year",
                "month",
            ]
        )["event_id"]
        .nunique()
        .reset_index(
            name="event_count"
        )
    )

    df_monthly = pd.merge(
        df_timeline,
        df_events_grouped,
        on=[
            "state_name",
            "year",
            "month",
        ],
        how="left"
    )

    df_monthly[
        "event_count"
    ] = (
        df_monthly[
            "event_count"
        ]
        .fillna(0)
        .astype(int)
    )

    df_monthly = (
        df_monthly
        .sort_values(
            [
                "state_name",
                "year",
                "month",
            ]
        )
        .reset_index(drop=True)
    )

    df_monthly.to_csv(
        MONTHLY_EVENTS_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    # ==================================================================
    # 13. BUILD STATE-LEVEL PREDICTION DATASET
    # ==================================================================

    print(
        "\nCreating state-level prediction features..."
    )

    prediction_rows = []

    for state in represented_states:

        state_df = (
            df_monthly[
                df_monthly["state_name"]
                == state
            ]
            .sort_values(
                [
                    "year",
                    "month",
                ]
            )
            .reset_index(drop=True)
        )

        counts = (
            state_df[
                "event_count"
            ]
            .to_numpy()
        )

        years = (
            state_df[
                "year"
            ]
            .to_numpy()
        )

        months = (
            state_df[
                "month"
            ]
            .to_numpy()
        )

        dates = (
            state_df[
                "date"
            ]
            .to_numpy()
        )

        n_months = len(
            state_df
        )

        for i in range(
            n_months
        ):

            current_year = int(
                years[i]
            )

            current_month = int(
                months[i]
            )

            current_date = dates[i]

            current_count = int(
                counts[i]
            )

            # ----------------------------------------------------------
            # Historical features
            # ----------------------------------------------------------

            previous_month = (
                int(counts[i - 1])
                if i >= 1
                else 0
            )

            previous_3_months = int(
                np.sum(
                    counts[
                        max(0, i - 3):i
                    ]
                )
            )

            previous_6_months = int(
                np.sum(
                    counts[
                        max(0, i - 6):i
                    ]
                )
            )

            previous_12_months = int(
                np.sum(
                    counts[
                        max(0, i - 12):i
                    ]
                )
            )

            # ----------------------------------------------------------
            # Same-month historical activity
            # ----------------------------------------------------------

            same_month_historical = 0

            for j in range(i):

                if (
                    int(months[j])
                    == current_month
                    and
                    int(years[j])
                    < current_year
                ):

                    same_month_historical += int(
                        counts[j]
                    )

            # ----------------------------------------------------------
            # Historical total
            # ----------------------------------------------------------

            historical_total = int(
                np.sum(
                    counts[:i]
                )
            )

            # ----------------------------------------------------------
            # Historical active months
            # ----------------------------------------------------------

            historical_active_months = int(
                np.sum(
                    counts[:i] > 0
                )
            )

            # ----------------------------------------------------------
            # Recent activity share
            # ----------------------------------------------------------

            recent_activity_share = (
                float(
                    previous_3_months
                )
                /
                (
                    float(
                        previous_12_months
                    )
                    + 1.0
                )
            )

            # ----------------------------------------------------------
            # Seasonal features
            # ----------------------------------------------------------

            month_sin = float(
                np.sin(
                    2.0
                    * np.pi
                    * current_month
                    / 12.0
                )
            )

            month_cos = float(
                np.cos(
                    2.0
                    * np.pi
                    * current_month
                    / 12.0
                )
            )

            years_since_2015 = int(
                current_year - 2015
            )

            # ----------------------------------------------------------
            # Next-month target
            #
            # Last month does not have a known next-month target
            # inside the available timeline, so it is excluded.
            # ----------------------------------------------------------

            if i + 1 >= n_months:
                continue

            next_month_event_count = int(
                counts[i + 1]
            )

            next_month_event = int(
                next_month_event_count > 0
            )

            prediction_rows.append(
                {
                    "state_name": state,

                    "year": current_year,

                    "month": current_month,

                    "date": current_date,

                    "current_event_count": current_count,

                    "previous_month_events": previous_month,

                    "previous_3_month_events": (
                        previous_3_months
                    ),

                    "previous_6_month_events": (
                        previous_6_months
                    ),

                    "previous_12_month_events": (
                        previous_12_months
                    ),

                    "same_month_historical_events": (
                        same_month_historical
                    ),

                    "historical_total_events": (
                        historical_total
                    ),

                    "historical_active_months": (
                        historical_active_months
                    ),

                    "recent_activity_share": (
                        recent_activity_share
                    ),

                    "month_sin": month_sin,

                    "month_cos": month_cos,

                    "years_since_2015": (
                        years_since_2015
                    ),

                    "next_month_event_count": (
                        next_month_event_count
                    ),

                    "next_month_event": (
                        next_month_event
                    ),
                }
            )

    df_prediction = pd.DataFrame(
        prediction_rows
    )

    df_prediction.to_csv(
        PREDICTION_DATASET_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    # ==================================================================
    # 14. STATISTICS
    # ==================================================================

    positive_targets = int(
        df_prediction[
            "next_month_event"
        ].sum()
    )

    negative_targets = (
        len(df_prediction)
        - positive_targets
    )

    positive_rate = (
        positive_targets
        / len(df_prediction)
        * 100.0
        if len(df_prediction) > 0
        else 0.0
    )

    # ==================================================================
    # 15. CREATE REPORT
    # ==================================================================

    report_lines = []

    report_lines.append(
        "=" * 70
    )

    report_lines.append(
        "INDIA STATE PREDICTION DATASET REPORT"
    )

    report_lines.append(
        "=" * 70
    )

    report_lines.append("")

    report_lines.append(
        f"Total EONET geometry observations: "
        f"{total_observations}"
    )

    report_lines.append(
        f"Total unique EONET events: "
        f"{total_unique_events}"
    )

    report_lines.append(
        f"Valid geometry observations: "
        f"{len(df_valid)}"
    )

    report_lines.append(
        f"Unique events with coordinates: "
        f"{df_valid['event_id'].nunique()}"
    )

    report_lines.append("")

    report_lines.append(
        f"Geometry observations intersecting Indian states: "
        f"{mapped_geometry_observations}"
    )

    report_lines.append(
        f"Unique events affecting India: "
        f"{mapped_unique_events}"
    )

    report_lines.append(
        f"State-event associations: "
        f"{len(df_state_events)}"
    )

    report_lines.append(
        f"States / UTs represented: "
        f"{len(represented_states)}"
    )

    report_lines.append(
        f"Multi-state events: "
        f"{len(multi_state_events)}"
    )

    report_lines.append("")

    report_lines.append(
        "EVENTS PER STATE"
    )

    report_lines.append(
        "-" * 70
    )

    state_counts = (
        df_state_events
        .groupby("state_name")["event_id"]
        .nunique()
        .sort_values(
            ascending=False
        )
    )

    for state, count in state_counts.items():

        report_lines.append(
            f"{state}: {count}"
        )

    report_lines.append("")

    report_lines.append(
        "EVENTS PER YEAR"
    )

    report_lines.append(
        "-" * 70
    )

    year_counts = (
        df_state_events
        .groupby("year")["event_id"]
        .nunique()
    )

    for year, count in year_counts.items():

        report_lines.append(
            f"{year}: {count}"
        )

    report_lines.append("")

    report_lines.append(
        "EVENTS BY CATEGORY"
    )

    report_lines.append(
        "-" * 70
    )

    category_counts = (
        df_state_events[
            "categories"
        ]
        .value_counts()
    )

    for category, count in category_counts.items():

        report_lines.append(
            f"{category}: {count}"
        )

    report_lines.append("")

    report_lines.append(
        "MULTI-STATE EVENTS"
    )

    report_lines.append(
        "-" * 70
    )

    if len(multi_state_events) > 0:

        for event_id, state_count in (
            multi_state_events
            .sort_values(
                ascending=False
            )
            .items()
        ):

            states = (
                df_state_events[
                    df_state_events[
                        "event_id"
                    ]
                    == event_id
                ]["state_name"]
                .unique()
                .tolist()
            )

            title = (
                df_state_events[
                    df_state_events[
                        "event_id"
                    ]
                    == event_id
                ]["title"]
                .iloc[0]
            )

            report_lines.append(
                f"{event_id}: "
                f"{title} | "
                f"{state_count} states | "
                f"{', '.join(states)}"
            )

    else:

        report_lines.append(
            "No multi-state events."
        )

    report_lines.append("")

    report_lines.append(
        "PREDICTION DATASET"
    )

    report_lines.append(
        "-" * 70
    )

    report_lines.append(
        f"Monthly rows: {len(df_monthly)}"
    )

    report_lines.append(
        f"Prediction rows: {len(df_prediction)}"
    )

    report_lines.append(
        f"Positive next-month events: "
        f"{positive_targets}"
    )

    report_lines.append(
        f"Negative next-month events: "
        f"{negative_targets}"
    )

    report_lines.append(
        f"Positive rate: "
        f"{positive_rate:.2f}%"
    )

    report_lines.append("")

    report_lines.append(
        "DATASET SAFETY"
    )

    report_lines.append(
        "-" * 70
    )

    report_lines.append(
        "india_state_unique_events.csv contains "
        "ONLY mapped Indian state-event associations."
    )

    report_lines.append(
        "Unmapped global EONET events are excluded."
    )

    report_lines.append(
        "Events affecting multiple states retain "
        "one record per state-event pair."
    )

    report_lines.append(
        "No nearest-state geographic assignment was used."
    )

    report_lines.append(
        "Existing global EONET and K-Means datasets "
        "were not modified."
    )

    report_lines.append(
        "Existing global prediction model was not modified."
    )

    report_lines.append(
        "No machine-learning model was trained in this step."
    )

    report_lines.append("")

    report_lines.append(
        "FILES CREATED"
    )

    report_lines.append(
        "-" * 70
    )

    report_lines.append(
        UNIQUE_EVENTS_OUTPUT
    )

    report_lines.append(
        MONTHLY_EVENTS_OUTPUT
    )

    report_lines.append(
        PREDICTION_DATASET_OUTPUT
    )

    report_lines.append(
        REPORT_OUTPUT
    )

    report_lines.append("")

    report_lines.append(
        "STATUS: SUCCESS"
    )

    with open(
        REPORT_OUTPUT,
        "w",
        encoding="utf-8"
    ) as report_file:

        report_file.write(
            "\n".join(
                report_lines
            )
        )

    # ==================================================================
    # 16. FINAL CONSOLE OUTPUT
    # ==================================================================

    print("\n")
    print("=" * 70)
    print(
        "STEP 2 - INDIA STATE DATASET COMPLETE"
    )
    print("=" * 70)

    print(
        f"Total unique EONET events: "
        f"{total_unique_events}"
    )

    print(
        f"Events affecting India: "
        f"{mapped_unique_events}"
    )

    print(
        f"State-event associations: "
        f"{len(df_state_events)}"
    )

    print(
        f"States represented: "
        f"{len(represented_states)}"
    )

    print(
        f"Multi-state events: "
        f"{len(multi_state_events)}"
    )

    print(
        f"Monthly rows: "
        f"{len(df_monthly)}"
    )

    print(
        f"Prediction rows: "
        f"{len(df_prediction)}"
    )

    print(
        f"Positive next-month events: "
        f"{positive_targets}"
    )

    print(
        f"Positive rate: "
        f"{positive_rate:.2f}%"
    )

    print("\nFiles created:")

    print(
        f"  {UNIQUE_EVENTS_OUTPUT}"
    )

    print(
        f"  {MONTHLY_EVENTS_OUTPUT}"
    )

    print(
        f"  {PREDICTION_DATASET_OUTPUT}"
    )

    print(
        f"  {REPORT_OUTPUT}"
    )

    print("\nExisting project:")
    print("UNCHANGED")

    print("\nNext:")
    print(
        "Validate the clean India state dataset "
        "before any model training."
    )


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    main()