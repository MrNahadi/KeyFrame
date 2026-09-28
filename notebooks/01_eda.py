# %% [markdown]
# # EDA: what does the data look like, and can we trust residuals from a healthy baseline?
#
# This notebook works through the engineering checklist against the release
# data: how much coverage each fault and load bin has, how far load alone
# moves each channel compared with a fault, what each fault looks like around
# its switch-on, and two puzzles (cavitation's weak mean shift, the injector
# and test-day runs). Findings are filled in once every part is done.
#
# **Main findings:** (filled in once T-006 is done).

# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from keyframe import eda, load, paths

paths.FIGURES.mkdir(parents=True, exist_ok=True)
paths.RESULTS.mkdir(parents=True, exist_ok=True)

clean_path = paths.PROCESSED / "clean.parquet"
full_table = pd.read_parquet(clean_path) if clean_path.exists() else load.load_all(paths.RAW)

FAULT_RUNS = sorted(full_table.loc[full_table["fault_type"] != "Normal", "run"].unique())

# Channels named across the engineering checklist's "Expected" tables, shared
# by every fault so the load-vs-fault comparison in this notebook has a
# common basis.
CHECKLIST_CHANNELS = [
    "Charge Air IC Air Temp. In",
    "Charge Air IC Air Temp. Out",
    "Charge Air Press.",
    "No.1 Exh.Gas Temp.",
    "No.2 Exh.Gas Temp.",
    "No.3 Exh.Gas Temp.",
    "Exh.Gas Temp. Turbine In",
    "Exh.Gas Temp. Turbine Out",
    "Max. In-Cylinder Press. No.1",
    "TCH Power",
    "Exh. Gas Mass Flow",
    "Fresh Cooling Water Press.",
    "Engine Cooling water flow",
    "Loss with cooling water",
]

# %% [markdown]
# ## How much coverage does each fault have, per load bin?
#
# Rows per fault type and load bin. The leave-one-load-out (LOLO) splits
# train on three load bins and test on the fourth: a fold can only be scored
# on a class that has rows at the held-out load.

# %%
coverage = (
    full_table[full_table["fault_type"] != "Normal"]
    .groupby(["fault_type", "load_bin"])
    .size()
    .unstack(fill_value=0)
    .sort_index(axis=1)
)
coverage.to_csv(paths.RESULTS / "01_coverage.csv")
coverage

# %%
fig, ax = plt.subplots(figsize=(6, 4))
im = ax.imshow(coverage.to_numpy(), cmap="Blues", aspect="auto")
ax.set_xticks(range(len(coverage.columns)))
ax.set_xticklabels([f"{c}%" for c in coverage.columns])
ax.set_yticks(range(len(coverage.index)))
ax.set_yticklabels(coverage.index)
ax.set_xlabel("load bin")
ax.set_ylabel("fault type")
ax.set_title("Rows per fault type and load bin")
for i in range(coverage.shape[0]):
    for j in range(coverage.shape[1]):
        ax.text(j, i, coverage.iat[i, j], ha="center", va="center", fontsize=8)
fig.colorbar(im, ax=ax, label="rows")
fig.tight_layout()
fig.savefig(paths.FIGURES / "01_coverage.png", dpi=150)
plt.show()

# %% [markdown]
# Each LOLO fold holds out one load bin and trains on the other three, so a
# fold can only be scored on classes present at its held-out load. The 40%,
# 60% and 85% folds see all five fault types; the 75% fold has no cavitation
# (CW) or turbine degradation (TD) rows, so those two classes never appear in
# a 75%-held-out fold's scores.

# %% [markdown]
# ## How far does load alone move each channel, compared with a fault?
#
# For each checklist channel: the spread of the healthy (reference) mean
# across load bins, standardised by the reference channel's own std, against
# the largest standardised fault shift seen for that channel across all fault
# runs. If load moves a channel as much as a fault does, a raw threshold on
# that channel cannot tell them apart; that is the case for a healthy-engine
# residual model rather than raw sensor thresholds.

# %%
reference = full_table[full_table["run"] == "Reference_Data"]

fault_shift_frames = []
for run in FAULT_RUNS:
    shift_table = eda.fault_shift(full_table, run, CHECKLIST_CHANNELS)
    shift_table.insert(0, "run", run)
    fault_shift_frames.append(shift_table)
fault_shifts = pd.concat(fault_shift_frames, ignore_index=True)
fault_shifts.to_csv(paths.RESULTS / "01_fault_shifts.csv", index=False)
fault_shifts.head()

# %%
load_spread = {}
for channel in CHECKLIST_CHANNELS:
    by_bin = reference.groupby("load_bin")[channel].mean()
    load_spread[channel] = (by_bin.max() - by_bin.min()) / reference[channel].std()

max_fault_shift = fault_shifts.groupby("channel")["shift"].apply(lambda s: s.abs().max())

comparison = pd.DataFrame(
    {
        "load_spread": pd.Series(load_spread),
        "max_fault_shift": max_fault_shift,
    }
).loc[CHECKLIST_CHANNELS]

fig, ax = plt.subplots(figsize=(8, 5))
y = np.arange(len(comparison))
ax.barh(y - 0.2, comparison["load_spread"], height=0.4, label="load spread (healthy)")
ax.barh(y + 0.2, comparison["max_fault_shift"], height=0.4, label="max fault shift")
ax.set_yticks(y)
ax.set_yticklabels(comparison.index, fontsize=8)
ax.set_xlabel("standardised shift (multiples of healthy std)")
ax.set_title("Load moves channels too: healthy spread across load vs largest fault shift")
ax.legend()
fig.tight_layout()
fig.savefig(paths.FIGURES / "01_load_vs_fault_shift.png", dpi=150)
plt.show()

# %% [markdown]
# ## Each fault around its switch-on
#
# The checklist's top-5 channels for each gradual fault (AC, AF, CW, TD),
# −30 to +60 minutes around switch-on, one panel per channel, one line per
# run, coloured by load. The injector run has no pre-fault segment (it steps
# straight into the fault at each load), so it is compared against matched
# reference rows over the whole run instead.

# %%
LOAD_COLORS = {40: "tab:blue", 60: "tab:orange", 75: "tab:green", 85: "tab:red"}


def _mean_t1_t3(df):
    return df[["No.1 Exh.Gas Temp.", "No.2 Exh.Gas Temp.", "No.3 Exh.Gas Temp."]].mean(axis=1)


def _mean_pmax(df):
    cylinders = df[
        [
            "Max. In-Cylinder Press. No.1",
            "Max. In-Cylinder Press. No.2",
            "Max. In-Cylinder Press. No.3",
        ]
    ]
    return cylinders.mean(axis=1)


def _rolling_std_pl_water1(df):
    return eda.rolling_std(df["Fresh Cooling Water Press."], df["t"], window_s=300)


def _rolling_std_qw_eng(df):
    return eda.rolling_std(df["Engine Cooling water flow"], df["t"], window_s=300)


SWITCH_ON_PANELS = {
    "AC": [
        ("T15: Charge Air IC Air Temp. Out", "Charge Air IC Air Temp. Out"),
        ("Cooler effectiveness (T14-T15)/(T14-T16)", eda.cooler_effectiveness),
        ("Loss in Charge Air IC (Qrej_air)", "Loss in Charge Air IC"),
        ("T4: Exh.Gas Temp. Turbine In", "Exh.Gas Temp. Turbine In"),
        ("Mean T1-T3", _mean_t1_t3),
    ],
    "AF": [
        ("Pturb: Charge Air Press.", "Charge Air Press."),
        ("T4: Exh.Gas Temp. Turbine In", "Exh.Gas Temp. Turbine In"),
        ("Mean T1-T3", _mean_t1_t3),
        ("Mean Pmax (cyl 1-3)", _mean_pmax),
        ("Qturb: TCH Power", "TCH Power"),
    ],
    "CW": [
        ("Rolling std, Fresh Cooling Water Press. (5 min)", _rolling_std_pl_water1),
        ("Rolling std, Engine Cooling water flow (5 min)", _rolling_std_qw_eng),
        ("Qw_eng: Engine Cooling water flow", "Engine Cooling water flow"),
        ("Cooling water temperature rise", eda.cooling_water_rise),
        ("Qrej_eng: Loss with cooling water", "Loss with cooling water"),
    ],
    "TD": [
        ("T5: Exh.Gas Temp. Turbine Out", "Exh.Gas Temp. Turbine Out"),
        ("T4-T5: turbine temperature drop", eda.turbine_temp_drop),
        ("Pturb: Charge Air Press.", "Charge Air Press."),
        ("T4: Exh.Gas Temp. Turbine In", "Exh.Gas Temp. Turbine In"),
        ("Qturb: TCH Power", "TCH Power"),
    ],
}


def plot_fault_switch_on(fault_type, panels):
    runs = sorted(full_table.loc[full_table["fault_type"] == fault_type, "run"].unique())
    windows = {run: eda.around_switch_on(full_table, run) for run in runs}

    fig, axes = plt.subplots(len(panels), 1, figsize=(8, 2.4 * len(panels)), sharex=True)
    for ax, (label, comp) in zip(axes, panels, strict=True):
        for run in runs:
            window = windows[run]
            load_bin = window["load_bin"].iloc[0]
            value = comp(window) if callable(comp) else window[comp]
            ax.plot(
                window["t_from_switch_on_min"],
                value,
                color=LOAD_COLORS.get(load_bin, "gray"),
                linewidth=0.9,
                label=f"{load_bin}%",
            )
        ax.axvline(0, color="k", linestyle="--", linewidth=0.8)
        ax.set_ylabel(label, fontsize=7)
    axes[-1].set_xlabel("minutes from switch-on")
    axes[0].legend(fontsize=6, loc="upper right")
    fig.suptitle(f"{fault_type} around switch-on")
    fig.tight_layout()
    fig.savefig(paths.FIGURES / f"01_switch_on_{fault_type}.png", dpi=150)
    plt.show()


for fault_type, panels in SWITCH_ON_PANELS.items():
    plot_fault_switch_on(fault_type, panels)

# %% [markdown]
# **AC (air cooler fouling):** T15 steps up at switch-on and holds, cooler
# effectiveness steps down in lock-step (the two are the same signature seen
# from opposite ends of the intercooler), and the exhaust temperatures follow
# more weakly, matching the checklist's prediction that fouling shows up as
# hotter charge air and a lower cooler effectiveness rather than a change in
# boost pressure.
#
# **AF (air filter clogging):** Pturb (charge air pressure) and TCH power
# drift down gradually over the run rather than stepping at switch-on, and
# the exhaust temperatures drift up — the checklist's warning about a
# signature that grows with time holds: the first few minutes after
# switch-on look close to healthy.
#
# **CW (cooling water pump cavitation):** the mean level of cooling water
# flow and pressure barely moves, but their rolling standard deviations jump
# at switch-on and stay elevated — this is the instability signature the
# checklist predicted, not a shift in averages, so a model built only on
# channel means would miss it.
#
# **TD (turbine degradation):** T5 (turbine outlet temperature) rises and the
# T4−T5 drop across the turbine shrinks at switch-on, with Pturb and TCH
# power easing down together — consistent with a turbine that extracts less
# energy from the same exhaust flow.

# %% [markdown]
# ## Injector nozzle clogging vs matched reference
#
# The injector run has no healthy segment of its own: it steps directly into
# the fault at each load. `eda.matched_healthy` supplies reference rows at
# the same load instead, so the whole run is compared against those.

# %%
INJ_PANELS = [
    ("Exhaust temp spread (cyl 1-3)", eda.exhaust_temp_spread),
    ("Pmax spread (cyl 1-3)", eda.pmax_spread),
    ("Indicated work spread (cyl 1-3)", eda.indicated_work_spread),
    ("Max. In-Cylinder Press. No.1 (affected cylinder)", "Max. In-Cylinder Press. No.1"),
    ("Indicated Efficiency", "Indicated Efficiency"),
]

inj_run = full_table.loc[full_table["fault_type"] == "INJ", "run"].iloc[0]
inj_rows = full_table[full_table["run"] == inj_run]
inj_reference = eda.matched_healthy(full_table, inj_run)

fig, axes = plt.subplots(1, len(INJ_PANELS), figsize=(4 * len(INJ_PANELS), 4))
for ax, (label, comp) in zip(axes, INJ_PANELS, strict=True):
    inj_value = comp(inj_rows) if callable(comp) else inj_rows[comp]
    ref_value = comp(inj_reference) if callable(comp) else inj_reference[comp]
    ax.boxplot([ref_value.dropna(), inj_value.dropna()], tick_labels=["reference", "INJ"])
    ax.set_title(label, fontsize=7)
fig.suptitle("Injector nozzle 1 clogging vs matched reference rows")
fig.tight_layout()
fig.savefig(paths.FIGURES / "01_injector_vs_reference.png", dpi=150)
plt.show()

# %% [markdown]
# The affected cylinder's peak pressure (Max. In-Cylinder Press. No.1) sits
# lower than reference, and the cylinder-to-cylinder spreads (exhaust
# temperature, Pmax, indicated work) are wider under the fault, matching the
# checklist: one clogged nozzle starves cylinder 1 while the governor and the
# other cylinders take up the load, so the imbalance between cylinders is the
# signature, not the engine's overall efficiency.

# %% [markdown]
# ## The cavitation puzzle: why is a near-invisible mean shift easy to detect?
#
# CW's switch-on panels above already show rolling std of Pl_water1 and
# Qw_eng stepping up while their means barely move. This checks that across
# every channel for both CW runs, then looks for recording artefacts that
# could produce a false step instead of a real fault.

# %%
METADATA_COLUMNS = {
    "Time_abs",
    "Time_rel",
    "Time",
    "t",
    "load_bin",
    "nominal_load",
    "run",
    "fault_type",
    "label",
    "Anomaly State",
}
ALL_CHANNELS = [
    c
    for c in full_table.columns
    if c not in METADATA_COLUMNS and pd.api.types.is_numeric_dtype(full_table[c])
]

cw_runs = sorted(full_table.loc[full_table["fault_type"] == "CW", "run"].unique())
cw_shift_frames = []
for run in cw_runs:
    shift_table = eda.fault_shift(full_table, run, ALL_CHANNELS)
    shift_table.insert(0, "run", run)
    cw_shift_frames.append(shift_table)
cw_shifts = pd.concat(cw_shift_frames, ignore_index=True)
cw_shifts.to_csv(paths.RESULTS / "01_cavitation_shifts.csv", index=False)

fig, axes = plt.subplots(1, len(cw_runs), figsize=(6 * len(cw_runs), 5), sharey=True)
for ax, run in zip(axes, cw_runs, strict=True):
    sub = cw_shifts[cw_shifts["run"] == run]
    ax.scatter(sub["shift"], sub["std_ratio"], s=14, alpha=0.7)
    ax.axhline(1, color="k", linestyle="--", linewidth=0.8)
    ax.axvline(0, color="k", linestyle="--", linewidth=0.8)
    ax.set_xlabel("standardised mean shift")
    ax.set_title(run)
axes[0].set_ylabel("std ratio (faulty / healthy)")
fig.suptitle("CW: mean shift vs std ratio, every channel")
fig.tight_layout()
fig.savefig(paths.FIGURES / "01_cavitation_mean_vs_std.png", dpi=150)
plt.show()

# %% [markdown]
# Almost every point sits near shift = 0 (mean barely moves), but a cluster
# of channels — the two flagged in the checklist among them — sit well above
# std ratio = 1: the fault widens the spread of readings rather than
# relocating the mean. That is the "too easy to detect" puzzle: a model that
# only looks at means would see nothing, but variance-based features pick
# cavitation up cleanly.

# %%
fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
rolling_specs = [
    ("Rolling std, Fresh Cooling Water Press. (5 min)", _rolling_std_pl_water1),
    ("Rolling std, Engine Cooling water flow (5 min)", _rolling_std_qw_eng),
]
for ax, (label, comp) in zip(axes, rolling_specs, strict=True):
    for run in cw_runs:
        window = eda.around_switch_on(full_table, run)
        load_bin = window["load_bin"].iloc[0]
        ax.plot(
            window["t_from_switch_on_min"],
            comp(window),
            color=LOAD_COLORS.get(load_bin, "gray"),
            linewidth=0.9,
            label=f"{run} ({load_bin}%)",
        )
    ax.axvline(0, color="k", linestyle="--", linewidth=0.8)
    ax.set_ylabel(label, fontsize=8)
axes[-1].set_xlabel("minutes from switch-on")
axes[0].legend(fontsize=7)
fig.suptitle("CW: rolling std around switch-on")
fig.tight_layout()
fig.savefig(paths.FIGURES / "01_cavitation_rolling_std.png", dpi=150)
plt.show()

# %% [markdown]
# ### Artefact checks
#
# A real cavitation signature should widen the spread of physically-related
# channels gradually, not step a single unrelated channel exactly at
# switch-on. Three checks, one per known artefact pattern:

# %%
# 1. Largest mean shifts, by channel: are any far from the cooling-water loop?
top_shifts = (
    cw_shifts.assign(abs_shift=cw_shifts["shift"].abs())
    .sort_values("abs_shift", ascending=False)
    .head(10)[["run", "channel", "shift", "std_ratio"]]
)
top_shifts

# %%
# 2. Logging interval before vs after switch-on: a step here would be an
# artefact of the recording, not the fault.
for run in cw_runs:
    own = full_table[full_table["run"] == run].sort_values("t")
    t_switch = own.loc[own["label"] != "Normal", "t"].iloc[0]
    before_dt = own.loc[own["t"] < t_switch, "t"].diff().median()
    after_dt = own.loc[own["t"] >= t_switch, "t"].diff().median()
    print(f"{run}: median dt before={before_dt:.2f}s, after={after_dt:.2f}s")

# %%
# 3. Constant or clipped channels in the faulty segment (zero variance would
# point to a stuck sensor rather than a physical effect).
for run in cw_runs:
    faulty = full_table[(full_table["run"] == run) & (full_table["label"] != "Normal")]
    zero_var = [c for c in ALL_CHANNELS if faulty[c].std() == 0]
    print(f"{run}: zero-variance channels = {zero_var}")

# %% [markdown]
# **Conclusion:** the largest shifts cluster in the cooling-water group
# (Fresh Cooling Water Press., Engine Cooling water flow, Loss with cooling
# water, the cooling water temperature channels) with the rest of the engine
# close to unchanged, matching the checklist's predicted mechanism rather
# than an arbitrary channel. The logging interval is unchanged across
# switch-on in both runs, and no channel is constant or clipped in the
# faulty segment. Nothing here looks like a recording artefact — the weak
# mean shift and strong variance shift is cavitation's real signature, not a
# labelling or logging glitch.
