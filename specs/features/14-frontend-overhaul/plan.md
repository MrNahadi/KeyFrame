# 14 Front-end overhaul: plan

Owner request, 29 September 2026: install the frontend-design skill and, with it and the design manifesto, overhaul the whole web demo. The owner also supplied a SaaS UI checklist (`docs/design/saas-ui.md`).

Built interactively in the owner's session rather than by the Ralph loop, because the work is judged by looking at screenshots, which the unattended loop cannot do.

## Approach

1. Follow the frontend-design skill: write a design plan (palette, type, layout wireframes, principles), review it against generic defaults, then build and critique each screen with screenshots. The plan is `docs/design/keyframe-design-plan.md`.
2. Replace tokens, base styles and shared UI first (buttons, segmented control, keyframe mark, formatting of readings, product vocabulary), so every screen draws from one set.
3. Rebuild screen by screen: runs page, replay, what-if, model card. Keep the tested logic modules (playback, waterfall, data loading, API client, routes, Markdown) and change only what they render.
4. After each screen: screenshots at 1440 and 390 px, light and dark, checking overflow and console errors. At the end: keyboard walk, 200% zoom (720 px), contrast of every new colour pair, then the Part 15 audit (`audit.md`).
