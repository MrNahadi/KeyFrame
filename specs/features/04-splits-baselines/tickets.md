# 04 Splits and baselines: tickets

## T-001: Model input columns with the exclusions enforced

Status: done
Blocked by:
Slice: One function gives the raw-sensor input columns; a test proves the excluded channels can never get through.
Test seam: `keyframe.features.raw_sensor_columns(df)`, `keyframe.features.EXCLUDED_COLUMNS`
Context: requirements R1-R3; tech-stack.md "Data and leakage"; tests/conftest.py
Acceptance:
- [x] Synthetic test: every excluded column present in the input is absent from the output; non-numeric columns are dropped
- [x] Data-marked test on `data/processed/clean.parquet` (skip if absent): output non-empty, no excluded column, no column with any missing value
Notes:

## T-002: Leave-one-load-out splitter and its nested inner loop

Status: done
Blocked by:
Slice: The validation protocol as code, with tests that no split mixes loads.
Test seam: `keyframe.splits.lolo_folds(df)`, `keyframe.splits.inner_lolo_folds(train_df)`
Context: requirements R4-R6; `sed -n '/^## Validation protocol/,/^## Workflow/p' specs/brief.md`; `grep -n 'def ' keyframe/splits.py`
Acceptance:
- [x] R6 tests pass on a synthetic table with a stepped run spanning bins
- [x] Data-marked test: four folds on the real table; the 75% fold's test set has no CW or TD rows
Notes:

## T-003: Metrics and the results log

Status: done
Blocked by:
Slice: The brief's metrics computed from labels, and a results log that records every experiment with its commit.
Test seam: `keyframe.evaluate` metric functions and `log_results`
Context: requirements R7, R10; `sed -n '/^## Goals and success metrics/,/^## Validation protocol/p' specs/brief.md`
Acceptance:
- [x] Hand-checked tests: macro F1 ignores classes absent from y_true; false alarm rate on a known case; confusion matrix order fixed
- [x] `log_results` writes a CSV with experiment, date and git_commit columns (test writes to a tmp dir)
Notes:

## T-004: Cross-validated predictions over LOLO folds

Status: done
Blocked by: T-002, T-003
Slice: Any sklearn model can be scored over the four held-out loads, giving per-row predictions and a pooled-plus-per-fold summary.
Test seam: `keyframe.evaluate.lolo_predict`, `keyframe.evaluate.summarise`
Context: requirements R8-R9; `grep -n 'def ' keyframe/splits.py keyframe/evaluate.py`
Acceptance:
- [x] Synthetic test: a model is fitted once per fold and never sees test rows (a spy estimator records the indices it was fitted on)
- [x] Summary has one pooled row and one row per fold; per-fold macro F1 uses only classes present in that fold
Notes:

## T-005: Notebook 02: four baselines on raw sensors

Status: done
Blocked by: T-001, T-004
Slice: Notebook 02 scores the four baselines on held-out loads and saves the table, predictions and figures.
Test seam: executing `notebooks/02_baselines.py`
Context: requirements R11-R13; tech-stack.md "Notebooks"; `grep -n '^# %%' notebooks/00_data_audit.py` (structure to copy)
Acceptance:
- [x] `reports/results/02_baselines.csv`, `data/processed/02_best_baseline_predictions.parquet`, `02_fold_scores.png`, `02_confusion_best.png`
- [x] Notebook executes and the executed `.ipynb` is committed
Notes:

## T-006: Notebook 02 findings against the brief's first check

Status: done
Blocked by: T-005
Slice: Notebook 02 opens and closes with findings for an engine engineer, comparing against the 0.52 first-check baseline.
Test seam: executing `notebooks/02_baselines.py`
Context: requirements R14; `reports/results/02_baselines.csv`; `grep -n '^# %%' notebooks/02_baselines.py`
Acceptance:
- [x] First cell: what the notebook answers and the headline numbers with spread; last section: what the baselines get wrong (weakest class, false alarms) and what feature engineering should target
- [x] Notebook executes and the executed `.ipynb` is committed
Notes:
