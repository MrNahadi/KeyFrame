# 03 EDA, engineering checklist and targets review: plan

Roadmap item 3 (brief milestones 3 and the milestone 4 gate). Done when the "Observed" half of the engineering checklist is committed and `reports/targets.md` records the one allowed target revision (or that none was needed).

## Approach

The "Expected" half of `reports/engineering_checklist.md` was pre-registered on main (commit 57ecbea) before any fault run was compared with healthy running. This feature does the comparison. Shared numeric logic (matched healthy baselines, effect sizes, windows around switch-on) goes into `keyframe/eda.py` with tests; notebook 01 calls it and presents the findings. No model is trained in this feature: no classifier, no regressor, nothing fitted to labels.

## Modules touched

- `keyframe/eda.py` and `tests/test_eda.py`
- `notebooks/01_eda.py` + executed `.ipynb`
- `reports/figures/01_*.png`, `reports/results/01_*.csv`
- `reports/engineering_checklist.md` (append below "Observed in the EDA" only)
- `reports/targets.md` (new)

## Order of work

T-001 eda helpers → T-002 coverage and load-shift → T-003 around switch-on → T-004 cavitation puzzle → T-005 injector / test-day puzzle → T-006 observed checklist and notebook summary → T-007 targets review.

## New dependencies

None.
