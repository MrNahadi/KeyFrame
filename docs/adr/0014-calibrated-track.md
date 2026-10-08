# 0014. Calibrated track: deviations from each run's own known-healthy baseline

Status: accepted
Decided-by: agent, under the owner's standing brief of 8 Oct 2026 ("improve the baselines and the specs of this model ... do whatever you want, just don't delete"), following G. W. M. Maina's review (ADR 0013, amendment 1)
Question: Every run can be recognised from its healthy readings alone (batch effect). Does comparing each reading with the same engine's own known-healthy running remove the session signature and expose the fault, and how should it be evaluated without fitting the held-out loads?

Decision:
1. **Protocol.** A calibrated system has a known-healthy recording for each operating point it monitors, such as commissioning data or a run after an overhaul. Here, each run's first 20 minutes at a given load (`BASELINE_S` = 1200) play that role. Every fault run switches on at least 28 minutes in, so the baseline never contains the fault. `cal_<x>` is the reading (or a rolling mean of it) minus its mean over that window. Rows are monitored only after the window is complete.
2. **Segments without a healthy baseline are left out**: the injector run (faulty from its first reading) and load segments shorter than 20 minutes. A calibrated system cannot detect a fault already present when it was calibrated, and the write-up says so. Labels decide only which segments have a healthy baseline, never a feature value.
3. **Three variants are scored on the same rows** (monitored rows of runs unseen in training):
   - `zero_shot`: v1's feature set.
   - `calibrated`: deviations, level-free rolling statistics (std, slope) and the operating point (speed, brake load, fuel flow).
   - `raw+calibrated`: v1's set plus the deviations.

   The model for every variant is v1's XGBoost with that fold's nested-tuned parameters. Nothing is tuned for this track, so any difference comes from the features.
4. **Nested, as in ADR 0013.** `inner --outer-fold K` scores the variants on the inner folds of K's training loads (3 seeds), together with the batch-effect test on their columns. Before any held-out score is seen, each fold's primary calibrated variant is the better of the two calibrated ones on inner score. `examine --outer-fold K` scores load K once, records every variant and the pre-chosen primary, and refuses a second run.
5. **Separately labelled.** The calibrated result is reported next to the zero-shot v1 and v2 results, never in place of them, so a reader can see how much comes from calibration rather than generalisation (the reviewer's request).

Basis: the reviewer's recommendation to report zero-shot and calibrated results side by side; the batch-effect measurement in ADR 0013 amendment 1; the pre-fault healthy stretch is at least 28 minutes in every fixed-load fault run (`reports/results/00_switch_on_points.csv`).

Consequences:
- The calibrated track scores a different row set from v1 (no injector run, no first 20 minutes of each segment). The zero-shot variant is scored on the same rows, so the comparison stays fair.
- The design was fixed before any held-out score of this track was computed. The protocol author has seen v1's held-out results, as stated in ADR 0013.
