# 15 Write-up: validation

## Automated

1. `uv run pytest`: `tests/test_paper_data.py` (committed paper data equals a fresh run) and `tests/test_replay_export.py` (replay alarm delays equal the evaluated ones).
2. `cd paper && latexmk -pdf main.tex` builds without errors or undefined references.
3. `bash scripts/reproduce.sh --experiments` runs every step on an existing checkout, each skipping existing outputs.

## Manual (owner)

- Read the paper PDF and the README on GitHub; check the author line and affiliation.
- Pick which AIMS repository is Marine AIMS, then add the link from `docs/launch/marine-aims-link.md` and update the link at the end of the README.
- Post the LinkedIn draft after making the repository and demo public.
