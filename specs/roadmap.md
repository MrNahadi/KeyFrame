# Roadmap

Each item is one feature, one branch (`feature/NN-slug`), one folder in `specs/features/`. Items follow the brief's milestones; the brief's milestone numbers are in brackets. Results lock at item 9, before any front-end work.

- [x] 1. **Scaffold** [M1]: pinned environment, `keyframe` package, one-command data download with checksum, lockbox set aside, lint/type/test commands passing, CI.
- [x] 2. **Data audit** [M2]: notebook 00 loads all 16 files into one clean table; units, gaps, missing channels and every fault switch-on point documented; row counts match the dataset index.
- [x] 3. **EDA, engineering checklist and targets review** [M3, M4 gate]: notebook 01 compares each fault with healthy running at matched load, looks into the cavitation and injector puzzles, commits `reports/engineering_checklist.md` before any model, and records the one allowed target revision (or "no change") in `reports/targets.md`.
- [ ] 4. **Splits and baselines** [M5]: leave-one-load-out splits with tests that no split mixes loads; notebook 02 scores dummy, logistic regression, random forest and gradient boosting on raw sensors, reproducing a macro F1 near 0.52.
- [ ] 5. **Feature engineering** [M6]: healthy-engine residuals, physics features and time-based rolling windows, each tested on its own; notebook 03 ablation table.
- [ ] 6. **Modelling and tuning** [M7]: notebook 04 compares LightGBM/XGBoost, random forest and logistic regression with nested Optuna tuning and class weights, plus sustained-alarm logic; best model recorded in the results log.
- [ ] 7. **Anomaly detection** [M8]: notebook 05 trains healthy-only detectors (Isolation Forest, PCA + Hotelling T², small autoencoder); AUROC and detection delay measured.
- [ ] 8. **Explainability** [M9]: notebook 06 with SHAP per class, per moment and per sensor group, permutation importance, PDP/ICE, one LIME comparison, and the physics check against the checklist.
- [ ] 9. **Evaluation and model card, results locked** [M10 gate]: notebook 07 with final held-out-load scores and spread, confusion matrix, calibration, run-by-run error analysis, the lockbox test and `reports/model_card.md`.
- [ ] 10. **Export** [M11]: notebook 08 retrains on all loads, saves model, preprocessing and explainer, and cuts replay files; a clean session reproduces a prediction.
- [ ] 11. **API** [M12]: FastAPI `/predict`, `/explain`, `/runs`; one prediction plus explanation in under 300 ms.
- [ ] 12. **Web demo: replay** [M13, part 1]: framework chosen (ADR), app scaffold following the design manifesto, replay view with traces, probabilities, alarm and delay.
- [ ] 13. **Web demo: explain, what-if and model card** [M13, part 2]: grouped SHAP waterfall on pause, what-if sliders, model card page.
- [ ] 14. **Write-up** [M14]: README with results, figures, dataset citation and reproduction steps; drafts of the LinkedIn post and the Marine AIMS README link for the owner to publish.
