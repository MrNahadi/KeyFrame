# 02 Data audit: plan

Roadmap item 2 (brief milestone 2). Done when row counts match the dataset index and every fault switch-on point is located.

## Approach

Build the loader first, with tests on tiny synthetic CSVs that copy the real three-row header. Then add a one-table builder, check it against `dataset_index.csv` with data-marked tests, and only then write notebook 00, which calls the package and presents the findings for an engine engineer.

## Modules touched

- `keyframe/load.py`: reading one CSV with its three-row header, loading a run with metadata columns, loading everything into one table.
- `keyframe/splits.py`: only `load_bin()` for now (the LOLO splitter comes in item 4).
- `keyframe/audit.py`: sampling intervals, missing channels, switch-on points, load-bin agreement, writing the clean Parquet table.
- `tests/conftest.py`, `tests/test_load.py`, `tests/test_audit.py`, `tests/test_data_integrity.py` (marked `data`).
- `notebooks/00_data_audit.py` + executed `.ipynb`; `reports/figures/00_*.png`; `reports/results/00_*.csv`.

## Order of work

T-001 reader → T-002 run loader and one table → T-003 audit functions → T-004 real-data integrity tests and the Parquet table → T-005 notebook part 1 → T-006 notebook part 2.

## New dependencies

None.
