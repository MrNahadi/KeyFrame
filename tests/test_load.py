"""Reading a release CSV keyed by full names, with its ColumnInfo metadata table."""

from pathlib import Path

import pandas as pd
import pytest

from keyframe import load, paths

FULL_NAMES = ["Time_abs", "Time_rel", "Anomaly State", "Shaft Power"]
SYMBOLS = ["Tabs", "Trel", "State", "Ps"]
UNITS = ["sec", "sec", "", "kW"]
REFERENCE_NAMES = ["Time", "Shaft Power"]
REFERENCE_SYMBOLS = ["T", "Ps"]
REFERENCE_UNITS = ["sec", "kW"]


def _write_csv(tmp_path: Path, name: str, full_names, symbols, units, rows) -> Path:
    path = tmp_path / name
    lines = [
        ",".join(full_names),
        ",".join(symbols),
        ",".join(units),
        *(",".join(row) for row in rows),
    ]
    path.write_text("\n".join(lines) + "\n")
    return path


def _dataset_index(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


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


def test_load_run_labels_scenario_rows_by_anomaly_state(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "AC_Fouling_40_Load.csv",
        FULL_NAMES,
        SYMBOLS,
        UNITS,
        rows=[
            ["0.0", "0.0", "0", "100.0"],
            ["1.0", "1.0", "1", "100.0"],
        ],
    )
    dataset_index = _dataset_index([{"file_name": "AC_Fouling_40_Load.csv", "nominal_load": "40%"}])

    data = load.load_run(path, dataset_index=dataset_index)

    assert list(data["label"]) == ["Normal", "AC"]
    assert list(data["fault_type"]) == ["AC", "AC"]
    assert list(data["run"]) == ["AC_Fouling_40_Load", "AC_Fouling_40_Load"]
    assert list(data["t"]) == [0.0, 1.0]
    assert list(data["nominal_load"]) == ["40%", "40%"]


def test_load_run_reference_file_uses_time_and_is_normal(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "Reference_Data.csv",
        REFERENCE_NAMES,
        REFERENCE_SYMBOLS,
        REFERENCE_UNITS,
        rows=[["10.0", "100.0"], ["11.0", "100.0"]],
    )
    dataset_index = _dataset_index(
        [{"file_name": "Reference_Data.csv", "nominal_load": "reference operating range"}]
    )

    data = load.load_run(path, dataset_index=dataset_index)

    assert list(data["label"]) == ["Normal", "Normal"]
    assert list(data["fault_type"]) == ["Normal", "Normal"]
    assert list(data["t"]) == [0.0, 1.0]
    assert "Anomaly State" not in data.columns


def test_load_all_unions_columns_and_orders_by_path(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    scenario_dir = raw_dir / "AC_Fouling"
    scenario_dir.mkdir(parents=True)
    (raw_dir / "lockbox").mkdir()

    _write_csv(
        scenario_dir,
        "AC_Fouling_40_Load.csv",
        FULL_NAMES,
        SYMBOLS,
        UNITS,
        rows=[["0.0", "0.0", "0", "100.0"]],
    )
    _write_csv(
        raw_dir,
        "Reference_Data.csv",
        REFERENCE_NAMES,
        REFERENCE_SYMBOLS,
        REFERENCE_UNITS,
        rows=[["10.0", "100.0"]],
    )
    _write_csv(
        raw_dir / "lockbox",
        "AC_Fouling_60_Load.csv",
        FULL_NAMES,
        SYMBOLS,
        UNITS,
        rows=[["0.0", "0.0", "0", "100.0"]],
    )
    pd.DataFrame(
        [
            {"file_name": "AC_Fouling/AC_Fouling_40_Load.csv", "nominal_load": "40%"},
            {"file_name": "Reference_Data.csv", "nominal_load": "reference operating range"},
        ]
    ).to_csv(raw_dir / "dataset_index.csv", index=False)

    data = load.load_all(raw_dir)

    assert len(data) == 2
    assert list(data["run"]) == ["AC_Fouling_40_Load", "Reference_Data"]
    assert pd.isna(data.loc[1, "Anomaly State"])
    assert pd.isna(data.loc[1, "Time_abs"])
