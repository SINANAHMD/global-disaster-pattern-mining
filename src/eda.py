"""
STEP 10 - Exploratory Data Analysis

Creates:
1. Regional event distribution
2. Top 20 regions
3. Category distribution
4. Yearly event trend
5. Regional feature correlation
6. Global regional activity map
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PROCESSED = ROOT / "data" / "processed"

OUTPUT = ROOT / "data" / "processed" / "eda"

OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)


EVENT_FILE = (
    PROCESSED
    / "eonet_events_final.csv"
)

REGIONAL_FILE = (
    PROCESSED
    / "regional_features.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("STEP 10 - EXPLORATORY DATA ANALYSIS")
print("=" * 70)

events = pd.read_csv(
    EVENT_FILE
)

regional = pd.read_csv(
    REGIONAL_FILE
)

events["event_date"] = pd.to_datetime(
    events["event_date"],
    errors="coerce",
    utc=True
)

events["year"] = (
    events["event_date"]
    .dt.year
)


# ============================================================
# 1. YEARLY EVENT TREND
# ============================================================

print("\nCreating yearly event trend...")

yearly = (
    events
    .groupby("year")
    .size()
    .reset_index(
        name="event_count"
    )
)

plt.figure(
    figsize=(12, 6)
)

plt.plot(
    yearly["year"],
    yearly["event_count"],
    marker="o"
)

plt.title(
    "Global EONET Event Observations by Year"
)

plt.xlabel(
    "Year"
)

plt.ylabel(
    "Number of Event Observations"
)

plt.xticks(
    yearly["year"]
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    OUTPUT / "01_yearly_event_trend.png",
    dpi=200
)

plt.close()


# ============================================================
# 2. TOP 20 REGIONS
# ============================================================

print(
    "Creating top-region chart..."
)

top_regions = (
    regional
    .sort_values(
        "total_events",
        ascending=False
    )
    .head(20)
    .sort_values(
        "total_events"
    )
)

plt.figure(
    figsize=(12, 8)
)

plt.barh(
    top_regions["region_id"],
    top_regions["total_events"]
)

plt.title(
    "Top 20 Geographic Regions by Event Observations"
)

plt.xlabel(
    "Event Observations"
)

plt.ylabel(
    "Geographic Region"
)

plt.tight_layout()

plt.savefig(
    OUTPUT / "02_top_20_regions.png",
    dpi=200
)

plt.close()


# ============================================================
# 3. EVENT COUNT DISTRIBUTION
# ============================================================

print(
    "Creating regional distribution chart..."
)

plt.figure(
    figsize=(10, 6)
)

plt.hist(
    regional["total_events"],
    bins=30
)

plt.title(
    "Distribution of Event Observations Across Regions"
)

plt.xlabel(
    "Total Event Observations"
)

plt.ylabel(
    "Number of Regions"
)

plt.tight_layout()

plt.savefig(
    OUTPUT / "03_regional_event_distribution.png",
    dpi=200
)

plt.close()


# ============================================================
# 4. CATEGORY DISTRIBUTION
# ============================================================

print(
    "Creating category distribution..."
)

category_columns = [
    column
    for column in regional.columns
    if column.startswith("cat_")
    and not column.endswith("_proportion")
]

category_totals = []

for column in category_columns:

    category_totals.append({

        "category":
            column.replace(
                "cat_",
                ""
            ).replace(
                "_",
                " "
            ).title(),

        "events":
            regional[column].sum()
    })


category_df = pd.DataFrame(
    category_totals
).sort_values(
    "events",
    ascending=False
)


plt.figure(
    figsize=(12, 7)
)

plt.bar(
    category_df["category"],
    category_df["events"]
)

plt.title(
    "Global Disaster/Event Category Distribution"
)

plt.xlabel(
    "Category"
)

plt.ylabel(
    "Event Observations"
)

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    OUTPUT / "04_category_distribution.png",
    dpi=200
)

plt.close()


# ============================================================
# 5. CORRELATION HEATMAP
# ============================================================

print(
    "Creating feature correlation heatmap..."
)

correlation_columns = [
    "total_events",
    "events_per_active_year",
    "active_years",
    "events_2023_2025"
]

correlation_columns += category_columns

correlation_columns = [
    column
    for column in correlation_columns
    if column in regional.columns
]


correlation = regional[
    correlation_columns
].corr()


plt.figure(
    figsize=(14, 10)
)

sns.heatmap(
    correlation,
    annot=False,
    cmap="coolwarm",
    center=0
)

plt.title(
    "Correlation Between Regional Disaster Features"
)

plt.tight_layout()

plt.savefig(
    OUTPUT / "05_feature_correlation.png",
    dpi=200
)

plt.close()


# ============================================================
# 6. GLOBAL REGIONAL ACTIVITY MAP
# ============================================================

print(
    "Creating global regional activity map..."
)

plt.figure(
    figsize=(14, 7)
)

scatter = plt.scatter(
    regional["region_longitude"],
    regional["region_latitude"],
    s=regional["total_events"] * 2 + 10,
    c=regional["total_events"],
    alpha=0.7
)

plt.colorbar(
    scatter,
    label="Event Observations"
)

plt.title(
    "Global Geographic Distribution of EONET Event Activity"
)

plt.xlabel(
    "Longitude"
)

plt.ylabel(
    "Latitude"
)

plt.xlim(
    -180,
    180
)

plt.ylim(
    -90,
    90
)

plt.grid(
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    OUTPUT / "06_global_regional_activity.png",
    dpi=200
)

plt.close()


# ============================================================
# SAVE YEARLY SUMMARY
# ============================================================

yearly.to_csv(
    OUTPUT / "yearly_event_summary.csv",
    index=False
)


# ============================================================
# SAVE CATEGORY SUMMARY
# ============================================================

category_df.to_csv(
    OUTPUT / "eda_category_summary.csv",
    index=False
)


# ============================================================
# FINAL REPORT
# ============================================================

report = []

report.append(
    "EDA SUMMARY"
)

report.append(
    "=" * 70
)

report.append(
    f"Event observations: {len(events):,}"
)

report.append(
    f"Geographic regions: {len(regional):,}"
)

report.append(
    f"Regional mean event count: "
    f"{regional['total_events'].mean():.2f}"
)

report.append(
    f"Regional median event count: "
    f"{regional['total_events'].median():.2f}"
)

report.append(
    f"Maximum regional event count: "
    f"{regional['total_events'].max():,}"
)

report.append(
    f"Minimum regional event count: "
    f"{regional['total_events'].min():,}"
)

report.append(
    "\nTop 10 regions:"
)

report.append(
    regional[
        [
            "region_id",
            "total_events"
        ]
    ]
    .sort_values(
        "total_events",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)

report.append(
    "\nCategory totals:"
)

report.append(
    category_df.to_string(
        index=False
    )
)


(OUTPUT / "eda_summary.txt").write_text(
    "\n".join(report),
    encoding="utf-8"
)


# ============================================================
# FINISHED
# ============================================================

print()
print("=" * 70)
print("STEP 10A COMPLETE")
print("=" * 70)

print(
    "\nEDA files created in:"
)

print(
    OUTPUT
)

print(
    "\nCharts:"
)

for file in sorted(
    OUTPUT.glob("*.png")
):

    print(
        f"  - {file.name}"
    )

print(
    "\nNext: inspect EDA results before selecting "
    "features for K-Means."
)