"""Cross-validated predictions and summary over LOLO folds."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import make_pipeline

from keyframe import evaluate, features, splits


class _SpyEstimator(BaseEstimator):
    """Records the row index it was fitted on and predicts the majority training class."""

    def __init__(self, fitted_indices: list[list[int]]) -> None:
        self._fitted_indices = fitted_indices
        self._majority = "Normal"

    def fit(self, X: pd.DataFrame, y: pd.Series) -> _SpyEstimator:
        self._fitted_indices.append(list(X.index))
        self.majority_ = y.mode().iloc[0]
        return self

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return pd.Series([self.majority_] * len(X), index=X.index)


def _synthetic_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "run": ["a", "a", "b", "b", "c", "c", "d", "d"],
            "load_bin": [40, 40, 60, 60, 75, 75, 85, 85],
            "label": ["Normal", "AC", "Normal", "AC", "Normal", "AC", "Normal", "AC"],
            "sensor_1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
        }
    )


def test_lolo_predict_fits_once_per_fold_and_never_sees_test_rows() -> None:
    df = _synthetic_table()
    fitted_indices: list[list[int]] = []

    def model_factory() -> _SpyEstimator:
        return _SpyEstimator(fitted_indices)

    predictions = evaluate.lolo_predict(model_factory, df, features=["sensor_1"])

    assert len(fitted_indices) == 4  # one fit per fold
    for fold_train_index, (_, train_index, test_index) in zip(
        fitted_indices, splits.lolo_folds(df), strict=True
    ):
        assert set(fold_train_index) == set(train_index)
        assert set(fold_train_index).isdisjoint(set(test_index))

    assert list(predictions.index) == list(df.index)
    assert set(predictions.columns) >= {"run", "load_bin", "fold", "y_true", "y_pred"}
    assert list(predictions["y_true"]) == list(df["label"])


def test_summarise_has_pooled_row_and_one_row_per_fold_with_local_classes() -> None:
    predictions = pd.DataFrame(
        {
            "run": ["a", "a", "b", "b"],
            "load_bin": [40, 40, 60, 60],
            "fold": [40, 40, 60, 60],
            "y_true": ["Normal", "AC", "Normal", "Normal"],
            "y_pred": ["Normal", "AC", "Normal", "AC"],
        }
    )

    summary = evaluate.summarise(predictions)

    assert set(summary["fold"]) == {"pooled", 40, 60}
    pooled_row = summary[summary["fold"] == "pooled"].iloc[0]
    assert pooled_row["macro_f1"] == evaluate.macro_f1(predictions["y_true"], predictions["y_pred"])

    fold_60 = summary[summary["fold"] == 60].iloc[0]
    fold_60_mask = predictions["fold"] == 60
    expected_fold_60_f1 = evaluate.macro_f1(
        predictions.loc[fold_60_mask, "y_true"], predictions.loc[fold_60_mask, "y_pred"]
    )
    assert fold_60["macro_f1"] == expected_fold_60_f1


_INPUTS = ["Engine Speed", "Water Brake Weight", "Fuel Flow"]
_TARGET = "Exhaust Temp 1"
_FEATURE_COLS = [*_INPUTS, _TARGET]


class _SpyResiduals(features.HealthyEngineResiduals):
    """Records the ``extra_healthy`` frame it was fitted with, per fold."""

    def __init__(self, *args, seen: list, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.seen = seen

    def fit(self, X: pd.DataFrame, y: pd.Series, extra_healthy: pd.DataFrame | None = None):
        self.seen.append(extra_healthy)
        return super().fit(X, y, extra_healthy=extra_healthy)


def _synthetic_engine_table() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 24
    speed = rng.uniform(1000, 2000, n)
    load = rng.uniform(0, 100, n)
    fuel = rng.uniform(5, 20, n)
    target = speed * 0.1 + load * 0.2 + fuel * 0.3
    return pd.DataFrame(
        {
            "run": [f"run{i % 4}" for i in range(n)],
            "load_bin": np.tile([40, 60, 75, 85], n // 4),
            "label": ["Normal" if i % 3 else "AC" for i in range(n)],
            "Engine Speed": speed,
            "Water Brake Weight": load,
            "Fuel Flow": fuel,
            "Exhaust Temp 1": target,
        }
    )


def _extra_healthy(df: pd.DataFrame):
    def _pick(held_out_bin: object) -> pd.DataFrame:
        return df.loc[df["load_bin"] != held_out_bin, _FEATURE_COLS].head(2)

    return _pick


def test_lolo_predict_extra_healthy_leaves_classifier_training_rows_unchanged() -> None:
    df = _synthetic_engine_table()
    fitted_without: list[list[int]] = []
    fitted_with: list[list[int]] = []

    def make_factory(sink: list[list[int]]):
        def factory():
            return make_pipeline(
                features.HealthyEngineResiduals(inputs=_INPUTS, targets=[_TARGET]),
                _SpyEstimator(sink),
            )

        return factory

    evaluate.lolo_predict(make_factory(fitted_without), df, _FEATURE_COLS)
    evaluate.lolo_predict(
        make_factory(fitted_with), df, _FEATURE_COLS, extra_healthy=_extra_healthy(df)
    )

    assert fitted_without == fitted_with


def test_lolo_predict_extra_healthy_reaches_residual_step() -> None:
    df = _synthetic_engine_table()
    seen: list[pd.DataFrame | None] = []

    def model_factory():
        return make_pipeline(
            _SpyResiduals(inputs=_INPUTS, targets=[_TARGET], seen=seen),
            DummyClassifier(strategy="most_frequent"),
        )

    evaluate.lolo_predict(model_factory, df, _FEATURE_COLS, extra_healthy=_extra_healthy(df))

    assert len(seen) == 4  # one fit per fold
    assert all(frame is not None and len(frame) == 2 for frame in seen)


def test_lolo_predict_default_behaviour_unchanged_without_extra_healthy() -> None:
    df = _synthetic_engine_table()
    seen: list[pd.DataFrame | None] = []

    def model_factory():
        return make_pipeline(
            _SpyResiduals(inputs=_INPUTS, targets=[_TARGET], seen=seen),
            DummyClassifier(strategy="most_frequent"),
        )

    result = evaluate.lolo_predict(model_factory, df, _FEATURE_COLS)

    assert len(result) == len(df)
    assert all(frame is None for frame in seen)
