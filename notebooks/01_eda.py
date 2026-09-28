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
