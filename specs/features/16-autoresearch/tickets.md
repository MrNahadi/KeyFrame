# 16 Autoresearch: tickets

## T-001: Fixed harness with guards

Status: done
Blocked by:
Slice: `uv run python -m keyframe.autoresearch score --outer-fold K [--no-day]` prints the inner-LOLO score of the candidate; `examine` scores the held-out load once.
Test seam: `keyframe.autoresearch.search_score`, `check_causal`, `select_checked`, `load_candidate`, `examine`
Context: requirements R1-R6; ADR 0013
Acceptance:
- [x] Spy test: no fit or predict call sees a held-out-load row
- [x] Look-ahead, out-of-bounds columns, unprefixed columns and file-reading source are refused (tests)
- [x] `examine` refuses a second run for one fold (test)
- [x] Baseline candidate reproduces the v1 inner score for fold 75 at seed 42 (0.5927)
Notes: one fold-75 score (3 seeds, 833 features) takes about 92 s on 4 cores.

## T-002: Agent program

Status: done
Blocked by: T-001
Slice: `autoresearch/program.md` that a fresh session can follow without asking.
Test seam: the trial run (T-003) follows it.
Context: requirements R7; ADR 0013
Acceptance:
- [x] Setup, loop, keep rule with ETA and the no-day gate, budget, log format, do-not-read list, hand-off

## T-003: Trial run on fold 75

Status: done
Blocked by: T-002
Slice: about 20 experiments on fold 75 following `program.md`.
Test seam: `specs/features/16-autoresearch/trial-fold75.md`
Context: requirements R8
Acceptance:
- [x] Run time per experiment, seed sd, ETA, keep rate and crashes recorded
- [x] Candidate reset to the baseline afterwards; `examine` not run
Notes: 20 experiments, 6 before and 15 after ADR 0013 amendment 1 (the shared baseline counted in both). Trial branch kept local.

## T-004: Trial report and go/no-go

Status: done
Blocked by: T-003
Slice: a recommendation on running the four searches, with what to change in the protocol first.
Test seam: `trial-fold75.md`, "Recommendation"
Context: ADR 0013
Acceptance:
- [x] States plainly whether the trial found gains above the noise margin and what that means for the full run

## T-005: Four isolated searches

Status: done
Blocked by: T-004
Slice: four cloud sessions (8 Oct 2026, 11:38 UTC), one per held-out load, each following `program.md` on branch `autoresearch/foldK` for 60 experiments.
Test seam: `reports/autoresearch/foldK_results.tsv` on each branch
Acceptance:
- [x] Four branches pushed with their logs
- [x] Each examined candidate passes `check_causal` and `check_bounded_memory`. Fold 40's final candidate failed the memory check, so its last compliant keep was examined (ADR 0013, amendment 3)

## T-006: v1 reference and examinations

Status: done
Blocked by: T-005
Slice: `reports/autoresearch/v1_unseen_foldK.json` (v1 on its held-out load, unseen runs only) and `v2_foldK.json` (each search's final candidate, once).
Test seam: `uv run python -m keyframe.autoresearch v1-reference|examine --outer-fold K [--candidate PATH]`
Acceptance:
- [x] v1 reference for all four folds: 0.404 / 0.818 / 0.500 / 0.517 (mean 0.560; locked per-fold mean 0.679 included seen-run rows)
- [x] One examination per fold, run after its search has stopped

## T-007: v2 write-up

Status: done
Blocked by: T-006
Slice: `reports/autoresearch/README.md`: v1 reference against v2 per fold, seed spread, experiments run and kept per search, what the searches learned, and the caveats (ADR 0013).
Acceptance:
- [x] Every number traceable to a JSON or TSV in `reports/autoresearch/`
