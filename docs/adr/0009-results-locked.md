# 0009. Results locked

Status: accepted
Decided-by: answerer (inferred), per ADR 0003's fully-automatic working agreement
Question: T-006 (09-evaluation), R9: what are the final numbers, and may they change?
Decision: The results below are final as of 2026-09-29. No score changes after this point. Roadmap items 10 onwards may not retrain for better scores; export retrains on all loads for the demo only.
Final numbers (XGBoost, `raw+physics+rolling`, leave one load out, `reports/results/04_best_model.csv`, `07_*.csv`):
1. Macro F1 0.717 (target 0.80, not met); per load 0.547 / 0.860 / 0.701 / 0.609 at 40 / 60 / 75 / 85%.
2. Lowest per-class recall 0.194, TD (target 0.70, not met).
3. False alarm rate 12.2% (target 5%, not met).
4. Detection delay: alarm fires on 6 of 13 fault runs, median 563 s; not met once undetected runs count.
5. Calibration: pooled ECE 0.176 (target 0.05, not met); temperature scaling worsened ECE in loads 40, 60, 75 and improved 85 only.
6. Sensitivity without day-dependent channels: macro F1 0.635 / 0.725 / 0.611 / 0.347.
7. Lockbox (unseen severity, scored once): 6,791 of 6,791 rows labelled INJ, 100% (target 90% met), but only INJ was predicted, so weak evidence.
8. Anomaly detectors: fault detection AUROC 0.528 (target 0.95, not met).
9. Physics check on SHAP explanations: 2 of 5 faults match the pre-registered checklist (AC, INJ; target 4 of 5, not met). AF and CW rely on day-dependent channels, TD on lube oil and efficiency proxies (`reports/physics_check.md`).
Basis: `reports/model_card.md` and notebook 07 report these numbers without tuning on any test fold or the lockbox.
Consequences: only the unseen-severity target is met. The model card states plainly that the model has not been tested on a ship.
