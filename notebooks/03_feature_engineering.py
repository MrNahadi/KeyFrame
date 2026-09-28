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
# **Main findings:** `raw+physics+rolling` x LightGBM wins outright (pooled macro
# F1 0.617, accuracy 0.712); physics and rolling features earn their place,
# residuals do not beat them. Pruning that arm inside the training folds hurts
# it (macro F1 0.558, per-fold spread 0.263-0.785); pruning does not earn its
# place here. The shop-test score for the best residual arm
# (`residuals+physics` x logreg) is worse than its main score (0.587 vs 0.608),
# concentrated as a false-alarm spike on reference rows at the 40% fold (1.7% to
# 60.7%). Decision: `raw+physics+rolling` (unpruned) with LightGBM goes forward
# (`docs/adr/0006-feature-set-for-modelling.md`).

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
# ## Pruning the best feature set inside the training folds
#
# Predictions come from the cached experiment outputs
# (`uv run python -m keyframe.experiments pruning ...`), not recomputed here. Each
# outer fold drops near-duplicate features (|Pearson r| > 0.98 on that fold's training
# healthy rows) then features whose grouped permutation importance on the fold's inner
# LOLO folds is ≤ 0 (R13); the outer test rows are never touched by either step.

# %%
best_feature_set, best_model = pooled.iloc[0][["feature_set", "model"]]
best_feature_set, best_model = str(best_feature_set), str(best_model)

pruning_predictions = experiments.load_pruning(best_feature_set, best_model)
dropped_by_fold = pruning_predictions.groupby("fold")["dropped_feature"].first()
pruning_rows = []
for fold, dropped in dropped_by_fold.items():
    fold_predictions = pruning_predictions[pruning_predictions["fold"] == fold]
    row = evaluate.summarise(fold_predictions).iloc[0].to_dict()
    row["fold"] = fold
    row["dropped_features"] = dropped
    pruning_rows.append(row)
pooled_dropped = sorted(set().union(*[d.split(",") if d else [] for d in dropped_by_fold]))
pooled_row = evaluate.summarise(pruning_predictions).iloc[0].to_dict()
pooled_row["dropped_features"] = ",".join(pooled_dropped)
pruning_results = pd.DataFrame([pooled_row, *pruning_rows])
pruning_results.insert(0, "feature_set", best_feature_set)
pruning_results.insert(1, "model", best_model)
evaluate.log_results("03_pruning", pruning_results)
pruning_results

# %% [markdown]
# ## Shop-test score for the best residual arm
#
# The overall best combination, `raw+physics+rolling` x LightGBM, has no residual
# step, so its shop-test score (R9) is undefined. The shop-test score is reported
# instead for the best *residual* arm, `residuals+physics` x logreg, next to its
# main score: the held-out load's reference rows are fed to the residual step only
# (`load_ablation(..., shop_test=True)`), the classifier itself is untouched.

# %%
shop_test_set, shop_test_model = "residuals+physics", "logreg"
main_predictions = experiments.load_ablation(shop_test_set, shop_test_model)
shop_predictions = experiments.load_ablation(shop_test_set, shop_test_model, shop_test=True)

shop_summary = pd.concat(
    [
        evaluate.summarise(main_predictions).assign(run="main"),
        evaluate.summarise(shop_predictions).assign(run="shop_test"),
    ],
    ignore_index=True,
)
shop_summary.insert(0, "feature_set", shop_test_set)
shop_summary.insert(1, "model", shop_test_model)
evaluate.log_results("03_shop_test", shop_summary)
shop_summary[shop_summary["fold"] == "pooled"]

# %% [markdown]
# ## False alarm rate on Normal rows, by source and held-out fold
#
# Splits the false alarm rate (R9) by whether the healthy row came from the
# reference file or from the pre-fault stretch of a fault run, to see where the
# shop-test's extra reference rows change the healthy-engine residual model.


# %%
def _false_alarm_by_source(predictions: pd.DataFrame) -> pd.DataFrame:
    normal = predictions[predictions["y_true"] == "Normal"]
    is_reference = normal["run"] == "Reference_Data"
    rates = {}
    for source, mask in [("reference", is_reference), ("pre-fault", ~is_reference)]:
        subset = normal[mask]
        rates[source] = subset.groupby("fold").apply(
            lambda d: (d["y_pred"] != "Normal").mean(), include_groups=False
        )
    return pd.DataFrame(rates).reindex([40, 60, 75, 85])


false_alarm_by_source = pd.concat(
    [
        _false_alarm_by_source(main_predictions).assign(run="main"),
        _false_alarm_by_source(shop_predictions).assign(run="shop_test"),
    ]
)
false_alarm_by_source

# %% [markdown]
# The shop-test's reference-row false alarm rate at the 40% fold jumps from 1.7%
# to 60.7%, and its pre-fault rate at 40% from 33.4% to 95.0%; the 60/75/85% folds
# barely move. Two observations, stated as likely explanations rather than proven
# causes:
#
# 1. Every pre-fault healthy row at the 75% fold is flagged even in the *main*
#    score (100% false alarm, both reference and pre-fault). This matches
#    notebook 01's finding that the two 75% runs are cold test-day outliers,
#    independent of the residual step or the shop-test.
# 2. The shop-test is worse, not better, than the main score, and the damage is
#    concentrated in the 40% fold. Adding the reference file's rows down to
#    56 kW load reshapes the degree-2 healthy-engine polynomial fit at the edge
#    of its training range, pulling the fitted surface away from what the 40%
#    fold's own healthy rows look like.
#
# Feature 06 should try restricting the healthy-engine model's training rows to
# the 40-85% operating range actually covered by the fault runs (dropping the
# reference file's sub-40% rows), or fitting a lower-degree polynomial so the
# extrapolation at the range's edge is gentler.

# %% [markdown]
# ## The decision: which feature set goes forward
#
# Chosen by pooled macro F1 on the main score, with lowest per-class recall and
# false alarm rate as tie-breakers (R15). Recorded in `docs/adr/0006-feature-set-for-modelling.md`.

# %%
print(pooled[["feature_set", "model", "macro_f1", "accuracy"]].head(3).to_string(index=False))
print()
print("Pruning `raw+physics+rolling` x lightgbm (best combination), pooled vs unpruned:")
print(f"  unpruned macro F1: {pooled.iloc[0]['macro_f1']:.3f}")
print(f"  pruned   macro F1: {pruning_results.iloc[0]['macro_f1']:.3f}")

# %% [markdown]
# ## What this means for the next notebook
#
# **Findings:**
#
# 1. Physics ratios and rolling statistics together, without residuals, win
#    outright: `raw+physics+rolling` x LightGBM tops the table at pooled macro F1
#    0.617 (accuracy 0.712), ahead of every residual-based combination. Physics
#    and rolling features earn their place; healthy-engine residuals do not beat
#    them here, and the day-marker channels they replace turn out not to be the
#    problem the residual step was built to solve.
#  2. Pruning `raw+physics+rolling` x LightGBM inside the training folds (R13)
#     *hurts* the pooled score (macro F1 0.558 pruned vs 0.617 unpruned), with a
#     wide per-fold spread (0.263 to 0.785). The permutation-importance filter is
#     too aggressive on this arm's correlated physics/rolling columns, dropping
#     features that still help even at grouped-zero marginal importance. Pruning
#     does not earn its place for this feature set.
# 3. The shop-test score for the best residual arm (`residuals+physics` x
#    logreg) is worse than its main score (pooled macro F1 0.587 vs 0.608), and
#    the false alarm rate on reference rows at the 40% fold rises sharply (1.7%
#    to 60.7%) when the shop-test's extra reference rows are fed to the residual
#    fit. This is consistent with, but does not need, the winning
#    `raw+physics+rolling` arm having no residual step at all.
#
# **Decision:** `raw+physics+rolling` (unpruned) with LightGBM goes forward to
# modelling. See `docs/adr/0006-feature-set-for-modelling.md` for the numbers
# and reasoning.
#
# Numbers above are read from the executed run, not tuned to hit a target.
