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

Status: todo
Blocked by: T-002
Slice: about 20 experiments on fold 75 following `program.md`.
Test seam: `specs/features/16-autoresearch/trial-fold75.md`
Context: requirements R8
Acceptance:
- [ ] Run time per experiment, seed sd, ETA, keep rate and crashes recorded
- [ ] Candidate reset to the baseline afterwards; `examine` not run

## T-004: Trial report and go/no-go

Status: todo
Blocked by: T-003
Slice: a recommendation on running the four searches, with what to change in the protocol first.
Test seam: `trial-fold75.md`, "Recommendation"
Context: ADR 0013
Acceptance:
- [ ] States plainly whether the trial found gains above the noise margin and what that means for the full run
