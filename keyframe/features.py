"""Model input columns for the raw-sensor baselines, with leakage exclusions enforced."""

from __future__ import annotations

import pandas as pd

EXCLUDED_COLUMNS: frozenset[str] = frozenset(
    {
        "Compressor Filter Loss",
        "Turbine Back Pressure",
        "Engine room Temp.",
        "Time",
        "Time_abs",
        "Time_rel",
        "Anomaly State",
        "run",
        "fault_type",
        "label",
        "t",
        "load_bin",
        "nominal_load",
    }
)


def raw_sensor_columns(df: pd.DataFrame) -> list[str]:
    """Return every numeric column of ``df`` not in ``EXCLUDED_COLUMNS``, in table order."""
    numeric = df.select_dtypes(include="number")
    return [column for column in numeric.columns if column not in EXCLUDED_COLUMNS]
