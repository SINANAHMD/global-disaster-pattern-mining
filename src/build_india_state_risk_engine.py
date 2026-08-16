"""
STEP 3U - INDIA STATE RISK ENGINE (FIXED)

Fix:
The previously saved HistGradientBoosting joblib model cannot be loaded because
it was serialized with an incompatible sklearn internal module (_loss).

Instead of loading that fragile pickle, this script retrains the SAME selected
India model (HistGradientBoostingClassifier) from the existing India dataset
using the same 2015-2024 training period, then generates the latest state scores.

Existing global systems are not modified.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
import joblib

BASE = "data/prediction/india"
DATASET = os.path.join(BASE, "india_state_prediction_dataset.csv")
MODEL_OUT = os.path.join(BASE, "india_state_model_retrained.joblib")
SCORES = os.path.join(BASE, "india_state_risk_scores.csv")
REPORT = os.path.join(BASE, "india_state_risk_report.txt")

FEATURES = [
    "current_event_count",
    "previous_month_events",
    "previous_3_month_events",
    "previous_6_month_events",
    "previous_12_month_events",
    "same_month_historical_events",
    "historical_total_events",
    "historical_active_months",
    "recent_activity_share",
    "month_sin",
    "month_cos",
    "years_since_2015",
]

def risk_level(p):
    if p >= 0.70:
        return "VERY HIGH"
    if p >= 0.50:
        return "HIGH"
    if p >= 0.30:
        return "MODERATE"
    if p >= 0.15:
        return "LOW"
    return "VERY LOW"

def coverage(events, months):
    if events >= 20 and months >= 12:
        return "HIGH DATA COVERAGE"
    if events >= 10 and months >= 6:
        return "MEDIUM DATA COVERAGE"
    return "LIMITED DATA COVERAGE"

def main():
    print("=" * 70)
    print("STEP 3U - INDIA STATE RISK ENGINE (FIXED)")
    print("=" * 70)

    if not os.path.exists(DATASET):
        raise FileNotFoundError(DATASET)

    df = pd.read_csv(DATASET)
    print(f"Rows: {len(df)}")
    print(f"States: {df['state_name'].nunique()}")

    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing features: {missing}")

    # Same chronological training period used by Step 3T.
    train = df[df["year"] <= 2024].copy()
    test = df[df["year"] == 2025].copy()

    X_train = train[FEATURES]
    y_train = train["next_month_event"]

    X_test = test[FEATURES]
    y_test = test["next_month_event"]

    print("\nRetraining selected model:")
    print("HistGradientBoostingClassifier")
    print(f"Training rows: {len(train)}")
    print(f"Training positives: {int(y_train.sum())}")

    model = HistGradientBoostingClassifier(
        max_iter=100,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Save a model generated in the current environment.
    joblib.dump(model, MODEL_OUT)

    # Use the latest available state/month row.
    latest = (
        df.sort_values(["state_name", "year", "month"])
        .groupby("state_name", as_index=False)
        .tail(1)
        .copy()
    )

    latest_probs = model.predict_proba(latest[FEATURES])[:, 1]
    latest["event_probability"] = np.clip(latest_probs, 0, 1)
    latest["event_probability_percent"] = (
        latest["event_probability"] * 100
    ).round(2)

    latest["risk_level"] = latest["event_probability"].apply(risk_level)
    latest["data_confidence"] = [
        coverage(int(e), int(m))
        for e, m in zip(
            latest["historical_total_events"],
            latest["historical_active_months"],
        )
    ]

    latest["prediction_target"] = (
        "Probability of at least one recorded EONET event "
        "in the following month"
    )

    latest["interpretation"] = latest.apply(
        lambda r: (
            f"{r['state_name']}: {r['event_probability_percent']:.2f}% "
            f"estimated probability of at least one recorded EONET event "
            f"in the following month. "
            f"Historical data coverage is {r['data_confidence'].lower()}."
        ),
        axis=1,
    )

    columns = [
        "state_name", "year", "month", "date",
        "event_probability", "event_probability_percent",
        "risk_level", "data_confidence",
        "current_event_count", "previous_month_events",
        "previous_3_month_events", "previous_6_month_events",
        "previous_12_month_events", "same_month_historical_events",
        "historical_total_events", "historical_active_months",
        "recent_activity_share", "next_month_event_count",
        "next_month_event", "prediction_target", "interpretation",
    ]

    latest = latest[columns].sort_values(
        "event_probability", ascending=False
    )
    latest.to_csv(SCORES, index=False, encoding="utf-8")

    # Optional 2025 evaluation using the retrained model.
    if len(test) > 0 and y_test.nunique() == 2:
        test_probs = model.predict_proba(X_test)[:, 1]
        roc = roc_auc_score(y_test, test_probs)
        pr = average_precision_score(y_test, test_probs)
        brier = brier_score_loss(y_test, test_probs)
    else:
        roc = pr = brier = float("nan")

    report = [
        "INDIA STATE RISK ENGINE REPORT",
        "=" * 70,
        "",
        "Model: HistGradientBoostingClassifier",
        "Training period: 2015-2024",
        "Model was retrained in the current Python environment.",
        "",
        f"States scored: {len(latest)}",
        "",
        "2025 test metrics:",
        f"ROC-AUC: {roc:.4f}",
        f"PR-AUC: {pr:.4f}",
        f"Brier score: {brier:.4f}",
        "",
        "Risk distribution:",
        latest["risk_level"].value_counts().to_string(),
        "",
        "Data coverage:",
        latest["data_confidence"].value_counts().to_string(),
        "",
        "Top predicted states:",
        latest[
            ["state_name", "event_probability_percent",
             "risk_level", "data_confidence"]
        ].head(10).to_string(index=False),
        "",
        "IMPORTANT:",
        "These are statistical estimates based on historical EONET observations.",
        "They are not official disaster warnings.",
        "The probability refers to at least one recorded EONET event in the following month.",
        "Data coverage is separate from model probability.",
        "",
        "Existing global K-Means: UNCHANGED",
        "Existing global prediction: UNCHANGED",
        "Frontend/backend: UNCHANGED",
    ]

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print("\n" + "=" * 70)
    print("STEP 3U COMPLETE")
    print("=" * 70)
    print("\nTop predicted states:")
    print(
        latest[
            ["state_name", "event_probability_percent",
             "risk_level", "data_confidence"]
        ].head(10).to_string(index=False)
    )

    print("\nFiles created:")
    print(MODEL_OUT)
    print(SCORES)
    print(REPORT)

    print("\nExisting systems remain unchanged.")

if __name__ == "__main__":
    main()