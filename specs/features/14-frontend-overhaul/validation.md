# 14 Front-end overhaul: validation

## Automated

1. `npm --prefix web test` and `npm --prefix web run build` pass (the build type-checks).
2. `web/src/styles/tokens.test.ts`: no raw colours outside `tokens.css`; no undefined tokens.
3. `web/src/modelcard/scorecard.test.ts`: every number in the targets table matches `reports/results/*.csv` and `reports/physics_check.md`.

## Screenshots (done in the build session)

- Runs, replay (fault run, paused after the alarm; healthy run), what-if (after moving a slider) and model card at 1440 and 390 px, light and dark: no overflow, no console errors.
- Keyboard walk and 720 px (200% zoom) on every screen.

## Manual (owner)

- Open the demo on a phone, play "Air cooler fouling at 75% load", and pause after the red keyframe.
- With the API running, open What-if, raise charge air temperature after the cooler, and watch the verdict bar.
