# 06 Modelling and tuning: plan

Roadmap item 6 (brief milestone 7). Done when the best model and its settings are recorded in the results log.

## Approach

Take the feature set chosen in feature 05 (its ADR) as fixed. Tune each candidate model with Optuna inside the nested loop: for every outer held-out load, trials are scored only on inner leave-one-load-out folds of the three training loads. Refit with the chosen settings on the outer training set and predict the held-out load. Then add sustained-alarm logic, whose parameters are also chosen inside the inner folds, and measure detection delay. Everything heavy runs as cached experiments (tech-stack.md "Notebooks").

## Modules touched

- `keyframe/alarm.py` (new): sustained alarms, detection delay, alarm-level false alarm rate
- `keyframe/tuning.py` (new): search spaces and the nested Optuna objective
- `keyframe/experiments.py`: `tuning`, `modelling` and `alarm` experiments
- `tests/test_alarm.py`, `tests/test_tuning.py`
- `notebooks/04_modelling.py` + executed `.ipynb`; `reports/results/04_*.csv`; `reports/figures/04_*.png`; `models/tuning/*.json`; an ADR

## Order of work

T-001 alarm logic → T-002 tuning module → T-003 tuning and modelling experiments → T-004 run all models → T-005 nested alarm selection → T-006 notebook → T-007 findings and decision.

## New dependencies

None (Optuna, LightGBM, XGBoost installed).
