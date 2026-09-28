"""Audit tables for notebook 00: sampling gaps, missing channels, switch-on, load bins."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from keyframe import paths

MISSING_CHANNELS = {"Compressor Filter Loss", "Turbine Back Pressure"}
GAP_THRESHOLD_S = 4
_FIXED_LOAD = re.compile(r"^\d+%$")


def sampling_intervals(df: pd.DataFrame) -> pd.DataFrame:
    """Per run: counts of each time step between consecutive rows and the largest gap."""
    rows = []
    for run, group in df.groupby("run", sort=False):
        steps = group["t"].diff().dropna()
        counts = steps.round(6).value_counts().sort_index()
        gaps = steps[steps > GAP_THRESHOLD_S]
        rows.append(
            {
                "run": run,
                "step_counts": counts.to_dict(),
                "max_gap_s": float(steps.max()) if not steps.empty else 0.0,
                "gaps_s": sorted(float(g) for g in gaps),
            }
        )
    return pd.DataFrame(rows)


def missing_by_channel(df: pd.DataFrame) -> pd.DataFrame:
    """Per run and channel: share of missing values, confirming the known fully-empty channels."""
    channels = [
        c
        for c in df.columns
        if c not in {"run", "fault_type", "label", "t", "load_bin", "nominal_load"}
    ]
    rows = []
    for run, group in df.groupby("run", sort=False):
        for channel in channels:
            share = group[channel].isna().mean()
            if share > 0:
                rows.append({"run": run, "channel": channel, "missing_share": share})
    result = pd.DataFrame(rows, columns=["run", "channel", "missing_share"])

    for channel in MISSING_CHANNELS:
        if channel not in channels:
            continue
        fully_empty_runs = result.loc[
            (result["channel"] == channel) & (result["missing_share"] == 1.0), "run"
        ]
        if len(fully_empty_runs) != 5:
            raise ValueError(
                f"missing_by_channel: expected 5 runs fully missing {channel!r}, "
                f"got {len(fully_empty_runs)}: {sorted(fully_empty_runs)}"
            )

    return result


def switch_on_points(df: pd.DataFrame) -> pd.DataFrame:
    """Per scenario run: first Anomaly State=1 row, and healthy/faulty segment lengths."""
    rows = []
    for run, group in df.groupby("run", sort=False):
        if run == "Reference_Data" or "Anomaly State" not in group.columns:
            continue
        group = group.reset_index(drop=True)
        anomaly = group["Anomaly State"] == 1
        n_rows = len(group)
        if not anomaly.any() or anomaly.iloc[0]:
            total_minutes = (group["t"].iloc[-1] - group["t"].iloc[0]) / 60.0
            all_faulty = bool(anomaly.iloc[0])
            rows.append(
                {
                    "run": run,
                    "row_index": None,
                    "t": None,
                    "Time_abs": None,
                    "healthy_rows": 0 if all_faulty else n_rows,
                    "faulty_rows": n_rows if all_faulty else 0,
                    "healthy_minutes": 0.0 if all_faulty else total_minutes,
                    "faulty_minutes": total_minutes if all_faulty else 0.0,
                }
            )
            continue
        first_idx = int(anomaly.to_numpy().argmax())
        healthy_rows = first_idx
        faulty_rows = n_rows - healthy_rows
        t0, t_switch, t_end = group["t"].iloc[0], group["t"].iloc[first_idx], group["t"].iloc[-1]
        rows.append(
            {
                "run": run,
                "row_index": first_idx,
                "t": float(t_switch),
                "Time_abs": float(group["Time_abs"].iloc[first_idx]),
                "healthy_rows": healthy_rows,
                "faulty_rows": faulty_rows,
                "healthy_minutes": (t_switch - t0) / 60.0,
                "faulty_minutes": (t_end - t_switch) / 60.0,
            }
        )
    return pd.DataFrame(rows)


def load_bin_agreement(df: pd.DataFrame) -> pd.DataFrame:
    """Per fixed-load run, the share matching nominal load; stepped/reference get bin counts."""
    rows: list[dict[str, object]] = []
    for run, group in df.groupby("run", sort=False):
        nominal = group["nominal_load"].iloc[0]
        if isinstance(nominal, str) and _FIXED_LOAD.match(nominal):
            target = int(nominal.rstrip("%"))
            share = (group["load_bin"] == target).mean()
            rows.append({"run": run, "fixed_load": True, "agreement_share": share})
        else:
            counts = group["load_bin"].value_counts().sort_index()
            rows.append({"run": run, "fixed_load": False, "bin_counts": counts.to_dict()})
    return pd.DataFrame(rows)


def write_clean_table(
    df: pd.DataFrame, path: str | Path = paths.PROCESSED / "clean.parquet"
) -> Path:
    """Write the clean table as Parquet, keeping every channel."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return path
