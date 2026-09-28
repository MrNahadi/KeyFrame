# Keyframe: notes for Claude

- Intent lives in `specs/brief.md` (owner's words; never change its meaning). Constitution: `specs/mission.md`, `specs/tech-stack.md`, `specs/roadmap.md`, `CONTEXT.md`. Decisions: `docs/adr/`.
- The build follows the spec-ralph skill in `.claude/skills/spec-ralph/`. Features live in `specs/features/NN-slug/`; the unattended loop is `.ralph/ralph.sh`.
- Working agreement (ADR 0003): fully automatic, the answerer (`.claude/agents/answerer.md`) decides open questions at xhigh effort, and the agent may merge to main after validating a feature.
- Feedback commands and conventions: `specs/tech-stack.md`. Leakage rules there are non-negotiable.
- Front-end design rules: `docs/design/manifesto.md` Parts 14 and 15.
- Commits are authored and committed as the repo owner, `Farid Nahadi <thenahadi@gmail.com>` (set `git config user.name/user.email` in a fresh clone), and messages never carry `Co-Authored-By`, `Claude-Session` or any other Claude/AI attribution lines (owner's rule, 28 Sep 2026).
