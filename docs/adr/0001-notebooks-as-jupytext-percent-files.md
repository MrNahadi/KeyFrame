# 0001. Notebooks are authored as jupytext percent files and committed executed

Status: accepted
Decided-by: agent (planning, owner present), 28 Sep 2026
Question: How should the nine notebooks be written and reviewed, given that an unattended loop edits them?
Decision: Each notebook's source is `notebooks/NN_name.py` in jupytext percent format. The executed `.ipynb` is generated with `uv run jupytext --set-kernel python3 --to ipynb --execute` and committed next to it.
Basis: Brief: "The work runs through nine Jupyter notebooks"; primary user reviews on GitHub in about five minutes, so outputs must be visible. Plain-text sources diff cleanly, lint with ruff and cost far fewer tokens to edit than notebook JSON (ranked trade-offs 3 and 4).
Consequences: jupytext is a dev dependency. The `.ipynb` is a build output: never edit it by hand. Executing a notebook is part of each notebook ticket's check.
