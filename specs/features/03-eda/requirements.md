# 03 EDA: requirements

## Shared helpers (`keyframe/eda.py`)

- R1. `matched_healthy(df, run)` returns the healthy rows to compare a fault run against: the run's own pre-fault segment plus reference-file rows whose `Shaft Power` lies within ±5 kW of the median shaft power of the run's faulty rows. For stepped injector runs, do this per load bin of the run (the injector run has no pre-fault segment, so only reference rows are used; say so in the notebook).
- R2. `fault_shift(df, run, channels)` returns one row per channel: healthy mean and std, faulty mean and std, standardised mean shift `(faulty mean − healthy mean) / healthy std`, and std ratio `faulty std / healthy std`. Faulty rows are the run's `label != "Normal"` rows. Gradual faults: also report the shift over the last 30 minutes of the run.
- R3. `around_switch_on(df, run, minutes_before=30, minutes_after=60)` returns the run's rows in that window with a column `t_from_switch_on_min`.
- R4. `rolling_std(series, t, window_s)` computes a time-based rolling standard deviation within one run (windows defined in seconds via `t`, never rows, never crossing runs). Used for the cavitation puzzle; the same helper will be reused by feature engineering.
- R5. Physics features needed by the checklist comparison are computed by small pure functions in `keyframe/eda.py` for now (they move to `keyframe/features.py` in item 5): cooler effectiveness `(T14 − T15) / (T14 − T16)`, exhaust temperature spread across cylinders 1–3 (max − min), Pmax spread, indicated work spread, turbine temperature drop `T4 − T5`, cooling water rise (mean of T7–T9 minus T6), fuel flow per kW.

## Notebook 01

- R6. Opens with a findings summary for an engine engineer (filled in last).
- R7. Coverage map: rows per fault × load bin (figure `01_coverage.png`), stating which classes each LOLO fold can test (the 75% fold has no CW or TD).
- R8. How much healthy readings move between loads compared with how much faults move them: for each checklist channel, the spread of the healthy mean across load bins versus the fault shift. This motivates healthy-engine residuals (figure `01_load_vs_fault_shift.png`).
- R9. Around switch-on: for each fault, the checklist's key channels over −30 to +60 minutes of each run, one panel per channel, runs overlaid and coloured by load (figure `01_switch_on_<FAULT>.png`, five figures). Injector: the whole run against matched reference rows instead.
- R10. Cavitation puzzle: mean shift versus std ratio for every channel in the two CW runs; rolling std of Pl_water1 and Qw_eng around switch-on; an explicit check for recording artefacts (a channel that steps exactly at switch-on with no mechanism, a change in logging interval, constant or clipped values). State the conclusion either way.
- R11. Injector / test-day puzzle: compare the slow, day-dependent channels (Engine room Temp., LO Cooling Water Temp. In T12, Charge Air IC Cooling Water Temp. In T16, Fuel Temp. T18, Fuel Oil Temp. Flow meter In T21, Pl_water2) across all runs and the reference file with per-run distributions. Report how far the injector run sits outside the others' ranges on these channels, and list which channels are "day markers" that feature engineering must treat with care. No classifier is trained.
- R12. Every figure saved at 150 dpi; every table to `reports/results/01_*.csv` (at least `01_fault_shifts.csv` with run, channel, shifts).

## Checklist and targets

- R13. Append to `reports/engineering_checklist.md` below "## Observed in the EDA": per fault, a table with each Expected row's channel, expected direction, observed standardised shift (median across the fault's runs) and std ratio, and Agree / Disagree / Unclear. Then one paragraph per fault on surprises. Never edit anything above that heading (a test checks the pre-registered part is byte-identical to commit 1c75bdf).
- R14. `reports/targets.md` records the milestone 4 gate: the brief's target table, the evidence from the EDA that bears on each target (coverage, fold composition, how separable each fault looks), and the decision: keep every target, or revise specific ones with the reason. The decision is taken by the answerer sub-agent (ask it with the evidence), labelled with its ADR. Revisions may only use EDA evidence, never model results. The file ends with "Targets final as of <date>."
