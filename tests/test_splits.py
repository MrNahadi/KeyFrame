"""Mapping shaft power to nominal load bins."""

import math

import pandas as pd
import pytest

from keyframe import splits


@pytest.mark.parametrize(
    "shaft_power_kw, expected",
    [
        (129.9, 40),
        (130, 60),
        (174.9, 60),
        (175, 75),
        (206.9, 75),
        (207, 85),
    ],
)
def test_load_bin_boundaries(shaft_power_kw: float, expected: int) -> None:
    assert splits.load_bin(shaft_power_kw) == expected


def test_load_bin_raises_on_nan() -> None:
    with pytest.raises(ValueError):
        splits.load_bin(math.nan)


def test_load_bin_works_on_series() -> None:
    result = splits.load_bin(pd.Series([50, 150, 180, 210]))
    assert list(result) == [40, 60, 75, 85]
