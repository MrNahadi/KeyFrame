# 08 Explainability: requirements

## Mapping features back to the engine

- R1. `keyframe.explain.source_channel(feature)` maps any model feature to the measured channel(s) it comes from: a raw channel to itself; `<channel>_roll_*` to `<channel>`; `resid_<channel>` to `<channel>`; `phys_*` to the channels its formula uses (documented table in the module, e.g. `phys_turbine_temp_drop` → Exh.Gas Temp. Turbine In and Out); `roll_warmup_*` to "window warm-up" (not a sensor).
- R2. `keyframe.explain.SENSOR_GROUPS` assigns every measured channel to one group: air path (charge air pressure and temperatures, turbocharger, exhaust gas mass flow, pressure ratio), combustion and power (in-cylinder pressures, exhaust temperatures per cylinder, indicated/effective work, torque, shaft power, efficiencies, engine speed, brake load), fuel system (fuel flow and temperatures, fuel transfer pump, injector cooling oil), cooling (cooling water temperatures, flows, pressures, heat rejection to water), lube oil (LO temperatures, pressures, heat rejection to LO). A test asserts every sensor channel in the feature table has exactly one group. Physics features take the group of their formula's main subject (listed explicitly).

## SHAP

- R3. The best model is XGBoost (ADR 0007) on `raw+physics+rolling` (ADR 0006), built with `keyframe.tuning.MODEL_BUILDERS["xgboost"](params)`; it is `keyframe.tuning._BalancedXGBClassifier`, whose fitted booster is `.model_` and whose class order is `.classes_` (string labels). Use `shap.TreeExplainer(model.model_)`, and map SHAP's per-class outputs to `classes_`. Experiment `uv run python -m keyframe.experiments shap --fold <bin>` refits the best model on that fold's training rows (tuned params from `models/tuning/`, same pipeline as feature 06), then computes SHAP TreeExplainer values on a seeded, label-stratified sample of up to 3,000 held-out rows, plus every held-out row within ±10 minutes of each switch-on in that fold (for the per-moment views). Writes values, base values, predictions and row metadata to `data/processed/experiments/shap_fold<bin>.parquet` (or `.npz` plus parquet metadata if more efficient). Under 9 minutes per fold.
- R4. Views (functions in `keyframe.explain`, used by the notebook): per-class mean |SHAP| ranking of features and of source channels; grouped SHAP per class (sum of SHAP within each sensor group); a waterfall for one moment, grouped, with the top individual features listed.

## Physics check

- R5. `keyframe.explain.physics_check(shap_rank_by_class, checklist)` applies the rule in `reports/targets.md` exactly: for each fault class, take the top 5 features by mean |SHAP| on held-out rows of that class, map each to its source channel(s), and count a match when a feature's source is among the checklist's "Expected top 5" for that fault or a channel marked "Agree" in its Observed table. A fault passes with at least 3 of 5 matches and none of the top 5 sourced from a day-dependent channel (LO Cooling Water Temp. In, Fuel Temp., Fuel Oil Temp. Flow meter In, Sea Cooling Water Press.). The checklist's expected lists are parsed from `reports/engineering_checklist.md` or transcribed into a tested constant with a test that checks it against the file.
- R6. `reports/physics_check.md` lists, per fault: the top 5 features, their source channels, match yes/no with the checklist line, pass/fail, and for every mismatch an investigation: is it a physically plausible mechanism the checklist missed (say which), a correlated proxy of an expected channel, or a shortcut such as test-day recognition? The brief target is 4 of 5 faults passing; say met or not met.

## Cross-checks

- R7. Grouped permutation importance of the best model on held-out rows per fold (reuse `keyframe.features.inner_permutation_importance`'s grouping idea, but here on outer test rows, which is allowed because nothing is being selected), compared with the SHAP ranking (rank correlation per fold).
- R8. Partial dependence and ICE (sklearn `PartialDependenceDisplay`) for the top 2 features of three faults, on one fold, saved as figures.
- R9. One LIME comparison (lime `LimeTabularExplainer`) for 3 moments (one per of three different faults): LIME's top features against SHAP's for the same rows, with a sentence on agreement. LIME is used once, only here.

## Notebook 06

- R10. Notebook 06 presents: per-class SHAP beeswarm for the top 15 features (`06_beeswarm_<CLASS>.png`), grouped SHAP per class (`06_grouped_shap.png`), a grouped waterfall for one moment of each fault shortly after its switch-on (`06_waterfall_<FAULT>.png`), the physics check table, the cross-checks, and opens with findings. It says plainly where explanations are unreliable because correlated sensors share credit.
