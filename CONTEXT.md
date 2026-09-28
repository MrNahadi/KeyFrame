# Context: shared glossary

Words with a specific meaning in Keyframe. Seeded from `specs/brief.md` section 7. Use these words, with these meanings, in code, notebooks and the demo.

## The engine and the data

| Term | Meaning |
|---|---|
| Engine | Matsui Iron Works MU323DGSC, a three-cylinder marine diesel on a test bench with a water brake |
| Dataset | Marine Engine Fault Dataset v1.0, Zenodo DOI 10.5281/zenodo.19857425, CC BY 4.0 |
| Run | One scenario CSV: one fault at one load (or a load program). 15 runs in total, 14 outside the lockbox |
| Reference file | `Reference_Data.csv`: 25,302 rows of healthy running from 56 to 244 kW, 70-column schema |
| Switch-on (onset) | The first row of a run with `Anomaly State` = 1. Injector runs have no healthy segment, so no switch-on inside the file |
| Pre-fault segment | Rows of a run before switch-on; labelled Normal |
| Channel | One sensor or derived column, keyed by its full variable name |
| Raw voltage channels | `Pl_lo`, `Pl_fuel`, `Pl_water1`, `Pl_water2`, `Pl_loturb`, `Pl_valve`: uncalibrated, used as relative signals |
| Excluded channels | dPf, dPex, engine room temperature and time columns; never model inputs (see tech-stack.md) |

## Classes

| Code | Class | Source |
|---|---|---|
| Normal | Healthy running | Reference file + pre-fault segments |
| AC | Air cooler fouling | `AC_Fouling_*` |
| AF | Air filter clogging (compressor inlet) | `AF_Clogging_*` |
| INJ | Injector nozzle clogging | `Clogged_Injector_Nozzle1_*` (the two-hole run is the lockbox) |
| CW | Cooling water pump cavitation | `CW_Pump_Cavitation_*` |
| TD | Turbine degradation (raised exhaust back pressure) | `Turbine_Degradation_*` |

## Evaluation

| Term | Meaning |
|---|---|
| Load bin | 40, 60, 75 or 85% load from shaft power: cut points 130, 175, 207 kW |
| LOLO | Leave one load out: train on three load bins, test on the fourth, four folds, predictions pooled |
| Held-out load | The load bin a LOLO fold tests on |
| Nested tuning | Hyperparameters chosen by an inner LOLO over the three training loads only |
| Main score | LOLO score where the healthy-engine model never sees the held-out load's reference rows |
| Shop-test score | The same, but the healthy-engine model may see all reference rows; reported separately |
| Lockbox | The two-hole injector run, used once at the very end |
| Macro F1 | F1 averaged over the six classes with equal weight |
| False alarm rate | Share of healthy rows predicted as any fault |
| Sustained alarm | A fault raised only when several consecutive windows agree |
| Detection delay | Median time from switch-on to the first sustained alarm, over runs with a switch-on |
| ECE | Expected calibration error |
| Results log | `reports/results/*.csv`, one file per experiment |

## Features and explanations

| Term | Meaning |
|---|---|
| Healthy-engine model | Regression fitted on healthy rows that predicts each sensor from speed, brake load and fuel flow |
| Residual | Measured reading minus the healthy-engine model's prediction |
| Physics features | Derived quantities such as turbocharger pressure ratio, charge air cooler effectiveness, exhaust temperature spread |
| Sensor group | Air path, fuel system, cooling, lube oil (plus combustion/power); SHAP values are summed per group for the demo |
| Engineering checklist | `reports/engineering_checklist.md`: expected sensor changes per fault, written before any model sees the data |
| Physics check | Comparing each fault's top 5 SHAP features against the engineering checklist |
