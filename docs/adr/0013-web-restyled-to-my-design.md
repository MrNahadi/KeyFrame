# 0013. Demo restyled to MY-DESIGN.md, and a marketing page added

Status: accepted
Decided-by: owner (stated), 14 Oct 2026
Question: The owner asked for a marketing page for Keyframe, treated as a startup, and a complete frontend overhaul of the demo, both following `MY-DESIGN.md`. That file replaces the styling half of ADR 0010 (Barlow webfonts, the bulkhead-grey palette, 8px buttons, a dark theme). How do the demo and the page change, and where does the page live?
Decision:
1. The demo keeps its stack, routes, data and behaviour (ADR 0010). Only its look changes: `web/src/styles/tokens.css` is `MY-DESIGN.md` §4.1 (light theme only, type in rem), plus Keyframe's data colours (sensor groups, alarm, fault span). The Barlow webfonts are removed for the system font stack. Every button is a pill, cards use 16px radii and 1px borders with no shadows, and the shell is a 260px sidebar with a 52px top bar that becomes a drawer below 1024px (§7.3). Status chips carry an icon and a word. Buttons use the §13.2 words (Retry, not Try again; Title Case labels).
2. `tokens.test.ts` also fails on px font sizes and on emoji anywhere in `web/src`.
3. The marketing page is a static `site/` folder (HTML, one stylesheet, inline Lucide icons, real screenshots of the demo), separate from the demo app so neither carries the other's code. `scripts/build-site.sh` puts the page at `/` and the demo at `/demo/` in `site-dist/`. The demo is built with relative paths (`--base=./`), so the site works on any static host.
4. The page is positioned as a pilot programme: the copy states the bench-only limits and the unmet targets, and makes no claim beyond the locked results. No customer logos, testimonials or pricing exist, so the page has none.
5. `replay/waterfall.ts` is renamed `replay/waterfallSteps.ts`. It differed from `replay/Waterfall.tsx` only in letter case, which breaks the build on Windows and macOS.
Basis: Owner instruction, and `MY-DESIGN.md` §0: an explicit user instruction beats that file, and that file beats earlier design choices. Honest evaluation (brief section 10) still governs every number on the page.
Consequences: ADR 0010's styling rows (Barlow, the dark theme, `Part 14` tokens) are superseded; its framework, chart, test and icon choices stand. `docs/design/manifesto.md` and `keyframe-design-plan.md` no longer describe the demo's look. The pilot email in `site/index.html` is a placeholder (`pilots@keyframe.example`) until the owner supplies a real address.
