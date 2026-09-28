"""Nominal load bins derived from measured shaft power."""

from __future__ import annotations

import numpy as np
import pandas as pd

_EDGES = [130, 175, 207]
_BINS = [40, 60, 75, 85]


def load_bin(shaft_power_kw: float | pd.Series) -> int | pd.Series:
    """Map shaft power (kW) to a nominal load bin: 40, 60, 75 or 85."""
    if isinstance(shaft_power_kw, pd.Series):
        if shaft_power_kw.isna().any():
            raise ValueError("load_bin: NaN shaft power")
        indices = np.searchsorted(_EDGES, shaft_power_kw.to_numpy(), side="right")
        return pd.Series([_BINS[i] for i in indices], index=shaft_power_kw.index)

    if pd.isna(shaft_power_kw):
        raise ValueError("load_bin: NaN shaft power")
    index = np.searchsorted(_EDGES, shaft_power_kw, side="right")
    return _BINS[int(index)]
