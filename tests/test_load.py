"""Reading a release CSV keyed by full names, with its ColumnInfo metadata table."""

import pandas as pd
import pytest

from keyframe import load, paths


def test_synthetic_csv_round_trips_full_names_nan_and_dtypes(write_three_row_csv) -> None:
    path = write_three_row_csv(
        full_names=[
            "Time",
            "Max. In-Cylinder Press. No.1",
            "Min. In-Cylinder Press. No.1",
            "Engine room Temp.",
            "Anomaly State",
        ],
        symbols=["T", "Pmax", "Pmax", "Tamb", "State"],
        units=["sec", "MPa", "MPa", "°C", ""],
        rows=[
            ["0.0", "1.5", "", "20.0", "0"],
            ["1.0", "1.6", "1.2", "21.0", "1"],
        ],
    )

    data, column_info = load.read_csv_with_header(path)

    assert list(data.columns) == [
        "Time",
        "Max. In-Cylinder Press. No.1",
        "Min. In-Cylinder Press. No.1",
        "Engine room Temp.",
        "Anomaly State",
    ]
    assert pd.isna(data.loc[0, "Min. In-Cylinder Press. No.1"])
    assert data["Time"].dtype == "float64"
    assert data["Anomaly State"].dtype == "int64"
    assert list(column_info.frame["symbol"]) == ["T", "Pmax", "Pmax", "Tamb", "State"]
    assert column_info.frame.loc[3, "unit"] == "°C"


@pytest.mark.data
def test_real_scenario_file_flags_exactly_the_six_raw_voltage_channels() -> None:
    path = paths.RAW / "AC_Fouling" / "AC_Fouling_85_Load.csv"
    if not path.exists():
        pytest.skip("dataset not downloaded")

    _, column_info = load.read_csv_with_header(path)

    flagged = set(column_info.frame.loc[column_info.frame["is_raw_voltage"], "symbol"])
    assert flagged == load.RAW_VOLTAGE_SYMBOLS
