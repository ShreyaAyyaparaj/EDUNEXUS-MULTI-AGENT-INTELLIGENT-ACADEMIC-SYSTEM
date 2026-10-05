"""Measure deterministic intent routing on a small, transparent evaluation set."""
import csv
import json
from pathlib import Path
from time import perf_counter

from agents.router import classify_question

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "evaluation"
CASES = [
    ("student", "What is my attendance?", "student_success"),
    ("student", "How am I performing?", "student_success"),
    ("student", "What subjects are in Semester VII?", "academic"),
    ("student", "What is the mentor-mentee policy?", "university"),
    ("faculty", "Which students have low attendance?", "faculty_intelligence"),
    ("faculty", "Explain the college anti-ragging policy", "university"),
    ("faculty", "What subjects are in Semester VII?", "academic"),
]


def svg_chart(rows, out):
    width, height, pad = 820, 360, 52
    vals = [r["latency_ms"] for r in rows]
    scale = (height - 2 * pad) / max(max(vals, default=1), 1)
    bars = []
    for i, row in enumerate(rows):
        x = pad + i * 105
        h = row["latency_ms"] * scale
        bars.append(f'<rect x="{x}" y="{height-pad-h:.2f}" width="54" height="{h:.2f}" fill="#7554e8"/><text x="{x+27}" y="{height-pad-h-8:.2f}" text-anchor="middle" font-size="11">{row["latency_ms"]:.3f}</text><text x="{x+27}" y="{height-pad+17}" text-anchor="middle" font-size="10">{row["expected"][:12]}</text>')
    out.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><text x="{pad}" y="26" font-family="Arial" font-size="16">Router classification latency (ms), measured per case</text>{"".join(bars)}<text x="{pad}" y="{height-12}" font-family="Arial" font-size="10">One in-process intent classification per case; not end-to-end LLM latency.</text></svg>', encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for role, question, expected in CASES:
        start = perf_counter()
        actual = classify_question(question, role)
        latency = (perf_counter() - start) * 1000
        results.append({"role": role, "question": question, "expected": expected,
                        "actual": actual, "correct": actual == expected, "latency_ms": latency})
    report = {"evaluation_set": "Hand-authored intent cases", "case_count": len(results),
              "correct": sum(row["correct"] for row in results),
              "accuracy": sum(row["correct"] for row in results) / len(results),
              "mean_routing_latency_ms": sum(row["latency_ms"] for row in results) / len(results),
              "cases": results}
    labels = sorted({row["expected"] for row in results} | {row["actual"] for row in results})
    by_route = {}
    for label in labels:
        tp = sum(row["expected"] == label and row["actual"] == label for row in results)
        fp = sum(row["expected"] != label and row["actual"] == label for row in results)
        fn = sum(row["expected"] == label and row["actual"] != label for row in results)
        precision = tp / (tp + fp) if tp + fp else 0
        recall = tp / (tp + fn) if tp + fn else 0
        by_route[label] = {"true_positive": tp, "false_positive": fp, "false_negative": fn,
                           "precision": precision, "recall": recall,
                           "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0,
                           "case_count": tp + fn, "task_success": tp / (tp + fn) if tp + fn else 0}
    report["metrics_by_route"] = by_route
    report["false_positive_count"] = sum(v["false_positive"] for v in by_route.values())
    report["false_negative_count"] = sum(v["false_negative"] for v in by_route.values())
    (OUT / "agent_routing_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    with (OUT / "agent_routing_cases.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    svg_chart(results, OUT / "agent_routing_latency.svg")
    svg_chart([{"expected": label, "latency_ms": by_route[label]["f1"]} for label in labels],
              OUT / "agent_routing_f1.svg")
    svg_chart([{"expected": label, "latency_ms": by_route[label]["task_success"]} for label in labels],
              OUT / "agent_routing_task_success.svg")
    errors = [("False positives", report["false_positive_count"]),
              ("False negatives", report["false_negative_count"]),
              ("Fallbacks", 0), ("Failed tasks", sum(not r["correct"] for r in results))]
    error_svg = ''.join(f'<text x="20" y="{70+i*52}" font-size="13">{label}</text><rect x="175" y="{52+i*52}" width="{min(450,count*80)}" height="28" fill="#7554e8"/><text x="{185+min(450,count*80)}" y="{72+i*52}" font-size="13">{count}</text>' for i,(label,count) in enumerate(errors))
    (OUT / "agent_routing_error_analysis.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="290"><rect width="100%" height="100%" fill="white"/><text x="20" y="28" font-family="Arial" font-size="16">Measured router case errors</text>{error_svg}</svg>', encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
