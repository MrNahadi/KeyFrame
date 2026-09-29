# 10 Export: validation

## Automated

1. `uv run pytest` passes, including the fresh-subprocess reproduction test (R3) and replay tests (R8).
2. Lint, format, typecheck pass.
3. `ls -la models/ models/replays/` shows the bundle, meta, reference prediction, 18 replay files and index, within the size limits.

## Manual (owner)

- Open one replay JSON: can you tell from `provenance` that its predictions are from a held-out load?
