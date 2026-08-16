"""
STEP 3T - PREDICTION API

Add-on API for the calibrated EONET prediction model.

IMPORTANT:
- Does NOT modify K-Means logic.
- Does NOT modify existing API endpoints.
- Reads the final calibrated prediction CSV.
"""

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException


# ============================================================
# PATH
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PREDICTION_FILE = (
    ROOT
    / "data"
    / "prediction"
    / "final_calibrated_prediction_scores.csv"
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/prediction",
    tags=["Prediction Intelligence"],
)


# ============================================================
# LOAD DATA
# ============================================================

def load_predictions():

    if not PREDICTION_FILE.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Final calibrated prediction file "
                "was not found."
            ),
        )

    return pd.read_csv(
        PREDICTION_FILE
    )


# ============================================================
# SUMMARY
# ============================================================

@router.get("/summary")
def prediction_summary():

    df = load_predictions()

    probabilities = (
        df["calibrated_probability"]
    )

    return {
        "model":
            "Logistic Regression + Sigmoid Calibration",

        "prediction_target":
            "Next-month EONET event probability",

        "prediction_year":
            int(df["year"].max()),

        "prediction_rows":
            int(len(df)),

        "regions":
            int(df["region_id"].nunique()),

        "average_probability":
            round(
                float(probabilities.mean()),
                4,
            ),

        "maximum_probability":
            round(
                float(probabilities.max()),
                4,
            ),

        "minimum_probability":
            round(
                float(probabilities.min()),
                4,
            ),

        "very_high_count":
            int(
                (
                    probabilities >= 0.70
                ).sum()
            ),

        "high_count":
            int(
                (
                    (probabilities >= 0.50)
                    &
                    (probabilities < 0.70)
                ).sum()
            ),

        "moderate_count":
            int(
                (
                    (probabilities >= 0.30)
                    &
                    (probabilities < 0.50)
                ).sum()
            ),

        "low_count":
            int(
                (
                    (probabilities >= 0.15)
                    &
                    (probabilities < 0.30)
                ).sum()
            ),

        "very_low_count":
            int(
                (
                    probabilities < 0.15
                ).sum()
            ),

        "disclaimer":
            (
                "Statistical estimate based on historical "
                "NASA EONET observations. Not an official "
                "disaster warning."
            ),
    }


# ============================================================
# ALL PREDICTIONS
# ============================================================

@router.get("/regions")
def prediction_regions():

    df = load_predictions()

    columns = [
        "region_id",
        "grid_lat",
        "grid_lon",
        "year",
        "month",
        "date",
        "calibrated_probability",
        "calibrated_probability_percent",
        "activity_level",
        "actual_next_month_event",
    ]

    available = [
        column
        for column in columns
        if column in df.columns
    ]

    result = df[
        available
    ].copy()

    result = result.replace(
        {
            float("nan"): None
        }
    )

    return {
        "count":
            int(len(result)),

        "predictions":
            result.to_dict(
                orient="records"
            ),
    }


# ============================================================
# TOP RISK AREAS
# ============================================================

@router.get("/top")
def top_predictions(
    limit: int = 20,
):

    if limit < 1 or limit > 100:

        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 100",
        )

    df = load_predictions()

    result = (
        df
        .sort_values(
            "calibrated_probability",
            ascending=False,
        )
        .head(limit)
    )

    columns = [
        "region_id",
        "grid_lat",
        "grid_lon",
        "year",
        "month",
        "date",
        "calibrated_probability",
        "calibrated_probability_percent",
        "activity_level",
    ]

    available = [
        column
        for column in columns
        if column in result.columns
    ]

    result = result[
        available
    ]

    return {
        "count":
            int(len(result)),

        "predictions":
            result.to_dict(
                orient="records"
            ),
    }


# ============================================================
# REGION LOOKUP
# ============================================================

@router.get("/region/{region_id}")
def prediction_for_region(
    region_id: str,
):

    df = load_predictions()

    result = df[
        df["region_id"] == region_id
    ].copy()

    if result.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No prediction found for "
                f"region {region_id}"
            ),
        )

    result = result.sort_values(
        "month"
    )

    columns = [
        "region_id",
        "grid_lat",
        "grid_lon",
        "year",
        "month",
        "date",
        "calibrated_probability",
        "calibrated_probability_percent",
        "activity_level",
        "actual_next_month_event",
    ]

    available = [
        column
        for column in columns
        if column in result.columns
    ]

    return {
        "region_id":
            region_id,

        "count":
            int(len(result)),

        "predictions":
            result[
                available
            ].to_dict(
                orient="records"
            ),
    }