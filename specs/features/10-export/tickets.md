# 10 Export: tickets

## T-001: Model bundle

Status: open
Blocked by:
Slice: The all-loads XGBoost model, its feature recipe, alarm settings and metadata saved and restored as one object that predicts and explains from raw readings.
Test seam: `keyframe.predict.KeyframeModel` (`save`, `load`, `features`, `predict_proba`, `explain`)
Context: requirements R1-R2, R4; `grep -n '^def \|^class ' keyframe/lockbox.py keyframe/explain.py`; `grep -n 'def build_feature_table\|def add_rolling_features\|def add_physics_features' keyframe/features.py`
Acceptance:
- [ ] Round-trip test on a small synthetic model: save, load, same probabilities
- [ ] `explain` returns five groups whose SHAP sums plus base value equal the raw margin for the predicted class (additivity, test)
Notes:

## T-002: Reproduction in a clean session

Status: open
Blocked by: T-001
Slice: The real bundle is saved, a reference prediction stored, and a fresh subprocess reproduces it.
Test seam: `tests/test_predict.py::test_clean_session_reproduces_reference`; `uv run python -m keyframe.experiments export`
Context: requirements R1, R3; `grep -n 'def evaluate_lockbox' -A30 keyframe/lockbox.py`
Acceptance:
- [ ] `models/keyframe_xgboost.joblib`, `models/model_meta.json`, `models/reference_prediction.json` written (one foreground command, under 9 minutes)
- [ ] Subprocess test matches to 1e-6 (data-marked; skips if the model file is absent)
Notes:

## T-003: Replay builder from held-out fold models

Status: open
Blocked by: T-001
Slice: One run becomes a replay JSON whose predictions and explanations come from the model that never saw its load.
Test seam: `keyframe.replay.build_replay`
Context: requirements R5, R8; `grep -n 'def run_shap' -A30 keyframe/experiments.py`; `grep -n 'def sustained_alarm' -A10 keyframe/alarm.py`
Acceptance:
- [ ] R8 tests on a synthetic run with a tiny fold model
- [ ] Mixed-bin runs use each row's own fold model (test)
Notes:

## T-004: Export every replay

Status: open
Blocked by: T-002, T-003
Slice: All 18 replay files and the index are written within the size limits.
Test seam: `uv run python -m keyframe.experiments replay [--run <id>]`; the files under `models/replays/`
Context: requirements R6-R7; `uv run python -m keyframe.experiments --help`
Acceptance:
- [ ] 18 files plus `index.json`, each under 2 MB, total under 30 MB (one foreground command per fold model or per run, each under 9 minutes)
- [ ] Index titles in plain words
Notes:

## T-005: Notebook 08

Status: open
Blocked by: T-004
Slice: Notebook 08 shows the export, the reproduction and one replay run.
Test seam: executing `notebooks/08_export.py`
Context: requirements R9; `grep -n '^# %%' notebooks/07_evaluation.py`
Acceptance:
- [ ] Figure `08_replay_example.png`; findings cell with sizes and the reproduction result
- [ ] Executes under 5 minutes from saved files; committed
Notes:
