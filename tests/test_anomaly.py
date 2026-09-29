import numpy as np
import pandas as pd
import pytest

from keyframe import SEED, features
from keyframe.anomaly import (
    AutoencoderDetector,
    IsolationForestDetector,
    PCADetector,
    detector_inputs,
    threshold_for_far,
)


def _healthy_cloud(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    return pd.DataFrame({"a": rng.normal(0, 1, n), "b": rng.normal(5, 2, n)})


def test_threshold_for_far_flags_about_that_share_of_healthy_scores() -> None:
    scores = np.arange(1, 101, dtype=float)

    threshold = threshold_for_far(scores, far=0.02)

    assert np.mean(scores >= threshold) == pytest.approx(0.02)


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


def test_autoencoder_scores_off_manifold_points_higher_than_healthy_ones() -> None:
    detector = AutoencoderDetector().fit(_correlated_healthy_cloud())

    healthy_like = pd.DataFrame({"a": [0.1, -0.1], "b": [0.1, -0.1], "c": [0.2, -0.2]})
    off_manifold = pd.DataFrame({"a": [10.0, -10.0], "b": [-10.0, 10.0], "c": [0.0, 0.0]})

    assert detector.score(off_manifold).mean() > detector.score(healthy_like).mean()


def test_autoencoder_fit_is_reproducible_with_the_project_seed() -> None:
    healthy = _correlated_healthy_cloud()
    probe = pd.DataFrame({"a": [3.0], "b": [-4.0], "c": [7.0]})

    first = AutoencoderDetector().fit(healthy).score(probe)
    second = AutoencoderDetector().fit(healthy).score(probe)

    np.testing.assert_array_equal(first, second)


def _residual_arm_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Engine Speed": [1000.0, 1010.0, 1020.0, 1005.0],
            "Water Brake Weight": [50.0, 51.0, 52.0, 50.5],
            "Fuel Flow": [5.0, 5.1, 5.2, 5.05],
            "Oil Temp": [80.0, 81.0, 82.0, 95.0],
            "phys_load": [0.5, 0.6, 0.7, 0.55],
            "Oil Temp_roll_5_mean": [80.0, 80.5, 81.0, 90.0],
            "Oil Temp_roll_5_std": [0.1, 0.2, 0.15, 1.2],
            "Oil Temp_roll_5_slope": [0.01, 0.02, -0.01, 0.5],
            "label": ["Normal", "Normal", "Normal", "AC"],
        }
    )


def test_detector_inputs_residual_arm_excludes_raw_levels_and_rolling_means() -> None:
    df = _residual_arm_table()

    columns, fit_view = detector_inputs(df, "residual")

    assert "resid_Oil Temp" in columns
    assert "phys_load" in columns
    assert "Oil Temp_roll_5_std" in columns
    assert "Oil Temp_roll_5_slope" in columns
    for raw_level in ("Oil Temp", "Engine Speed", "Water Brake Weight", "Fuel Flow"):
        assert raw_level not in columns
    assert "Oil Temp_roll_5_mean" not in columns

    view = fit_view(df, df["label"])
    projected = view(df)
    assert set(projected.columns) == set(columns)


def test_detector_inputs_residual_arm_fits_on_training_fold_healthy_rows_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    df = _residual_arm_table()
    seen_healthy_index: list[pd.Index] = []
    real_fit = features.HealthyEngineResiduals.fit

    def spy_fit(self, X, y, extra_healthy=None):
        y = pd.Series(np.asarray(y), index=X.index)
        seen_healthy_index.append(X.index[y == "Normal"])
        return real_fit(self, X, y, extra_healthy=extra_healthy)

    monkeypatch.setattr(features.HealthyEngineResiduals, "fit", spy_fit, raising=True)

    _, fit_view = detector_inputs(df, "residual")
    fit_view(df, df["label"])

    assert seen_healthy_index
    assert set(df.loc[seen_healthy_index[0], "label"]) == {"Normal"}
    assert len(seen_healthy_index[0]) == 3
