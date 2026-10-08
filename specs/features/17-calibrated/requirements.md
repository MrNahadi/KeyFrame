# 17 Calibrated track: requirements

Under the owner's standing brief (8 Oct 2026), from the reviewer's recommendation to report a zero-shot and a calibrated result side by side. Protocol and reasons: ADR 0014.

- R1. `keyframe.calibrated.segment_ids` splits each run wherever its load bin changes.
- R2. `add_calibrated(table)` adds `cal_<x>` = reading minus its mean over the first 20 minutes of the same run and load segment, for raw readings, physics features and rolling means (a rolling mean is compared with the baseline of the reading it averages). `ready` marks rows after a complete baseline whose window is all healthy. Tested: the session level cancels out, the fault shows as a deviation, no row of the baseline window is monitored, a faulty-from-the-start or short segment is never monitored, each load segment gets its own baseline, and later rows never change earlier values.
- R3. `arm_columns(table, arm)` for `zero_shot`, `calibrated` and `raw+calibrated` (ADR 0014, decision 3). Tested: the calibrated variant has no absolute level apart from the operating point.
- R4. `uv run python -m keyframe.calibrated inner --outer-fold K` writes `reports/calibrated/inner_foldK.csv`: per variant, the 3-seed inner-LOLO macro F1 on monitored rows of unseen runs, its seed sd, per-class recall, and the batch-effect test on the variant's columns.
- R5. `... examine --outer-fold K` scores load K once per fold, writes `reports/calibrated/outer_foldK.json` with every variant and the primary variant chosen from the inner file, and refuses a second run.
- R6. The write-up (`reports/calibrated/README.md`) reports zero-shot and calibrated side by side and states that the calibrated track cannot detect the injector fault.
