# 02 Data audit: validation

## Automated

1. `uv run pytest` passes, including the `data`-marked integrity tests (R12) with the dataset downloaded.
2. `uv run ruff check .`, `uv run ruff format --check .` and `uv run mypy` pass.
3. `uv run jupytext --set-kernel python3 --to ipynb --execute notebooks/00_data_audit.py` runs without error and writes `data/processed/clean.parquet`.
4. `uv run python -c "import pandas as pd; d=pd.read_parquet('data/processed/clean.parquet'); print(d.shape, d['label'].value_counts().to_dict())"` shows 107,979 rows and the R12 class totals.

## Manual (owner)

- Read the top cell of notebook 00 on GitHub: does it tell an engine engineer, in under a minute, what is in the data and what to watch out for?
- Check the switch-on figure: does each marked switch-on line up with a visible change in the plotted channel?
