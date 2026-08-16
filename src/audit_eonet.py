"""Step 2 helper: audit the collected EONET CSV. Run after collect_eonet.py."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
files = sorted((ROOT/"data/raw").glob("eonet_events_*_flat.csv"))
if not files:
    raise FileNotFoundError("No flattened EONET CSV found. Run collect_eonet.py first.")

path = files[-1]
df = pd.read_csv(path)

print("FILE:", path)
print("ROWS:", len(df))
print("COLUMNS:", len(df.columns))
print("\nDATA TYPES:\n", df.dtypes)
print("\nMISSING VALUES:\n", df.isna().sum().sort_values(ascending=False))
print("\nDUPLICATE EVENT IDS:", df["event_id"].duplicated().sum())
print("\nDATE RANGE:", df["event_date"].min(), "to", df["event_date"].max())
print("\nTOP CATEGORIES:")
print(df["categories"].value_counts(dropna=False).head(20))
print("\nCOORDINATE RANGE:")
print("Latitude:", df["latitude"].min(), "to", df["latitude"].max())
print("Longitude:", df["longitude"].min(), "to", df["longitude"].max())
