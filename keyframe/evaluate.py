"""Metrics computed from true and predicted labels, and the shared results log."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, recall_score

from keyframe import paths, splits
from keyframe.features import HealthyEngineResiduals

CLASS_ORDER: list[str] = ["Normal", "AC", "AF", "INJ", "CW", "TD"]


def macro_f1(y_true: pd.Series, y_pred: pd.Series) -> float:
    """Macro F1 over the classes present in ``y_true`` (absent classes don't dilute it)."""
    labels = sorted(pd.unique(y_true))
    return float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0))


def per_class_recall(y_true: pd.Series, y_pred: pd.Series) -> pd.Series:
    """Recall per class present in ``y_true``, indexed by class name."""
    labels = sorted(pd.unique(y_true))
    scores = recall_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    return pd.Series(scores, index=labels)


def false_alarm_rate(y_true: pd.Series, y_pred: pd.Series) -> float:
    """Share of true Normal rows predicted as any fault."""
    normal_mask = y_true == "Normal"
    if not normal_mask.any():
        return float("nan")
    false_alarms = normal_mask & (y_pred != "Normal")
    return float(false_alarms.sum() / normal_mask.sum())


def confusion(y_true: pd.Series, y_pred: pd.Series) -> pd.DataFrame:
    """Confusion matrix with rows/columns in the fixed ``CLASS_ORDER``."""
    matrix = confusion_matrix(y_true, y_pred, labels=CLASS_ORDER)
    return pd.DataFrame(matrix, index=CLASS_ORDER, columns=CLASS_ORDER)


def accuracy(y_true: pd.Series, y_pred: pd.Series) -> float:
    """Plain accuracy (reported, not a target)."""
    return float(np.mean(np.asarray(y_true) == np.asarray(y_pred)))


def lolo_predict(
    model_factory: Callable[[], Any],
    df: pd.DataFrame,
    features: list[str],
    extra_healthy: Callable[[Any], pd.DataFrame] | None = None,
) -> pd.DataFrame:
    """Fit a fresh model per LOLO fold and predict the held-out rows.

    ``extra_healthy(held_out_bin)``, when given, returns reference rows for the
    held-out load. They are fitted into the pipeline's ``HealthyEngineResiduals``
    step only (a shop-test variant), never added to the classifier's training rows
    and never scored.

    Returns a DataFrame (original index) with ``run``, ``load_bin``, ``fold``,
    ``y_true``, ``y_pred`` and, when the model supports it, one probability
    column per class it was fitted on.
    """
    rows = []
    for held_out_bin, train_index, test_index in splits.lolo_folds(df):
        model = model_factory()
        X_train = df.loc[train_index, features]
        y_train = df.loc[train_index, "label"]
        X_test = df.loc[test_index, features]
        fit_params = {}
        if extra_healthy is not None:
            step_name = _residual_step_name(model)
            fit_params[f"{step_name}__extra_healthy"] = extra_healthy(held_out_bin)
        model.fit(X_train, y_train, **fit_params)
        y_pred = model.predict(X_test)

        fold_result = pd.DataFrame(
            {
                "run": df.loc[test_index, "run"],
                "load_bin": df.loc[test_index, "load_bin"],
                "fold": held_out_bin,
                "y_true": df.loc[test_index, "label"],
                "y_pred": np.asarray(y_pred),
            },
            index=test_index,
        )
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X_test)
            for class_index, class_label in enumerate(model.classes_):
                fold_result[f"proba_{class_label}"] = proba[:, class_index]
        rows.append(fold_result)

    return pd.concat(rows).loc[df.index]


def _residual_step_name(model: Any) -> str:
    """Name of the ``HealthyEngineResiduals`` step in a ``Pipeline``, for routing fit params."""
    for name, step in getattr(model, "steps", []):
        if isinstance(step, HealthyEngineResiduals):
            return name
    raise ValueError("extra_healthy given but model has no HealthyEngineResiduals step")


def summarise(predictions: pd.DataFrame) -> pd.DataFrame:
    """Headline metrics pooled over all folds, plus one row per fold.

    Per-fold scores cover only the classes present in that fold's true labels.
    """
    rows = [_score_slice("pooled", predictions["y_true"], predictions["y_pred"])]
    for fold in sorted(predictions["fold"].unique()):
        mask = predictions["fold"] == fold
        rows.append(
            _score_slice(fold, predictions.loc[mask, "y_true"], predictions.loc[mask, "y_pred"])
        )
    return pd.DataFrame(rows)


def _score_slice(fold: object, y_true: pd.Series, y_pred: pd.Series) -> dict[str, object]:
    recall = per_class_recall(y_true, y_pred)
    worst_class = recall.idxmin()
    return {
        "fold": fold,
        "macro_f1": macro_f1(y_true, y_pred),
        "accuracy": accuracy(y_true, y_pred),
        "false_alarm_rate": false_alarm_rate(y_true, y_pred),
        "worst_recall": recall.min(),
        "worst_recall_class": worst_class,
    }


def _git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=paths.ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def log_results(name: str, table: pd.DataFrame, results_dir: Path = paths.RESULTS) -> Path:
    """Write ``table`` to ``<results_dir>/<name>.csv`` with experiment, date and git_commit columns."""
    results_dir.mkdir(parents=True, exist_ok=True)
    out = table.copy()
    out["experiment"] = name
    out["date"] = date.today().isoformat()
    out["git_commit"] = _git_commit()
    out_path = results_dir / f"{name}.csv"
    out.to_csv(out_path, index=False)
    return out_path
