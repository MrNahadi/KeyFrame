# 0010. Web demo stack: React + Vite SPA, Recharts, Vitest, plain CSS tokens, Lucide

Status: accepted
Decided-by: answerer (inferred for the framework and styling; researched for packages and versions), per ADR 0003's fully-automatic working agreement
Question: Roadmap item 12 (web demo, planning): which framework and build tool, chart library, test runner, styling approach and icon package?
Decision: A client-only single-page app in `web/`, scaffolded from the official `create-vite` `react-ts` template, with Recharts for all charts, Vitest + Testing Library + jsdom for tests, plain CSS custom properties plus CSS Modules for styling, and `lucide-react` for icons. No router, state, data-fetching, UI-kit or CSS-framework packages.

Packages (versions checked on the npm registry on 2026-09-29):

| Role | Package | Range | Licence |
| --- | --- | --- | --- |
| Framework | `react`, `react-dom` | `^19.3.0` | MIT |
| Build | `vite` | `^8.3.1` | MIT |
| Build | `@vitejs/plugin-react` | `^6.1.1` | MIT |
| Language | `typescript` | `~6.0.3` (not 7.x) | Apache-2.0 |
| Types | `@types/react`, `@types/react-dom` | `^19.3.0` | MIT |
| Types | `@types/node` | `^24.19.0` (from the template, for `vite.config.ts`) | MIT |
| Charts | `recharts` | `^3.10.1` | MIT |
| Icons | `lucide-react` | `^1.48.0` | ISC |
| Tests | `vitest` | `^4.1.11` (not 5.x yet) | MIT |
| Tests | `jsdom` | `^30.1.1` (needs Node >= 22.22.2) | MIT |
| Tests | `@testing-library/react` | `^16.3.3` | MIT |
| Tests | `@testing-library/dom` | `^10.4.2` (peer of the above) | MIT |
| Tests | `@testing-library/user-event` | `^14.6.7` (keyboard-access tests) | MIT |

Details:
1. Framework and build. Scaffold with `npm create vite@latest web -- --template react-ts`, then drop `oxlint`, because no feedback command runs it and strict `tsc` is the gate. Scripts: `"build": "tsc -b && vite build"`, `"test": "vitest run"`. Set `"strict": true` explicitly in `tsconfig.app.json`. Stay on TypeScript 6.0 because the official template pins `~6.0.2`. TypeScript 7.0 (the native port, released 2026-07-08) is not in the template yet. Use hash routes (`#/replay/<run>`, `#/explain`, `#/what-if`, `#/model-card`) through a small typed hook, so any static host works without rewrite rules. Fetch data with native `fetch` behind typed wrappers in `web/src/api/`. In development, the Vite `server.proxy` forwards `/api` to `http://localhost:8000`. The production API base comes from `import.meta.env.VITE_API_URL`. Replay and explain read the static replay JSON, so they work without the API. What-if needs the API and shows an error state when the API cannot be reached.
2. Charts. Recharts draws SVG, so the chart colours can be the token variables themselves (`stroke="var(--color-data-1)"`) and follow light and dark mode with no re-initialisation. It is also a typed React component library with the most examples. Chart layout:
   - Sensor traces: small multiples, one `LineChart` per sensor, with `ReferenceLine`s for the switch-on time and the alarm.
   - Class probabilities: a horizontal `BarChart`.
   - SHAP waterfall: a `BarChart` whose bars take `[start, end]` range values.
   - Every chart sets `isAnimationActive={false}`, which suits live data and reduced motion.
   Size: a run has about 800 frames × 8 sensors, roughly 6,400 points (checked in `models/replays/AC_Fouling_40_Load.json`, 801 frames). SVG handles that comfortably.
   ECharts 6.1 was rejected. It draws on a canvas, so dark mode needs theme re-initialisation, token colours must be read through `getComputedStyle`, and it adds a larger bundle. Its extra speed only matters above tens of thousands of points.
3. Tests. Choose Vitest 4.1, the maintained `V4` dist-tag, whose peer range covers Vite 8. Vitest 5.0.x was only four days old at decision time, and its breaking changes (mocks cleared by default, stricter text matchers) add risk for an unattended loop. Move to 5.x in a later ticket, after 5.1. `ResponsiveContainer` measures zero in jsdom, so chart tests pass a fixed width and height, and data transforms are tested as pure functions.
4. Styling. Put every Part 14 value as a CSS custom property in `web/src/styles/tokens.css`:
   - colour roles, with light values plus `prefers-color-scheme: dark` and a `[data-theme]` override
   - the `--color-data-1..8` data palette
   - `--space-*` (4, 8, 12, 16, 24, 32, 48, 64, 96)
   - radii
   - the type scale in rem
   - motion durations, set to 0 under `prefers-reduced-motion`
   Components use CSS Modules (`*.module.css`), which Vite supports with no extra dependency. There is no Tailwind, because its arbitrary values (`bg-[#123456]`, `p-[13px]`) make it easy to break "no raw hex values" and "one set of sizes". Add a Vitest test that fails if a hex or `rgb(` colour appears anywhere in `web/src` outside `tokens.css`.
5. Icons. `lucide-react`, used only through a wrapper `<Icon>` whose `size` prop is typed `16 | 20 | 24`, with one stroke width. Icon-only buttons require an `aria-label`.

Basis: The brief says "React with Vite has the most chart libraries (Recharts, ECharts) and tutorials, and shows up in the most job listings" (Front-end demo), and names TypeScript for the front end (section 9). The primary user is an engineer or recruiter at an engine maker, so engineering credibility (rank 2) favours the most widely recognised stack. The unattended loop needs the stack with the most examples. Reproducibility (rank 3) favours proven majors over days-old ones. Simplicity (rank 4) favours few dependencies and zero-dependency CSS. For styling and icons, the manifesto's Part 14 asks for semantic tokens with light and dark values for every role, no raw hex in components, and "Lucide ... Sizes 16 / 20 / 24 only". Sources: npm registry metadata (versions, peer dependencies, engines, licences, release dates) at https://registry.npmjs.org/; the official template at https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts (react ^19.3.0, vite ^8.3.1, @vitejs/plugin-react ^6.1.1, typescript ~6.0.2); Vitest 5.0 release notes at https://github.com/vitest-dev/vitest/releases/tag/v5.0.0.
Consequences:
- `npm --prefix web run build` and `npm --prefix web test` become the front-end feedback commands, as `specs/tech-stack.md` already anticipates. Update the tech-stack Front end row to name React 19 + Vite 8.
- `package-lock.json` is committed.
- Node >= 22.22.2 is required, because of jsdom 30. Declare it in `web/package.json` `engines`.
- The output is a static `web/dist` that can be hosted anywhere, and the replay works without the API.
- Adding any further runtime dependency needs a new ADR.
