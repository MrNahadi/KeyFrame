# 10 Export: requirements

## The deployable model

- R1. `keyframe.predict.KeyframeModel` bundles: the fitted XGBoost model (all loads, the lockbox fit's settings: median of per-fold tuned params, see `keyframe.lockbox`), the ordered feature column list, class labels, the feature-building settings (rolling windows and stats, physics feature list), the alarm settings (median of the per-fold chosen `min_duration_s` and `min_probability` from `reports/results/04_alarms.csv` for XGBoost), the sensor-group map, library versions and the git commit. `save(dir)` writes `models/keyframe_xgboost.joblib` and a human-readable `models/model_meta.json`; `load(dir)` restores it and warns if library versions differ.
- R2. `KeyframeModel.features(run_df)` turns raw readings of one run (clean-table columns, time in `t`) into the model's feature frame with the exact functions used in training (`add_physics_features`, `add_rolling_features`, causal, per run). `predict_proba(run_df)` returns class probabilities per row; `explain(run_df, row)` returns grouped SHAP (per sensor group, for the predicted class and all classes), the top 8 features with values and SHAP, and the base value, using `shap.TreeExplainer` on the booster (created at load time, not pickled).
- R3. `models/reference_prediction.json` stores one fixed input window (the raw rows of a real run needed for the rolling features up to a chosen moment, e.g. 15 minutes of an AC run after switch-on) and the expected probabilities for its last row. A test starts a fresh Python subprocess (`uv run python -c ...`), loads the model from disk, recomputes, and matches the stored probabilities to 1e-6. This is the milestone's "done when".
- R4. Model file size under 50 MB; if larger, say why in the notebook.

## Replay files (held-out behaviour)

- R5. `keyframe.replay.build_replay(run, fold_model)` produces JSON for one run: run id, fault, nominal load, switch-on time (or null), sampling note, and a list of frames thinned to one every 10 s of `t` (keep the switch-on frame exactly). Each frame: `t` (s from run start), 8 key sensor readings (charge air pressure, charge air temp after cooler, turbine in and out temperatures, exhaust temperature spread, cooling water flow, fresh cooling water pressure, fuel flow) with units, probabilities for all six classes, the sustained-alarm state computed with the exported alarm settings, and grouped SHAP for the predicted class (five groups) plus the top 3 features. Top-level `provenance`: "predictions from the model trained without this run's load (leave-one-load-out fold <bin>)" plus git commit.
- R6. Runs exported: every fixed-load fault run (13), the one-hole injector run, and one reference segment per load bin (30 minutes each, labelled Normal). The lockbox run is not exported. For the stepped injector run and the reference file, each row uses the fold model of its own load bin.
- R7. Each replay file under 2 MB; total under 30 MB; written to `models/replays/<run>.json` plus `models/replays/index.json` (id, title in plain words such as "Turbine degradation at 85% load", duration, switch-on, alarm delay).
- R8. Tests: frames are in time order, include the switch-on frame, probabilities sum to 1, grouped SHAP has five groups, and the provenance names the fold whose load was held out.

## Notebook 08

- R9. `notebooks/08_export.py` builds and saves the model bundle, writes the reference prediction, reproduces it in a subprocess, builds the replay files (reading the experiment outputs if heavy), and shows one replay run as a figure (traces, probabilities, alarm) to prove the files carry what the demo needs. Opens with findings (file sizes, reproduction result).
