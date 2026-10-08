# 17 Calibrated track: plan

Branch `auto-research` (it shares the harness from feature 16). Done when the inner scores for all four folds are in and the examination has run once per fold.

Approach: compute deviations from each run's own first 20 minutes per load segment; score three feature variants with v1's per-fold model on identical rows, inner folds first, held-out loads once at the end.

Modules: `keyframe/calibrated.py` (new), `keyframe/autoresearch.py` (shared `identify_runs`), `tests/test_calibrated.py`, `docs/adr/0014-calibrated-track.md`, `reports/calibrated/`.

Order: T-001 features and tests → T-002 inner scores, 4 folds → T-003 examination, once per fold → T-004 write-up.

New dependencies: none.
