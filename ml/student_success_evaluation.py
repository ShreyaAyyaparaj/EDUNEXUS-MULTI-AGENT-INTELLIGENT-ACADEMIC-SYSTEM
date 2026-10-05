"""Synthetic, non-institutional future-outcome experiment for Evaluation I."""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "evaluation"
FEATURES = ["attendance_pct", "avg_internal_marks", "previous_sgpa", "previous_cgpa",
            "failed_subjects", "assessment_completion_pct", "attendance_trend", "marks_trend", "semester"]


def synthetic_dataset(n=1200, seed=41):
    rng = np.random.default_rng(seed)
    data = pd.DataFrame({
        "attendance_pct": rng.uniform(45, 100, n),
        "avg_internal_marks": rng.uniform(25, 100, n),
        "previous_sgpa": rng.uniform(4.5, 10, n),
        "previous_cgpa": rng.uniform(4.5, 10, n),
        "failed_subjects": rng.integers(0, 5, n),
        "assessment_completion_pct": rng.uniform(40, 100, n),
        "attendance_trend": rng.normal(0, 12, n),
        "marks_trend": rng.normal(0, 14, n),
        "semester": rng.integers(2, 8, n),
    })
    # The target is a simulated following-semester outcome. It uses only current and prior features.
    score = (0.035 * (75 - data.attendance_pct) + 0.025 * (60 - data.avg_internal_marks)
             + 0.45 * data.failed_subjects + 0.06 * (70 - data.assessment_completion_pct)
             - 0.035 * data.attendance_trend - 0.025 * data.marks_trend
             + 0.5 * (7 - data.previous_sgpa) + rng.normal(0, 1.3, n))
    data["future_at_risk"] = (score > 1.15).astype(int)
    return data


def svg_bars(labels, values, title, target, percent=False):
    maximum = max(values) if values else 1
    scale = 500 / maximum if maximum else 1
    height = 70 + 34 * len(labels)
    bars = []
    for i, (label, value) in enumerate(zip(labels, values)):
        y = 42 + i * 34
        shown = f"{value:.3f}" if percent else f"{value:.3f}"
        bars.append(f'<text x="12" y="{y+14}" font-size="12">{label}</text><rect x="210" y="{y}" width="{value*scale:.2f}" height="20" fill="#7554e8"/><text x="{218+value*scale:.2f}" y="{y+15}" font-size="11">{shown}</text>')
    target.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="{height}"><rect width="100%" height="100%" fill="white"/><text x="12" y="24" font-family="Arial" font-size="16">{title}</text>{"".join(bars)}</svg>', encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = synthetic_dataset()
    train_x, test_x, train_y, test_y = train_test_split(
        data[FEATURES], data.future_at_risk, test_size=0.25, random_state=17, stratify=data.future_at_risk)
    model = RandomForestClassifier(n_estimators=250, min_samples_leaf=3, class_weight="balanced",
                                   random_state=17, n_jobs=-1)
    model.fit(train_x, train_y)
    start = perf_counter()
    pred = model.predict(test_x)
    scores = model.predict_proba(test_x)[:, 1]
    elapsed_ms = (perf_counter() - start) * 1000 / len(test_x)
    matrix = confusion_matrix(test_y, pred, labels=[0, 1]).tolist()
    report = {
        "dataset_label": "Synthetic Evaluation Dataset; not institutional records",
        "seed": 41, "rows": len(data), "train_rows": len(train_x), "test_rows": len(test_x),
        "target": "simulated next-semester at-risk outcome",
        "features": FEATURES, "positive_rate": float(data.future_at_risk.mean()),
        "accuracy": float(accuracy_score(test_y, pred)),
        "precision": float(precision_score(test_y, pred, zero_division=0)),
        "recall": float(recall_score(test_y, pred, zero_division=0)),
        "f1": float(f1_score(test_y, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(test_y, scores)),
        "confusion_matrix_labels_0_1": matrix,
        "mean_prediction_latency_ms": elapsed_ms,
        "feature_importance": {name: float(value) for name, value in zip(FEATURES, model.feature_importances_)},
        "limitations": ["Simulated features and future labels.", "Metrics do not describe real students.",
                        "Replace with consented, time-split institutional outcomes before operational use."],
    }
    data.to_csv(OUT / "student_success_synthetic_dataset.csv", index=False)
    (OUT / "student_success_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    joblib.dump(model, OUT / "student_success_synthetic_model.joblib")
    matrix_svg = []
    for r in range(2):
        for c in range(2):
            color = "#7554e8" if r == c else "#bd6a78"
            matrix_svg.append(f'<rect x="{220+c*145}" y="{75+r*115}" width="120" height="90" fill="{color}"/><text x="{280+c*145}" y="{130+r*115}" text-anchor="middle" fill="white" font-size="22">{matrix[r][c]}</text>')
    (OUT / "student_success_confusion_matrix.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="620" height="340"><rect width="100%" height="100%" fill="white"/><text x="25" y="32" font-family="Arial" font-size="16">Synthetic holdout confusion matrix (true/predicted class)</text><text x="210" y="65">Predicted 0</text><text x="355" y="65">Predicted 1</text><text x="130" y="135">True 0</text><text x="130" y="250">True 1</text>'+''.join(matrix_svg)+'</svg>', encoding="utf-8")
    names = sorted(report["feature_importance"], key=report["feature_importance"].get, reverse=True)
    svg_bars(names, [report["feature_importance"][n] for n in names],
             "Synthetic model feature importance", OUT / "student_success_feature_importance.svg")
    risk_counts = data.future_at_risk.value_counts().sort_index()
    svg_bars(["Not at risk", "At risk"], [int(risk_counts.get(0, 0)), int(risk_counts.get(1, 0))],
             "Synthetic future-outcome distribution (counts)", OUT / "student_success_risk_distribution.svg")
    print(json.dumps({k: v for k, v in report.items() if k not in {"features", "feature_importance", "limitations"}}, indent=2))


if __name__ == "__main__":
    main()
