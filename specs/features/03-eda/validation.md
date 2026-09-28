# 03 EDA: validation

## Automated

1. `uv run pytest` passes, including `tests/test_eda.py` and the check that the pre-registered part of `reports/engineering_checklist.md` is unchanged.
2. Lint, format and typecheck pass.
3. `uv run jupytext --set-kernel python3 --to ipynb --execute notebooks/01_eda.py` runs without error and writes the figures and tables listed in R7–R12.
4. `grep -c 'Targets final as of' reports/targets.md` is 1.
5. No file under `notebooks/` or `keyframe/` fits a model to labels in this feature (`grep -nE '\.fit\(' keyframe/eda.py notebooks/01_eda.py` is empty).

## Manual (owner)

- Read the Observed section of the engineering checklist: do the agreements and surprises make engineering sense?
- Read `reports/targets.md`: is the revision decision (if any) justified by EDA evidence alone?
