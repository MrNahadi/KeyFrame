"""The ablation experiment on a tiny synthetic table."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from keyframe import experiments, tuning


def _synthetic_table() -> pd.DataFrame:
    runs = [f"run{i}" for i in range(8)]
    load_bins = [40, 40, 60, 60, 75, 75, 85, 85]
    labels = ["Normal", "AC", "Normal", "AC", "Normal", "AC", "Normal", "AC"]
    return pd.DataFrame(
        {
            "run": runs,
            "t": [0.0] * 8,
            "load_bin": load_bins,
            "label": labels,
            "Anomaly State": [0] * 8,
            "Engine Speed": [1000.0 + 10 * i for i in range(8)],
            "Fuel Flow": [5.0 + i for i in range(8)],
        }
    )


def test_run_ablation_writes_predictions_and_skips_existing(tmp_path) -> None:
    df = _synthetic_table()

    out_path = experiments.run_ablation(df, "raw", "logreg", output_dir=tmp_path)

    assert out_path.exists()
    predictions = pd.read_parquet(out_path)
    assert len(predictions) == len(df)
    assert set(predictions["y_true"]) <= {"Normal", "AC"}

    mtime_before = out_path.stat().st_mtime_ns
    experiments.run_ablation(df, "raw", "logreg", output_dir=tmp_path)
    assert out_path.stat().st_mtime_ns == mtime_before

    experiments.run_ablation(df, "raw", "logreg", output_dir=tmp_path, force=True)
    assert out_path.exists()


def test_run_tuning_and_modelling_predict_every_row_once(tmp_path) -> None:
    df = _synthetic_table()
    tuning_dir = tmp_path / "tuning"
    output_dir = tmp_path / "experiments"

    for fold in (40, 60, 75, 85):
        out_path = experiments.run_tuning(df, "logreg", fold, n_trials=2, output_dir=tuning_dir)
        assert out_path.exists()
        payload = json.loads(out_path.read_text())
        assert payload["model"] == "logreg"
        assert payload["n_trials"] == 2
        assert "best_params" in payload and "best_inner_score" in payload

    mtime_before = out_path.stat().st_mtime_ns
    experiments.run_tuning(df, "logreg", 85, n_trials=2, output_dir=tuning_dir)
    assert out_path.stat().st_mtime_ns == mtime_before

    predictions_path = experiments.run_modelling(
        df, "logreg", tuning_dir=tuning_dir, output_dir=output_dir, results_dir=tmp_path
    )
    predictions = pd.read_parquet(predictions_path)
    assert sorted(predictions.index) == sorted(df.index)
    assert set(predictions["y_true"]) <= {"Normal", "AC"}


def test_run_alarm_chooses_params_from_inner_folds_only(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    df = _synthetic_table()
    tuning_dir = tmp_path / "tuning"
    modelling_dir = tmp_path / "experiments"
    results_dir = tmp_path / "results"

    for fold in (40, 60, 75, 85):
        experiments.run_tuning(df, "logreg", fold, n_trials=2, output_dir=tuning_dir)
    experiments.run_modelling(
        df, "logreg", tuning_dir=tuning_dir, output_dir=modelling_dir, results_dir=results_dir
    )

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
    out_path = experiments.run_alarm(
        df,
        "logreg",
        tuning_dir=tuning_dir,
        modelling_dir=modelling_dir,
        results_dir=results_dir,
    )

    assert out_path.exists()
    outer_folds = (40, 60, 75, 85)
    assert seen_indices and len(seen_indices) % len(outer_folds) == 0
    group_size = len(seen_indices) // len(outer_folds)
    for i, fold in enumerate(outer_folds):
        outer_test_index = set(df.index[df["load_bin"] == fold])
        for index in seen_indices[i * group_size : (i + 1) * group_size]:
            assert not (set(index) & outer_test_index)

    result = pd.read_csv(out_path)
    assert {"model", "min_duration_s", "min_probability", "false_alarm_rate", "fold"} <= set(
        result.columns
    )


def test_run_ablation_shop_test_needs_a_residual_feature_set(tmp_path) -> None:
    df = _synthetic_table()

    try:
        experiments.run_ablation(df, "raw", "logreg", shop_test=True, output_dir=tmp_path)
    except ValueError as error:
        assert "residualising" in str(error)
    else:
        raise AssertionError("expected a ValueError")


def _anomaly_table() -> pd.DataFrame:
    rows = []
    for bin_ in (40, 60, 75, 85):
        for i in range(6):
            label = "Normal" if i < 4 else "AC"
            rows.append(
                {
                    "run": f"run{bin_}_{i}",
                    "t": float(i),
                    "load_bin": bin_,
                    "label": label,
                    "Anomaly State": 0,
                    "Engine Speed": 1000.0 + 10 * i + bin_,
                    "Fuel Flow": 5.0 + i + bin_ / 10,
                }
            )
    return pd.DataFrame(rows)


def test_run_anomaly_fits_healthy_training_rows_only(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    df = _anomaly_table()
    seen_index: list[pd.Index] = []
    real_factory = experiments.DETECTOR_FACTORIES["iforest"]

    def spy_factory():
        detector = real_factory()
        real_fit = detector.fit

        def fit(X_healthy):
            seen_index.append(X_healthy.index)
            return real_fit(X_healthy)

        detector.fit = fit
        return detector

    monkeypatch.setitem(experiments.DETECTOR_FACTORIES, "iforest", spy_factory)

    out_path = experiments.run_anomaly(df, "iforest", 60, output_dir=tmp_path)

    assert out_path.exists()
    assert seen_index
    fitted = df.loc[seen_index[0]]
    assert (fitted["label"] == "Normal").all()
    assert (fitted["load_bin"] != 60).all()

    predictions = pd.read_parquet(out_path)
    assert set(predictions["load_bin"]) == {60}
    assert set(predictions.index) == set(df.index[df["load_bin"] == 60])
    assert {"run", "load_bin", "label", "t", "score"} <= set(predictions.columns)
    assert set(predictions["label"]) == {"Normal", "AC"}

    mtime_before = out_path.stat().st_mtime_ns
    experiments.run_anomaly(df, "iforest", 60, output_dir=tmp_path)
    assert out_path.stat().st_mtime_ns == mtime_before


def test_run_anomaly_pca_writes_t2_and_q_parts(tmp_path) -> None:
    df = _anomaly_table()

    out_path = experiments.run_anomaly(df, "pca", 40, output_dir=tmp_path)

    predictions = pd.read_parquet(out_path)
    assert {"t2", "q", "score"} <= set(predictions.columns)


def test_run_anomaly_logs_auroc_once_every_fold_exists(tmp_path) -> None:
    df = _anomaly_table()
    results_dir = tmp_path / "results"

    for fold in (40, 60, 75):
        experiments.run_anomaly(df, "iforest", fold, output_dir=tmp_path, results_dir=results_dir)
    assert not (results_dir / "05_anomaly.csv").exists()

    experiments.run_anomaly(df, "iforest", 85, output_dir=tmp_path, results_dir=results_dir)

    summary = pd.read_csv(results_dir / "05_anomaly.csv")
    assert set(summary["fold"].astype(str)) == {"pooled", "40", "60", "75", "85"}
    assert {"auroc", "auroc_AC"} <= set(summary.columns)
