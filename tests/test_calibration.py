import numpy as np
import pytest

from keyframe.calibration import expected_calibration_error, reliability_curve

CLASSES = np.array(["a", "b"])


def test_perfectly_calibrated_gives_zero() -> None:
    # Confidence 0.8 on every row, and exactly 80% of the labels are right.
    proba = np.tile([0.8, 0.2], (10, 1))
    y_true = np.array(["a"] * 8 + ["b"] * 2)
    assert expected_calibration_error(y_true, proba, CLASSES) == pytest.approx(0.0)


def test_always_certain_half_wrong_gives_half() -> None:
    proba = np.tile([1.0, 0.0], (10, 1))
    y_true = np.array(["a"] * 5 + ["b"] * 5)
    assert expected_calibration_error(y_true, proba, CLASSES) == pytest.approx(0.5)


def test_empty_bins_are_skipped() -> None:
    proba = np.tile([1.0, 0.0], (4, 1))
    y_true = np.array(["a"] * 4)
    curve = reliability_curve(y_true, proba, CLASSES, n_bins=15)
    assert len(curve) == 1
    assert curve["count"].iloc[0] == 4
    assert curve["confidence"].iloc[0] == pytest.approx(1.0)
    assert curve["accuracy"].iloc[0] == pytest.approx(1.0)
