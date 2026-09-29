# 13 Web demo: explain, what-if and model card: plan

Roadmap item 13 (brief milestone 13, part 2). Done when someone who hasn't seen the project can play a fault run and read why the alarm fired, try their own readings, and read the model's limits.

## Approach

Three additions to the app built in item 12, same stack and rules (ADR 0010, `docs/design/manifesto.md` Parts 14 and 15):

1. **Explain panel** on the replay screen: when paused (or stepping), a grouped SHAP waterfall for the current frame, read from the replay file (no API needed).
2. **What-if view**: pick a load, move sliders for key readings, see the diagnosis and its grouped explanation update, through the FastAPI service (`/api/whatif/baselines`, `/api/explain`). Honest about its assumption (a steady reading) and about the API being unavailable.
3. **Model card page**: `reports/model_card.md` rendered in the app (copied at build time, rendered by a small, tested, escape-first Markdown renderer), plus the confusion matrix figure.

## Modules touched

- `web/src/replay/Explain*.tsx`, `web/src/replay/waterfall.ts`
- `web/src/whatif/` (api client, screen)
- `web/src/modelcard/` (renderer, page)
- `web/scripts/sync-replays.mjs` (also copies `reports/model_card.md` and `reports/figures/07_confusion.png`)
- `web/src/app/App.tsx` (routes)

## Order of work

T-001 waterfall data → T-002 explain panel → T-003 model card → T-004 what-if client → T-005 what-if screen → T-006 audit.

## New dependencies

None.
