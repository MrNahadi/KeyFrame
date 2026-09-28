# 03 EDA: tickets

## T-001: EDA helpers for matched baselines, shifts, windows and physics quantities

Status: done
Blocked by:
Slice: Tested helpers that give, for any fault run, its matched healthy baseline, per-channel shifts, a window around switch-on, time-based rolling std, and the checklist's physics quantities.
Test seam: `keyframe.eda.matched_healthy`, `fault_shift`, `around_switch_on`, `rolling_std`, and the physics functions
Context: requirements R1-R5; `grep -n '^def ' keyframe/load.py keyframe/audit.py keyframe/splits.py`; tests/conftest.py; tech-stack.md "Data and leakage"
Acceptance:
- [x] Synthetic tests with known answers for each helper (a +2 std step gives shift 2.0; rolling std over 60 s uses time, not rows, and resets at run boundaries; cooler effectiveness of a known triple)
- [x] `matched_healthy` never returns rows from another fault run
Notes:

## T-002: Notebook 01 part 1: coverage and load versus fault shifts

Status: done
Blocked by: T-001
Slice: Notebook 01 exists, loads `data/processed/clean.parquet` (building it via keyframe if missing) and shows the coverage map and the load-versus-fault comparison.
Test seam: executing `notebooks/01_eda.py`
Context: requirements R6-R8, R12; tech-stack.md "Notebooks"; `grep -n '^# %%' notebooks/00_data_audit.py` (copy its structure)
Acceptance:
- [x] `01_coverage.png`, `01_load_vs_fault_shift.png`, `reports/results/01_fault_shifts.csv`
- [x] Notebook executes and the executed `.ipynb` is committed
Notes:

## T-003: Notebook 01 part 2: each fault around its switch-on

Status: done
Blocked by: T-002
Slice: Five figures showing the checklist's key channels around switch-on for every run of each fault.
Test seam: executing `notebooks/01_eda.py`
Context: requirements R9; `grep -n 'Expected top 5' reports/engineering_checklist.md` (the key channels per fault); `grep -n '^# %%' notebooks/01_eda.py`
Acceptance:
- [x] `01_switch_on_AC.png`, `_AF`, `_CW`, `_TD`, and `01_injector_vs_reference.png`
- [x] A short markdown finding under each figure, in engine terms
- [x] Notebook executes and the executed `.ipynb` is committed
Notes:

## T-004: Notebook 01 part 3: the cavitation puzzle

Status: done
Blocked by: T-003
Slice: A section that explains why cavitation is easy to detect when its averages barely move, and checks for recording artefacts.
Test seam: executing `notebooks/01_eda.py`
Context: requirements R4, R10; `grep -n '^# %%' notebooks/01_eda.py`; `sed -n '/## Cooling water pump cavitation/,/## Turbine/p' reports/engineering_checklist.md`
Acceptance:
- [x] Mean-shift versus std-ratio figure `01_cavitation_mean_vs_std.png` and rolling-std figure `01_cavitation_rolling_std.png`
- [x] Explicit artefact checks with their results, and a stated conclusion
- [x] Notebook executes and the executed `.ipynb` is committed
Notes:

## T-005: Notebook 01 part 4: the injector and test-day puzzle

Status: done
Blocked by: T-003
Slice: A section that measures how far each run's day-dependent channels separate it from the others, and names the day-marker channels.
Test seam: executing `notebooks/01_eda.py`
Context: requirements R11; `grep -n '^# %%' notebooks/01_eda.py`
Acceptance:
- [x] Figure `01_day_markers.png` (per-run distributions of the R11 channels) and table `reports/results/01_day_markers.csv`
- [x] A named list of day-marker channels with a recommendation for feature engineering (drop, residualise, or keep), justified in engine terms
- [x] No model is trained
- [x] Notebook executes and the executed `.ipynb` is committed
Notes:

## T-006: Observed checklist and the notebook's findings summary

Status: done
Blocked by: T-004, T-005
Slice: The checklist gains its Observed section, protected by a test, and notebook 01 opens with its findings.
Test seam: `tests/test_checklist.py`; executing `notebooks/01_eda.py`
Context: requirements R6, R13; `reports/results/01_fault_shifts.csv` (read with pandas, filter to checklist channels); `sed -n '/^## Observed in the EDA/,$p' reports/engineering_checklist.md`
Acceptance:
- [x] Observed tables and surprise paragraphs appended below "## Observed in the EDA"
- [x] A test asserts everything above that heading is byte-identical to the pre-registered version (commit 1c75bdf), pinned by SHA-256
- [x] First cell of notebook 01 summarises the findings with real numbers; notebook executes and is committed
Notes:

## T-007: Targets review (milestone 4 gate)

Status: open
Blocked by: T-006
Slice: `reports/targets.md` records the one allowed target revision or that none was needed, decided by the answerer on EDA evidence alone.
Test seam: `grep -c 'Targets final as of' reports/targets.md`
Context: requirements R14; `sed -n '/^## Goals and success metrics/,/^## Validation protocol/p' specs/brief.md`; notebook 01's first markdown cell (`sed -n '1,40p' notebooks/01_eda.py`); `reports/results/01_*.csv` headers only
Acceptance:
- [ ] `reports/targets.md` has the target table, the EDA evidence per target, the decision and the ADR it links to
- [ ] Ends with "Targets final as of <date>."
Notes:
