# 0007. XGBoost is the best model, but none of the four meet the targets

Status: accepted
Decided-by: answerer (inferred), per ADR 0003's fully-automatic working agreement
Question: T-007 (06-modelling), R13: which model goes forward as the best model, and does it meet the targets?
Decision: XGBoost (`raw+physics+rolling`, per-fold tuned params in `reports/results/04_best_model.csv`) is the best model. It wins outright on pooled macro F1 (0.717) against LightGBM (0.667), random forest (0.648) and logreg (0.542, `reports/results/04_models.csv`), so R13's tie-break (lowest per-class recall, then false alarm rate) is not needed. XGBoost still misses every target in `reports/targets.md`:
1. Macro F1 0.717 vs the 0.80 target.
2. Lowest per-class recall 0.194 (Turbine Degradation) vs the 0.70 target.
3. False alarm rate 12.2% vs the 5% target.
4. Detection delay: XGBoost's sustained alarm fires on only 6 of the 13 fault runs (`reports/results/04_alarms.csv`); median delay among those is 563 s (9.4 min, under the 600 s target), but the other 6 runs never trigger an alarm at all, so the target is not met once undetected runs are counted honestly.
Basis: scores computed without each run's first 10 minutes after switch-on (`reports/results/04_first_10_min.csv`) are close to the full scores, so gradual fault onset does not explain the shortfall; it reflects the model's real discrimination limits on this feature set at held-out loads.
Consequences: no model from this feature is ready to ship as a detector. A future feature should treat XGBoost/`raw+physics+rolling` as the baseline to beat and investigate why half the fault runs raise no alarm (per-run diagnostics, not just pooled scores) before trying new models or features.
