# 12 Web demo: replay: tickets

## T-001: Replay types and loading

Status: done
Blocked by:
Slice: The app can fetch the run index and one run, typed and validated.
Test seam: `web/src/replay/data.ts` (`loadIndex`, `loadRun`)
Context: requirements R2-R3; `head -c 1500 web/public/replays/index.json`; `head -c 2500 web/public/replays/<first run>.json` (after `npm --prefix web run sync-replays`); `ls web/src`
Acceptance:
- [x] Types match the real files; validation rejects a malformed file with a typed error (tests with fixtures in `web/src/replay/__fixtures__/`, small hand-trimmed copies)
Notes:
- Parked stash: T-001 parked (types, loaders, fixtures and tests written; `npm --prefix web test` passes 9/9; `npm --prefix web run build` fails: `data.test.ts` lines 21 and 36 index an empty tuple, TS2493. The earlier iteration could not run the web checks; `.ralph/settings.json` now allows them)

## T-002: Playback engine

Status: done
Blocked by: T-001
Slice: A tested, DOM-free playback state machine with speeds, stepping, seeking and jump to switch-on.
Test seam: `web/src/replay/playback.ts`
Context: requirements R4-R5
Acceptance:
- [x] Tests for 1x/10x/60x frame advance per elapsed time, bounds, seek, switch-on jump, stop at end
Notes:

## T-003: Run picker and routing

Status: done
Blocked by: T-001
Slice: The replay route lists runs grouped by fault in plain words and opens one.
Test seam: `web/src/replay/RunPicker.tsx` via Testing Library
Context: requirements R1, R6, R11; `docs/design/manifesto.md` Part 14 only (`sed -n '/^# Part 14/,/^# Part 15/p'`); `ls web/src/ui web/src/app`
Acceptance:
- [x] Grouped list with load and duration; choosing a run updates the hash route (test)
- [x] Loading skeleton, error with retry, empty states (tests)
Notes:

## T-004: Sensor traces

Status: done
Blocked by: T-002, T-003
Slice: Eight small-multiple traces with switch-on, alarm and current-frame markers, past emphasised over future.
Test seam: `web/src/replay/Traces.tsx`
Context: requirements R7, R11; `grep -n 'data-' web/src/styles/tokens.css`; ADR 0010 chart notes (`sed -n '/Charts/,/Tests/p' docs/adr/0010-web-stack.md`)
Acceptance:
- [x] Renders eight charts with units in titles for a fixture run (test with fixed width/height)
- [x] Reflows to one column under 640 px (CSS)
Notes:

## T-005: Probabilities, alarm status and provenance

Status: done
Blocked by: T-002
Slice: The current frame's class probabilities, the predicted-class sentence, the alarm status line and the held-out provenance note.
Test seam: `web/src/replay/status.ts` (pure sentence functions) and `web/src/replay/Probabilities.tsx`
Context: requirements R8-R10
Acceptance:
- [x] Sentence tests for every alarm case in R9 and the probability sentence
- [x] Bars show text labels and percentages (test)
Notes:

## T-006: Replay screen, keyboard and reduced motion

Status: open
Blocked by: T-004, T-005
Slice: The full replay screen: controls, scrubber, traces, probabilities, status, with keyboard control.
Test seam: `web/src/replay/ReplayScreen.tsx` via Testing Library and user-event
Context: requirements R5, R11; `grep -n 'export' web/src/replay/*.ts web/src/replay/*.tsx`
Acceptance:
- [ ] Keyboard tests: Space, arrows, Home/End, S
- [ ] `npm --prefix web run build` passes
Notes:

## T-007: Screen audit

Status: open
Blocked by: T-006
Slice: The replay screen is checked against the manifesto's Part 15 and fixed where it fails.
Test seam: `specs/features/12-web-replay/audit.md`
Context: requirements R13; `sed -n '/^# Part 15/,/^## The last word/p' docs/design/manifesto.md`; `grep -rn 'className' web/src/replay/*.tsx | head -40`
Acceptance:
- [ ] Every Part 15 item answered; failures fixed in the code or explained
Notes:
