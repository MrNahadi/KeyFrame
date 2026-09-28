import numpy as np
import pandas as pd
import pytest

from keyframe import SEED
from keyframe.anomaly import IsolationForestDetector, PCADetector


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


def _correlated_healthy_cloud(n: int = 500) -> pd.DataFrame:
    # a and b are almost perfectly correlated, so PCA (at 95% variance) keeps a
    # component spanning their shared direction plus the independent column c,
    # and drops the tiny-variance residual direction (a - b).
    rng = np.random.default_rng(SEED)
    a = rng.normal(0, 1, n)
    b = a + rng.normal(0, 0.01, n)
    c = rng.normal(0, 1, n)
    return pd.DataFrame({"a": a, "b": b, "c": c})


def test_shift_along_retained_component_raises_t2_more_than_q() -> None:
    detector = PCADetector().fit(_correlated_healthy_cloud())

    # c aligns with a retained component; a shift here should move mostly the
    # in-subspace T2 score, not the residual Q score.
    along_retained = pd.DataFrame({"a": [0.0], "b": [0.0], "c": [10.0]})
    parts = detector.score_parts(along_retained).iloc[0]

    assert parts["t2"] > parts["q"]


def test_shift_orthogonal_to_retained_components_raises_q_more_than_t2() -> None:
    detector = PCADetector().fit(_correlated_healthy_cloud())

    # a and -b move opposite while their sum (the retained direction) stays put,
    # so this shift lands in the dropped residual direction (a - b).
    orthogonal = pd.DataFrame({"a": [10.0], "b": [-10.0], "c": [0.0]})
    parts = detector.score_parts(orthogonal).iloc[0]

    assert parts["q"] > parts["t2"]


def test_combined_score_is_max_of_parts_normalised_by_training_99th_percentiles() -> None:
    detector = PCADetector().fit(_correlated_healthy_cloud())

    probe = pd.DataFrame({"a": [3.0], "b": [-4.0], "c": [7.0]})
    parts = detector.score_parts(probe).iloc[0]

    expected = max(parts["t2"] / detector.t2_p99_, parts["q"] / detector.q_p99_)
    assert parts["score"] == pytest.approx(expected)
    assert detector.score(probe)[0] == pytest.approx(expected)
