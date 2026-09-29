# 09 Evaluation: validation

## Automated

1. `uv run pytest` passes, including ECE hand-checks (R2) and the lockbox isolation test (R5).
2. Lint, format, typecheck pass.
3. `reports/results/07_lockbox.csv` exists and `git log --format=%h -- reports/results/07_lockbox.csv` shows exactly one commit.
4. `reports/model_card.md` exists; the target table in notebook 07 marks every target met / not met.

## Manual (owner)

- Read the model card as a Wärtsilä engineer would: is anything overclaimed? Are the limits plain?
