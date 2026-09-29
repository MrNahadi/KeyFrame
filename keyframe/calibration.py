"""Calibration metrics: top-label expected calibration error and reliability curves."""

from collections.abc import Sequence

import numpy as np
import pandas as pd


def reliability_curve(
    y_true: Sequence[object] | np.ndarray,
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
    y_true: Sequence[object] | np.ndarray,
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
