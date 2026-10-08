# 16 Autoresearch: plan

Owner request, 8 Oct 2026. Branch `auto-research`. Done when the harness, program and tests are in, and the trial report says whether the full run is worth it.

## Approach

Copy autoresearch's shape: a fixed evaluator, one editable file, a program the human edits, a keep-or-revert git loop with a log. Change three things for a dataset of 4 loads and 14 fault runs (ADR 0013): the keep signal is nested (inner folds of the training loads only), a change must beat the best by a seed-noise margin, and a day-robust gate stops the loop from rewarding test-day recognition. Each held-out load gets its own isolated search; the held-out load is scored once, at the end.

## Modules touched

- `keyframe/autoresearch.py` (new): harness, guards, `score` and `examine` commands
- `autoresearch/candidate.py` (new, agent-editable), `autoresearch/program.md` (new)
- `tests/test_autoresearch.py` (new)
- `docs/adr/0013-autoresearch-protocol.md`, `specs/roadmap.md`, `.gitignore`

## Order of work

T-001 harness and guards → T-002 program → T-003 trial run on fold 75 → T-004 trial report and go/no-go.

## New dependencies

None.
