# 11 API: tickets

## T-001: App skeleton, health and runs

Status: open
Blocked by:
Slice: The API starts, reports its model, and serves the replay index and files.
Test seam: `GET /health`, `GET /runs`, `GET /runs/{run_id}` via `fastapi.testclient.TestClient`
Context: requirements R1-R3, R8; `ls models/ models/replays/ | head`; `grep -n 'def load\|class KeyframeModel' keyframe/predict.py`
Acceptance:
- [ ] Tests: health with and without model files (tmp dir); runs index; known and unknown run ids; path traversal rejected
Notes:

## T-002: Predict from a window

Status: open
Blocked by: T-001
Slice: A window of raw readings returns probabilities, predicted class and alarm state for its last row.
Test seam: `POST /predict` with `rows`
Context: requirements R4-R5; `grep -n 'def features\|def predict_proba' -A15 keyframe/predict.py`
Acceptance:
- [ ] Test with a real 15-minute window from the clean table (data-marked) matches `KeyframeModel.predict_proba` for the last row
- [ ] Missing channels → 422 listing them; excluded channels ignored
Notes:

## T-003: Explain

Status: open
Blocked by: T-002
Slice: The same input returns grouped SHAP, top features and base value.
Test seam: `POST /explain`
Context: requirements R6; `grep -n 'def explain' -A30 keyframe/predict.py`
Acceptance:
- [ ] Additivity test within 1e-4; five groups; top 8 features with source channel and group
Notes:

## T-004: What-if baselines and steady-state mode

Status: open
Blocked by: T-002
Slice: The what-if view can fetch typical healthy readings per load and ask for a prediction from a single reading.
Test seam: `GET /whatif/baselines`; `POST /predict` with `reading`
Context: requirements R4, R7; `grep -n 'def run_export\|add_parser' keyframe/experiments.py`
Acceptance:
- [ ] `models/whatif_baselines.json` exported (one command) and served
- [ ] Data-marked test: the steady-state prediction for each load's baseline reading returns a well-formed response with the steady-state warning; the predicted class per load is written to `reports/results/11_whatif_baselines.csv` (a baseline predicted as a fault is reported, not hidden)
Notes:

## T-005: Latency under 300 ms

Status: open
Blocked by: T-003, T-004
Slice: Predict and explain each answer in under 300 ms, measured and recorded.
Test seam: `tests/test_api_latency.py`
Context: requirements R9; `grep -n 'def features' -A25 keyframe/predict.py`
Acceptance:
- [ ] Median of 10 calls under 300 ms for `/predict` and `/explain`; `reports/results/11_latency.csv` written
- [ ] `specs/tech-stack.md` Feedback commands mention how to run the API (edit only that table row)
Notes:
