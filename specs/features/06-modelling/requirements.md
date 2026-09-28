# 06 Modelling and tuning: requirements

## Candidate models

- R1. Four candidates on the feature set chosen in feature 05 (ADR 0006: `raw+physics+rolling`, unpruned, 833 columns): LightGBM, XGBoost, random forest and logistic regression, each with class weights for the imbalance (`class_weight="balanced"` or per-row `sample_weight` for XGBoost), seed `keyframe.SEED`. Build every candidate with `keyframe.features.build_pipeline(<chosen set>, model)`, so residual steps are refitted per fold. Models that cannot take NaN (logistic regression, random forest) get the per-fold median imputer used in `keyframe.experiments.MODEL_FACTORIES`; reuse those factories rather than redefining models. Load data with `keyframe.experiments.load_feature_table()`.

## Nested tuning

- R2. `keyframe.tuning.SEARCH_SPACES` defines a small, sensible Optuna space per model (e.g. LightGBM: num_leaves, learning_rate, n_estimators, min_child_samples, feature_fraction, reg_lambda; XGBoost: max_depth, learning_rate, n_estimators, subsample, colsample_bytree, reg_lambda; random forest: max_depth, min_samples_leaf, max_features, max_samples; logistic regression: C, penalty l2).
- R3. `keyframe.tuning.tune(model_name, train_df, features, n_trials, timeout_s)` runs an Optuna study (TPE sampler seeded with `SEED`) whose objective is pooled macro F1 over `inner_lolo_folds(train_df)`. It never receives outer test rows. To afford enough trials, trials fit and score on every 4th row of each run (`keyframe.tuning.thin(df, step=4)`, keeping rows in time order within each run; consecutive readings 1–2 s apart are near-duplicates, so little information is lost). The final refit in R5 uses every row. The notebook states this. Returns the best params and the study's trial table.
- R4. Experiment `uv run python -m keyframe.experiments tuning --model <m> --outer-fold <bin> [--n-trials N] [--timeout-s S]` tunes one model for one outer fold, writing `models/tuning/<m>_fold<bin>.json` (best params, best inner score, number of trials, git commit). Each invocation must finish under 9 minutes; `--timeout-s` defaults to 420. For scale: one LightGBM fit on the full 833-column feature table takes about 15 s per outer fold, so an inner-LOLO trial costs roughly 30–45 s; aim for at least 10 trials per invocation and shrink the search space's `n_estimators` range if needed.
- R5. Experiment `modelling --model <m>` refits each outer fold with that fold's tuned params on the outer training rows and predicts the outer test rows, writing `data/processed/experiments/modelling_<m>.parquet` (feature 04's `lolo_predict` format with probabilities) and a summary via `log_results` to `reports/results/04_models.csv`.
- R6. Tests: a spy proves `tune` sees only training rows; tuned params round-trip through JSON; the modelling experiment on a tiny synthetic table produces predictions for every row exactly once.

## Alarm logic

- R7. `keyframe.alarm.sustained_alarm(predictions, min_duration_s, min_probability)` works per run in time order: a fault alarm for class c is active at a row when every prediction over the trailing `min_duration_s` seconds of that run is c with probability ≥ `min_probability`. Output: `alarm` column (`Normal` or the fault class). Causal only; never crosses runs.
- R8. `keyframe.alarm.detection_delay(alarms, switch_on)` returns, per run with a switch-on, the time from switch-on to the first alarm of any fault class that starts at or after switch-on and the class it named; NaN if never raised. Alarms raised before switch-on are false alarms and counted separately.
- R9. Alarm-level metrics: false alarm rate (share of healthy rows under an active alarm), median detection delay over runs, share of runs detected, correct-class share of first alarms.
- R10. Alarm parameters are chosen from a small grid (`min_duration_s` in {30, 60, 120, 300}; `min_probability` in {0.5, 0.6, 0.7, 0.8}) inside the inner folds for each outer fold, by lowest median detection delay subject to an inner false alarm rate ≤ 5% (fall back to the lowest false alarm rate if none qualifies). The outer test rows never choose the parameters.

## Notebook 04 and the decision

- R11. Notebook 04 presents: model comparison (pooled macro F1, per-fold mean ± std and each fold, lowest per-class recall and class, false alarm rate, accuracy) at the row level; the tuned params per fold; the pooled confusion matrix of the best model (`04_confusion_best.png`); per-fold scores figure (`04_fold_scores.png`); the alarm-level results (detection delay per run, `04_detection_delay.png`); and scores with and without the first 10 minutes after each switch-on (brief risk "Gradual faults").
- R12. Every row-level and alarm-level number is compared with the brief's targets in one table, marked met / not met, with no rounding in the model's favour.
- R13. The best model is chosen by pooled macro F1 (main score), tie-broken by lowest per-class recall then false alarm rate, and recorded with its settings in `reports/results/04_best_model.csv` and an ADR. The notebook opens with the findings.
