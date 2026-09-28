# 02 Data audit: requirements

## Reading files

- R1. `keyframe.load.read_csv_with_header(path)` returns the data as a DataFrame keyed by full variable names (header row 1), plus a `ColumnInfo` table (full name, symbol, unit) from rows 2 and 3. Data start on row 4. Empty cells are NaN, never zero. Columns are numeric (float) except `Anomaly State` (int).
- R2. Symbols are metadata only: several repeat (`Pmax`, `Pmin`, `Wi`, `We`), so they must never be used as keys.
- R3. The six raw-voltage channels (`Pl_lo`, `Pl_fuel`, `Pl_water1`, `Pl_water2`, `Pl_loturb`, `Pl_valve`, unit `V`) are flagged in `ColumnInfo` (`is_raw_voltage`).

## One clean table

- R4. `keyframe.load.load_run(path)` adds metadata columns to one file:
  - `run`: file stem, e.g. `AC_Fouling_40_Load`; `Reference_Data` for the reference file.
  - `fault_type`: the run's fault code (`AC`, `AF`, `INJ`, `CW`, `TD`), `Normal` for the reference file. Mapping from folder/file name prefix.
  - `label`: the class of the row: `fault_type` where `Anomaly State` = 1, else `Normal`. Reference rows are `Normal`.
  - `t`: seconds since the start of the file (`Time_rel` for scenario files; `Time - Time.iloc[0]` for the reference file).
  - `load_bin`: from `Shaft Power` via R6.
  - `nominal_load`: the file's nominal load as text from `dataset_index.csv` (`40%`, `40%, 60%, 85% (stepped)`, `reference operating range`).
- R5. `keyframe.load.load_all(raw_dir=paths.RAW)` concatenates the 15 files in `raw_dir` (14 runs + reference) into one DataFrame with the union of columns. Columns missing from a file (the reference has no `Turbine Back Pressure`, `Time_abs`, `Time_rel`, `Anomaly State`) are NaN. It never reads `data/lockbox/`. Row order: files sorted by path, rows in file order.
- R6. `keyframe.splits.load_bin(shaft_power_kw)` maps shaft power to 40, 60, 75 or 85: below 130 kW → 40, 130 up to 175 → 60, 175 up to 207 → 75, 207 and above → 85. Works on a scalar or a Series; NaN input raises `ValueError`.

## Audit

- R7. `keyframe.audit.sampling_intervals(df)` returns, per run, the count of each time step between consecutive rows (1 s, 2 s, other) and the largest gap in seconds. Any step over 4 s is a gap and is listed.
- R8. `keyframe.audit.missing_by_channel(df)` returns, per run and channel, the share of missing values. It must confirm `Compressor Filter Loss` and `Turbine Back Pressure` are fully empty in exactly the five runs the dataset README names, and report any other channel with missing values.
- R9. `keyframe.audit.switch_on_points(df)` returns one row per scenario run: the row index within the run, `t` and `Time_abs` of the first `Anomaly State` = 1 row, and the length of the healthy and faulty segments in rows and minutes. Injector runs report no switch-on (all faulty from the first row).
- R10. `keyframe.audit.load_bin_agreement(df)` returns, per fixed-load run, the share of rows whose `load_bin` matches the nominal load. Stepped runs and the reference file report the row count per bin instead.
- R11. `keyframe.audit.write_clean_table(df, path=paths.PROCESSED / "clean.parquet")` writes the clean table as Parquet and returns the path. The table keeps every channel (excluded channels are dropped later, at feature time, not here).

## Integrity against the release

- R12. Tests marked `data` check, on the real files: each file's row count equals `data_rows` in `data/raw/dataset_index.csv`; scenario files have 73 columns and the reference 70; class totals are Normal 51,893, AC 17,500, AF 15,074, INJ 6,492 (the other 6,791 injector rows are in the lockbox), CW 9,174, TD 7,846; every fixed-load scenario run has exactly one switch-on (labels go 0…0 then 1…1, never back).

## Notebook 00

- R13. `notebooks/00_data_audit.py` opens with a markdown cell for an engine engineer: what the notebook answers and its main findings in plain words (filled in once the numbers are known).
- R14. Sections, each headed by a question or finding: which files and how many rows (table vs the index); what units and which channels are raw voltages; how often the bench logged (the 1 s / 2 s pattern, gaps); which channels are missing where; where each fault switches on (table plus one figure: a key channel per run with the switch-on marked); which load bins each run falls in; what this means for the next notebooks (the leakage and windowing rules that follow from the audit).
- R15. Figures saved to `reports/figures/00_*.png` (150 dpi); audit tables saved to `reports/results/00_*.csv`; the clean table saved via R11.
- R16. The notebook calls package functions for all logic; cells only load, call, display and plot.
