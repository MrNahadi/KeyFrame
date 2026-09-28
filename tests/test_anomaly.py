import numpy as np
import pandas as pd
import pytest

from keyframe import SEED
from keyframe.anomaly import IsolationForestDetector


def _healthy_cloud(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    return pd.DataFrame({"a": rng.normal(0, 1, n), "b": rng.normal(5, 2, n)})


def test_far_points_score_higher_than_points_inside_the_healthy_cloud() -> None:
    detector = IsolationForestDetector().fit(_healthy_cloud())

    inside = pd.DataFrame({"a": [0.1, -0.2, 0.0], "b": [5.1, 4.9, 5.0]})
    far = pd.DataFrame({"a": [50.0, -50.0], "b": [200.0, -200.0]})

    assert detector.score(far).mean() > detector.score(inside).mean()


def test_imputation_and_standardisation_use_only_training_healthy_rows() -> None:
    healthy = _healthy_cloud()
    healthy.loc[0, "a"] = np.nan
    detector = IsolationForestDetector().fit(healthy)

    healthy_median = healthy["a"].median()
    healthy_mean = healthy["a"].fillna(healthy_median).mean()
    assert detector.imputer_.statistics_[0] == healthy_median
    assert detector.scaler_.mean_[0] == pytest.approx(healthy_mean)

    frozen_median = detector.imputer_.statistics_.copy()
    frozen_mean = detector.scaler_.mean_.copy()

    # Scoring wild, NaN-laden test rows must not move the fitted statistics.
    detector.score(pd.DataFrame({"a": [np.nan, 1000.0], "b": [np.nan, -1000.0]}))

    np.testing.assert_array_equal(detector.imputer_.statistics_, frozen_median)
    np.testing.assert_array_equal(detector.scaler_.mean_, frozen_mean)
