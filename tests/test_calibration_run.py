"""run_calibration: the calibrator sees inner-fold predictions only (R3)."""

from __future__ import annotations

import json

import pandas as pd

from keyframe import calibration, experiments


def _setup(tmp_path, confidence: float):
    df = pd.DataFrame(
        {
            "run": [f"run{i}" for i in range(8)],
            "t": [0.0] * 8,
            "load_bin": [40, 40, 60, 60, 75, 75, 85, 85],
            "label": ["Normal", "AC"] * 4,
            "Anomaly State": [0] * 8,
            "Engine Speed": [1000.0 + 10 * i for i in range(8)],
            "Fuel Flow": [5.0 + i for i in range(8)],
        }
    )
    tuning_dir = tmp_path / "tuning"
    tuning_dir.mkdir()
    for fold in (40, 60, 75, 85):
        (tuning_dir / f"xgboost_fold{fold}.json").write_text(json.dumps({"best_params": {}}))
    # Always predicts Normal with the given confidence, so it is right half the time.
    outer = pd.DataFrame(
        {
            "run": df["run"],
            "load_bin": df["load_bin"],
            "fold": df["load_bin"],
            "y_true": df["label"],
            "y_pred": "Normal",
            "proba_AC": 1 - confidence,
            "proba_Normal": confidence,
        }
    )
    modelling_dir = tmp_path / "experiments"
    modelling_dir.mkdir()
    outer.to_parquet(modelling_dir / "modelling_xgboost.parquet")
    return df, tuning_dir, modelling_dir


def test_calibrator_never_sees_outer_test_rows(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(experiments, "MODELLING_FEATURE_SET", "raw")
    df, tuning_dir, modelling_dir = _setup(tmp_path, confidence=0.95)
    seen_train, fitted_on = [], []

    def inner_predict(factory, train_df, columns):
        seen_train.append(train_df)
        return pd.DataFrame(
            {
                "y_true": ["Normal", "AC"] * 3,
                "proba_AC": [0.05] * 6,
                "proba_Normal": [0.95] * 6,
            }
        )

    def spy_fit(y_true, proba, classes):
        fitted_on.append(len(y_true))
        return calibration.fit_calibrator(y_true, proba, classes)

    experiments.run_calibration(
        df,
        40,
        tuning_dir=tuning_dir,
        modelling_dir=modelling_dir,
        results_dir=tmp_path,
        inner_predict=inner_predict,
        fit=spy_fit,
    )

    assert fitted_on == [6]
    assert 40 not in set(seen_train[0]["load_bin"])
    row = pd.read_csv(tmp_path / "07_calibration.csv").iloc[0]
    assert row["recalibrated"]
    assert row["ece_after"] < row["ece_before"]
    assert row["macro_f1_after"] == row["macro_f1_before"]


def test_skips_recalibration_when_pooled_ece_is_low(tmp_path) -> None:
    df, tuning_dir, modelling_dir = _setup(tmp_path, confidence=0.5)

    def inner_predict(*args, **kwargs):
        raise AssertionError("no inner predictions needed when already calibrated")

    experiments.run_calibration(
        df,
        60,
        tuning_dir=tuning_dir,
        modelling_dir=modelling_dir,
        results_dir=tmp_path,
        inner_predict=inner_predict,
    )

    row = pd.read_csv(tmp_path / "07_calibration.csv").iloc[0]
    assert not row["recalibrated"]
    assert row["ece_after"] == row["ece_before"]
