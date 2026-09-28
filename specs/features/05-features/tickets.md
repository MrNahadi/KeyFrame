# 05 Feature engineering: tickets

## T-001: Physics features

Status: done
Blocked by:
Slice: One call adds every physics feature from the brief to the clean table, with NaN-safe denominators, and notebook 01 keeps working.
Test seam: `keyframe.features.add_physics_features(df)`
Context: requirements R1-R2; `grep -n '^def ' keyframe/eda.py keyframe/features.py`; `grep -n 'phys\|effectiveness\|spread' keyframe/eda.py | head -30`
Acceptance:
- [x] Hand-computed tests for pressure ratio, cooler effectiveness, spreads, turbine drop, fuel per kW, heat-balance shares; zero denominators give NaN
- [x] Physics functions live in `features.py`; `eda.py` imports them; `tests/test_eda.py` still passes
Notes:

## T-002: Causal time-based rolling features

Status: done
Blocked by:
Slice: Trailing 1, 5 and 15 minute mean, std and slope per run, fast enough for the full table.
Test seam: `keyframe.features.add_rolling_features(df, channels, windows_s, stats)`
Context: requirements R3-R5; `grep -n 'def rolling_std' -A25 keyframe/eda.py`; tests/conftest.py
Acceptance:
- [x] Synthetic two-run test: no value depends on another run's rows or on later rows (changing a future row or the other run leaves earlier values unchanged)
- [x] Slope of a line with known gradient is exact; warm-up flag is 1 exactly while the window is filling
- [x] A data-marked test times the full table under 2 minutes (skip if data absent)
Notes:

## T-003: Healthy-engine residual transformer

Status: done
Blocked by:
Slice: A pipeline step fitted on healthy rows of the training fold that turns each sensor into its deviation from what a healthy engine would read.
Test seam: `keyframe.features.HealthyEngineResiduals`
Context: requirements R6-R8; `grep -n 'def lolo_predict' -A35 keyframe/evaluate.py`; `grep -n 'EXCLUDED_COLUMNS\|def raw_sensor_columns' -A5 keyframe/features.py`
Acceptance:
- [x] Fit uses only rows with y == "Normal" (test proves fault rows don't change the fit)
- [x] Synthetic linear engine: healthy residuals ≈ 0, injected fault offset recovered
- [x] Works inside a sklearn Pipeline with `lolo_predict`
Notes:

## T-004: Shop-test hook for the residual model

Status: done
Blocked by: T-003
Slice: The shop-test variant can give the residual model the held-out load's reference rows without the classifier ever seeing them.
Test seam: `keyframe.evaluate.lolo_predict(..., extra_healthy=...)`
Context: requirements R9; `grep -n 'def lolo_predict' -A35 keyframe/evaluate.py`; `grep -n 'class HealthyEngineResiduals' -A40 keyframe/features.py`
Acceptance:
- [x] Test with a spy classifier: its training rows are identical with and without `extra_healthy`
- [x] Test: the residual step saw the extra rows when `extra_healthy` is given
- [x] Default behaviour (no hook) is unchanged; existing tests pass
Notes:

## T-005: Feature-set registry

Status: done
Blocked by: T-001, T-002, T-003
Slice: Named feature sets that build the column list and the pipeline for any model, used by the ablation.
Test seam: `keyframe.features.FEATURE_SETS`, `keyframe.features.build_pipeline(feature_set, model)`
Context: requirements R10-R11; `grep -n '^def \|^class \|^[A-Z_]* =' keyframe/features.py`; `head -20 reports/results/01_day_markers.csv`; `grep -n -i 'day.marker' -A8 notebooks/01_eda.py | head -40`
Acceptance:
- [x] Every set excludes every column in EXCLUDED_COLUMNS (test over all sets on a synthetic table)
- [x] Residual sets replace day-marker temperature channels by their residuals as notebook 01 recommended
- [x] `build_pipeline` returns an unfitted sklearn Pipeline usable with `lolo_predict`
Notes:

## T-006: Notebook 03 part 1: the ablation

Status: done
Blocked by: T-004, T-005
Slice: Every feature set scored with logistic regression and LightGBM on held-out loads through a cached experiment command, and presented with fold spread in notebook 03.
Test seam: `uv run python -m keyframe.experiments ablation --feature-set <name> --model <model>`; executing `notebooks/03_feature_engineering.py`
Context: requirements R12; tech-stack.md "Notebooks" (heavy experiments bullet); `grep -n '^# %%' notebooks/02_baselines.py`; `grep -n 'LogisticRegression\|LGBM\|RandomForest' -A4 notebooks/02_baselines.py | head -40` (reuse the same settings); tech-stack.md "Notebooks"
Acceptance:
- [x] `reports/results/03_ablation.csv` via `log_results`; `03_ablation.png` shows per-fold scores
- [x] Physics and rolling columns computed once, before the LOLO loop; residuals fitted inside it
- [x] `keyframe/experiments.py` with the `ablation` experiment: skips existing outputs unless `--force`; a unit test runs it on a tiny synthetic table in a tmp dir
- [x] All 12 combinations run per fold (`--fold`), outputs under `data/processed/experiments/`; read them with `keyframe.experiments.load_ablation`
- [x] Notebook reads the outputs, executes in under 5 minutes, and the executed `.ipynb` is committed
Notes:
- Validation fix (commits 8322d4a, a02ba93): the first run compared identical inputs (physics/rolling columns were never built; residual sets only residualised four channels). Fixed, feature table cached at `data/processed/features.parquet`, and all 48 fold runs regenerated by the planner. Remaining for this ticket: the notebook presentation (`03_ablation.csv` via `log_results`, `03_ablation.png`), reading outputs with `load_ablation`. Do not rerun the experiments.

## T-007: Notebook 03 part 2: pruning inside the training folds

Status: done
Blocked by: T-006
Slice: Near-duplicate and useless features dropped using training-fold statistics only, and the pruned set rescored.
Test seam: `keyframe.features.prune_correlated`, `keyframe.features.inner_permutation_importance`; `uv run python -m keyframe.experiments pruning --feature-set <best> --model <best> --fold <bin>`; executing the notebook
Context: requirements R13; `grep -n 'def inner_lolo_folds' -A10 keyframe/splits.py`; `grep -n '^# %%' notebooks/03_feature_engineering.py`
Acceptance:
- [x] Unit tests: `prune_correlated` drops one of a perfectly correlated pair and keeps uncorrelated ones; permutation importance uses only inner-fold rows (spy test)
- [x] Permutation importance is grouped by source channel (a channel, its residual, its rolling statistics and physics features count as their own groups), permuting each group together with `n_repeats=3`; features of groups with mean importance ≤ 0 across inner folds are dropped. Per-column permutation over hundreds of correlated columns is neither affordable nor meaningful (brief: "Grouping features by system before explaining keeps the story readable and more honest")
- [x] One invocation per outer fold (`--fold`), each under 9 minutes
- [x] Pruning and the pruned set's LOLO score run as a cached experiment (`uv run python -m keyframe.experiments pruning ...`), under 9 minutes per invocation
- [x] `reports/results/03_pruning.csv` lists features dropped per outer fold; pruned set scored and logged
- [x] Notebook executes and is committed
Notes:
- Planner (validation): code finished in 7366db4; pruning outputs for the best arm, `raw+physics+rolling` × `lightgbm`, exist for all four folds (read with `keyframe.experiments.load_pruning`; the dropped features are in the `dropped_feature` column). Do not rerun experiments. Remaining: `reports/results/03_pruning.csv` and the notebook section.

## T-008: Shop-test score, findings and the decision

Status: done
Blocked by: T-007
Slice: Notebook 03 reports the shop-test score for the best set, states which families earned their place, and records the feature set going forward.
Test seam: executing the notebook; the ADR file
Context: requirements R14-R15; `reports/results/03_ablation.csv`, `reports/results/03_pruning.csv` (read with pandas, summary only); `grep -n '^# %%' notebooks/03_feature_engineering.py`
Acceptance:
- [x] Shop-test score computed via `uv run python -m keyframe.experiments ablation --feature-set <best> --model <best> --shop-test`, reported next to the main score and logged
- [x] First cell summarises findings with numbers and spread; ADR records the chosen set
- [x] Notebook executes and is committed
Notes:
- Planner: the best arm has no residual step, so its shop-test score is undefined. The shop-test score is reported for the best residual arm, `residuals+physics` × `logreg` (outputs exist: `load_ablation('residuals+physics', 'logreg', shop_test=True)`), next to that arm's main score. Do not rerun experiments.
- Planner check, false alarm rate on Normal rows for `residuals+physics` × `logreg`, by source and held-out fold:
  main: reference rows 0.017 / 0.000 / 0.127 / 0.000 and pre-fault rows 0.334 / 0.192 / 1.000 / 0.280 (folds 40/60/75/85);
  shop-test: reference rows 0.607 / 0.000 / 0.127 / 0.000 and pre-fault rows 0.950 / 0.332 / 1.000 / 0.295.
  Report both honestly: (1) every pre-fault healthy row at 75% is flagged even in the main score, which fits notebook 01's finding that the two 75% runs are cold test-day outliers; (2) the shop-test is worse, not better, and the damage is in the 40% fold, where adding reference rows down to 56 kW reshapes the degree-2 healthy-engine model at the edge of its range. State these as observations with their likely explanation, not as proven causes, and say what feature 06 should try (e.g. restricting the healthy-engine model's training rows to the 40–85% operating range, or a lower-degree fit).

