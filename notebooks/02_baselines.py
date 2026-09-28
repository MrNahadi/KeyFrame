# %% [markdown]
# # Baselines: how well do off-the-shelf models diagnose faults at held-out loads?
#
# Four baselines on the raw sensor channels — majority-class dummy, logistic
# regression, random forest and gradient boosting (LightGBM) — scored with
# leave-one-load-out (LOLO): each of the four load bins is held out as test
# in turn, so every score reflects a load the model never trained on.
#
# **Main findings:** logistic regression wins on pooled macro F1 (0.440),
# ahead of LightGBM (0.389), random forest (0.285) and the majority-class
# dummy (0.108). None of the four generalise well to an unseen load: the best
# model's worst per-class recall is 0.13 (TD), and LightGBM and random forest
# both collapse to near-zero recall on at least one class when that load is
# held out. Raw-sensor baselines with no load-aware features are not enough;
# later notebooks need features that separate the fault signal from the load
# shift itself.

# %%
import lightgbm as lgb
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from keyframe import SEED, evaluate, features, paths

paths.FIGURES.mkdir(parents=True, exist_ok=True)
paths.RESULTS.mkdir(parents=True, exist_ok=True)
paths.PROCESSED.mkdir(parents=True, exist_ok=True)

clean = pd.read_parquet(paths.PROCESSED / "clean.parquet")
FEATURE_COLUMNS = features.raw_sensor_columns(clean)

# %% [markdown]
# ## The four baselines
#
# Scalers and estimators are fit inside each LOLO fold, never on the pooled
# table, so no held-out load leaks into training.

# %%
MODEL_FACTORIES = {
    "dummy_majority": lambda: DummyClassifier(strategy="most_frequent"),
    "logistic_regression": lambda: make_pipeline(
        StandardScaler(),
        LogisticRegression(class_weight="balanced", max_iter=2000, random_state=SEED),
    ),
    "random_forest": lambda: RandomForestClassifier(
        n_estimators=300, class_weight="balanced", random_state=SEED
    ),
    "lightgbm": lambda: lgb.LGBMClassifier(class_weight="balanced", random_state=SEED, verbose=-1),
}

# %% [markdown]
# ## Pooled and per-fold scores for each baseline

# %%
predictions_by_model = {
    name: evaluate.lolo_predict(factory, clean, FEATURE_COLUMNS)
    for name, factory in MODEL_FACTORIES.items()
}

summaries = []
for name, predictions in predictions_by_model.items():
    summary = evaluate.summarise(predictions)
    summary.insert(0, "model", name)
    summaries.append(summary)
results = pd.concat(summaries, ignore_index=True)
evaluate.log_results("02_baselines", results)
results

# %% [markdown]
# ## Which baseline generalises best to an unseen load?
#
# Ranked by pooled macro F1 (the headline target), not accuracy, since the
# classes are imbalanced.

# %%
pooled = results[results["fold"] == "pooled"].sort_values("macro_f1", ascending=False)
best_model = pooled.iloc[0]["model"]
pooled

# %%
best_predictions = predictions_by_model[best_model]
best_predictions.to_parquet(paths.PROCESSED / "02_best_baseline_predictions.parquet")
best_model

# %% [markdown]
# ## Per-fold spread: does any model fall apart at a particular load?

# %%
per_fold = results[results["fold"] != "pooled"]
fig, ax = plt.subplots(figsize=(7, 4))
for name, group in per_fold.groupby("model"):
    group = group.sort_values("fold")
    ax.plot(group["fold"].astype(str), group["macro_f1"], marker="o", label=name)
ax.set_xlabel("held-out load bin")
ax.set_ylabel("macro F1")
ax.set_title("Per-fold macro F1 by baseline")
ax.legend()
fig.tight_layout()
fig.savefig(paths.FIGURES / "02_fold_scores.png", dpi=150)
plt.show()

# %% [markdown]
# ## Confusion matrix of the best baseline
#
# Pooled over all four folds, rows normalised to recall so each row shows
# where that class's predictions land.

# %%
confusion = evaluate.confusion(best_predictions["y_true"], best_predictions["y_pred"])
confusion_recall = confusion.div(confusion.sum(axis=1), axis=0)

fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(confusion_recall, cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(len(evaluate.CLASS_ORDER)), evaluate.CLASS_ORDER)
ax.set_yticks(range(len(evaluate.CLASS_ORDER)), evaluate.CLASS_ORDER)
ax.set_xlabel("predicted")
ax.set_ylabel("true")
ax.set_title(f"Confusion matrix ({best_model}), rows normalised to recall")
for i in range(len(evaluate.CLASS_ORDER)):
    for j in range(len(evaluate.CLASS_ORDER)):
        ax.text(j, i, f"{confusion_recall.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
fig.colorbar(im, ax=ax, label="recall")
fig.tight_layout()
fig.savefig(paths.FIGURES / "02_confusion_best.png", dpi=150)
plt.show()

# %% [markdown]
# ## What this means for the next notebooks
#
# Numbers above are read from the executed run, not tuned to hit a target.
