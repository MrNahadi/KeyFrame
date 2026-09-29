# 08 Explainability: plan

Roadmap item 8 (brief milestone 9). Done when every fault has been checked against the engineering checklist, and any mismatch is explained.

## Approach

Explain the best model from feature 06 (its ADR and `reports/results/04_best_model.csv`) as it was evaluated: one model per LOLO fold, explained on that fold's held-out rows, so explanations describe predictions on unseen loads. SHAP TreeExplainer gives exact per-row, per-class values. Because sensors move together, the headline view sums SHAP by sensor group (air path, fuel system, cooling, lube oil, combustion and power). The physics check applies the rule fixed in `reports/targets.md` before modelling. Heavy SHAP runs are cached experiments, one fold per invocation.

## Modules touched

- `keyframe/explain.py` (new): channel-to-group map, feature-to-source-channel map, SHAP helpers, grouped SHAP, physics check
- `keyframe/experiments.py`: `shap` experiment (per fold)
- `tests/test_explain.py`
- `notebooks/06_explainability.py` + executed `.ipynb`; `reports/results/06_*.csv`; `reports/figures/06_*.png`; `reports/physics_check.md`

## Order of work

T-001 groups and source mapping → T-002 SHAP experiment → T-003 grouped and per-class views → T-004 physics check → T-005 cross-checks (permutation, PDP/ICE, LIME) → T-006 notebook findings.

## New dependencies

None (shap, lime installed).
