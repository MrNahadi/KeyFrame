"""Synthetic tests for nested Optuna tuning (R6)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from keyframe import tuning


def _synthetic_table(n_per_bin: int = 16) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    for bin_value in (40, 60, 75):
        for i in range(n_per_bin):
            label = "Normal" if i % 3 == 0 else "AC"
            rows.append(
                {
                    "run": f"run_{bin_value}",
                    "load_bin": bin_value,
                    "t": float(i),
                    "label": label,
                    "x1": rng.normal(),
                    "x2": rng.normal(),
                }
            )
    return pd.DataFrame(rows)


def test_thin_keeps_every_step_th_row_per_run_in_time_order() -> None:
    df = pd.DataFrame(
        {
            "run": ["a"] * 6 + ["b"] * 6,
            "t": [5.0, 3.0, 1.0, 0.0, 4.0, 2.0] + list(range(6)),
        }
    )

    thinned = tuning.thin(df, step=3)

    assert list(thinned.loc[thinned["run"] == "a", "t"]) == [0.0, 3.0]
    assert list(thinned.loc[thinned["run"] == "b", "t"]) == [0.0, 3.0]


def test_tune_never_fits_or_scores_outside_train_df(monkeypatch: pytest.MonkeyPatch) -> None:
    train_df = _synthetic_table()

    seen_indices: list[pd.Index] = []
    real_builder = tuning.MODEL_BUILDERS["logreg"]

    def spy_builder(params: dict) -> object:
        model = real_builder(params)
        real_fit = model.fit

        def fit(X, y, **kwargs):
            seen_indices.append(X.index)
            return real_fit(X, y, **kwargs)

        model.fit = fit
        return model

    monkeypatch.setitem(tuning.MODEL_BUILDERS, "logreg", spy_builder)

    tuning.tune("logreg", train_df, ["x1", "x2"], n_trials=2)

    assert seen_indices  # the spy actually ran
    thinned_train_index = set(tuning.thin(train_df).index)
    for index in seen_indices:
        assert set(index) <= thinned_train_index


def test_tune_is_reproducible() -> None:
    train_df = _synthetic_table()

    best_params_1, _ = tuning.tune("logreg", train_df, ["x1", "x2"], n_trials=3)
    best_params_2, _ = tuning.tune("logreg", train_df, ["x1", "x2"], n_trials=3)

    assert best_params_1 == best_params_2


def test_xgboost_wrapper_takes_string_labels_and_returns_them():
    import numpy as np
    import pandas as pd

    from keyframe import tuning

    rng = np.random.default_rng(0)
    X = pd.DataFrame({"a": rng.normal(size=60), "b": rng.normal(size=60)})
    y = np.where(X["a"] > 0.5, "AC", np.where(X["a"] < -0.5, "TD", "Normal"))
    model = tuning.MODEL_BUILDERS["xgboost"]({"n_estimators": 10, "max_depth": 2})
    model.fit(X, y)
    assert set(model.predict(X)) <= {"AC", "Normal", "TD"}
    assert list(model.classes_) == ["AC", "Normal", "TD"]
    assert model.predict_proba(X).shape == (60, 3)
