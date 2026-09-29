# 09 Evaluation: tickets

## T-001: Calibration metrics

Status: done
Blocked by:
Slice: Top-label ECE and reliability curves from held-out probabilities.
Test seam: `keyframe.calibration.expected_calibration_error`, `reliability_curve`
Context: requirements R2; `grep -n 'proba_' keyframe/evaluate.py | head`
Acceptance:
- [x] Hand-made cases: perfect calibration gives 0; always-certain-half-wrong gives 0.5; bins with no rows are skipped
Notes:

## T-002: Recalibration inside the training folds

Status: open
Blocked by: T-001
Slice: If pooled ECE exceeds 0.05, each outer fold gets a calibrator fitted only on inner-fold predictions, and held-out probabilities are recalibrated.
Test seam: `uv run python -m keyframe.experiments calibration --fold <bin>`; `keyframe.calibration.fit_calibrator`
Context: requirements R3; `grep -n 'def run_alarm' -A30 keyframe/experiments.py` (it already builds inner-fold predictions); `grep -n 'def load_tuned_params' -A10 keyframe/experiments.py`
Acceptance:
- [ ] Spy test: the calibrator never sees outer test rows
- [ ] ECE and macro F1 before/after per fold in `reports/results/07_calibration.csv` (one foreground command per fold); if pooled ECE ≤ 0.05 already, record that and skip recalibration
Notes:

## T-003: Run-by-run error analysis

Status: open
Blocked by:
Slice: A per-run table showing where the model goes wrong and when.
Test seam: `keyframe.evaluate.per_run_errors`
Context: requirements R4; `head -3 reports/results/04_alarms.csv reports/results/00_switch_on_points.csv`
Acceptance:
- [ ] Test on a synthetic prediction table with a known per-run answer
- [ ] `reports/results/07_runs.csv` written for XGBoost
Notes:

## T-007: Shortcut sensitivity without day-dependent channels

Status: open
Blocked by: T-003
Slice: The best model re-scored on held-out loads without day-dependent channels and their derivatives, to show how much AF and CW rely on them.
Test seam: `uv run python -m keyframe.experiments sensitivity --fold <bin>`; `keyframe.features.without_day_channels(columns)`
Context: requirements R4b; `sed -n '/^## Result/,/^## Mismatch/p' reports/physics_check.md`; `grep -n 'def source_channel' -A20 keyframe/explain.py`; `grep -n 'def run_modelling' -A25 keyframe/experiments.py`
Acceptance:
- [ ] Test: `without_day_channels` removes each day-dependent channel and every rolling, residual and physics feature derived from it, and nothing else
- [ ] Four fold outputs (one foreground command each); `reports/results/07_sensitivity.csv` with headline vs no-day-channel metrics per class
Notes:

## T-004: The lockbox, once

Status: open
Blocked by: T-003
Slice: The two-hole injector run is scored once by a model trained on all loads, and the result is stored and guarded.
Test seam: `keyframe.lockbox.evaluate_lockbox`; `uv run python -m keyframe.experiments lockbox`
Context: requirements R5-R6; `grep -n 'LOCKBOX' keyframe/*.py`; `grep -n 'def load_run\|def build_feature_table\|def load_tuned_params' keyframe/*.py`
Acceptance:
- [ ] Tests (without reading the real lockbox): the guard returns the stored result and does not refit when the CSV exists; no module besides `download.py` and `lockbox.py` references the lockbox path
- [ ] Run once; `reports/results/07_lockbox.csv` committed in this ticket's commit
Notes:

## T-005: Notebook 07

Status: open
Blocked by: T-002, T-004, T-007
Slice: Notebook 07 presents the final scores, calibration, errors by run, the lockbox and the full target table.
Test seam: executing `notebooks/07_evaluation.py`
Context: requirements R1, R7; `grep -n '^# %%' notebooks/04_modelling.py`; `head -3 reports/results/07_*.csv`; `sed -n '1,30p' reports/physics_check.md`
Acceptance:
- [ ] `07_confusion.png`, `07_reliability.png`, per-fold figure; final target table with met / not met for every brief target
- [ ] Executes under 5 minutes from cached outputs; committed
Notes:

## T-006: Model card and results lock

Status: open
Blocked by: T-005
Slice: A one-page model card for an engine-maker engineer, and an ADR locking the results.
Test seam: `reports/model_card.md`; the ADR
Context: requirements R8-R9; notebook 07's first cell (`sed -n '1,40p' notebooks/07_evaluation.py`); `sed -n '/^## Dataset/,/^## Goals/p' specs/brief.md`; `grep -n 'CC BY\|zenodo\|arXiv' README.md`
Acceptance:
- [ ] Model card covers every R8 item, 600 to 900 words, cites both dataset works, says it has not been tested on a ship
- [ ] ADR "results locked" with the final numbers
Notes:
