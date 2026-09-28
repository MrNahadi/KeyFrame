# 04 Splits and baselines: plan

Roadmap item 4 (brief milestone 5). Done when the split tests pass and the raw-sensor baseline reproduces a macro F1 near 0.52.

## Approach

Put the validation protocol into code before any model is scored: the model-input column list (with the exclusions enforced by a test), the leave-one-load-out splitter and its nested inner loop, the metrics the brief reports, and a results log. Then score four baselines on raw sensors in notebook 02.

## Modules touched

- `keyframe/features.py` (new): `EXCLUDED_COLUMNS`, `raw_sensor_columns()`
- `keyframe/splits.py`: `lolo_folds()`, `inner_lolo_folds()` (next to `load_bin()`)
- `keyframe/evaluate.py` (new): metrics, LOLO cross-validated predictions, results log
- `tests/test_features.py`, `tests/test_splits.py`, `tests/test_evaluate.py`
- `notebooks/02_baselines.py` + executed `.ipynb`; `reports/results/02_*.csv`; `reports/figures/02_*.png`

## Order of work

T-001 input columns → T-002 splitter → T-003 metrics and results log → T-004 LOLO predictions → T-005 notebook 02 → T-006 findings.

## New dependencies

None.
