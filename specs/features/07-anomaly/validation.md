# 07 Anomaly detection: validation

## Automated

1. `uv run pytest` passes, including the healthy-only fit spy test (R3).
2. Lint, format, typecheck pass.
3. 12 score files exist (3 detectors × 4 folds); `reports/results/05_anomaly.csv` logged.
4. Notebook 05 executes from cached outputs in under 5 minutes.

## Manual (owner)

- Are the per-fault AUROCs and delays plausible from an engineering view (e.g. gradual AF slowest)?
