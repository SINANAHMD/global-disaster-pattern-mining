import os
import sys
import json
import unicodedata
import pandas as pd
from shapely.geometry import shape, Point
from shapely.prepared import prep

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = os.path.join("data", "prediction", "india")
os.makedirs(DATA_DIR, exist_ok=True)

CSV_PATH = os.path.join("data", "processed", "eonet_events_final.csv")
GEOJSON_PATH = os.path.join("data", "prediction", "boundaries", "india_adm1.geojson")

UNIQUE_EVENTS_OUTPUT = os.path.join(DATA_DIR, "india_state_unique_events.csv")
DIAGNOSTIC_CSV_OUTPUT = os.path.join(DATA_DIR, "india_state_mapping_diagnostic.csv")
REPORT_OUTPUT = os.path.join(DATA_DIR, "india_state_mapping_report.txt")

def normalize_state_name(raw_name):
    if not raw_name:
        return ""
    s = unicodedata.normalize('NFKD', str(raw_name)).encode('ASCII', 'ignore').decode('utf-8').strip()
    return s

def main():
    print("======================================================================")
    print("RUNNING INDIA STATE MAPPING VALIDATION & DIAGNOSTICS")
    print("======================================================================")

    # 1. Load India ADM1 Polygons
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        gdata = json.load(f)

    prep_states = []
    all_state_names = []
    for feat in gdata.get("features", []):
        props = feat.get("properties", {})
        raw_name = props.get("shapeName", "")
        norm_name = normalize_state_name(raw_name)
        poly = shape(feat["geometry"])
        prep_poly = prep(poly)
        prep_states.append({
            "raw_name": raw_name,
            "norm_name": norm_name,
            "poly": poly,
            "prep_poly": prep_poly
        })
        if norm_name not in all_state_names:
            all_state_names.append(norm_name)

    print(f"Loaded {len(prep_states)} Indian ADM1 state boundaries.")

    # 2. Load EONET Event Observations
    df_raw = pd.read_csv(CSV_PATH)
    total_obs = len(df_raw)
    total_unique_events = df_raw["event_id"].nunique()

    # Filter valid coordinates
    valid_mask = (
        df_raw["latitude"].notna() &
        df_raw["longitude"].notna() &
        (df_raw["latitude"] >= -90) & (df_raw["latitude"] <= 90) &
        (df_raw["longitude"] >= -180) & (df_raw["longitude"] <= 180)
    )
    df_valid = df_raw[valid_mask].copy()
    valid_obs_count = len(df_valid)
    unique_events_with_coords = df_valid["event_id"].nunique()

    print(f"Total EONET Geometry Observations: {total_obs}")
    print(f"Total Unique Event IDs: {total_unique_events}")
    print(f"Valid Geometry Observations: {valid_obs_count}")
    print(f"Unique Events with Valid Coordinates: {unique_events_with_coords}")

    # 3. Spatial Test ALL Geometry Observations against ALL ADM1 Polygons
    mapped_records = []

    for idx, row in df_valid.iterrows():
        pt = Point(row["longitude"], row["latitude"]) # Longitude X, Latitude Y
        for st in prep_states:
            if st["prep_poly"].intersects(pt):
                mapped_records.append({
                    "event_id": row["event_id"],
                    "title": row["title"],
                    "categories": row["categories"],
                    "event_date": row["event_date"],
                    "year": row["year"],
                    "month": row["month"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "state_name_raw": st["raw_name"],
                    "state_name": st["norm_name"]
                })

    df_mapped_obs = pd.DataFrame(mapped_records)
    mapped_obs_count = len(df_mapped_obs)

    # 4. Multi-State & State Deduplication Analysis
    if mapped_obs_count > 0:
        # Group by event_id to see which events affect which states
        event_to_states = df_mapped_obs.groupby("event_id")["state_name"].unique().to_dict()
        events_affecting_india = len(event_to_states)
        
        # Multi-state event breakdown
        multi_state_events = {eid: states for eid, states in event_to_states.items() if len(states) > 1}
        multi_state_count = len(multi_state_events)
        max_states_affected = max([len(states) for states in event_to_states.values()]) if event_to_states else 0
    else:
        event_to_states = {}
        events_affecting_india = 0
        multi_state_events = {}
        multi_state_count = 0
        max_states_affected = 0

    no_india_intersection_count = unique_events_with_coords - events_affecting_india

    print("\n----------------------------------------------------------------------")
    print("MAPPING SUMMARY RESULTS")
    print("----------------------------------------------------------------------")
    print(f"Geometry observations intersecting Indian states: {mapped_obs_count}")
    print(f"Unique events affecting India: {events_affecting_india}")
    print(f"Events with NO Indian state intersection: {no_india_intersection_count}")
    print(f"Events affecting MULTIPLE Indian states: {multi_state_count}")
    print(f"Maximum states affected by single event: {max_states_affected}")

    # 5. Create State-Event Representative Records (File 1: india_state_unique_events.csv)
    # Deduplicate within each (state_name, event_id) pair and compute representative mean lat/lon
    mapped_unique_rows = []

    if mapped_obs_count > 0:
        grouped_state_event = df_mapped_obs.groupby(["state_name", "event_id"])
        for (state, eid), group in grouped_state_event:
            first_row = group.iloc[0]
            mean_lat = float(group["latitude"].mean())
            mean_lon = float(group["longitude"].mean())

            mapped_unique_rows.append({
                "event_id": eid,
                "title": first_row["title"],
                "categories": first_row["categories"],
                "event_date": first_row["event_date"],
                "year": first_row["year"],
                "month": first_row["month"],
                "latitude": round(mean_lat, 6),
                "longitude": round(mean_lon, 6),
                "state_name_raw": first_row["state_name_raw"],
                "state_name": state,
                "geometry_mapping_status": "mapped"
            })

    df_mapped_unique = pd.DataFrame(mapped_unique_rows)

    # Also append unmapped events for complete coverage record
    all_mapped_eids = set(event_to_states.keys())
    unmapped_unique_rows = []

    df_dedup_all = df_valid.drop_duplicates(subset=["event_id"]).copy()
    for idx, row in df_dedup_all.iterrows():
        eid = row["event_id"]
        if eid not in all_mapped_eids:
            unmapped_unique_rows.append({
                "event_id": eid,
                "title": row["title"],
                "categories": row["categories"],
                "event_date": row["event_date"],
                "year": row["year"],
                "month": row["month"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "state_name_raw": "",
                "state_name": "",
                "geometry_mapping_status": "unmapped"
            })

    df_unmapped_unique = pd.DataFrame(unmapped_unique_rows)
    df_all_events_export = pd.concat([df_mapped_unique, df_unmapped_unique], ignore_index=True)

    df_all_events_export.to_csv(UNIQUE_EVENTS_OUTPUT, index=False, encoding="utf-8")
    print(f"Saved: {UNIQUE_EVENTS_OUTPUT} ({len(df_all_events_export)} total rows)")

    # 6. Create Diagnostic CSV (File 2: india_state_mapping_diagnostic.csv)
    diagnostic_rows = []

    if mapped_obs_count > 0:
        state_obs_grouped = df_mapped_obs.groupby("state_name")
        for state, sgroup in state_obs_grouped:
            u_events = sgroup["event_id"].nunique()
            g_obs = len(sgroup)
            min_y = int(sgroup["year"].min())
            max_y = int(sgroup["year"].max())

            diagnostic_rows.append({
                "state_name": state,
                "unique_events": u_events,
                "geometry_observations": g_obs,
                "first_event_year": min_y,
                "last_event_year": max_y
            })

    df_diagnostic = pd.DataFrame(diagnostic_rows).sort_values(by="unique_events", ascending=False).reset_index(drop=True)
    df_diagnostic.to_csv(DIAGNOSTIC_CSV_OUTPUT, index=False, encoding="utf-8")
    print(f"Saved: {DIAGNOSTIC_CSV_OUTPUT} ({len(df_diagnostic)} state rows)")

    # 7. Create Diagnostic Text Report (File 3: india_state_mapping_report.txt)
    num_represented_states = len(df_diagnostic)

    # Top 20 Multi-State Events
    multi_state_list = []
    if mapped_obs_count > 0:
        for eid, states in event_to_states.items():
            if len(states) > 1:
                sample_row = df_mapped_obs[df_mapped_obs["event_id"] == eid].iloc[0]
                multi_state_list.append({
                    "event_id": eid,
                    "title": sample_row["title"],
                    "states": sorted(list(states)),
                    "num_states": len(states)
                })
        multi_state_list.sort(key=lambda x: x["num_states"], reverse=True)

    # Coordinate Quality Samples
    coord_samples = []
    if len(df_mapped_unique) > 0:
        sample_df = df_mapped_unique.head(15)
        for idx, srow in sample_df.iterrows():
            coord_samples.append({
                "event_id": srow["event_id"],
                "title": srow["title"],
                "state": srow["state_name"],
                "lat": srow["latitude"],
                "lon": srow["longitude"]
            })

    report_lines = [
        "============================================================",
        "INDIA STATE MAPPING DIAGNOSTIC",
        "============================================================",
        f"Total EONET geometry observations: {total_obs}",
        f"Total unique event IDs: {total_unique_events}",
        f"Unique events with valid coordinates: {unique_events_with_coords}",
        "",
        f"Geometry observations intersecting India: {mapped_obs_count}",
        f"Unique events affecting India: {events_affecting_india}",
        "",
        f"Number of states/UTs represented: {num_represented_states}",
        "",
        "Top states by unique event count:"
    ]

    for idx, drow in df_diagnostic.iterrows():
        report_lines.append(f"  - {drow['state_name']}: {drow['unique_events']} unique events ({drow['geometry_observations']} observations, {drow['first_event_year']}–{drow['last_event_year']})")

    report_lines.extend([
        "",
        f"Events with no India state intersection: {no_india_intersection_count}",
        f"Events affecting multiple Indian states: {multi_state_count}",
        f"Maximum number of states affected by a single event: {max_states_affected}",
        "",
        "------------------------------------------------------------",
        "MULTI-STATE EVENTS (TOP 20):",
        "------------------------------------------------------------"
    ])

    if multi_state_list:
        for item in multi_state_list[:20]:
            states_str = ", ".join(item["states"])
            report_lines.append(f"  - {item['event_id']} | '{item['title']}' | {item['num_states']} states: [{states_str}]")
    else:
        report_lines.append("  - None")

    report_lines.extend([
        "",
        "------------------------------------------------------------",
        "COORDINATE QUALITY & PLAUSIBILITY SAMPLES:",
        "------------------------------------------------------------"
    ])

    for cs in coord_samples:
        report_lines.append(f"  - {cs['event_id']} | {cs['state']} | ({cs['lat']}°N, {cs['lon']}°E) | '{cs['title']}'")

    report_text = "\n".join(report_lines)

    with open(REPORT_OUTPUT, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Saved: {REPORT_OUTPUT}")

    # 8. Print Final Required Output Format
    print("\n======================================================================")
    print("STEP 2 - INDIA STATE MAPPING VALIDATION COMPLETE")
    print("======================================================================")
    print(f"Unique events: {total_unique_events}")
    print(f"Events affecting India: {events_affecting_india}")
    print(f"States represented: {num_represented_states}")
    print(f"Multi-state events: {multi_state_count}")
    print("\nExisting project:")
    print("UNCHANGED")
    print("\nNext:")
    print("Review mapping diagnostics before rebuilding the state-level monthly prediction dataset.")

if __name__ == "__main__":
    main()
