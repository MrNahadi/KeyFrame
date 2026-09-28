"""Cross-validated predictions and summary over LOLO folds."""

from __future__ import annotations

import pandas as pd

from keyframe import evaluate, splits


class _SpyEstimator:
    """Records the row index it was fitted on and predicts the majority training class."""

    def __init__(self, fitted_indices: list[list[int]]) -> None:
        self._fitted_indices = fitted_indices
        self._majority = "Normal"

    def fit(self, X: pd.DataFrame, y: pd.Series) -> _SpyEstimator:
        self._fitted_indices.append(list(X.index))
        self._majority = y.mode().iloc[0]
        return self

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return pd.Series([self._majority] * len(X), index=X.index)


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
