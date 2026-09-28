"""Metrics computed from labels, and the results log."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from keyframe import evaluate


def test_macro_f1_ignores_classes_absent_from_y_true() -> None:
    y_true = pd.Series(["Normal", "Normal", "AC", "AC"])
    y_pred = pd.Series(["Normal", "Normal", "AC", "AC"])
    perfect_but_narrow = evaluate.macro_f1(y_true, y_pred)

    # A wrong guess of an absent class ("TD") must not shrink the score below
    # a perfect classifier restricted to the two classes actually present.
    y_pred_with_td_guess = pd.Series(["Normal", "Normal", "AC", "AC"])
    assert evaluate.macro_f1(y_true, y_pred_with_td_guess) == perfect_but_narrow == 1.0


def test_false_alarm_rate_known_case() -> None:
    y_true = pd.Series(["Normal", "Normal", "Normal", "Normal", "AC"])
    y_pred = pd.Series(["Normal", "AC", "AC", "Normal", "AC"])
    # 2 of 4 true-Normal rows were predicted as a fault.
    assert evaluate.false_alarm_rate(y_true, y_pred) == 0.5


def test_confusion_matrix_fixed_class_order() -> None:
    y_true = pd.Series(["Normal", "AC", "TD"])
    y_pred = pd.Series(["Normal", "AC", "TD"])
    matrix = evaluate.confusion(y_true, y_pred)
    assert list(matrix.index) == ["Normal", "AC", "AF", "INJ", "CW", "TD"]
    assert list(matrix.columns) == ["Normal", "AC", "AF", "INJ", "CW", "TD"]
    assert matrix.loc["Normal", "Normal"] == 1
    assert matrix.loc["AC", "AC"] == 1
    assert matrix.loc["TD", "TD"] == 1


def test_per_class_recall() -> None:
    y_true = pd.Series(["Normal", "Normal", "AC", "AC"])
    y_pred = pd.Series(["Normal", "AC", "AC", "AC"])
    recall = evaluate.per_class_recall(y_true, y_pred)
    assert recall["Normal"] == 0.5
    assert recall["AC"] == 1.0


def test_log_results_writes_csv_with_experiment_date_and_git_commit(tmp_path: Path) -> None:
    table = pd.DataFrame({"macro_f1": [0.8], "accuracy": [0.9]})
    out_path = evaluate.log_results("my_experiment", table, results_dir=tmp_path)

    assert out_path == tmp_path / "my_experiment.csv"
    written = pd.read_csv(out_path)
    assert list(written["experiment"]) == ["my_experiment"]
    assert "date" in written.columns
    assert written["git_commit"].iloc[0]
    assert len(written["git_commit"].iloc[0]) > 0
