# 06 Modelling and tuning: tickets

## T-001: Sustained alarms and detection delay

Status: done
Blocked by:
Slice: Row predictions become sustained alarms per run, with detection delay and alarm-level false alarm rate.
Test seam: `keyframe.alarm.sustained_alarm`, `detection_delay`, `alarm_metrics`
Context: requirements R7-R9; `grep -n '^def ' keyframe/evaluate.py keyframe/audit.py`; tests/conftest.py
Acceptance:
- [x] Synthetic tests: an alarm fires exactly `min_duration_s` after a sustained run of confident predictions; a single stray prediction never fires; alarms never carry across runs or look ahead
- [x] Detection delay on a synthetic run with a known switch-on; pre-switch-on alarms counted as false alarms
Notes:

## T-002: Nested Optuna tuning

Status: done
Blocked by:
Slice: Each model can be tuned for one outer fold using only the inner folds of its training loads.
Test seam: `keyframe.tuning.tune`, `keyframe.tuning.SEARCH_SPACES`
Context: requirements R1-R3, R6; `grep -n 'def inner_lolo_folds' -A10 keyframe/splits.py`; `grep -n 'def lolo_predict\|def summarise\|def macro_f1' keyframe/evaluate.py`; `ls docs/adr/` then read only the feature-set ADR from feature 05
Acceptance:
- [x] Spy test: the objective never fits on or scores rows outside `train_df`
- [x] Seeded study is reproducible (same best params twice on a tiny synthetic table)
- [x] `thin(df, step)` keeps every step-th row within each run in time order (test)
Notes:

## T-003: Tuning and modelling experiments

Status: done
Blocked by: T-002
Slice: `tuning` and `modelling` experiment commands that write tuned params and held-out predictions.
Test seam: `uv run python -m keyframe.experiments tuning ...`, `... modelling ...`
Context: requirements R4-R6; `grep -n 'def \|argparse\|add_parser' keyframe/experiments.py | head -40`
Acceptance:
- [x] Unit test runs both experiments on a tiny synthetic table in a tmp dir; every row predicted exactly once
- [x] Existing outputs are skipped unless `--force`
Notes:

## T-004: Tune and fit all four models

Status: done
Blocked by: T-003
Slice: Tuned params for 4 models × 4 outer folds and held-out predictions for every model exist.
Test seam: files under `models/tuning/` and `data/processed/experiments/modelling_*.parquet`
Context: requirements R4-R5; `uv run python -m keyframe.experiments --help`
Acceptance:
- [x] 16 tuning JSONs committed under `models/tuning/` (each invocation under 9 minutes; one command at a time)
- [x] 4 modelling outputs; `reports/results/04_models.csv` logged
- [x] If a model cannot finish a fold in 9 minutes with at least 10 trials, lower `n_estimators` bounds in its search space and note it in the ticket Notes
Notes: lightgbm, xgboost and random_forest all needed narrower search spaces (smaller `n_estimators`/`num_leaves`/`max_depth`/`max_samples` upper bounds, plus `--timeout-s 300`) to fit >=1 trial reliably under 9 minutes on the 833-column feature table; logreg needed no changes. Added `_log_modelling_summary` to `run_modelling` (R5) since it wasn't writing `reports/results/04_models.csv`; each per-model CLI call replaces that model's rows in the CSV so all 4 models' summaries accumulate across separate invocations. Found and kept a leftover xgboost-wrapper unit test and 3 stale 1-trial xgboost JSONs from an earlier, uncommitted attempt at this ticket; all 16 JSONs were regenerated with the final search spaces.

## T-005: Alarm parameters chosen inside the inner folds

Status: done
Blocked by: T-001, T-004
Slice: Alarm settings picked per outer fold from inner-fold predictions, then applied to the held-out predictions of every model.
Test seam: `uv run python -m keyframe.experiments alarm --model <m>`; `keyframe.alarm.choose_alarm_params`
Context: requirements R10; `grep -n '^def ' keyframe/alarm.py keyframe/experiments.py`
Acceptance:
- [x] Test: parameter choice uses only inner-fold predictions (spy)
- [x] `reports/results/04_alarms.csv` with per-run detection delay, false alarm rate at alarm level, chosen params per fold, for every model
Notes:

## T-006: Notebook 04: comparison, confusion, alarms

Status: open
Blocked by: T-005
Slice: Notebook 04 presents every model's held-out results, the tuned settings and the alarm behaviour from cached outputs.
Test seam: executing `notebooks/04_modelling.py`
Context: requirements R11-R12; `grep -n '^# %%' notebooks/03_feature_engineering.py` (structure to copy); `head -3 reports/results/04_models.csv reports/results/04_alarms.csv`
Acceptance:
- [ ] `04_fold_scores.png`, `04_confusion_best.png`, `04_detection_delay.png`
- [ ] Target table (met / not met) and scores with and without the first 10 minutes after switch-on
- [ ] Executes under 5 minutes; executed `.ipynb` committed
Notes:

## T-007: Findings and the best-model decision

Status: open
Blocked by: T-006
Slice: The best model and its settings are recorded, and notebook 04 opens with honest findings.
Test seam: `reports/results/04_best_model.csv`; the ADR
Context: requirements R13; `reports/results/04_models.csv` and `04_alarms.csv` (pandas summary only); `grep -n '^# %%' notebooks/04_modelling.py`
Acceptance:
- [ ] `04_best_model.csv` with model, per-fold params, pooled and per-fold scores
- [ ] ADR recording the choice and tie-breaks; first notebook cell summarises findings against targets
- [ ] Notebook executes and is committed
Notes:
