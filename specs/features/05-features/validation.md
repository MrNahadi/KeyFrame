# 05 Feature engineering: validation

## Automated

1. `uv run pytest` passes, including causality and run-boundary tests for rolling features (R4), the Normal-only fit test for residuals (R7), the shop-test isolation test (R9) and the exclusion test for every feature set (R10).
2. Lint, format, typecheck pass.
3. `uv run jupytext --set-kernel python3 --to ipynb --execute notebooks/03_feature_engineering.py` runs and writes `reports/results/03_ablation.csv`.
4. Notebook 01 still executes (physics functions moved).

## Manual (owner)

- Does the ablation table show clearly which feature families earn their place, with fold spread?
- Is the gap between the main score and the shop-test score plausible?
