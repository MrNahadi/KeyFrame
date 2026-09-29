# %% [markdown]
# # How good is the final model, where does it fail, and which targets are met?
#
# This notebook reads the cached XGBoost predictions
# (`data/processed/experiments/modelling_xgboost.parquet`) and the
# `reports/results/07_*.csv` outputs of the evaluation experiments. It never
# refits and never touches the lockbox files.
#
# **Main findings:**
# - Pooled macro F1 is 0.717 against a 0.80 target, and the weakest class
#   (turbine degradation, TD) is recalled only 19% of the time against 0.70.
#   The false alarm rate (12.2%) is more than double its 5% target.
# - Confidence is not trustworthy: pooled expected calibration error is 0.176
#   against 0.05. Temperature scaling, fitted inside the training folds, made
#   ECE worse in three of four folds, so it does not fix this. Class
#   predictions are unchanged by it.
# - Errors concentrate in a few runs (AF at 75% and 85% load are about 20%
#   correct). Removing the day-dependent channels does not give a cleaner
#   model: macro F1 falls in three of four folds, so part of the headline
#   score leans on channels that identify the day, not the fault.
# - The lockbox (unseen severity) labels every row as INJ, so the 90% target
#   is met, but the model predicted only INJ there, so this is weak evidence.
# - Of the brief's targets, only the unseen-severity target is met; the final
#   table below lists each one.

# %%
import matplotlib.pyplot as plt
import pandas as pd

from keyframe import calibration, evaluate, experiments, paths

paths.FIGURES.mkdir(parents=True, exist_ok=True)

predictions = experiments.load_modelling("xgboost")
classes = evaluate.CLASS_ORDER
proba = predictions[[f"proba_{c}" for c in classes]].to_numpy()

# %% [markdown]
# ## Final scores: pooled and per fold

# %%
scores = evaluate.summarise(predictions)
scores

# %%
folds = scores[scores["fold"] != "pooled"]
pd.Series(
    {"macro_f1_mean": folds["macro_f1"].mean(), "macro_f1_std": folds["macro_f1"].std()},
)

# %% [markdown]
# ## Per-class recall and precision (pooled)
#
# CW is trained on two runs and TD on three, and the 75% load bin has no CW
# or TD, so their scores rest on very little data (flagged in the table).

# %%
from sklearn.metrics import precision_score, recall_score

recall = recall_score(predictions["y_true"], predictions["y_pred"], labels=classes, average=None)
precision = precision_score(
    predictions["y_true"], predictions["y_pred"], labels=classes, average=None, zero_division=0
)
per_class = pd.DataFrame({"recall": recall, "precision": precision}, index=classes)
per_class["thin_coverage"] = [c in ("CW", "TD") for c in per_class.index]
per_class

# %%
confusion = evaluate.confusion(predictions["y_true"], predictions["y_pred"])
normalised = confusion.div(confusion.sum(axis=1), axis=0)

fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(normalised.to_numpy(), cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(len(classes)), classes)
ax.set_yticks(range(len(classes)), classes)
for i in range(len(classes)):
    for j in range(len(classes)):
        colour = "white" if normalised.iat[i, j] > 0.5 else "black"
        ax.text(
            j,
            i,
            f"{normalised.iat[i, j]:.2f}\n({confusion.iat[i, j]})",
            ha="center",
            va="center",
            fontsize=8,
            color=colour,
        )
ax.set_xlabel("predicted")
ax.set_ylabel("true")
ax.set_title("Pooled confusion matrix, row-normalised (counts in brackets)")
fig.colorbar(im, ax=ax)
fig.tight_layout()
fig.savefig(paths.FIGURES / "07_confusion.png", dpi=150)
plt.show()

# %% [markdown]
# ## Does the score hold at every load?

# %%
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(folds["fold"].astype(str), folds["macro_f1"], color="tab:blue")
ax.axhline(0.80, color="black", linestyle="--", linewidth=1, label="target 0.80")
ax.set_xlabel("held-out load bin")
ax.set_ylabel("macro F1")
ax.set_title("Per-fold macro F1 (XGBoost)")
ax.legend()
fig.tight_layout()
fig.savefig(paths.FIGURES / "07_fold_scores.png", dpi=150)
plt.show()

# %% [markdown]
# ## Can the model's confidence be trusted?

# %%
calib = pd.read_csv(paths.RESULTS / "07_calibration.csv")
calib[["fold", "pooled_ece_before", "recalibrated", "temperature", "ece_before", "ece_after"]]

# %%
curve = calibration.reliability_curve(predictions["y_true"], proba, classes)
pooled_ece = calibration.expected_calibration_error(predictions["y_true"], proba, classes)

fig, (ax_curve, ax_ece) = plt.subplots(1, 2, figsize=(11, 4.5))
ax_curve.plot([0, 1], [0, 1], "k--", linewidth=1, label="perfect")
ax_curve.plot(curve["confidence"], curve["accuracy"], marker="o", label="before")
ax_curve.set_xlabel("confidence")
ax_curve.set_ylabel("accuracy")
ax_curve.set_title(f"Reliability, pooled (ECE {pooled_ece:.3f})")
ax_curve.legend()

x = range(len(calib))
ax_ece.bar([i - 0.2 for i in x], calib["ece_before"], width=0.4, label="before")
ax_ece.bar([i + 0.2 for i in x], calib["ece_after"], width=0.4, label="after temperature scaling")
ax_ece.set_xticks(list(x), calib["fold"].astype(str))
ax_ece.axhline(0.05, color="black", linestyle="--", linewidth=1, label="target 0.05")
ax_ece.set_xlabel("held-out load bin")
ax_ece.set_ylabel("ECE")
ax_ece.set_title("Per-fold ECE before and after recalibration")
ax_ece.legend(fontsize=8)
fig.tight_layout()
fig.savefig(paths.FIGURES / "07_reliability.png", dpi=150)
plt.show()

# %% [markdown]
# Temperature scaling was tried because pooled ECE exceeded 0.05. It helped
# only in fold 85 and made folds 40, 60 and 75 worse, so the reported ECE is
# the uncalibrated one. Macro F1 is identical before and after (argmax is
# unchanged).

# %% [markdown]
# ## Which runs does the model get wrong?

# %%
runs = pd.read_csv(paths.RESULTS / "07_runs.csv")
runs[
    [
        "run",
        "rows",
        "share_correct",
        "top_wrong_label",
        "recall_first_10_min",
        "recall_after",
        "alarm_delay_s",
    ]
].sort_values("share_correct").to_string(max_rows=20)

# %% [markdown]
# ## Does the model lean on day-dependent channels?

# %%
sens = pd.read_csv(paths.RESULTS / "07_sensitivity.csv")
sens_f1 = sens[sens["metric"] == "macro_f1"][["fold", "headline", "no_day_channels"]]
sens_f1

# %%
sens[sens["metric"].str.startswith("recall_")].pivot(
    index="fold", columns="metric", values="no_day_channels"
).round(2)

# %% [markdown]
# Without the 40 day-dependent channels macro F1 rises in fold 40 but falls
# in folds 60, 75 and 85 (fold 85: 0.609 to 0.347). The headline score
# therefore partly rests on channels that encode the day, not the fault.

# %% [markdown]
# ## What happens on unseen severity (the lockbox)?
#
# The lockbox was evaluated once (`keyframe.lockbox`); it is not re-run here.

# %%
lockbox = pd.read_csv(paths.RESULTS / "07_lockbox.csv")
lockbox[["scope", "load_bin", "label", "n_rows", "share"]]

# %% [markdown]
# Every lockbox row was labelled INJ, the class of the lockbox runs, so the
# 90% and 97% targets are met. The model predicted only INJ there, which
# makes this a weak test: it cannot show the model tells INJ from the others.

# %% [markdown]
# ## Final target table

# %%
t4 = pd.read_csv(paths.RESULTS / "04_targets.csv").set_index("metric")
t5 = pd.read_csv(paths.RESULTS / "05_targets.csv").set_index("metric")
pooled_row = scores[scores["fold"] == "pooled"].iloc[0]
lock_share = float(lockbox[lockbox["scope"] == "all"]["share"].iloc[0])
physics_passed = 2  # reports/physics_check.md: 2 of 5 faults pass


def status(met: bool) -> str:
    return "met" if met else "not met"


rows = [
    ("Macro F1, held-out loads", "0.52 raw / 0.60 residuals", 0.80, 0.90, pooled_row["macro_f1"]),
    ("Lowest per-class recall", "0.00 (TD, raw)", 0.70, 0.85, pooled_row["worst_recall"]),
    ("False alarm rate", "29.8% raw / 13.4% residuals", 0.05, 0.02, pooled_row["false_alarm_rate"]),
    (
        "Fault detection AUROC",
        "not measured",
        0.95,
        0.98,
        t5.loc["Fault detection AUROC, held-out loads", "value"],
    ),
    (
        "Detection delay (s, median of detected runs)",
        "not measured",
        600,
        300,
        t4.loc["Detection delay (median of detected runs)", "value"],
    ),
    ("Expected calibration error", "not measured", 0.05, 0.03, pooled_ece),
    ("Unseen severity", "not measured", 0.90, 0.97, lock_share),
    ("Physics check (faults passing, of 5)", "not done", 4, 5, physics_passed),
]
lower_is_better = {
    "False alarm rate",
    "Detection delay (s, median of detected runs)",
    "Expected calibration error",
}
table = pd.DataFrame(rows, columns=["metric", "baseline", "target", "stretch", "achieved"])
table["met"] = [
    status(r.achieved <= r.target if r.metric in lower_is_better else r.achieved >= r.target)
    for r in table.itertuples()
]
table["stretch_met"] = [
    status(r.achieved <= r.stretch if r.metric in lower_is_better else r.achieved >= r.stretch)
    for r in table.itertuples()
]
# Notebook 04 judged the delay target not met because 7 of 13 runs were never
# detected; keep that verdict rather than rewarding the median of the detected ones.
delay_row = table["metric"].str.startswith("Detection delay")
table.loc[delay_row, "met"] = status(
    bool(t4.loc["Detection delay (median of detected runs)", "met"])
)
table.loc[delay_row, "stretch_met"] = "not met"
table.loc[len(table)] = [
    "Demo response time (ms)",
    "not built",
    300,
    100,
    float("nan"),
    "measured in roadmap item 11",
    "measured in roadmap item 11",
]
table

# %% [markdown]
# Spread across folds where it exists: macro F1 per fold ranges from 0.55 to
# 0.86 (see the fold table above). Detection delay uses only the runs the
# alarm ever detected, so it flatters the model; the run table shows how many
# runs were never detected.
