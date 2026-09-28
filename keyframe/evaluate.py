"""Metrics computed from true and predicted labels, and the shared results log."""

from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, recall_score

from keyframe import paths

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
