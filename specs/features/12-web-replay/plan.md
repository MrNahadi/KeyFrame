# 12 Web demo: replay: plan

Roadmap item 12 (brief milestone 13, part 1). Done when someone who hasn't seen the project can pick a fault run, play it, and see when and why the alarm fired (the "why" panel is item 13; here the alarm and its delay).

## Approach

Stack per ADR 0010: React 19 + Vite 8 + TypeScript (strict), Recharts, Vitest + Testing Library, plain CSS custom properties (`web/src/styles/tokens.css`) with CSS Modules, `lucide-react` through one `<Icon>` wrapper. The scaffold (package install, tokens, app shell, one passing test, build) is done by the planner before the loop starts. The replay reads static JSON copied from `models/replays/` into `web/public/replays/` by an npm script, so the replay works on any static host with no API.

Design rules: `docs/design/manifesto.md` Part 14 (rules sheet) for every value, Part 15 (screen audit) as the checklist every screen must pass.

## Modules touched

- `web/src/app/` (shell, hash routing), `web/src/replay/` (data loading, playback state, views), `web/src/ui/` (shared components: Button, Icon, Skeleton, ErrorState, etc.), `web/src/styles/`
- `web/scripts/sync-replays.mjs`
- tests beside components (`*.test.tsx`)

## Order of work

T-001 replay data loading and types → T-002 playback engine → T-003 run picker → T-004 sensor traces → T-005 probabilities, alarm and delay → T-006 states and accessibility → T-007 screen audit.

## New dependencies

Installed by the planner in the scaffold (ADR 0010). The loop adds none.
