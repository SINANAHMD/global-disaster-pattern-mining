"""
GLOBAL DISASTER PATTERN MINING
STEP 19 - COMPLETE FASTAPI BACKEND

APIs:
    GET /
    GET /api/summary
    GET /api/clusters
    GET /api/regions
    GET /api/regions/{region_id}
    GET /api/trends
    GET /api/categories
"""

from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prediction_api import router as prediction_router


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PROCESSED = ROOT / "data" / "processed"

REGIONAL_FILE = PROCESSED / "regional_features.csv"
CLUSTER_FILE = PROCESSED / "final_region_clusters.csv"
PROFILE_FILE = PROCESSED / "final_cluster_profiles.csv"
EVENT_FILE = PROCESSED / "eonet_events_final.csv"
EVENT_WITH_COUNTRY_FILE = PROCESSED / "eonet_events_with_country.csv"


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Global Disaster Pattern Mining API",
    description=(
        "Backend API for NASA EONET disaster-event "
        "pattern mining and regional K-Means clustering."
    ),
    version="1.0.0",
)
app.include_router(prediction_router)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATA LOADING
# ============================================================

def load_regional_data():
    return pd.read_csv(REGIONAL_FILE)


def load_cluster_data():
    return pd.read_csv(CLUSTER_FILE)


def load_profile_data():
    return pd.read_csv(PROFILE_FILE)


def load_event_data():
    return pd.read_csv(EVENT_FILE)


# ============================================================
# HELPER
# ============================================================

def clean_records(df):
    """
    Convert pandas values into JSON-safe Python values.
    """

    df = df.copy()

    df = df.where(
        pd.notnull(df),
        None
    )

    return df.to_dict(
        orient="records"
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "project":
            "Global Disaster Pattern Mining",

        "status":
            "running",

        "message":
            "NASA EONET disaster analysis API is working.",

        "documentation":
            "/docs",
    }


# ============================================================
# API 1 - SUMMARY
# ============================================================

@app.get("/api/summary")
def get_summary():

    regional_df = load_regional_data()
    cluster_df = load_cluster_data()

    total_regions = len(
        regional_df
    )

    total_events = int(
        regional_df["total_events"].sum()
    )

    total_clusters = int(
        cluster_df["cluster"].nunique()
    )

    average_events = round(
        regional_df["total_events"].mean(),
        2
    )

    maximum_events = int(
        regional_df["total_events"].max()
    )

    minimum_events = int(
        regional_df["total_events"].min()
    )

    return {

        "project":
            "Global Disaster Pattern Mining",

        "dataset":
            "NASA EONET",

        "analysis_period":
            "2015-2025",

        "total_regions":
            total_regions,

        "total_event_observations":
            total_events,

        "total_clusters":
            total_clusters,

        "average_events_per_region":
            average_events,

        "maximum_events_in_region":
            maximum_events,

        "minimum_events_in_region":
            minimum_events,

        "model":
            "K-Means",

        "final_k":
            total_clusters,

        "silhouette_score":
            0.4682,

        "status":
            "success",
    }


# ============================================================
# API 2 - CLUSTERS
# ============================================================

@app.get("/api/clusters")
def get_clusters():

    profile_df = load_profile_data()

    return {
        "count": len(profile_df),
        "clusters": clean_records(profile_df),
    }


# ============================================================
# API 3 - ALL REGIONS
# ============================================================

@app.get("/api/regions")
def get_regions():

    cluster_df = load_cluster_data()

    # Only return useful dashboard fields.
    preferred_columns = [
        "region_id",
        "cluster",
        "total_events",
        "region_latitude",
        "region_longitude",
        "first_event_year",
        "last_event_year",
        "active_years",
        "events_per_active_year",
        "events_2023_2025",
    ]

    available_columns = [
        column
        for column in preferred_columns
        if column in cluster_df.columns
    ]

    result = cluster_df[
        available_columns
    ].copy()

    return {
        "count": len(result),
        "regions": clean_records(result),
    }


# ============================================================
# API 3.5 - ALL COUNTRIES
# ============================================================

_COUNTRY_CACHE = None

def get_country_aggregated_data():
    global _COUNTRY_CACHE
    if _COUNTRY_CACHE is not None:
        return _COUNTRY_CACHE

    if not EVENT_WITH_COUNTRY_FILE.exists() or not CLUSTER_FILE.exists():
        return []

    import numpy as np
    events_df = pd.read_csv(EVENT_WITH_COUNTRY_FILE)
    regions_df = pd.read_csv(CLUSTER_FILE)

    region_coords = regions_df[['region_id', 'cluster', 'region_latitude', 'region_longitude']].values

    def find_nearest_region(lat, lng):
        if pd.isna(lat) or pd.isna(lng):
            return None, None
        lats = region_coords[:, 2].astype(float)
        lngs = region_coords[:, 3].astype(float)
        dist = (lats - lat)**2 + (lngs - lng)**2
        idx = np.argmin(dist)
        return region_coords[idx, 0], int(region_coords[idx, 1])

    mapped_regions = []
    mapped_clusters = []
    for _, row in events_df.iterrows():
        rid, clus = find_nearest_region(row.get('latitude'), row.get('longitude'))
        mapped_regions.append(rid)
        mapped_clusters.append(clus)

    events_df['region_id'] = mapped_regions
    events_df['cluster'] = mapped_clusters

    country_stats = []
    for country_name, group in events_df.groupby('country'):
        if not country_name or pd.isna(country_name):
            continue
        total_events = int(len(group))
        recent_events = int(len(group[group['year'] >= 2023]))
        cat_counts = group['categories'].value_counts()
        dom_cat = str(cat_counts.index[0]) if len(cat_counts) > 0 else 'Unknown'
        dom_cat_prop = round(float((cat_counts.iloc[0] / total_events) * 100), 1) if len(cat_counts) > 0 else 0.0
        
        iso3 = None
        if 'country_iso3' in group and len(group['country_iso3'].dropna()) > 0:
            iso3 = str(group['country_iso3'].dropna().iloc[0])
            
        unique_regions = int(group['region_id'].dropna().nunique())
        cluster_counts = group['cluster'].dropna().value_counts()
        dom_cluster = int(cluster_counts.index[0]) if len(cluster_counts) > 0 else 0
        
        country_stats.append({
            'country': str(country_name),
            'country_iso3': iso3,
            'total_events': total_events,
            'recent_events': recent_events,
            'dominant_category': dom_cat,
            'dominant_category_proportion': dom_cat_prop,
            'region_count': unique_regions,
            'dominant_cluster': dom_cluster
        })

    _COUNTRY_CACHE = country_stats
    return _COUNTRY_CACHE


@app.get("/api/countries")
def get_countries():
    data = get_country_aggregated_data()
    return {
        "count": len(data),
        "countries": data,
    }


# ============================================================
# API 4 - SINGLE REGION
# ============================================================

@app.get("/api/regions/{region_id}")
def get_region(region_id: str):

    cluster_df = load_cluster_data()

    result = cluster_df[
        cluster_df["region_id"] == region_id
    ]

    if result.empty:

        raise HTTPException(
            status_code=404,
            detail=f"Region '{region_id}' not found.",
        )

    row = result.iloc[0]

    # Convert one row into a dictionary.
    data = row.to_dict()

    # Replace NaN with None.
    for key, value in data.items():

        if pd.isna(value):
            data[key] = None

    return {
        "region": data
    }


# ============================================================
# API 5 - YEARLY TRENDS
# ============================================================

@app.get("/api/trends")
def get_trends():

    event_df = load_event_data()

    if "year" not in event_df.columns:

        if "event_date" in event_df.columns:

            event_df["event_date"] = pd.to_datetime(
                event_df["event_date"],
                errors="coerce"
            )

            event_df["year"] = (
                event_df["event_date"]
                .dt.year
            )

        else:

            raise HTTPException(
                status_code=500,
                detail="Year information not available.",
            )

    yearly = (
        event_df
        .dropna(subset=["year"])
        .groupby("year")
        .size()
        .reset_index(name="event_observations")
    )

    yearly["year"] = (
        yearly["year"]
        .astype(int)
    )

    yearly = yearly.sort_values(
        "year"
    )

    return {
        "count": len(yearly),
        "trends": clean_records(yearly),
    }


# ============================================================
# API 6 - CATEGORY DISTRIBUTION
# ============================================================

@app.get("/api/categories")
def get_categories():

    event_df = load_event_data()

    if "categories" not in event_df.columns:

        raise HTTPException(
            status_code=500,
            detail="Category information not available.",
        )

    category_counts = {}

    for value in event_df["categories"].dropna():

        categories = str(value).split("|")

        for category in categories:

            category = category.strip()

            if not category:
                continue

            category_counts[category] = (
                category_counts.get(
                    category,
                    0
                ) + 1
            )

    category_df = pd.DataFrame(
        [
            {
                "category": category,
                "event_observations": count,
            }
            for category, count
            in category_counts.items()
        ]
    )

    if category_df.empty:

        return {
            "count": 0,
            "categories": [],
        }

    category_df = category_df.sort_values(
        "event_observations",
        ascending=False
    )

    category_df = category_df.reset_index(
        drop=True
    )

    return {
        "count": len(category_df),
        "categories": clean_records(category_df),
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health_check():

    files = {
        "regional_features":
            REGIONAL_FILE.exists(),

        "final_region_clusters":
            CLUSTER_FILE.exists(),

        "final_cluster_profiles":
            PROFILE_FILE.exists(),

        "eonet_events":
            EVENT_FILE.exists(),
    }

    return {
        "status": "healthy",
        "files": files,
    }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )