"""Data-marked tests: the loaded table matches the real dataset_index.csv release exactly."""

import pandas as pd
import pytest

from keyframe import audit, download, load, paths

pytestmark = pytest.mark.data


@pytest.fixture(scope="module")
def dataset_index():
    if not paths.RAW.exists():
        pytest.skip("dataset not downloaded")
    return pd.read_csv(paths.RAW / "dataset_index.csv")


@pytest.fixture(scope="module")
def full_table(dataset_index):
    return load.load_all(paths.RAW)


def test_row_counts_and_column_counts_match_the_index(dataset_index, full_table):
    for _, row in dataset_index.iterrows():
        if row["file_name"].endswith(download.LOCKBOX_FILE):
            continue
        run = row["file_name"].split("/")[-1].removesuffix(".csv")
        run_df = full_table[full_table["run"] == run]
        assert len(run_df) == row["data_rows"], run
        raw_columns = row["columns"]
        expected = 73 if run != "Reference_Data" else 70
        assert raw_columns == expected, run


def test_class_totals_match_r12(full_table):
    totals = full_table.groupby("label").size().to_dict()
    assert totals == {
        "Normal": 51_893,
        "AC": 17_500,
        "AF": 15_074,
        "INJ": 6_492,
        "CW": 9_174,
        "TD": 7_846,
    }
    assert len(full_table) == 107_979


def test_every_fixed_load_run_has_exactly_one_switch_on(full_table):
    result = audit.switch_on_points(full_table)
    fixed_load_runs = (
        full_table[["run", "nominal_load"]].drop_duplicates().set_index("run")["nominal_load"]
    )
    for _, row in result.iterrows():
        nominal = fixed_load_runs.get(row["run"])
        if isinstance(nominal, str) and audit._FIXED_LOAD.match(nominal):
            assert row["healthy_rows"] > 0
            assert row["faulty_rows"] > 0


def test_injector_run_has_no_switch_on(full_table):
    result = audit.switch_on_points(full_table).set_index("run")
    injector_runs = full_table.loc[full_table["fault_type"] == "INJ", "run"].unique()
    for run in injector_runs:
        assert pd.isna(result.loc[run, "row_index"])


def test_dpf_and_dpex_are_fully_empty_in_the_four_raw_runs(full_table):
    result = audit.missing_by_channel(full_table)
    for channel in audit.MISSING_CHANNELS:
        fully_empty = set(
            result.loc[
                (result["channel"] == channel)
                & (result["missing_share"] == 1.0)
                & (result["run"] != "Reference_Data"),
                "run",
            ]
        )
        assert fully_empty == audit.EXPECTED_EMPTY_RUNS & set(full_table["run"])


def test_fifth_expected_empty_run_is_the_lockboxed_run(full_table):
    assert audit.EXPECTED_EMPTY_RUNS - set(full_table["run"]) == {
        "Clogged_Injector_Nozzle2_LoadProgram"
    }
    assert download.LOCKBOX_FILE == "Clogged_Injector_Nozzle2_LoadProgram.csv"
