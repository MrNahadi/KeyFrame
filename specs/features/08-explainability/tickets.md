# 08 Explainability: tickets

## T-001: Map features to source channels and sensor groups

Status: open
Blocked by:
Slice: Any model feature can be traced to the engine channels it comes from and to one sensor group.
Test seam: `keyframe.explain.source_channel`, `keyframe.explain.SENSOR_GROUPS`, `keyframe.explain.group_of`
Context: requirements R1-R2; `grep -n '^def ' keyframe/features.py`; `grep -n 'def add_physics_features' -A25 keyframe/features.py`; `cut -d, -f1,7 data/raw/variable_dictionary.csv`
Acceptance:
- [ ] Every sensor channel in the feature table has exactly one group (data-marked test; skip if absent)
- [ ] Source mapping tests for raw, rolling, residual and each physics feature
Notes:

## T-002: SHAP experiment per fold

Status: open
Blocked by: T-001
Slice: SHAP values for the best model on each fold's held-out rows, cached per fold.
Test seam: `uv run python -m keyframe.experiments shap --fold <bin>`
Context: requirements R3; `ls docs/adr/ | tail -3` then the best-model ADR; `grep -n 'def run_modelling\|def run_tuning\|add_parser' keyframe/experiments.py`; `head -3 reports/results/04_best_model.csv`
Acceptance:
- [ ] Unit test on a tiny synthetic table: SHAP values plus base value reproduce the model's raw output for a sampled row (additivity)
- [ ] Four fold outputs written, one foreground command each, under 9 minutes
Notes:

## T-003: Grouped and per-class SHAP views

Status: open
Blocked by: T-002
Slice: Rankings per class, grouped SHAP per class and grouped waterfalls for single moments.
Test seam: `keyframe.explain` view functions
Context: requirements R4, R10 (figures); `grep -n '^def ' keyframe/explain.py`
Acceptance:
- [ ] Tests: grouped SHAP sums equal the per-feature sums; rankings are by mean |SHAP| on the class's rows
- [ ] Beeswarm, grouped SHAP and waterfall figures written by notebook 06 (first sections), which executes and is committed
Notes:

## T-004: Physics check against the pre-registered checklist

Status: open
Blocked by: T-003
Slice: Each fault's top 5 SHAP features scored against the checklist with the rule fixed before modelling, with every mismatch investigated.
Test seam: `keyframe.explain.physics_check`
Context: requirements R5-R6; `sed -n '/Physics check/,/^$/p' reports/targets.md`; `grep -n 'Expected top 5\|Agree' reports/engineering_checklist.md`
Acceptance:
- [ ] Rule tests on hand-made rankings (3 of 5 passes, 2 of 5 fails, a day-dependent channel fails)
- [ ] `reports/physics_check.md` with per-fault table, mismatch investigations and met / not met against 4 of 5
Notes:

## T-005: Cross-checks: permutation importance, PDP/ICE, one LIME comparison

Status: open
Blocked by: T-003
Slice: Independent checks on the SHAP story.
Test seam: executing `notebooks/06_explainability.py`
Context: requirements R7-R9; `grep -n '^# %%' notebooks/06_explainability.py`; `grep -n 'def inner_permutation_importance' -A10 keyframe/features.py`
Acceptance:
- [ ] Rank correlation between grouped permutation importance and grouped SHAP per fold, in `reports/results/06_crosscheck.csv`
- [ ] PDP/ICE figures and the LIME comparison for 3 moments
- [ ] Notebook executes and is committed (heavy parts cached; under 5 minutes)
Notes:

## T-006: Notebook 06 findings

Status: open
Blocked by: T-004, T-005
Slice: Notebook 06 opens with honest findings for an engine engineer.
Test seam: executing the notebook
Context: requirements R10; `reports/physics_check.md`; `reports/results/06_crosscheck.csv` (summary only); `grep -n '^# %%' notebooks/06_explainability.py`
Acceptance:
- [ ] First cell: which readings drive each diagnosis, physics check result, where credit-sharing makes explanations unreliable
- [ ] Notebook executes and is committed
Notes:
