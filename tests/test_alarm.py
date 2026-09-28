"""Synthetic tests for sustained alarms and detection delay."""

from __future__ import annotations

import pandas as pd

from keyframe.alarm import detection_delay, sustained_alarm


def _predictions(run_rows: list[tuple[str, float, str, float]]) -> pd.DataFrame:
    """Build a predictions frame from (run, t, y_pred, proba_of_y_pred) rows."""
    rows = []
    for run, t, y_pred, proba in run_rows:
        row = {"run": run, "t": t, "y_pred": y_pred, f"proba_{y_pred}": proba}
        rows.append(row)
    return pd.DataFrame(rows)


def test_alarm_fires_exactly_min_duration_after_sustained_confident_predictions() -> None:
    # Sampling every 1s, confident AC predictions from t=0.
    predictions = _predictions([("run1", float(t), "AC", 0.95) for t in range(0, 12)])

    alarm = sustained_alarm(predictions, min_duration_s=10.0, min_probability=0.9)

    assert list(alarm.iloc[:10]) == ["Normal"] * 10
    assert list(alarm.iloc[10:]) == ["AC", "AC"]


def test_single_stray_prediction_never_fires() -> None:
    rows = [("run1", float(t), "AC", 0.95) for t in range(0, 5)]
    rows.append(("run1", 5.0, "TD", 0.95))  # a single stray prediction
    rows += [("run1", float(t), "AC", 0.95) for t in range(6, 20)]
    predictions = _predictions(rows)

    alarm = sustained_alarm(predictions, min_duration_s=10.0, min_probability=0.9)

    # The stray row resets the streak, so AC needs 10 more seconds after t=6.
    assert (alarm == "TD").sum() == 0
    assert alarm.loc[predictions["t"] < 16.0].eq("Normal").all()
    assert alarm.loc[predictions["t"] >= 16.0].eq("AC").all()


def test_alarms_never_cross_runs() -> None:
    rows = [("run1", float(t), "AC", 0.95) for t in range(0, 15)]
    rows += [("run2", float(t), "AC", 0.95) for t in range(0, 5)]
    predictions = _predictions(rows)

    alarm = sustained_alarm(predictions, min_duration_s=10.0, min_probability=0.9)

    assert alarm.loc[predictions["run"] == "run2"].eq("Normal").all()


def test_alarm_never_looks_ahead() -> None:
    # Confident AC only starts partway through; alarm must not appear before enough history.
    rows = [("run1", float(t), "Normal", 0.99) for t in range(0, 5)]
    rows += [("run1", float(t), "AC", 0.95) for t in range(5, 20)]
    predictions = _predictions(rows)

    alarm = sustained_alarm(predictions, min_duration_s=10.0, min_probability=0.9)

    assert alarm.iloc[:15].eq("Normal").all()
    assert alarm.iloc[15:].eq("AC").all()


def test_detection_delay_on_known_switch_on() -> None:
    rows = [("run1", float(t), "Normal", 0.99) for t in range(0, 5)]
    rows += [("run1", float(t), "AC", 0.95) for t in range(5, 20)]
    predictions = _predictions(rows)
    alarm = sustained_alarm(predictions, min_duration_s=10.0, min_probability=0.9)
    alarms = pd.DataFrame({"run": predictions["run"], "t": predictions["t"], "alarm": alarm})
    switch_on = pd.DataFrame({"run": ["run1"], "t": [5.0]})

    result = detection_delay(alarms, switch_on)

    assert result.loc[0, "run"] == "run1"
    assert result.loc[0, "class"] == "AC"
    assert result.loc[0, "delay_s"] == 10.0  # alarm onsets at t=15, switch-on at t=5


def test_detection_delay_counts_pre_switch_on_alarm_as_false_alarm_not_detection() -> None:
    # Alarm episode starts before switch-on and continues after; it should not
    # count as a fresh detection at or after switch-on.
    rows = [("run1", float(t), "AC", 0.95) for t in range(0, 20)]
    predictions = _predictions(rows)
    alarm = sustained_alarm(predictions, min_duration_s=10.0, min_probability=0.9)
    alarms = pd.DataFrame({"run": predictions["run"], "t": predictions["t"], "alarm": alarm})
    switch_on = pd.DataFrame({"run": ["run1"], "t": [15.0]})

    result = detection_delay(alarms, switch_on)

    assert result.loc[0, "delay_s"] != result.loc[0, "delay_s"]  # NaN: no onset at/after t=15
    assert result.loc[0, "class"] is None


def test_detection_delay_skips_runs_without_switch_on() -> None:
    alarms = pd.DataFrame({"run": ["run1"], "t": [0.0], "alarm": ["Normal"]})
    switch_on = pd.DataFrame({"run": ["run1"], "t": [float("nan")]})

    result = detection_delay(alarms, switch_on)

    assert result.empty
