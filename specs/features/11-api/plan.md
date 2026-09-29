# 11 API: plan

Roadmap item 11 (brief milestone 12). Done when one prediction plus explanation comes back in under 300 ms.

## Approach

A small FastAPI app in `api/` that loads the exported `KeyframeModel` once at startup and serves the replay files. Predictions need 15 minutes of history (the rolling features), so `/predict` and `/explain` accept either a window of raw readings or a single steady-state reading for the what-if view, which the API expands into a constant 15-minute window (rolling spread and trend then read as zero, and the response says so). What-if baselines (typical healthy readings per load) are exported as a small JSON so the API never needs the dataset.

## Modules touched

- `api/main.py` (app, routes), `api/schemas.py` (pydantic), `api/service.py` (model loading, window handling)
- `keyframe/experiments.py` or `keyframe/predict.py`: export `models/whatif_baselines.json`
- `tests/test_api.py` (httpx TestClient), latency test
- `specs/tech-stack.md` Feedback commands: how to run the API

## Order of work

T-001 app skeleton with /health and /runs → T-002 /predict → T-003 /explain → T-004 what-if baselines and single-reading mode → T-005 latency.

## New dependencies

None (FastAPI, Uvicorn, pydantic, httpx installed).
