"""The ablation experiment on a tiny synthetic table."""

from __future__ import annotations

import pandas as pd

from keyframe import experiments


def _synthetic_table() -> pd.DataFrame:
    runs = [f"run{i}" for i in range(8)]
    load_bins = [40, 40, 60, 60, 75, 75, 85, 85]
    labels = ["Normal", "AC", "Normal", "AC", "Normal", "AC", "Normal", "AC"]
    return pd.DataFrame(
        {
            "run": runs,
            "load_bin": load_bins,
            "label": labels,
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


def test_run_ablation_shop_test_needs_a_residual_feature_set(tmp_path) -> None:
    df = _synthetic_table()

    try:
        experiments.run_ablation(df, "raw", "logreg", shop_test=True, output_dir=tmp_path)
    except ValueError as error:
        assert "residualising" in str(error)
    else:
        raise AssertionError("expected a ValueError")
