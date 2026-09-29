# 11 API: validation

## Automated

1. `uv run pytest` passes, including API tests (TestClient) and the latency test.
2. Lint, format, typecheck pass (mypy covers `api`).
3. `uv run uvicorn api.main:app --port 8000` starts; `curl localhost:8000/health` shows `model_loaded: true`.

## Manual (owner)

- `curl localhost:8000/runs` lists runs with plain titles.
