"""EDA helpers: matched healthy baselines, per-channel shifts, switch-on windows,
time-based rolling std, and the checklist's physics quantities.
"""

from __future__ import annotations

import pandas as pd

from keyframe.features import (
    cooler_effectiveness,
    cooling_water_rise,
    exhaust_temp_spread,
    fuel_flow_per_kw,
    indicated_work_spread,
    pmax_spread,
    turbine_temp_drop,
)

__all__ = [
    "matched_healthy",
    "fault_shift",
    "around_switch_on",
    "rolling_std",
    "cooler_effectiveness",
    "exhaust_temp_spread",
    "pmax_spread",
    "indicated_work_spread",
    "turbine_temp_drop",
    "cooling_water_rise",
    "fuel_flow_per_kw",
]

GRADUAL_FAULT_TYPES = {"AC", "AF", "CW", "TD"}
LOAD_MATCH_TOLERANCE_KW = 5.0


def matched_healthy(df: pd.DataFrame, run: str) -> pd.DataFrame:
    """Healthy rows to compare `run` against: its own pre-fault segment plus
    reference rows within 5 kW of the median shaft power of its faulty rows.

    Stepped runs with no pre-fault segment (e.g. the injector run) are matched
    per load bin instead, using only reference rows.
    """
    own = df[df["run"] == run]
    healthy_own = own[own["label"] == "Normal"]
    faulty = own[own["label"] != "Normal"]
    reference = df[df["run"] == "Reference_Data"]

    if healthy_own.empty:
        parts = []
        for load_bin, group in faulty.groupby("load_bin"):
            median_power = group["Shaft Power"].median()
            parts.append(
                reference[
                    (reference["load_bin"] == load_bin)
                    & ((reference["Shaft Power"] - median_power).abs() <= LOAD_MATCH_TOLERANCE_KW)
                ]
            )
        return pd.concat(parts) if parts else df.iloc[0:0]

    median_power = faulty["Shaft Power"].median()
    matched_reference = reference[
        (reference["Shaft Power"] - median_power).abs() <= LOAD_MATCH_TOLERANCE_KW
    ]
    return pd.concat([healthy_own, matched_reference])


def fault_shift(df: pd.DataFrame, run: str, channels: list[str]) -> pd.DataFrame:
    """Per channel: healthy/faulty mean and std, standardised mean shift, std ratio.

    Gradual faults also report the shift over the run's last 30 minutes.
    """
    faulty = df[(df["run"] == run) & (df["label"] != "Normal")]
    healthy = matched_healthy(df, run)
    fault_type = df.loc[df["run"] == run, "fault_type"].iloc[0]
    is_gradual = fault_type in GRADUAL_FAULT_TYPES
    t_max = faulty["t"].max()
    last30 = faulty[faulty["t"] >= t_max - 30 * 60]

    rows = []
    for channel in channels:
        healthy_mean, healthy_std = healthy[channel].mean(), healthy[channel].std()
        faulty_mean, faulty_std = faulty[channel].mean(), faulty[channel].std()
        row = {
            "channel": channel,
            "healthy_mean": healthy_mean,
            "healthy_std": healthy_std,
            "faulty_mean": faulty_mean,
            "faulty_std": faulty_std,
            "shift": (faulty_mean - healthy_mean) / healthy_std,
            "std_ratio": faulty_std / healthy_std,
        }
        if is_gradual:
            last30_mean = last30[channel].mean()
            row["last30_mean"] = last30_mean
            row["last30_shift"] = (last30_mean - healthy_mean) / healthy_std
        rows.append(row)
    return pd.DataFrame(rows)


def around_switch_on(
    df: pd.DataFrame, run: str, minutes_before: float = 30, minutes_after: float = 60
) -> pd.DataFrame:
    """The run's rows within `minutes_before`/`minutes_after` of switch-on,
    with a `t_from_switch_on_min` column.
    """
    own = df[df["run"] == run].sort_values("t")
    faulty_t = own.loc[own["label"] != "Normal", "t"]
    if faulty_t.empty:
        raise ValueError(f"around_switch_on: no switch-on found for run {run!r}")
    t_switch = faulty_t.iloc[0]

    window = own[
        (own["t"] >= t_switch - minutes_before * 60) & (own["t"] <= t_switch + minutes_after * 60)
    ].copy()
    window["t_from_switch_on_min"] = (window["t"] - t_switch) / 60.0
    return window


def rolling_std(series: pd.Series, t: pd.Series, window_s: float) -> pd.Series:
    """Time-based rolling standard deviation over the trailing `window_s` seconds.

    Windows are defined via `t`, never rows; call this once per run so it never
    crosses a run boundary.
    """
    time_index = pd.to_timedelta(t.to_numpy(), unit="s")
    ordered = pd.Series(series.to_numpy(), index=time_index).sort_index()
    result = ordered.rolling(f"{window_s}s", min_periods=1).std()
    return pd.Series(result.reindex(time_index).to_numpy(), index=series.index)
