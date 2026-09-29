# 08 Explainability: validation

## Automated

1. `uv run pytest` passes, including the group-coverage test (R2), source mapping tests (R1) and the physics-check rule tests with hand-made rankings (R5).
2. Lint, format, typecheck pass.
3. Four SHAP outputs exist; `reports/physics_check.md` exists and states the target as met or not met.
4. Notebook 06 executes from cached outputs in under 5 minutes.

## Manual (owner)

- Do the grouped explanations and the mismatch investigations make sense to a marine engineer?
