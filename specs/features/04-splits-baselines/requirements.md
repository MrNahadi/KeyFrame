# 04 Splits and baselines: requirements

## Model inputs

- R1. `keyframe.features.EXCLUDED_COLUMNS` is the single list of columns that are never model inputs: `Compressor Filter Loss`, `Turbine Back Pressure`, `Engine room Temp.`, `Time`, `Time_abs`, `Time_rel`, `Anomaly State`, and the metadata columns (`run`, `fault_type`, `label`, `t`, `load_bin`, `nominal_load`).
- R2. `keyframe.features.raw_sensor_columns(df)` returns every numeric column of the clean table not in `EXCLUDED_COLUMNS`, in table order. A test asserts no excluded column is ever returned and that the result is non-empty on the real table.
- R3. If notebook 01 (roadmap item 3) named day-marker channels with a recommendation to drop them, `raw_sensor_columns` does **not** apply that here: baselines use raw sensors as the brief's first check did. The day-marker decision is applied in feature engineering (item 5).

## Splits

- R4. `keyframe.splits.lolo_folds(df)` yields one fold per load bin present (40, 60, 75, 85) as `(held_out_bin, train_index, test_index)`, using each row's `load_bin`. The test set is every row in the held-out bin; the train set is every other row. A stepped run (the injector run, the reference file) contributes rows to several folds according to each row's bin.
- R5. `keyframe.splits.inner_lolo_folds(train_df)` does the same over the load bins present in a training set, for nested tuning. It never sees the outer test rows.
- R6. Tests: no fold's train and test sets share a load bin or a row; the union of test sets is the whole table exactly once; inner folds of an outer fold never contain the outer held-out bin.

## Metrics and results log

- R7. `keyframe.evaluate` provides, from true and predicted labels: macro F1 over the classes present in `y_true`; per-class recall; false alarm rate (share of true Normal rows predicted as any fault); confusion matrix with a fixed class order `Normal, AC, AF, INJ, CW, TD`; accuracy (reported, not a target).
- R8. `keyframe.evaluate.lolo_predict(model_factory, df, features)` fits a fresh model per LOLO fold (from `model_factory()`, an unfitted sklearn estimator or pipeline) on the train rows and predicts the test rows. It returns a DataFrame with the original index, `run`, `load_bin`, `fold`, `y_true`, `y_pred` and, when the model supports it, one probability column per class.
- R9. `keyframe.evaluate.summarise(predictions)` returns the headline metrics pooled over all folds plus one row per fold (scores per fold cover only the classes present in that fold), so spread across folds is always reported next to the pooled number.
- R10. `keyframe.evaluate.log_results(name, table)` writes `reports/results/<name>.csv`, adding columns `experiment`, `date` and `git_commit` (short hash).

## Notebook 02

- R11. Baselines on raw sensors: majority-class dummy, logistic regression (standardised, `class_weight="balanced"`, max_iter high enough to converge), random forest (`class_weight="balanced"`, 300 trees), and gradient boosting (LightGBM with default settings plus `class_weight="balanced"`). Seeds from `keyframe.SEED`. Scalers live inside the pipeline so they are fitted per fold.
- R12. Report for each: pooled macro F1, per-fold macro F1 (mean ± std and each fold), lowest per-class recall and which class, false alarm rate, accuracy. Save `reports/results/02_baselines.csv` via R10 and the per-row predictions of the best baseline to `data/processed/02_best_baseline_predictions.parquet`.
- R13. Figures: per-fold macro F1 per model (`02_fold_scores.png`) and the pooled confusion matrix of the best baseline (`02_confusion_best.png`), with rows normalised to recall.
- R14. A findings section compares the result with the brief's first-check baseline (0.52 raw sensors, turbine degradation recall 0.00, false alarm rate 29.8%). If the numbers differ materially, say so and give the likely reason; never tune to match.
