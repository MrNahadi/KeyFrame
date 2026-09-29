# 15 Write-up: plan

Roadmap item 15. Built interactively in the owner's session: the owner supplied a LaTeX template mid-task and asked for the paper in that form, and the pages are judged by looking at the compiled PDF.

1. README rewritten around the locked results, with the demo screenshot, figures, reproduction steps, citation and limits.
2. `scripts/reproduce.sh`: the experiment invocations recovered from the saved outputs, in order, then the notebooks.
3. The paper in `paper/`: `make_data.py` writes `data/results.tex` (macros), table rows and plot CSVs from the results files; `main.tex` follows the owner's template; screenshots of the production build in `figures/`.
4. Writing the paper compared the demo's alarm delays with the evaluation's and found they differed (ADR 0012); the replays were regenerated with each fold's own alarm settings and a test now holds them equal.
5. Launch drafts for the owner in `docs/launch/`.
