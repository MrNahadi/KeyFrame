# 12 Web demo: replay: requirements

## Shell and data

- R1. App shell (scaffold): header with the name "Keyframe" and primary navigation (icon plus label) to Replay, What-if and Model card; hash routes (`#/replay/<run>`, `#/what-if`, `#/model-card`); the active item shown; light and dark themes from `prefers-color-scheme` with every colour from `tokens.css`. What-if and Model card are placeholders until item 13, each an honest empty state ("Coming in the next release" is not allowed; say what the page will do and link back to Replay).
- R2. `web/scripts/sync-replays.mjs` copies `../models/replays/*.json` into `web/public/replays/`; `npm run sync-replays` runs it and `prebuild` calls it. The copied files are git-ignored; the build fails with a plain message if `models/replays/index.json` is missing.
- R3. `web/src/replay/types.ts` defines the replay JSON types exactly as `keyframe.replay` writes them (read one real file with `head -c 1500` to confirm field names); `loadIndex()` and `loadRun(id)` fetch and validate (unknown shape → typed error).

## Playback

- R4. A playback engine (pure TypeScript, tested without the DOM): current frame index, play/pause, speed 1x/10x/60x (frames are 10 s apart; at 1x one frame per 10 s of wall time, at 60x six frames per second), step forward/back one frame, seek to a time, jump to switch-on. Uses `requestAnimationFrame` time, not timers per frame; stops at the end.
- R5. Keyboard: Space play/pause, Left/Right step, Home/End, `S` jump to switch-on. All controls are real buttons with accessible names; the scrubber is an `<input type="range">` with a text value ("12 min 30 s").

## Views

- R6. Run picker: the runs from `index.json` grouped by fault (plain names: "Air cooler fouling", "Air filter clogging", "Injector nozzle clogging", "Cooling water pump cavitation", "Turbine degradation", "Healthy running"), each showing load and duration; choosing one opens `#/replay/<id>`.
- R7. Sensor traces: small multiples, one per key sensor (8), each a Recharts line with unit in the title, a vertical marker for switch-on, one for the alarm if raised, and a moving cursor for the current frame. Values up to the current frame are drawn prominently, later values muted (the future is visible but secondary). Charts use `isAnimationActive={false}` and data colours from the data palette tokens.
- R8. Class probabilities: a horizontal bar per class for the current frame, with the class name as text and the percentage as text (colour is never the only signal); the predicted class stated in a sentence ("The model reads this as air cooler fouling (82%)").
- R9. Alarm: a status line that always answers "has the alarm fired?": before switch-on "Engine healthy by design until <mm:ss>"; after switch-on and before alarm "Fault switched on <x> ago, no alarm yet"; after alarm "Alarm: <class> raised <delay> after switch-on"; runs with no alarm say so at the end. Healthy runs say "No fault in this run".
- R10. Provenance: a short note on the replay screen: "Predictions come from a model that never saw this engine load (held-out load)." linked to the model card route.

## Quality

- R11. States for every data view: loading skeleton matching the layout, error with retry, empty. Works from 360 px to wide desktop (traces reflow to one column on phones). Reduced motion: no animated transitions; playback still works.
- R12. Tests (Vitest): playback engine (speeds, bounds, seek, switch-on), alarm status sentences for each case, probability sentence, types validation, keyboard handling on the replay screen, and the token rule (no hex or `rgb(` outside `tokens.css`). `npm --prefix web run build` and `npm --prefix web test` pass.
- R13. The replay screen passes the manifesto's Part 15 audit; the answers are written in `specs/features/12-web-replay/audit.md` (one line per checklist item: pass, or what was changed).
