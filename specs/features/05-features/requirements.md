# 05 Feature engineering: requirements

## Physics features (stateless)

- R1. `keyframe.features.add_physics_features(df)` returns a copy with these columns added (names prefixed `phys_`), each a documented pure function of one row:
  - turbocharger pressure ratio proxy: `(Charge Air Press. + 1.0332) / 1.0332` (kgf/cm² gauge to absolute ratio against standard atmosphere; documented as a proxy because compressor inlet pressure is not measured)
  - charge air cooler effectiveness `(T14 − T15) / (T14 − T16)`
  - exhaust temperature spread across cylinders 1–3 (max − min) and each cylinder's deviation from the three-cylinder mean
  - turbine temperature drop `T4 − T5`
  - peak pressure spread (max − min of Max. In-Cylinder Press. No.1–3)
  - indicated work spread (max − min of Indicated Work No.1–3)
  - fuel flow per kW (`Fuel Flow / Shaft Power`)
  - exhaust mass flow per unit fuel (`Exh. Gas Mass Flow / Fuel Flow`)
  - each heat exchanger's share of the heat balance (`Loss with cooling water`, `Loss with LO`, `Loss in Charge Air IC`, `Loss with TCH LO`, each divided by `Total Heat Loss in Heat Exchangers`)
  - cooling water temperature rise (mean of T7–T9 minus T6)
- R2. Division by zero or a non-positive denominator gives NaN, never inf. The physics functions currently in `keyframe/eda.py` move to `features.py`; `eda.py` imports them so notebook 01 still runs unchanged.

## Rolling windows (stateless, causal)

- R3. `keyframe.features.add_rolling_features(df, channels, windows_s=(60, 300, 900), stats=("mean", "std", "slope"))` adds, per run, trailing time-based windows over `t` (1, 5 and 15 minutes). A row's window contains only rows of the same run with `t` in `(t − window, t]`. Slope is the least-squares slope against `t` in units per minute. Rows whose window is not yet full (the first `window` seconds of a run) get the value computed on the partial window plus a column `roll_warmup_<window>` that is 1 while the window is filling.
- R4. Rolling features never cross a run boundary and never look forward. Tests prove both on a synthetic two-run table.
- R5. Performance: all rolling features for the full clean table (107,979 rows, the raw sensor channels plus physics features, three windows, three stats) compute in under 2 minutes on 4 cores. Use pandas time-based rolling on a per-run DatetimeIndex (or an equivalent vectorised method), not Python loops over rows.

## Healthy-engine residuals (fitted inside each fold)

- R6. `keyframe.features.HealthyEngineResiduals(inputs=("Engine Speed", "Water Brake Weight", "Fuel Flow"), targets=None, degree=2, alpha=1.0)` is an sklearn transformer. `fit(X, y)` fits, on the rows where `y == "Normal"` only, one polynomial (degree 2) ridge regression per target channel from the inputs, with standardisation inside. `transform(X)` returns X with `resid_<target>` columns added (measured − predicted), keeping the original columns. `targets=None` means every raw sensor channel except the inputs. Polynomial ridge rather than trees because held-out loads at 40% and 85% are the edges of the training range and trees cannot extrapolate; the notebook shows this choice with one comparison.
- R7. Tests: fitting uses only `Normal` rows (a spy or a construction where fault rows would change the fit); a synthetic linear engine gives residuals near zero on healthy rows and the injected offset on fault rows; `get_feature_names_out` works so it composes in a Pipeline.
- R8. Main score: inside `lolo_predict`, the transformer is fitted on the training fold only, so it never sees the held-out load's reference rows (this falls out of R6 plus feature 04's splitter).
- R9. Shop-test score: `lolo_predict(..., extra_healthy=callable)` lets the caller add rows to the training data **for the residual model only**: `extra_healthy(held_out_bin)` returns reference-file rows of the held-out bin, which are passed to the pipeline's `HealthyEngineResiduals` step via a fit parameter, never to the classifier and never scored. A test proves the classifier's training rows are unchanged. Reported separately and always labelled "shop-test".

## Feature sets and ablation

- R10. `keyframe.features.FEATURE_SETS` names the sets used in the ablation, each a function from the clean table (with physics and rolling columns already added) to a column list, plus a flag for whether residuals are added in the pipeline: `raw`, `raw+physics`, `residuals`, `residuals+physics`, `residuals+physics+rolling`, `raw+physics+rolling`. Excluded columns (feature 04 R1) can never appear; a test checks every set.
- R11. Day markers from notebook 01 (`reports/results/01_day_markers.csv` and its recommendation) are handled as the EDA recommended: in residual feature sets the raw temperature day-marker channels are replaced by their residuals. Record this in the notebook.
- R12. The ablation runs as a cached experiment (tech-stack.md "Notebooks", heavy experiments): `uv run python -m keyframe.experiments ablation --feature-set <name> --model <logreg|lightgbm> [--shop-test]`, one invocation per combination, each under 9 minutes. Notebook 03 reads the outputs and presents the ablation: every feature set × {logistic regression, LightGBM} with the notebook 02 settings, LOLO main score, reporting pooled macro F1, per-fold macro F1 (mean ± std), lowest per-class recall and class, false alarm rate. Saved via `log_results` to `reports/results/03_ablation.csv`. Figure `03_ablation.png` shows per-fold spread, not only means.
- R13. Pruning, computed inside training folds only: (a) drop one of any pair of features with |Pearson r| > 0.98 on the training fold's healthy rows; (b) permutation importance of the best set's features on inner LOLO folds of each training set (feature 04 `inner_lolo_folds`), dropping features whose mean importance is ≤ 0. Report which features were dropped in how many folds and the pruned set's LOLO score. Pruning never uses the outer test rows.
- R14. For the best feature set, also report the shop-test score (R9) next to the main score.
- R15. The notebook ends with the decision: which feature set (pruned or not) goes forward to modelling, chosen by pooled macro F1 on the main score with lowest per-class recall and false alarm rate as tie-breakers, recorded in `docs/adr/` (next number) with the numbers. It states plainly which families earned their place and which did not.
