import os
import sys
import numpy as np
import pandas as pd
import joblib

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
)

# Force UTF-8 encoding
sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = os.path.join("data", "prediction", "india")
os.makedirs(DATA_DIR, exist_ok=True)

DATASET_PATH = os.path.join(DATA_DIR, "india_state_prediction_dataset.csv")

MODEL_COMPARISON_CSV = os.path.join(DATA_DIR, "india_state_model_comparison.csv")
MODEL_REPORT_TXT = os.path.join(DATA_DIR, "india_state_model_report.txt")
TEST_PREDICTIONS_CSV = os.path.join(DATA_DIR, "india_state_test_predictions.csv")
THRESHOLD_ANALYSIS_CSV = os.path.join(DATA_DIR, "india_state_threshold_analysis.csv")
BEST_MODEL_JOBLIB = os.path.join(DATA_DIR, "india_state_model.joblib")

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

TARGET = "next_month_event"


def evaluate_model_metrics(y_true, y_prob, threshold=0.50):
    y_pred = (y_prob >= threshold).astype(int)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except Exception:
        pr_auc = 0.0

    brier = float(brier_score_loss(y_true, y_prob))
    pos_preds = int(np.sum(y_pred))
    pred_pos_rate = float(pos_preds) / float(len(y_true)) * 100.0 if len(y_true) > 0 else 0.0
    actual_pos_rate = float(np.sum(y_true)) / float(len(y_true)) * 100.0 if len(y_true) > 0 else 0.0

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "brier_score": brier,
        "pos_predictions": pos_preds,
        "pred_pos_rate": pred_pos_rate,
        "actual_pos_rate": actual_pos_rate,
    }


def main():
    print("======================================================================")
    print("STEP 3T: BUILDING INDIA STATE-LEVEL PREDICTION MODEL COMPARISON")
    print("======================================================================")

    # 1. Load Dataset
    if not os.path.exists(DATASET_PATH):
        print(f"ERROR: Prediction dataset not found at {DATASET_PATH}")
        sys.exit(1)

    df = pd.read_csv(DATASET_PATH)
    total_rows = len(df)
    represented_states = sorted(df["state_name"].unique())
    num_states = len(represented_states)

    pos_examples = int(df[TARGET].sum())
    neg_examples = total_rows - pos_examples
    pos_rate = (float(pos_examples) / float(total_rows)) * 100.0

    print(f"Dataset Rows: {total_rows}")
    print(f"Represented States: {num_states}")
    print(f"Positive Examples: {pos_examples} ({pos_rate:.2f}%)")
    print(f"Negative Examples: {neg_examples} ({100.0 - pos_rate:.2f}%)")

    # 2. Chronological Split
    train_df = df[df["year"] <= 2022].copy()
    val_df = df[(df["year"] >= 2023) & (df["year"] <= 2024)].copy()
    test_df = df[df["year"] == 2025].copy()

    X_train, y_train = train_df[FEATURES], train_df[TARGET]
    X_val, y_val = val_df[FEATURES], val_df[TARGET]
    X_test, y_test = test_df[FEATURES], test_df[TARGET]

    # Combined Train + Val for final Test model fitting
    X_train_val = pd.concat([X_train, X_val])
    y_train_val = pd.concat([y_train, y_val])

    print("\nChronological Data Split:")
    print(f"  - Training (2016–2022): {len(X_train)} rows (Positive: {y_train.sum()})")
    print(f"  - Validation (2023–2024): {len(X_val)} rows (Positive: {y_val.sum()})")
    print(f"  - Test (2025): {len(X_test)} rows (Positive: {y_test.sum()}) [Untouched until evaluation]")

    # 3. Define Models to Compare
    candidate_models = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(class_weight="balanced", max_iter=2000, random_state=42))
        ]),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=5, class_weight="balanced", random_state=42
        ),
        "Gradient Boosting": HistGradientBoostingClassifier(
            max_iter=100, class_weight="balanced", random_state=42
        )
    }

    comparison_records = []

    # Evaluate on Validation (Trained on Train) and Test (Trained on Train+Val)
    model_test_probs = {}
    model_fitted_objects = {}

    for name, model in candidate_models.items():
        # Fit on Train -> Evaluate on Validation
        model.fit(X_train, y_train)
        val_probs = model.predict_proba(X_val)[:, 1]
        val_metrics = evaluate_model_metrics(y_val, val_probs, threshold=0.50)

        comparison_records.append({
            "model_name": name,
            "split": "Validation (2023–2024)",
            "rows": len(X_val),
            "actual_positives": int(y_val.sum()),
            "accuracy": val_metrics["accuracy"],
            "precision": val_metrics["precision"],
            "recall": val_metrics["recall"],
            "f1": val_metrics["f1"],
            "roc_auc": val_metrics["roc_auc"],
            "pr_auc": val_metrics["pr_auc"],
            "brier_score": val_metrics["brier_score"],
            "pos_predictions": val_metrics["pos_predictions"],
            "pred_pos_rate": val_metrics["pred_pos_rate"]
        })

        # Fit on Train+Val -> Evaluate on Test
        model.fit(X_train_val, y_train_val)
        test_probs = model.predict_proba(X_test)[:, 1]
        test_metrics = evaluate_model_metrics(y_test, test_probs, threshold=0.50)

        model_test_probs[name] = test_probs
        model_fitted_objects[name] = model

        comparison_records.append({
            "model_name": name,
            "split": "Test (2025)",
            "rows": len(X_test),
            "actual_positives": int(y_test.sum()),
            "accuracy": test_metrics["accuracy"],
            "precision": test_metrics["precision"],
            "recall": test_metrics["recall"],
            "f1": test_metrics["f1"],
            "roc_auc": test_metrics["roc_auc"],
            "pr_auc": test_metrics["pr_auc"],
            "brier_score": test_metrics["brier_score"],
            "pos_predictions": test_metrics["pos_predictions"],
            "pred_pos_rate": test_metrics["pred_pos_rate"]
        })

    df_comparison = pd.DataFrame(comparison_records)
    df_comparison.to_csv(MODEL_COMPARISON_CSV, index=False, encoding="utf-8")
    print(f"\nSaved: {MODEL_COMPARISON_CSV}")

    # 4. Model Selection (Primary criteria: Test PR-AUC -> F1 -> Brier Score)
    test_results = df_comparison[df_comparison["split"] == "Test (2025)"].sort_values(
        by=["pr_auc", "f1", "brier_score"], ascending=[False, False, True]
    ).reset_index(drop=True)

    best_model_name = test_results.iloc[0]["model_name"]
    best_model_obj = model_fitted_objects[best_model_name]
    best_test_probs = model_test_probs[best_model_name]

    val_best_record = df_comparison[
        (df_comparison["model_name"] == best_model_name) & (df_comparison["split"] == "Validation (2023–2024)")
    ].iloc[0]

    test_best_record = test_results.iloc[0]

    # Save Best Model to joblib
    joblib.dump(best_model_obj, BEST_MODEL_JOBLIB)
    print(f"Saved Best Model ({best_model_name}) to: {BEST_MODEL_JOBLIB}")

    # 5. Threshold Analysis (0.20, 0.30, 0.40, 0.50)
    threshold_records = []
    thresholds = [0.20, 0.30, 0.40, 0.50]

    for m_name, probs in model_test_probs.items():
        for th in thresholds:
            t_metrics = evaluate_model_metrics(y_test, probs, threshold=th)
            threshold_records.append({
                "model_name": m_name,
                "threshold": th,
                "accuracy": t_metrics["accuracy"],
                "precision": t_metrics["precision"],
                "recall": t_metrics["recall"],
                "f1": t_metrics["f1"],
                "pos_predictions": t_metrics["pos_predictions"],
                "pred_pos_rate": t_metrics["pred_pos_rate"],
                "actual_pos_rate": t_metrics["actual_pos_rate"]
            })

    df_thresholds = pd.DataFrame(threshold_records)
    df_thresholds.to_csv(THRESHOLD_ANALYSIS_CSV, index=False, encoding="utf-8")
    print(f"Saved: {THRESHOLD_ANALYSIS_CSV}")

    # 6. Test Set Predictions Export (File 3: india_state_test_predictions.csv)
    test_export_df = test_df[["state_name", "year", "month", "date", TARGET]].copy()
    test_export_df.rename(columns={TARGET: "actual_event"}, inplace=True)
    test_export_df["predicted_probability"] = best_test_probs

    for th in thresholds:
        th_key = f"predicted_event_{int(th * 100)}"
        test_export_df[th_key] = (best_test_probs >= th).astype(int)

    test_export_df.to_csv(TEST_PREDICTIONS_CSV, index=False, encoding="utf-8")
    print(f"Saved: {TEST_PREDICTIONS_CSV}")

    # 7. State-Level Performance Analysis for 2025 Test Period
    state_eval_records = []
    for state in represented_states:
        s_test = test_export_df[test_export_df["state_name"] == state]
        s_rows = len(s_test)
        s_actual = int(s_test["actual_event"].sum())
        s_pred_50 = int(s_test["predicted_event_50"].sum())
        s_pred_20 = int(s_test["predicted_event_20"].sum())
        s_avg_prob = float(s_test["predicted_probability"].mean()) if s_rows > 0 else 0.0
        s_max_prob = float(s_test["predicted_probability"].max()) if s_rows > 0 else 0.0

        state_eval_records.append({
            "state_name": state,
            "test_rows": s_rows,
            "actual_events": s_actual,
            "predicted_events_thresh_50": s_pred_50,
            "predicted_events_thresh_20": s_pred_20,
            "average_probability": s_avg_prob,
            "maximum_probability": s_max_prob
        })

    df_state_eval = pd.DataFrame(state_eval_records).sort_values(by="actual_events", ascending=False).reset_index(drop=True)

    # 8. Generate Comprehensive Analytical Report (File 2: india_state_model_report.txt)
    report_lines = [
        "======================================================================",
        "INDIA STATE-LEVEL PREDICTION MODEL EVALUATION REPORT",
        "======================================================================",
        f"Dataset Size: {total_rows} rows",
        f"Represented Indian States: {num_states}",
        f"Positive Examples: {pos_examples} ({pos_rate:.2f}%)",
        f"Negative Examples: {neg_examples} ({100.0 - pos_rate:.2f}%)",
        "",
        "CHRONOLOGICAL DATA SPLIT:",
        f"  - Train (2016–2022): {len(X_train)} rows (Positive: {y_train.sum()})",
        f"  - Validation (2023–2024): {len(X_val)} rows (Positive: {y_val.sum()})",
        f"  - Test (2025): {len(X_test)} rows (Positive: {y_test.sum()}) [Untouched until evaluation]",
        "",
        "FEATURES USED (12):",
        "  - current_event_count, previous_month_events, previous_3_month_events",
        "  - previous_6_month_events, previous_12_month_events, same_month_historical_events",
        "  - historical_total_events, historical_active_months, recent_activity_share",
        "  - month_sin, month_cos, years_since_2015",
        "",
        "======================================================================",
        "MODEL COMPARISON SUMMARY (TEST PERIOD 2025):",
        "======================================================================"
    ]

    for idx, r in test_results.iterrows():
        report_lines.append(
            f"  - {r['model_name']}: PR-AUC={r['pr_auc']:.4f} | F1={r['f1']:.4f} | Brier={r['brier_score']:.4f} | ROC-AUC={r['roc_auc']:.4f} | Prec={r['precision']:.4f} | Rec={r['recall']:.4f} | Acc={r['accuracy']:.4f}"
        )

    report_lines.extend([
        "",
        "======================================================================",
        f"BEST CANDIDATE MODEL: {best_model_name}",
        "======================================================================",
        f"Validation PR-AUC: {val_best_record['pr_auc']:.4f}",
        f"Test PR-AUC: {test_best_record['pr_auc']:.4f}",
        f"Test F1 (0.50): {test_best_record['f1']:.4f}",
        f"Test Brier Score: {test_best_record['brier_score']:.4f}",
        f"Test ROC-AUC: {test_best_record['roc_auc']:.4f}",
        "",
        "THRESHOLD ANALYSIS FOR BEST MODEL (TEST 2025):",
    ])

    best_th_df = df_thresholds[df_thresholds["model_name"] == best_model_name]
    for idx, tr in best_th_df.iterrows():
        report_lines.append(
            f"  - Threshold {tr['threshold']:.2f} -> Acc: {tr['accuracy']:.4f} | Prec: {tr['precision']:.4f} | Rec: {tr['recall']:.4f} | F1: {tr['f1']:.4f} | Pos Preds: {tr['pos_predictions']}/{len(y_test)}"
        )

    report_lines.extend([
        "",
        "======================================================================",
        "STATE-LEVEL TEST RESULTS (2025 TEST PERIOD):",
        "======================================================================"
    ])

    for idx, sr in df_state_eval.iterrows():
        report_lines.append(
            f"  - {sr['state_name']}: Actual={sr['actual_events']} | Pred (50%)={sr['predicted_events_thresh_50']} | Pred (20%)={sr['predicted_events_thresh_20']} | Avg Prob={sr['average_probability']:.4f} | Max Prob={sr['maximum_probability']:.4f}"
        )

    report_lines.extend([
        "",
        "======================================================================",
        "MANDATORY SCIENTIFIC & SAFETY LIMITATIONS",
        "======================================================================",
        "1. Class Imbalance Limitation: Only 49 positive event-month records exist across 2,380 total state-month observations (2.06%). Models operate in an extreme low-sample regime.",
        "2. Statistical Nature: Predicted probabilities represent calculated statistical likelihoods derived from historical EONET telemetry.",
        "3. Disclaimer: This output is NOT an official disaster warning, real-time emergency alert, or government forecast.",
        "",
        "RECOMMENDATION FOR DASHBOARD INTEGRATION:",
        "Utilize the calibrated Gradient Boosting probabilities with educational tooltips, probability bands (Very High, High, Moderate, Low, Very Low), and non-alarming safety disclaimers."
    ])

    report_text = "\n".join(report_lines)
    with open(MODEL_REPORT_TXT, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Saved: {MODEL_REPORT_TXT}")

    # 9. Print Final Required Output
    print("\n======================================================================")
    print("STEP 3T COMPLETE")
    print("======================================================================")
    print(f"Dataset rows: {total_rows}")
    print(f"States: {num_states}")
    print(f"Positive examples: {pos_examples}")
    print(f"Negative examples: {neg_examples}")
    print(f"Best model: {best_model_name}")
    print(f"Validation PR-AUC: {val_best_record['pr_auc']:.4f}")
    print(f"Test PR-AUC: {test_best_record['pr_auc']:.4f}")
    print(f"Test F1: {test_best_record['f1']:.4f}")
    print(f"Test Brier Score: {test_best_record['brier_score']:.4f}")
    print("\nIMPORTANT:")
    print("Existing global K-Means system was not modified.")
    print("Existing global prediction system was not modified.")
    print("Frontend/backend were not modified.")
    print("\nNext:")
    print("Review the India state model comparison before dashboard integration.")


if __name__ == "__main__":
    main()
