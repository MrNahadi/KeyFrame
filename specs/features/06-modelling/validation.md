# 06 Modelling and tuning: validation

## Automated

1. `uv run pytest` passes, including the alarm causality and run-boundary tests and the tuning isolation test.
2. Lint, format, typecheck pass.
3. `models/tuning/` has one JSON per model per outer fold; `reports/results/04_models.csv` and `04_best_model.csv` exist.
4. `uv run jupytext --set-kernel python3 --to ipynb --execute notebooks/04_modelling.py` runs in under 5 minutes from cached outputs.

## Manual (owner)

- Is the comparison against the brief's targets honest (met / not met)?
- Do the detection delays per run make engineering sense (AF, the gradual fault, slowest)?
