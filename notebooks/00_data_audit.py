# %% [markdown]
# # Data audit: can we trust this dataset for fault detection?
#
# This notebook checks the release before any modelling: do the files match the
# published index, what do the units and raw-voltage channels mean, how often
# did the bench log (and where did it skip), which channels are missing and
# where, where each fault switches on, and which load bin each run falls in.
# The findings drive the leakage and windowing rules used in every notebook
# that follows.

# %%
import matplotlib.pyplot as plt
import pandas as pd

from keyframe import audit, download, load, paths

paths.FIGURES.mkdir(parents=True, exist_ok=True)
paths.RESULTS.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## Do the files and row counts match the published index?

# %%
dataset_index = pd.read_csv(paths.RAW / "dataset_index.csv")
full_table = load.load_all(paths.RAW)

row_counts = dataset_index[~dataset_index["file_name"].str.endswith(download.LOCKBOX_FILE)].copy()
row_counts["run"] = row_counts["file_name"].str.split("/").str[-1].str.removesuffix(".csv")
row_counts["actual_rows"] = row_counts["run"].map(full_table.groupby("run").size())
row_counts["rows_match"] = row_counts["actual_rows"] == row_counts["data_rows"]
row_counts = row_counts[["run", "data_rows", "actual_rows", "rows_match", "columns"]]
row_counts.to_csv(paths.RESULTS / "00_row_counts.csv", index=False)
row_counts

# %% [markdown]
# ## What units do the channels use, and which are raw voltages?

# %%
_, reference_columns = load.read_csv_with_header(paths.RAW / "Reference_Data.csv")
_, scenario_columns = load.read_csv_with_header(paths.RAW / "AC_Fouling" / "AC_Fouling_40_Load.csv")

raw_voltage_channels = scenario_columns.frame[scenario_columns.frame["is_raw_voltage"]]
raw_voltage_channels[["full_name", "symbol", "unit"]]

# %% [markdown]
# ## How often did the bench log, and where does it skip?
#
# The tech stack notes say sampling is not a fixed 2 s: time stamps step
# alternately 1 s and 2 s (about 1.6 s on average). This section checks that
# pattern and flags any gap over 4 s.

# %%
intervals = audit.sampling_intervals(full_table)
step_values = sorted({round(v, 3) for counts in intervals["step_counts"] for v in counts})
step_totals = {v: sum(counts.get(v, 0) for counts in intervals["step_counts"]) for v in step_values}

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar([str(v) for v in step_totals], step_totals.values())
ax.set_xlabel("time step (s)")
ax.set_ylabel("row count across all runs")
ax.set_title("Logging interval: step sizes between consecutive rows")
fig.tight_layout()
fig.savefig(paths.FIGURES / "00_sampling_intervals.png", dpi=150)
plt.show()

intervals[["run", "max_gap_s", "gaps_s"]]

# %% [markdown]
# ## Which channels are missing, and where?

# %%
missing_channels = audit.missing_by_channel(full_table)
missing_channels.to_csv(paths.RESULTS / "00_missing_channels.csv", index=False)
missing_channels
