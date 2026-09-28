# 02 Data audit: tickets

## T-001: Read one dataset CSV with its three-row header

Status: open
Blocked by:
Slice: Read any release CSV into a DataFrame keyed by full names, with a ColumnInfo table of symbols, units and raw-voltage flags.
Test seam: `keyframe.load.read_csv_with_header(path)` (public interface only)
Context: requirements R1-R3; tech-stack.md "Python" and "Data and leakage"; `head -3 data/raw/AC_Fouling/AC_Fouling_85_Load.csv | cut -c1-400`; `head -3 data/raw/Reference_Data.csv | cut -c1-300`
Acceptance:
- [ ] A synthetic fixture CSV with repeated symbols, a `°C` unit and an empty column round-trips: full-name keys, NaN for empty cells, float dtypes, int `Anomaly State`
- [ ] ColumnInfo marks exactly the six `Pl_*` channels as raw voltage in a real scenario file (data-marked test)
- [ ] Shared test fixtures that write synthetic three-row-header CSVs live in `tests/conftest.py`
Notes:

## T-002: Load runs with metadata into one table

Status: open
Blocked by: T-001
Slice: Load a scenario or reference file with run, fault_type, label, t, load_bin and nominal_load columns, and concatenate all raw files into one table.
Test seam: `keyframe.load.load_run(path)`, `keyframe.load.load_all(raw_dir)`, `keyframe.splits.load_bin(x)`
Context: requirements R4-R6; `data/raw/dataset_index.csv` (read with pandas, show columns file_name and nominal_load); tests/conftest.py
Acceptance:
- [ ] `load_bin` puts 129.9 → 40, 130 → 60, 174.9 → 60, 175 → 75, 206.9 → 75, 207 → 85, and raises on NaN
- [ ] A synthetic scenario run labels rows before switch-on `Normal` and after it with the fault code; a synthetic reference file gets `Normal`, `t` from `Time`, NaN `Anomaly State`
- [ ] `load_all` on a synthetic raw folder unions columns, never reads a `lockbox` folder, and orders rows by file path then file order
Notes:

## T-003: Audit functions for sampling, missing channels, switch-on and load bins

Status: open
Blocked by: T-002
Slice: Functions that turn the one table into the audit tables notebook 00 shows, and write it as Parquet.
Test seam: `keyframe.audit.sampling_intervals`, `missing_by_channel`, `switch_on_points`, `load_bin_agreement`, `write_clean_table`
Context: requirements R7-R11; keyframe/load.py (signatures only: `grep -n '^def ' keyframe/load.py`); tests/conftest.py
Acceptance:
- [ ] Each function is tested on a small synthetic table with a known answer (a 7 s gap is reported; an all-empty channel is 100% missing; a run with no switch-on reports none; bin agreement is 1.0 for a run fully inside its bin)
- [ ] `write_clean_table` round-trips through Parquet with dtypes preserved
Notes:

## T-004: Check the real files against the dataset index

Status: open
Blocked by: T-003
Slice: Data-marked tests prove the one table matches the release exactly; the clean Parquet table is written.
Test seam: `keyframe.load.load_all()`, `keyframe.audit.switch_on_points`, `keyframe.audit.missing_by_channel`
Context: requirements R8, R12; `data/raw/dataset_index.csv`; tests/test_download.py (skip pattern for missing data)
Acceptance:
- [ ] Per-file row counts equal `data_rows` in the index; 73 columns per scenario file, 70 for the reference
- [ ] Class totals equal R12 exactly (107,979 rows in total)
- [ ] Every fixed-load run has exactly one switch-on and never returns to 0; injector run has none
- [ ] dPf and dPex are fully empty in exactly the five runs named in R8
- [ ] Tests skip cleanly when `data/raw` is absent
Notes:

## T-005: Notebook 00, part 1: files, units, sampling and missing channels

Status: open
Blocked by: T-004
Slice: Notebook 00 runs end to end and shows the first four audit sections with tables and one sampling figure.
Test seam: executing `notebooks/00_data_audit.py` with jupytext
Context: requirements R13-R16; tech-stack.md "Notebooks"; keyframe/audit.py (signatures only: `grep -n '^def ' keyframe/*.py`)
Acceptance:
- [ ] Sections: files and row counts vs index; units and raw-voltage channels; logging interval (1 s / 2 s pattern, gaps over 4 s); missing channels
- [ ] Figure `reports/figures/00_sampling_intervals.png`; tables `reports/results/00_row_counts.csv`, `00_missing_channels.csv`
- [ ] The notebook executes with the jupytext command and the executed `.ipynb` is committed
Notes:

## T-006: Notebook 00, part 2: switch-on points, load bins and findings

Status: open
Blocked by: T-005
Slice: Notebook 00 locates every switch-on, shows load-bin agreement, writes the clean table and opens with a findings summary for an engine engineer.
Test seam: executing `notebooks/00_data_audit.py` with jupytext
Context: requirements R9-R11, R13-R15; `grep -n '^# %%' notebooks/00_data_audit.py` then read only the last section and the first cell
Acceptance:
- [ ] Switch-on table saved to `reports/results/00_switch_on_points.csv`; figure `reports/figures/00_switch_on.png` shows one key channel per fixed-load run with the switch-on marked
- [ ] Load-bin table saved to `reports/results/00_load_bins.csv`
- [ ] `data/processed/clean.parquet` written by the notebook
- [ ] The first markdown cell states the findings in plain words with the real numbers; the last section lists what the audit means for the next notebooks
- [ ] Notebook executes and the executed `.ipynb` is committed
Notes:
