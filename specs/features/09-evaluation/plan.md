# 09 Evaluation and model card, results locked: plan

Roadmap item 9 (brief milestone 10, a gate). Done when the model card is written. Scores are not changed after this point.

## Approach

Everything here reads the held-out predictions already produced for the best model (XGBoost, ADR 0007), except two things that need new fits: recalibration (fitted inside the training folds only, if calibration is poor) and the lockbox test (one model trained on every fold's data, applied once to the two-hole injector run). The lockbox is opened by exactly one function, which records its result and refuses to run again. Then the model card summarises data, metrics with spread, limits and intended use, and an ADR records that results are locked.

## Modules touched

- `keyframe/calibration.py` (new): ECE, reliability curve, per-fold recalibration fitted on inner folds
- `keyframe/lockbox.py` (new): the single lockbox evaluation with its run-once guard
- `keyframe/experiments.py`: `calibration` and `lockbox` experiments
- `tests/test_calibration.py`, `tests/test_lockbox.py`
- `notebooks/07_evaluation.py` + executed `.ipynb`; `reports/results/07_*.csv`; `reports/figures/07_*.png`; `reports/model_card.md`; an ADR "results locked"

## Order of work

T-001 calibration metrics → T-002 recalibration experiment → T-003 error analysis by run → T-004 lockbox → T-005 notebook 07 → T-006 model card and lock.

## New dependencies

None.
