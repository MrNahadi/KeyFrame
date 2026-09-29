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

# %%
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import shap
from matplotlib import pyplot as plt

from keyframe import experiments, explain, features, paths

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
