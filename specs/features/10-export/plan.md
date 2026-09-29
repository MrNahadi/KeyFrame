# 10 Export: plan

Roadmap item 10 (brief milestone 11). Done when a clean Python session loads the files and reproduces a prediction.

## Approach

Two kinds of output, kept apart on purpose:

1. **The deployable model** for the API and the what-if view: XGBoost retrained on every load (the same fit the lockbox used), saved with everything needed to turn raw readings into features, a prediction and a grouped explanation.
2. **Replay files** for the demo: real runs with sensor traces, class probabilities, alarm state and grouped SHAP per moment. These come from the leave-one-load-out fold model that never saw that run's load, so the demo shows held-out behaviour, not in-sample fits. Each replay file says so.

Scores are locked (feature 09); nothing here is tuned.

## Modules touched

- `keyframe/predict.py` (new): `KeyframeModel` (save, load, features from raw readings, predict, explain)
- `keyframe/replay.py` (new): building replay JSON for a run from held-out fold models
- `keyframe/experiments.py`: `export` and `replay` experiments
- `tests/test_predict.py`, `tests/test_replay.py`
- `notebooks/08_export.py` + executed `.ipynb`; `models/keyframe_xgboost.joblib`, `models/model_meta.json`, `models/replays/*.json`, `models/reference_prediction.json`

## Order of work

T-001 model bundle → T-002 clean-session reproduction → T-003 replay builder → T-004 export all replays → T-005 notebook 08.

## New dependencies

None.
