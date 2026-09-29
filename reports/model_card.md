# Model card: Keyframe engine fault classifier

Results locked 29 September 2026 (ADR 0009).

## Model details

XGBoost classifier on 833 features built from 2-second marine diesel sensor logs: the raw channels, physics-derived quantities (for example pressure ratios and temperature differences across the air cooler and turbine) and rolling-window statistics (mean, spread and trend over recent minutes). It predicts one of six states: Normal, air cooler fouling (AC), air filter clogging (AF), injector nozzle clogging (INJ), cooling water pump cavitation (CW) and turbine degradation (TD). Hyperparameters were tuned inside each training fold.

## Intended use

A showcase of fault diagnosis on bench data. It is not an onboard tool and must not be used to make operating or maintenance decisions.

## Data

Marine Engine Fault Dataset v1.0, a Matsui Iron Works MU323DGSC diesel on a test bench, CC BY 4.0. Please cite both works:

- BahooToroody, A., Bondarenko, O., Abaei, M. M., Niki, Y., & Zio, E. (2026). Marine Engine Fault Dataset (Version 1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.19857425
- BahooToroody, A., Bondarenko, O., Abaei, M. M., Niki, Y., & Zio, E. (2026). Marine Engine Fault Dataset: Open-Access Data under Controlled Reference and Fault Scenario Conditions. Preprint, arXiv:2607.19444.

Left out: the compressor filter loss and turbine back pressure settings (the researchers set them to create two faults, and they are empty in 5 of 15 runs), engine room temperature (drifts with the day) and time columns.

## Evaluation protocol

Leave one load out (40, 60, 75, 85%), with nested tuning inside the training loads. A lockbox of unseen injector severity was scored once, after all choices were fixed.

## Results

Pooled over the four held-out loads: macro F1 0.717 (target 0.80), false alarm rate 12.2% (target 5%), lowest per-class recall 0.194, TD (target 0.70). Macro F1 per held-out load: 0.547 (40%), 0.860 (60%), 0.701 (75%), 0.609 (85%), so the spread is wide. The confusion matrix shows the errors concentrated in a few runs: AF at 75% and 85% load is only about 20% correct, and TD at 40, 60 and 85% about 50%. The sustained alarm fires on 6 of 13 fault runs, with a median delay of 563 s among those. On the lockbox all 6,791 rows were labelled INJ, which meets the 90% target, but only INJ was ever predicted there, so this is weak evidence. Only that target is met.

## Calibration

Confidence is unreliable: pooled expected calibration error is 0.176 (target 0.05). Temperature scaling fitted inside the training folds made it worse in loads 40, 60 and 75 and better only at 85 (0.499 to 0.418). It leaves predicted classes unchanged.

## Explainability

Grouped SHAP values agree with the physics: INJ leans on combustion and power channels, CW on cooling, AC on the air path. AF also leans mostly on cooling, which is less obviously causal. Window warm-up features carry almost no weight.

## Limits

- Bench, not ship. **This model has not been tested on a ship.**
- One small engine at steady loads, 15 fault runs in total; TD and CW are thin (3 and 2 runs).
- AF and CW results are partly explained by test-day channels. Without the 40 day-dependent features, macro F1 moves from 0.547 to 0.635 (40%), 0.860 to 0.725 (60%), 0.701 to 0.611 (75%) and 0.609 to 0.347 (85%). CW recall at 60% falls from 0.956 to 0.0, so part of the headline score identifies the day, not the fault.
- Healthy segments show warm-up drift that can look like a fault.
- Anomaly detectors trained on healthy data are near chance (fault detection AUROC 0.528, target 0.95).
- Alarm detects 6 of 13 fault runs; the other 7 never raise one.
