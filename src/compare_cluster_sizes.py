import pandas as pd
from sklearn.cluster import KMeans

# Load scaled ML dataset
df = pd.read_csv(
    "data/processed/ml_features_scaled.csv"
)

# Remove region ID
X = df.drop(
    columns=["region_id"]
)

print("=" * 70)
print("CLUSTER SIZE COMPARISON")
print("=" * 70)

for k in [8, 9, 10]:

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=20
    )

    labels = model.fit_predict(X)

    sizes = (
        pd.Series(labels)
        .value_counts()
        .sort_index()
    )

    print()
    print(f"K = {k}")
    print("-" * 30)
    print(sizes.to_string())

    print(
        f"Total regions: {sizes.sum()}"
    )

print()
print("=" * 70)
print("COMPARISON COMPLETE")
print("=" * 70)