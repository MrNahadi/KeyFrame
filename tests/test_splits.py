"""Mapping shaft power to nominal load bins, and leave-one-load-out folds."""

import math

import pandas as pd
import pytest

from keyframe import paths, splits


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


def _synthetic_table() -> pd.DataFrame:
    # A stepped run (e.g. the reference file) contributes rows to several bins.
    stepped = pd.DataFrame({"run": ["stepped"] * 4, "load_bin": [40, 60, 75, 85]})
    steady = pd.DataFrame(
        {
            "run": ["a", "a", "b", "b", "c", "c"],
            "load_bin": [40, 60, 75, 85, 40, 85],
        }
    )
    return pd.concat([stepped, steady], ignore_index=True)


def test_lolo_folds_no_shared_bin_and_full_coverage() -> None:
    df = _synthetic_table()
    seen_test_rows: list[int] = []
    for held_out_bin, train_index, test_index in splits.lolo_folds(df):
        train_bins = set(df.loc[train_index, "load_bin"])
        test_bins = set(df.loc[test_index, "load_bin"])
        assert test_bins == {held_out_bin}
        assert held_out_bin not in train_bins
        assert set(train_index).isdisjoint(set(test_index))
        seen_test_rows.extend(test_index)

    assert sorted(seen_test_rows) == sorted(df.index)
    assert len(seen_test_rows) == len(set(seen_test_rows))


def test_inner_lolo_folds_never_see_outer_held_out_bin() -> None:
    df = _synthetic_table()
    for held_out_bin, train_index, _test_index in splits.lolo_folds(df):
        train_df = df.loc[train_index]
        for inner_bin, inner_train_index, inner_test_index in splits.inner_lolo_folds(train_df):
            assert held_out_bin != inner_bin
            inner_bins = set(df.loc[inner_train_index, "load_bin"]) | set(
                df.loc[inner_test_index, "load_bin"]
            )
            assert held_out_bin not in inner_bins


@pytest.mark.data
def test_lolo_folds_75_percent_bin_has_no_cw_or_td() -> None:
    path = paths.PROCESSED / "clean.parquet"
    if not path.exists():
        pytest.skip("data/processed/clean.parquet not built")
    df = pd.read_parquet(path)

    folds = list(splits.lolo_folds(df))
    assert len(folds) == 4

    for held_out_bin, _train_index, test_index in folds:
        if held_out_bin == 75:
            test_fault_types = set(df.loc[test_index, "fault_type"])
            assert not test_fault_types & {"CW", "TD"}
