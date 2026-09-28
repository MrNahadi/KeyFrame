# %% [markdown]
# # Feature engineering: do physics ratios, rolling stats or healthy-engine
# # residuals help a model generalise to an unseen load?
#
# Six feature sets (raw, +physics, +physics+rolling, and the same three with
# healthy-engine residuals in place of the raw day-marker channels) scored
# with logistic regression and LightGBM under the same leave-one-load-out
# (LOLO) protocol as notebook 02. Physics and rolling columns are computed
# once, before the LOLO loop, from `keyframe.features.build_feature_table`;
# residuals are fitted inside each fold, on that fold's healthy rows only.
#
# **Main findings:** read from the table below once computed.

# %%
import matplotlib.pyplot as plt
import pandas as pd

from keyframe import evaluate, experiments, features, paths

paths.FIGURES.mkdir(parents=True, exist_ok=True)
paths.RESULTS.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## Pooled and per-fold scores for every feature set x model combination
#
# Predictions come from the cached experiment outputs
# (`uv run python -m keyframe.experiments ablation ...`), not recomputed here.

# %%
MODELS = ["logreg", "lightgbm"]

summaries = []
for feature_set in features.FEATURE_SETS:
    for model in MODELS:
        predictions = experiments.load_ablation(feature_set, model)
        if predictions is None:
            continue
        summary = evaluate.summarise(predictions)
        summary.insert(0, "feature_set", feature_set)
        summary.insert(1, "model", model)
        summaries.append(summary)
results = pd.concat(summaries, ignore_index=True)
evaluate.log_results("03_ablation", results)
results

# %% [markdown]
# ## Which feature set x model generalises best to an unseen load?
#
# Ranked by pooled macro F1, the headline target.

# %%
pooled = results[results["fold"] == "pooled"].sort_values("macro_f1", ascending=False)
pooled

# %% [markdown]
# ## Per-fold spread: does any combination fall apart at a particular load?

# %%
per_fold = results[results["fold"] != "pooled"]
fig, ax = plt.subplots(figsize=(9, 5))
for (feature_set, model), group in per_fold.groupby(["feature_set", "model"]):
    group = group.sort_values("fold")
    ax.plot(
        group["fold"].astype(str),
        group["macro_f1"],
        marker="o",
        label=f"{feature_set} ({model})",
    )
ax.set_xlabel("held-out load bin")
ax.set_ylabel("macro F1")
ax.set_title("Per-fold macro F1 by feature set and model")
ax.legend(fontsize=7, ncol=2)
fig.tight_layout()
fig.savefig(paths.FIGURES / "03_ablation.png", dpi=150)
plt.show()

# %% [markdown]
# ## What this means for the next notebook
#
# Numbers above are read from the executed run, not tuned to hit a target.
# Notebook 03 part 2 prunes feature sets inside the training folds; part 3
# reports the shop-test score, findings and the decision.
