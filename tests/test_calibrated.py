"""Synthetic tests for the calibrated track (feature 17, ADR 0014)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from keyframe import calibrated


def _run(name: str, load: int, n: int, fault_from: int | None, level: float) -> pd.DataFrame:
    t = np.arange(n, dtype=float) * 60.0  # one row a minute
    label = np.where(fault_from is not None and np.arange(n) >= (fault_from or 0), "AC", "Normal")
    return pd.DataFrame(
        {
            "run": name,
            "load_bin": load,
            "t": t,
            "label": label,
            "Engine Speed": 1000.0 + load,
            "Water Brake Weight": float(load),
            "Fuel Flow": load / 10.0,
            "Fuel Temp.": level + np.where(label == "AC", 5.0, 0.0),
        }
    )


def _table() -> pd.DataFrame:
    return pd.concat(
        [
            _run("fault_40", 40, 60, fault_from=30, level=40.0),
            _run("healthy_40", 40, 60, fault_from=None, level=45.0),
            _run("faulty_from_start", 60, 60, fault_from=0, level=50.0),
            _run("short", 75, 10, fault_from=None, level=55.0),
        ],
        ignore_index=True,
    )


def test_deviation_is_measured_from_the_first_twenty_minutes():
    table, ready = calibrated.add_calibrated(_table())
    fault = table[table["run"] == "fault_40"]
    # baseline is the session's own healthy level (40), so the fault shows as +5
    assert fault.loc[fault["label"] == "AC", "cal_Fuel Temp."].eq(5.0).all()
    assert fault.loc[fault["label"] == "Normal", "cal_Fuel Temp."].eq(0.0).all()
    # the session level itself (40 vs 45) is gone
    healthy = table[table["run"] == "healthy_40"]
    assert healthy["cal_Fuel Temp."].eq(0.0).all()


def test_rows_inside_the_baseline_window_are_not_monitored():
    table, ready = calibrated.add_calibrated(_table())
    fault = table["run"] == "fault_40"
    assert not ready[fault & (table["t"] < calibrated.BASELINE_S)].any()
    assert ready[fault & (table["t"] >= calibrated.BASELINE_S)].all()


def test_segments_without_a_complete_healthy_baseline_are_dropped():
    _, ready = calibrated.add_calibrated(_table())
    table = _table()
    assert not ready[table["run"] == "faulty_from_start"].any()
    assert not ready[table["run"] == "short"].any()


def test_a_new_load_segment_gets_its_own_baseline():
    a = _run("stepped", 40, 30, fault_from=None, level=40.0)
    b = _run("stepped", 60, 30, fault_from=None, level=70.0)
    b["t"] += a["t"].iloc[-1] + 60.0
    table, ready = calibrated.add_calibrated(pd.concat([a, b], ignore_index=True))
    assert table.loc[ready, "cal_Fuel Temp."].eq(0.0).all()
    assert calibrated.segment_ids(table).nunique() == 2


def test_baseline_ignores_later_rows():
    original, _ = calibrated.add_calibrated(_table())
    changed = _table()
    late = (changed["run"] == "fault_40") & (changed["t"] >= 50 * 60.0)
    changed.loc[late, "Fuel Temp."] += 100.0
    table, _ = calibrated.add_calibrated(changed)
    early = (changed["run"] == "fault_40") & ~late
    pd.testing.assert_series_equal(
        table.loc[early, "cal_Fuel Temp."], original.loc[early, "cal_Fuel Temp."]
    )


def test_calibrated_arm_drops_absolute_levels_but_keeps_the_operating_point():
    table, _ = calibrated.add_calibrated(_table())
    columns = calibrated.arm_columns(table, "calibrated")
    assert "Fuel Temp." not in columns
    assert "cal_Fuel Temp." in columns
    assert set(calibrated.LOAD_INPUTS) <= set(columns)
    zero_shot = calibrated.arm_columns(table, "zero_shot")
    assert not any(c.startswith("cal_") for c in zero_shot)
    both = calibrated.arm_columns(table, "raw+calibrated")
    assert len(both) == len(set(both))
    with pytest.raises(ValueError, match="unknown arm"):
        calibrated.arm_columns(table, "nope")
