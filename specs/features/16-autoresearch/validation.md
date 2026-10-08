# 16 Autoresearch: validation

## Automated

1. `uv run pytest` passes, including `tests/test_autoresearch.py`.
2. Lint, format and typecheck pass.
3. `uv run python -m keyframe.autoresearch score --outer-fold 75` on the baseline candidate prints `macro_f1` ≈ 0.581 (seeds 42, 1, 2: 0.593, 0.580, 0.569).

## Manual (owner)

- Read `trial-fold75.md` and decide whether to run the four searches.
- Check ADR 0013's protocol, especially the 60-experiment budget and the day-robust gate.
