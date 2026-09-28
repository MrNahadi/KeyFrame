# Mission

Derived from `specs/brief.md` v1.0 (28 Sep 2026). The brief wins if the two ever disagree.

## Summary

Keyframe diagnoses faults on a marine diesel engine from its sensor readings, and keeps working at engine loads it never saw in training. It is built on real test-bench data (Marine Engine Fault Dataset v1.0, a Matsui MU323DGSC), developed in nine Jupyter notebooks backed by a small tested `keyframe` package, and shown through a FastAPI service and a TypeScript web demo that replays real runs and explains every alarm.

## Users

- **Primary: an engineer or recruiter at an engine maker (e.g. Wärtsilä).** Knows diesel engines and their faults, knows basic ML words, and has about five minutes. Needs to see quickly that the evaluation is honest and the explanations make engineering sense. Every page, notebook heading and demo label is written for this reader: engine terms are fine, ML jargon is explained in a phrase.
- Secondary: a Masters admissions panel, looking for research method (pre-registered targets, leakage-free validation, spread across folds, a model card with limits).
- Owner: Farid Muigu, for whom this is the successor to Marine AIMS.

## Goals

Every number is measured on held-out engine loads (leave one load out), never on a random split.

| Goal | Target | Stretch |
|---|---|---|
| Macro F1, held-out loads | 0.80 | 0.90 |
| Lowest per-class recall | 0.70 | 0.85 |
| False alarm rate on healthy rows | 5% | 2% |
| Fault detection AUROC (healthy-only detector) | 0.95 | 0.98 |
| Median detection delay | 10 min | 5 min |
| Expected calibration error | 0.05 | 0.03 |
| Two-hole injector lockbox labelled INJ | 90% | 97% |
| SHAP top 5 matches engineering checklist | 4 of 5 faults | 5 of 5 |
| Demo prediction plus explanation | 300 ms | 100 ms |

Targets may be revised once, after the EDA (roadmap item 3), with the reason written in `reports/targets.md`. Never after test results.

## In scope

The thirteen user outcomes in brief section 5: reproducible data, audit, EDA with a pre-registered engineering checklist, baselines, feature ablation, tuned models with alarm logic, anomaly detection, explainability with a physics check, locked evaluation and model card, export, API, web demo (replay, explain, what-if, model card), and the README write-up.

## Out of scope

- Onboard or real-ship deployment, and live sensor feeds.
- User accounts, sign in or saved sessions.
- Other engines or datasets.
- Retraining or tuning from the demo.
- A native mobile app.

## Principles

1. Honest evaluation beats every other consideration (brief section 10).
2. An explanation that contradicts engine physics is a bug to investigate, not a result to publish.
3. Anyone can rebuild everything from a fresh clone with the commands in the README.
