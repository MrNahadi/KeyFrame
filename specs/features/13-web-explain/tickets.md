# 13 Web demo: tickets

## T-001: Waterfall data from a frame

Status: done
Blocked by:
Slice: A frame's grouped SHAP becomes ordered waterfall steps from base value to output.
Test seam: `web/src/replay/waterfall.ts`
Context: requirements R1; `head -c 3000 web/public/replays/AC_Fouling_60_Load.json` (after `npm --prefix web run sync-replays`); `grep -n 'shap\|Shap' web/src/replay/types.ts`
Acceptance:
- [x] Tests: steps sum from base to output; ordered by absolute size; signs; plain group names
Notes:

## T-002: Explain panel on pause

Status: done
Blocked by: T-001
Slice: Pausing the replay shows why the model reads the current moment as it does.
Test seam: `web/src/replay/ExplainPanel.tsx` via Testing Library
Context: requirements R2-R3; `grep -n 'export\|paused\|playing' web/src/replay/ReplayScreen.tsx | head -30`; `grep -n 'lowConfidenceNote' web/src/replay/status.ts`
Acceptance:
- [x] Tests: panel shows title, summary sentence, top three features and caveat when paused; hint while playing; low-confidence wording when applicable
- [x] Waterfall renders with fixed width/height in tests; below probabilities under 640 px
Notes:

## T-003: Model card page

Status: done
Blocked by:
Slice: The model card is copied at build and rendered safely in the app with the confusion matrix.
Test seam: `web/src/modelcard/markdown.ts`; `web/src/modelcard/ModelCardPage.tsx`
Context: requirements R7-R9; `cat web/scripts/sync-replays.mjs`; `sed -n '1,12p' reports/model_card.md`; `grep -n 'model-card' web/src/app/App.tsx`
Acceptance:
- [x] Renderer tests for every construct and for `<script>` rendered as text
- [x] Page test with a fixture card; loading and error states
Notes:

## T-004: What-if API client

Status: done
Blocked by:
Slice: A typed client for baselines and explain that turns every failure into a typed result.
Test seam: `web/src/whatif/api.ts`
Context: requirements R4; `grep -n 'class PredictRequest' -A30 api/main.py`; `grep -n '@app.post("/explain")' -A40 api/main.py`; `grep -n '@app.get("/whatif/baselines")' -A12 api/main.py`; `head -c 1500 models/whatif_baselines.json`
Acceptance:
- [x] Tests with a mocked `fetch`: success shapes, unreachable, 422 message, unexpected shape
Notes:

## T-005: What-if screen

Status: done
Blocked by: T-001, T-004
Slice: Pick a load, move readings, and watch the diagnosis and explanation update, with honest states.
Test seam: `web/src/whatif/WhatIfScreen.tsx` via Testing Library with a mocked client
Context: requirements R5-R6; `grep -n 'export' web/src/replay/Probabilities.tsx web/src/replay/ExplainPanel.tsx`
Acceptance:
- [x] Tests: baseline loads per load; slider change triggers one debounced request; latest response wins; API-unavailable state with the start command and retry; steady-state notice always visible
Notes:

## T-006: Screen audit

Status: open
Blocked by: T-002, T-003, T-005
Slice: The explain panel, what-if and model card screens are checked against the manifesto's Part 15.
Test seam: `specs/features/13-web-explain/audit.md`
Context: requirements R10; `sed -n '/^# Part 15/,/^## The last word/p' docs/design/manifesto.md`
Acceptance:
- [ ] Every Part 15 item answered for each screen; failures fixed or explained
Notes:
