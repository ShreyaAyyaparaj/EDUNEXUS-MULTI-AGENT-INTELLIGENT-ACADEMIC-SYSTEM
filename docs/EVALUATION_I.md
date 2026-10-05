# EduNexus Evaluation I Evidence

This folder contains reproducible demonstrations and their generated outputs. The student success experiment uses a **Synthetic Evaluation Dataset** with simulated next-semester outcomes. Its scores and plots are not measurements of institutional student performance and must not be described as such.

Run `python scripts/evaluate_agents.py` from the repository root to generate the deterministic routing case table, measured in-process routing latencies, per-route precision/recall/F1, task success and error counts, summary JSON, and SVG figures under `docs/evaluation/`. The seven hand-authored cases are a small smoke benchmark, not a statistically representative estimate of production routing accuracy. It does not measure Gemini, RAG grounding, or end-to-end network latency.

Run `python ml/student_success_evaluation.py` from the repository root to generate a seeded synthetic CSV, train/test metrics, model artifact, confusion-matrix SVG, and feature-importance SVG under `docs/evaluation/`. Features describe the current/prior snapshot; the simulated target represents a later outcome. The target is generated from a transparent rule plus noise, so the experiment demonstrates an evaluation workflow rather than predictive validity.

Real evaluation still requires labeled, permissioned longitudinal institutional data, representative reviewed agent cases, measured end-to-end calls, labeled RAG relevance/grounding judgments, and visual output screenshots. No RAG relevance score is emitted until such a labeled retrieval set is available. Do not copy illustrative metrics from planning material into a final report.
