# 04 Splits and baselines: validation

## Automated

1. `uv run pytest` passes, including the split tests (R6) and the exclusion test (R2).
2. Lint, format and typecheck pass.
3. `uv run jupytext --set-kernel python3 --to ipynb --execute notebooks/02_baselines.py` runs and writes `reports/results/02_baselines.csv`.
4. `grep -rnE 'train_test_split|KFold|ShuffleSplit|StratifiedKFold' keyframe notebooks` finds nothing (no random row splits).

## Manual (owner)

- Is the best raw-sensor macro F1 near 0.52, and is any difference explained?
