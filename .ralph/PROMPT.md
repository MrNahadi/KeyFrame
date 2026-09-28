# Ralph iteration

You are one iteration of an unattended build loop. You remember nothing from earlier iterations; the files are your memory. Do exactly one ticket, then stop.

**Token budget: stay under about 25,000 tokens of work for the whole iteration** (what you read, run and write, on top of the fixed start of this session). Every file you read and every command output you print costs tokens. Read the least that lets you do the ticket right. Keep your own messages to a line or two; do not summarise files back to yourself.

## 1. Pick the ticket first (cheap reads only)

1. `cat .ralph/current-feature` gives the feature folder, called FEATURE below.
2. Check the branch and tree: `git branch --show-current` must start with `feature/`, and `git status --porcelain` must be empty. If not, write `STOPPED: <reason>` to `.ralph/done` and stop.
3. List ticket states without reading the file: `grep -nE '^## T-|^Status:|^Blocked by:|^Notes:.*stash' FEATURE/tickets.md`
4. Pick the first ready ticket:
   - `Status: open` or `Status: checkpoint`, and every ticket under `Blocked by` is `done`, or
   - `Status: blocked-question` whose question file is now in `questions/answered/` (read that file; treat the ticket as open).
   If the ticket names a parked or checkpoint stash under Notes, `git stash list`, then `git stash pop` that entry.
5. If no ticket is ready:
   - Every ticket is `done`: run the Feedback commands (section 4, full set including all e2e). All pass: write `COMPLETE` to `.ralph/done`. One fails: add a ticket describing it, commit, stop.
   - Otherwise write `WAITING` to `.ralph/done`, then one line per unfinished ticket with its ID and status. Stop.
6. Read only your ticket's block: `sed -n '<start>,<end>p' FEATURE/tickets.md` using the line numbers from step 3. Set it to `Status: in-progress`.

## 2. Load only the context this ticket needs

Read in this order and stop as soon as you know enough:

- The ticket's `Context:` line, if present, names the spec sections and file ranges to read. Read exactly those.
- `tail -n 20 .ralph/progress.md` (not the whole file).
- Requirements: only the R-numbers the ticket refers to. Find them with `grep -n 'R12\|R13' FEATURE/requirements.md`, then read those lines. Read `FEATURE/plan.md` only if the ticket leaves the approach unclear, and then only its "Modules touched" section.
- `specs/tech-stack.md`: only the Conventions subsection that applies, plus `## Feedback commands`. Find them with `grep -n '^##' specs/tech-stack.md`.
- `specs/brief.md`, `specs/mission.md`: do not read. If intent is unclear, ask the answerer (section 3).
- UI tickets: if `tech-stack.md` names a design-rules or style-guide document, read its checklist plus the one section you need. Copy the structure and styles of the nearest existing screen instead of inventing new ones. The screen must pass every checklist item.
- Code: locate with `grep -rn` or Glob, then read focused ranges with offset and limit (150 lines or less at a time). Never read a whole file over about 300 lines, a lockfile, build output or dependencies. Never print whole test logs.

### Keyframe specifics

- Notebooks: edit only `notebooks/NN_name.py` (jupytext percent format). Never read or edit `notebooks/*.ipynb`; regenerate it with `uv run jupytext --set-kernel python3 --to ipynb --execute notebooks/NN_name.py 2>&1 | tail -n 15` and commit it with the `.py`.
- Data: never print a whole CSV or DataFrame. Use `head`, `.shape`, `.describe()` on a few columns, or `.to_string(max_rows=20)`. Files are in `data/raw/`; if missing, run `uv run python -m keyframe.download`.
- Never read `data/lockbox/` unless your ticket says it is the lockbox evaluation.
- Leakage rules (tech-stack.md "Data and leakage") are non-negotiable. If a ticket seems to need breaking one, ask the answerer.
- Results: when a number is worse than the target, report it honestly. Never tune on the test fold to reach a target.

## 3. Build it

Write the failing test first, through the interface named in the ticket's Test seam, then make it pass, then tidy.

When the ticket, the R-numbers you read and the ADRs don't answer a question, don't guess. Ask the answerer sub-agent once, with the ticket ID, the question and what you considered.

- `VERDICT: ANSWERED`: follow it. Challenge it at most once, only with a concrete reason.
- `VERDICT: ESCALATE`: park the work: `git stash push -u -m "<ticket-id> parked"`, write `questions/open/<ticket-id>-<slug>.md` (question, why it blocks, options), set `Status: blocked-question` with `Parked stash: <ticket-id> parked` under Notes, commit those two files as `chore(<ticket-id>): blocked on question`, stop.

## 4. Check it, cheapest first

1. Run only the tests you touched (the test runner with file paths), piped through `tail -n 25`.
2. Then every Feedback command from `tech-stack.md`, each piped through `tail -n 20` (or `grep -m 20 error` for a type checker).
3. Slow end-to-end suites: run only the specs related to this ticket. The full suite runs only in the COMPLETE check (section 1, step 5).

**Two fix attempts, then checkpoint.** If checks still fail after two attempted fixes, or you are past about 20,000 tokens and not close to done, stop debugging:

1. `git stash push -u -m "<ticket-id> checkpoint"`.
2. Under the ticket's Notes add, in 5 lines or fewer: the failing check, the key error line, what you tried, and your best next idea. Add `Checkpoint stash: <ticket-id> checkpoint`.
3. If the Notes already show two earlier checkpoints for this ticket, set `Status: blocked-failing`; otherwise set `Status: checkpoint` so a fresh iteration retries it.
4. Commit only the ticket file: `chore(<ticket-id>): checkpoint`. Stop.

## 5. Finish

1. Tick the ticket's acceptance boxes and set `Status: done`.
2. Append one line to `.ralph/progress.md`: the ticket ID, what changed, and any gotcha the next iteration needs.
3. Commit everything: `feat(<ticket-id>): <summary>`.
4. Stop. Don't start another ticket.

## Never

- Add `Co-Authored-By` or any other Claude or AI attribution line to a commit message (owner's rule).
- Edit `specs/brief.md`, `specs/mission.md` or `specs/roadmap.md`.
- Add a dependency that isn't installed. If a ticket needs one, escalate it as a question.
- Push, merge, rebase, reset, or switch branches.
- Weaken, skip or delete a test to make it pass.
- Create, read or print credentials or `.env` files.
- Run the code-review skill or other long reviews; that happens once per feature in the validation phase.
