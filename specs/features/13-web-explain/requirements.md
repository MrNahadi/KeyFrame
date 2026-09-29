# 13 Web demo: requirements

## Explain panel (replay screen)

- R1. `web/src/replay/waterfall.ts` turns a frame's `shap_groups` (five sensor groups) into waterfall steps for the predicted class: start at the base value, one step per group ordered by absolute size, end at the model's output; each step has a start, end, sign and plain group name ("Air path", "Combustion and power", "Fuel system", "Cooling", "Lube oil"). Pure and tested (steps sum to the output; order; signs). Read the exact field names from a replay file (`head -c 3000 web/public/replays/AC_Fouling_60_Load.json`).
- R2. The replay screen shows an explain panel for the current frame whenever playback is paused: title "Why the model reads this as <class>", the waterfall (Recharts range bars, positive and negative steps distinguished by direction, sign text and a label, never colour alone), a one-sentence summary ("Air path readings pushed the most towards air cooler fouling"), the top three features in plain words with their value and push, and a caveat line: "Sensors move together, so credit between groups is approximate." While playing, the panel shows a short hint ("Pause to see why") rather than updating every frame.
- R3. For runs where the held-out model is barely confident (the item 12 low-confidence note), the explain panel says the explanation describes a model that is barely confident.

## What-if view

- R4. `web/src/whatif/api.ts`: typed client for `GET /whatif/baselines` and `POST /explain` matching `api/main.py` exactly (read its pydantic models and response dicts with `grep -n` and focused ranges); base URL from `import.meta.env.VITE_API_BASE`, default `/api` (the dev proxy). Errors become typed results: API unreachable, validation error (with the API's message), unexpected response.
- R5. The what-if screen: a load selector (40/60/75/85%, segmented control), sliders for the API's slider channels with their ranges, units and current value as text, starting from that load's healthy baseline; a "Reset to healthy baseline" action; the diagnosis (probability bars reused from the replay, predicted-class sentence), the grouped explanation (reuse the waterfall), and the API's warnings shown plainly (the steady-state assumption always visible: "Assumes the engine has held these readings steady for 15 minutes"). Requests are debounced (250 ms) and the latest response wins; while a request is in flight the previous result stays visible and is marked as updating.
- R6. States: loading (skeleton), API unavailable (what happened, how to fix: "Start the API with `uv run uvicorn api.main:app --port 8000`", and a retry), validation error (the API's message). Keyboard: sliders are native range inputs with labels; every control reachable by Tab.

## Model card page

- R7. `web/scripts/sync-replays.mjs` also copies `../reports/model_card.md` to `public/model_card.md` and `../reports/figures/07_confusion.png` to `public/figures/07_confusion.png` (git-ignored copies; fail with a plain message if missing).
- R8. `web/src/modelcard/markdown.ts`: a small renderer to React elements for the subset the model card uses (headings, paragraphs, bullet lists, bold, inline code, links); text is never injected as HTML. Tested against a fixture that covers each construct, plus a test that `<script>` in the input is rendered as text.
- R9. The model card page renders the card, then the confusion matrix figure with alt text and a caption, and a link to the full evaluation notebook on GitHub (`notebooks/07_evaluation.ipynb`). States: loading and error.

## Quality

- R10. `npm --prefix web test` and `npm --prefix web run build` pass. Every new screen passes the manifesto's Part 15 audit, written in `specs/features/13-web-explain/audit.md`. Works at 390 px without horizontal scroll (explain panel below the probabilities on phones).
