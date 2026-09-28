"""Nominal load bins derived from measured shaft power, and leave-one-load-out folds."""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np
import pandas as pd

_EDGES = [130, 175, 207]
LOAD_BINS: tuple[int, ...] = (40, 60, 75, 85)
_BINS = list(LOAD_BINS)


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


def lolo_folds(df: pd.DataFrame) -> Iterator[tuple[int, pd.Index, pd.Index]]:
    """Leave-one-load-out folds: one per bin present, holding that bin out as test."""
    for bin_value in sorted(df["load_bin"].unique()):
        test_index = df.index[df["load_bin"] == bin_value]
        train_index = df.index[df["load_bin"] != bin_value]
        yield bin_value, train_index, test_index


def inner_lolo_folds(train_df: pd.DataFrame) -> Iterator[tuple[int, pd.Index, pd.Index]]:
    """Nested leave-one-load-out folds over the bins present in a training set only."""
    yield from lolo_folds(train_df)
