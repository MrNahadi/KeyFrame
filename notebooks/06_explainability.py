# %% [markdown]
# # What does the model actually key on, and does that match the physics?
#
# SHAP TreeExplainer values for the tuned XGBoost model, refit per held-out
# load (`keyframe.experiments.run_shap`), on a seeded stratified sample of
# held-out rows plus every held-out row within 10 minutes of a fault's
# switch-on. This first section builds the base views
# (`keyframe.explain.feature_ranking`, `channel_ranking`, `grouped_shap`,
# `waterfall`, R4): per-class beeswarms, grouped SHAP per class, and a
# grouped waterfall for one moment of each fault shortly after switch-on.
# The physics check, cross-checks and findings follow in later sections.
#
# ## Findings for an engine engineer
#
# **Which readings drive each diagnosis** (top 5 features by mean |SHAP| on
# each fault's own held-out rows, all four load folds combined):
#
# - **AC (charge-air cooler fouling):** charge-air cooler outlet air temperature
#   (T15, level and 60/300/900 s rolling means), plus mechanical efficiency.
# - **INJ (injector fault):** the exhaust gas temperatures of cylinder 3
#   (T1-T3), its deviation from the other cylinders and the cylinder spread.
# - **AF (air filter clogging):** engine cooling water flow and two fuel
#   temperature channels.
# - **CW (cooling water cavitation):** sea cooling water pressure, LO cooling
#   water temperature in and charge-air cooler cooling water temperature in.
# - **TD (turbine degradation):** indicated efficiency (rolling std), fuel flow
#   per kW and lubricating-oil system flows and pressure.
#
# **Physics check** (`reports/physics_check.md`, pre-registered checklist): **2
# of 5 faults pass, target was 4 of 5, so the target is not met.** AC and INJ
# are explained by the mechanism an engineer would expect. AF and CW lean on
# day-dependent channels (fuel temperature, sea water pressure, LO water
# temperature), which is the test-day shortcut the checklist warned about: they
# tell us which day a run was recorded on, not that a fault is present. TD's top
# features are not day-dependent but none is in the expected turbine set
# (Pturb, T4, T5, Qturb); they look like downstream consequences or load
# proxies and should not be trusted without residualising against load.
#
# **Where explanations are unreliable:** many sensors are near-duplicates
# (rolling windows of one channel, cylinder temperatures that move together, the
# cooling circuits that share load and temperature). SHAP splits credit among
# correlated features arbitrarily, so a single feature's rank is not evidence
# that it is the cause; read the grouped-by-source views, not single bars. The
# cross-checks agree only modestly: grouped permutation importance vs mean
# |SHAP| has Spearman r of 0.07 to 0.29 across folds, and LIME and SHAP share
# about 2.7 of their top 8 features on average. Treat the AC and INJ stories as
# credible and the AF, CW and TD stories as unconfirmed.

# %%
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import shap
from lime.lime_tabular import LimeTabularExplainer
from matplotlib import pyplot as plt
from sklearn.inspection import PartialDependenceDisplay

from keyframe import SEED, experiments, explain, features, paths, tuning

paths.FIGURES.mkdir(parents=True, exist_ok=True)
paths.RESULTS.mkdir(parents=True, exist_ok=True)

FOLDS = [40, 60, 75, 85]
CLASSES = ["AC", "AF", "CW", "INJ", "Normal", "TD"]
FAULT_CLASSES = [c for c in CLASSES if c != "Normal"]
SHAP_DIR = paths.PROCESSED / "experiments"

first_row_group = pq.ParquetFile(paths.PROCESSED / "features.parquet").read_row_group(0).to_pandas()
columns = features.FEATURE_SETS[experiments.MODELLING_FEATURE_SET].columns(first_row_group)


def _load_fold(fold: int) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    metadata = pd.read_parquet(SHAP_DIR / f"shap_fold{fold}.parquet")
    npz = np.load(SHAP_DIR / f"shap_fold{fold}.npz", allow_pickle=True)
    return metadata, npz["shap_values"], list(npz["classes"])


folds = {fold: _load_fold(fold) for fold in FOLDS}


def class_shap(cls: str) -> np.ndarray:
    """This class's own-class SHAP values for its rows, pooled across every fold that has
    held-out rows of it."""
    parts = []
    for metadata, shap_values, classes in folds.values():
        mask = (metadata["y_true"] == cls).to_numpy()
        if mask.any():
            parts.append(shap_values[mask, :, classes.index(cls)])
    return np.concatenate(parts, axis=0)


# %% [markdown]
# ## Per-class beeswarm: top 15 features (R10)

# %%
for cls in CLASSES:
    values = class_shap(cls)
    top15 = list(explain.feature_ranking(values, columns).index[:15])
    top_idx = [columns.index(c) for c in top15]
    shap.summary_plot(values[:, top_idx], feature_names=top15, show=False, plot_size=(8, 6))
    plt.title(f"SHAP beeswarm — {cls} (top 15 features)")
    plt.tight_layout()
    plt.savefig(paths.FIGURES / f"06_beeswarm_{cls}.png", dpi=150)
    plt.close()

# %% [markdown]
# ## Grouped SHAP per class (R4, R10)
#
# Signed SHAP summed within each sensor group (`keyframe.explain.grouped_shap`), averaged
# over each class's own rows.

# %%
grouped_by_class = pd.DataFrame(
    {cls: explain.grouped_shap(class_shap(cls), columns) for cls in CLASSES}
)
grouped_by_class.to_csv(paths.RESULTS / "06_grouped_shap.csv")

grouped_by_class.plot.barh(figsize=(8, 6))
plt.xlabel("mean signed SHAP")
plt.title("Grouped SHAP per class")
plt.tight_layout()
plt.savefig(paths.FIGURES / "06_grouped_shap.png", dpi=150)
plt.close()

# %% [markdown]
# ## Grouped waterfall for one moment of each fault, shortly after switch-on (R4, R10)

# %%
switch_t = (
    pd.read_parquet(paths.PROCESSED / "clean.parquet", columns=["run", "t", "label"])
    .loc[lambda d: d["label"] != "Normal"]
    .groupby("run")["t"]
    .min()
)


def switch_on_row(cls: str) -> tuple[int, int]:
    """(fold, row index) of `cls`'s held-out row closest to (at or after) its run's
    switch-on, across every fold."""
    best: tuple[int, int, float] | None = None
    for fold, (metadata, _, _) in folds.items():
        candidates = metadata[metadata["y_true"] == cls].join(switch_t.rename("t_switch"), on="run")
        candidates = candidates.dropna(subset=["t_switch"])
        candidates = candidates[candidates["t"] >= candidates["t_switch"]]
        if candidates.empty:
            continue
        delay = candidates["t"] - candidates["t_switch"]
        row_id = delay.idxmin()
        if best is None or delay[row_id] < best[2]:
            best = (fold, row_id, delay[row_id])
    assert best is not None, f"no held-out row after switch-on for {cls}"
    return best[0], best[1]


for cls in FAULT_CLASSES:
    fold, row_id = switch_on_row(cls)
    metadata, shap_values, classes = folds[fold]
    position = metadata.index.get_loc(row_id)
    grouped, top = explain.waterfall(shap_values[position, :, classes.index(cls)], columns)

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    grouped.sort_values().plot.barh(ax=axes[0])
    axes[0].set_title(f"{cls}: grouped SHAP")
    top.sort_values().plot.barh(ax=axes[1])
    axes[1].set_title(f"{cls}: top individual features")
    fig.suptitle(
        f"{cls} — fold {fold}, {metadata.loc[row_id, 't'] - switch_t[metadata.loc[row_id, 'run']]:.0f}s after switch-on"
    )
    plt.tight_layout()
    plt.savefig(paths.FIGURES / f"06_waterfall_{cls}.png", dpi=150)
    plt.close()

# %% [markdown]
# ## Cross-check 1: grouped permutation importance vs. SHAP, per fold (R7)
#
# `keyframe.experiments.run_crosscheck` refits the model per outer fold, runs grouped
# permutation importance (`keyframe.features.outer_permutation_importance`) on the exact
# rows `run_shap` explained, and rank-correlates it (Spearman) against those rows' mean
# total |SHAP| per source group — the same grouping permutation importance uses.

# %%
feature_table = experiments.load_feature_table()

crosscheck_path = paths.RESULTS / "06_crosscheck.csv"
if not crosscheck_path.exists():
    experiments.run_crosscheck(feature_table)
crosscheck = pd.read_csv(crosscheck_path)
crosscheck

# %% [markdown]
# ## Partial dependence and ICE for the top 2 features of three faults, one fold (R8)
#
# Fold 60% is one of the two folds with every fault class among its held-out rows, so one
# model fit there serves both this section and the LIME comparison below.

# %%
PDP_FOLD = 60
pdp_params = experiments.load_tuned_params("xgboost", PDP_FOLD)
pdp_model = tuning.MODEL_BUILDERS["xgboost"](pdp_params)
pdp_train = feature_table[feature_table["load_bin"] != PDP_FOLD]
pdp_model.fit(pdp_train[columns], pdp_train["label"])

pdp_metadata, pdp_shap_values, pdp_classes = folds[PDP_FOLD]
X_pdp = feature_table.loc[pdp_metadata.index, columns]

for cls in ["AC", "INJ", "TD"]:
    top2 = list(explain.feature_ranking(class_shap(cls), columns).index[:2])
    display = PartialDependenceDisplay.from_estimator(
        pdp_model, X_pdp, top2, target=cls, kind="both"
    )
    display.figure_.suptitle(f"PDP/ICE — {cls} (fold {PDP_FOLD}, top 2 SHAP features)")
    display.figure_.tight_layout()
    display.figure_.savefig(paths.FIGURES / f"06_pdp_{cls}.png", dpi=150)
    plt.close(display.figure_)

# %% [markdown]
# ## One LIME comparison for 3 moments, one per fault (R9)
#
# LIME's top 8 features for one held-out row per fault, at or after its run's switch-on
# (`switch_on_row`, restricted to `PDP_FOLD` so the same fitted model explains every row),
# against SHAP's top 8 for that same row. LIME is used only here, once.


# %%
def switch_on_row_in_fold(cls: str, fold: int) -> int:
    """The held-out row of `cls` closest to (at or after) its run's switch-on, in `fold`."""
    metadata, _, _ = folds[fold]
    candidates = metadata[metadata["y_true"] == cls].join(switch_t.rename("t_switch"), on="run")
    candidates = candidates.dropna(subset=["t_switch"])
    candidates = candidates[candidates["t"] >= candidates["t_switch"]]
    delay = candidates["t"] - candidates["t_switch"]
    return delay.idxmin()


lime_explainer = LimeTabularExplainer(
    training_data=X_pdp.to_numpy(),
    feature_names=columns,
    class_names=list(pdp_model.classes_),
    mode="classification",
    random_state=SEED,
)

lime_rows = []
for cls in ["AC", "AF", "CW"]:
    row_id = switch_on_row_in_fold(cls, PDP_FOLD)
    row = feature_table.loc[row_id, columns]
    class_idx = list(pdp_model.classes_).index(cls)

    explanation = lime_explainer.explain_instance(
        row.to_numpy(), pdp_model.predict_proba, num_features=8, labels=[class_idx]
    )
    lime_top = {
        columns[i] for i, _ in sorted(explanation.as_map()[class_idx], key=lambda p: abs(p[1]))[-8:]
    }

    position = pdp_metadata.index.get_loc(row_id)
    _, shap_top = explain.waterfall(
        pdp_shap_values[position, :, list(pdp_classes).index(cls)], columns
    )
    shap_top_set = set(shap_top.index)

    lime_rows.append(
        {
            "fault": cls,
            "row": row_id,
            "lime_top8": ", ".join(sorted(lime_top)),
            "shap_top8": ", ".join(sorted(shap_top_set)),
            "overlap": len(lime_top & shap_top_set),
        }
    )

lime_comparison = pd.DataFrame(lime_rows)
lime_comparison

# %%
print(
    f"LIME and SHAP agree on {lime_comparison['overlap'].mean():.1f} of 8 top features on "
    "average across these three moments: both explainers, one linear and local, the other "
    "exact for trees, point at largely the same channels for a fault shortly after switch-on."
)
