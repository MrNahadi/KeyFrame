# Calibrated track: results

Feature 17, ADR 0014. Run on 8 October 2026 at commit `fa33af1` (inner) and `c15942d` (examination). These results are **separately labelled**. v1's locked numbers (ADR 0009) are unchanged.

## What was tested

The reviewer's suggestion was to compare each reading with the same engine's own known-healthy running. Here each run's first 20 minutes at a load stand in for commissioning data. Every variant is scored on the same rows: rows after the 20-minute baseline, from runs the model has not seen at another load (so the injector run and the healthy reference run are not scored). The model is v1's XGBoost with each fold's nested-tuned parameters. Nothing was tuned for this track.

- `zero_shot`: v1's 833 features (v1 itself, re-scored on these rows).
- `calibrated`: deviations from the baseline, level-free rolling statistics, and speed, brake load and fuel flow.
- `raw+calibrated`: v1's features plus the deviations.

For each fold, the primary calibrated variant was fixed by inner score before any held-out score was computed.

## Inner folds (training loads only, 3 seeds)

| Outer fold | zero_shot | calibrated | raw+calibrated | Batch effect, zero_shot → calibrated |
|---|---:|---:|---:|---:|
| 40 | 0.404 | 0.379 | **0.489** | 0.93 → 0.75 |
| 60 | 0.177 | **0.254** | 0.244 | 0.92 → 0.84 |
| 75 | 0.548 | 0.299 | **0.569** | 0.91 → 0.85 |
| 85 | **0.350** | 0.252 | 0.197 | 0.88 → 0.82 |

Bold marks the best variant per fold. Batch effect: how well healthy rows name their run (balanced accuracy over the training loads).

## Held-out loads (scored once)

| Held-out load | zero_shot | Primary (variant) | calibrated | raw+calibrated |
|---|---:|---:|---:|---:|
| 40% | 0.266 | 0.281 (raw+calibrated) | 0.304 | 0.281 |
| 60% | **0.857** | 0.233 (calibrated) | 0.233 | 0.733 |
| 75% | 0.360 | 0.473 (raw+calibrated) | 0.483 | 0.473 |
| 85% | 0.454 | 0.372 (calibrated) | 0.372 | 0.474 |
| Mean of folds | 0.484 | **0.340** | 0.348 | 0.490 |

All values are macro F1, mean of 3 seeds. Per-seed values, worst-class recall and false alarm rate are in `outer_fold*.json`.

## What it means

1. **Calibration as defined here does not improve the classifier.** The pre-registered primary variant scores 0.340 against zero-shot's 0.484. Adding deviations to v1's features (`raw+calibrated`, 0.490) is a tie within the spread between folds.
2. **It does weaken the session signature, but not enough.** Healthy rows name their run less easily after calibration (about 0.92 → 0.81), but still far above chance. Twenty minutes of baseline at the start of a session does not capture everything that changes between sessions.
3. **Deviations alone lose cavitation.** Cooling water pump cavitation recall is 0 in the `calibrated` variant at 60% and 85% load, where cavitation exists. Its signal appears to sit in absolute pressure and flow levels, which a run-start baseline cancels.
4. **The calibrated track cannot detect the injector fault**, which is present from the first reading of its run. It was excluded by design.
5. **A finding about v1 itself:** at 75% load, v1 (`zero_shot`) predicts a fault for every monitored healthy row of the unseen runs (false alarm rate 1.0 on these rows). v1's locked false alarm rate at 75% (25%) was measured on healthy rows that were about 60% from the reference run, which v1 had trained on at other loads. On healthy stretches of runs it had never seen, v1 at 75% load raises an alarm every time.

## Recommendation

Keep calibration as an *added* input at most (`raw+calibrated`), never a replacement, and do not pursue it further without new data. Two things would test it properly: a baseline recorded on a different day from the fault run (true commissioning data), and runs repeated across days. Neither exists in dataset v1.0.
