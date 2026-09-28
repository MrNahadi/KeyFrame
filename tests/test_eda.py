"""Matched healthy baselines, shifts, switch-on windows, rolling std, physics quantities."""

import numpy as np
import pandas as pd

from keyframe import eda


def _fault_run_df(fault_type: str = "AC") -> pd.DataFrame:
    n_healthy, n_faulty = 10, 10
    n = n_healthy + n_faulty
    t = np.arange(n, dtype=float) * 2.0
    label = ["Normal"] * n_healthy + [fault_type] * n_faulty
    channel = np.concatenate([np.zeros(n_healthy), np.full(n_faulty, 2.0)])
    return pd.DataFrame(
        {
            "run": ["Run_A"] * n,
            "fault_type": [fault_type] * n,
            "label": label,
            "t": t,
            "Shaft Power": np.full(n, 150.0),
            "load_bin": np.full(n, 60),
            "channel": channel,
        }
    )


def _reference_df(shaft_power: float = 150.0, n: int = 20) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return pd.DataFrame(
        {
            "run": ["Reference_Data"] * n,
            "fault_type": ["Normal"] * n,
            "label": ["Normal"] * n,
            "t": np.arange(n, dtype=float) * 2.0,
            "Shaft Power": np.full(n, shaft_power) + rng.normal(0, 0.1, n),
            "load_bin": np.full(n, 60),
            "channel": rng.normal(0, 1, n),
        }
    )


def test_matched_healthy_uses_own_pre_fault_and_matched_reference() -> None:
    df = pd.concat([_fault_run_df(), _reference_df(), _reference_df(shaft_power=300)])
    matched = eda.matched_healthy(df, "Run_A")
    assert set(matched["run"]) <= {"Run_A", "Reference_Data"}
    assert (matched.loc[matched["run"] == "Run_A", "label"] == "Normal").all()
    assert (matched["Shaft Power"] - 150.0).abs().max() <= 5.0


def test_matched_healthy_never_returns_other_fault_runs() -> None:
    other = _fault_run_df(fault_type="INJ")
    other["run"] = "Run_B"
    df = pd.concat([_fault_run_df(), other, _reference_df()])
    matched = eda.matched_healthy(df, "Run_A")
    assert "Run_B" not in set(matched["run"])


def test_matched_healthy_stepped_run_uses_reference_per_load_bin() -> None:
    stepped = _fault_run_df(fault_type="INJ")
    stepped["label"] = "INJ"  # no pre-fault segment at all
    df = pd.concat([stepped, _reference_df()])
    matched = eda.matched_healthy(df, "Run_A")
    assert (matched["run"] == "Reference_Data").all()


def test_fault_shift_reports_known_standardised_shift() -> None:
    # No reference rows match this run's load, so the baseline is exactly its
    # own pre-fault segment: mean 0, std 1. A +2 std faulty step gives shift 2.0.
    healthy_channel = np.array([-1.0, 0.0, 1.0])  # mean 0, std 1 (ddof=1)
    faulty_channel = np.array([1.0, 2.0, 3.0])  # mean 2
    n = len(healthy_channel) + len(faulty_channel)
    df = pd.DataFrame(
        {
            "run": ["Run_A"] * n,
            "fault_type": ["AC"] * n,
            "label": ["Normal"] * len(healthy_channel) + ["AC"] * len(faulty_channel),
            "t": np.arange(n, dtype=float) * 2.0,
            "Shaft Power": np.full(n, 150.0),
            "load_bin": np.full(n, 60),
            "channel": np.concatenate([healthy_channel, faulty_channel]),
        }
    )
    df = pd.concat([df, _reference_df(shaft_power=300.0)])
    result = eda.fault_shift(df, "Run_A", ["channel"])
    row = result.loc[result["channel"] == "channel"].iloc[0]
    assert row["healthy_mean"] == 0.0
    assert row["healthy_std"] == 1.0
    assert row["faulty_mean"] == 2.0
    assert row["shift"] == 2.0


def test_fault_shift_adds_last30_for_gradual_faults() -> None:
    df = pd.concat([_fault_run_df(fault_type="AC"), _reference_df()])
    result = eda.fault_shift(df, "Run_A", ["channel"])
    assert "last30_shift" in result.columns


def test_fault_shift_omits_last30_for_injector() -> None:
    df = pd.concat([_fault_run_df(fault_type="INJ"), _reference_df()])
    result = eda.fault_shift(df, "Run_A", ["channel"])
    assert "last30_shift" not in result.columns


def test_around_switch_on_adds_relative_minutes_column() -> None:
    df = _fault_run_df()
    window = eda.around_switch_on(df, "Run_A", minutes_before=1, minutes_after=1)
    switch_t = df.loc[df["label"] != "Normal", "t"].iloc[0]
    expected = (df["t"] - switch_t) / 60.0
    pd.testing.assert_series_equal(
        window["t_from_switch_on_min"],
        expected.loc[window.index],
        check_names=False,
    )


def test_rolling_std_uses_time_not_rows() -> None:
    # Uneven spacing: two points 1 s apart, then a big gap, so a 5 s window
    # should only ever see the two nearby points, never row-count based.
    t = pd.Series([0.0, 1.0, 100.0, 101.0])
    series = pd.Series([1.0, 3.0, 10.0, 50.0])
    result = eda.rolling_std(series, t, window_s=5)
    assert result.iloc[0] != result.iloc[0]  # NaN: single point, std undefined
    assert result.iloc[1] == series.iloc[:2].std()
    assert result.iloc[2] != result.iloc[2]  # only itself in window: NaN
    assert result.iloc[3] == series.iloc[2:4].std()


def test_cooler_effectiveness_known_triple() -> None:
    df = pd.DataFrame(
        {
            "Charge Air IC Air Temp. In": [50.0],
            "Charge Air IC Air Temp. Out": [30.0],
            "Charge Air IC Cooling Water Temp. In": [10.0],
        }
    )
    result = eda.cooler_effectiveness(df)
    assert result.iloc[0] == (50.0 - 30.0) / (50.0 - 10.0)


def test_turbine_temp_drop() -> None:
    df = pd.DataFrame({"Exh.Gas Temp. Turbine In": [400.0], "Exh.Gas Temp. Turbine Out": [300.0]})
    assert eda.turbine_temp_drop(df).iloc[0] == 100.0


def test_cooling_water_rise() -> None:
    df = pd.DataFrame(
        {
            "Cooling Water Temp. Engine Out I": [40.0],
            "Cooling Water Temp. Engine Out II": [42.0],
            "Cooling Water Temp. Engine Out III": [44.0],
            "Cooling Water Temp. Engine In": [30.0],
        }
    )
    assert eda.cooling_water_rise(df).iloc[0] == 42.0 - 30.0


def test_fuel_flow_per_kw() -> None:
    df = pd.DataFrame({"Fuel Flow": [10.0], "Shaft Power": [100.0]})
    assert eda.fuel_flow_per_kw(df).iloc[0] == 0.1
