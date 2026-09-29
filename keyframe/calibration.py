"""Calibration metrics: top-label expected calibration error and reliability curves."""

from collections.abc import Sequence

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

Labels = Sequence[object] | np.ndarray | pd.Series


def reliability_curve(
    y_true: Labels,
    proba: np.ndarray,
    classes: Sequence[object] | np.ndarray,
    n_bins: int = 15,
) -> pd.DataFrame:
    """Per-bin mean top-label confidence, accuracy and row count; empty bins are skipped."""
    proba = np.asarray(proba, dtype=float)
    class_array = np.asarray(classes)
    confidence = proba.max(axis=1)
    correct = class_array[proba.argmax(axis=1)] == np.asarray(y_true)
    # Equal-width bins on (0, 1]; a confidence of exactly 1 falls in the last bin.
    bin_index = np.clip(np.ceil(confidence * n_bins).astype(int) - 1, 0, n_bins - 1)
    rows = []
    for bin_number in range(n_bins):
        in_bin = bin_index == bin_number
        count = int(in_bin.sum())
        if count == 0:
            continue
        rows.append(
            {
                "bin": bin_number,
                "confidence": float(confidence[in_bin].mean()),
                "accuracy": float(correct[in_bin].mean()),
                "count": count,
            }
        )
    return pd.DataFrame(rows, columns=["bin", "confidence", "accuracy", "count"])


def expected_calibration_error(
    y_true: Labels,
    proba: np.ndarray,
    classes: Sequence[object] | np.ndarray,
    n_bins: int = 15,
) -> float:
    """Top-label ECE: count-weighted mean gap between confidence and accuracy per bin."""
    curve = reliability_curve(y_true, proba, classes, n_bins)
    if curve.empty:
        return 0.0
    gap = (curve["confidence"] - curve["accuracy"]).abs()
    return float((gap * curve["count"]).sum() / curve["count"].sum())


class TemperatureCalibrator:
    """Multiclass temperature scaling: ``p_k`` becomes proportional to ``p_k ** (1 / T)``.

    One parameter, so it cannot overfit the few inner folds, and it never changes the
    argmax (macro F1 is unchanged); isotonic or per-class sigmoids would need more rows
    per class than the rare fault classes have.
    """

    def __init__(self, temperature: float = 1.0) -> None:
        self.temperature = temperature

    def transform(self, proba: np.ndarray) -> np.ndarray:
        logits = np.log(np.clip(np.asarray(proba, dtype=float), 1e-12, 1.0)) / self.temperature
        logits -= logits.max(axis=1, keepdims=True)
        scaled = np.exp(logits)
        return scaled / scaled.sum(axis=1, keepdims=True)


def fit_calibrator(
    y_true: Labels,
    proba: np.ndarray,
    classes: Sequence[object] | np.ndarray,
) -> TemperatureCalibrator:
    """Fit the temperature that minimises log loss on ``proba`` (columns ordered as ``classes``)."""
    proba = np.asarray(proba, dtype=float)
    class_index = {label: i for i, label in enumerate(np.asarray(classes).tolist())}
    target = np.array([class_index[label] for label in np.asarray(y_true).tolist()])

    def log_loss(log_temperature: float) -> float:
        scaled = TemperatureCalibrator(float(np.exp(log_temperature))).transform(proba)
        return float(-np.log(np.clip(scaled[np.arange(len(target)), target], 1e-12, 1.0)).mean())

    result = minimize_scalar(log_loss, bounds=(-3.0, 3.0), method="bounded")
    return TemperatureCalibrator(float(np.exp(result.x)))
