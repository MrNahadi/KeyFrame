"""Raw-sensor input columns exclude leakage columns and non-numeric columns."""

import pandas as pd
import pytest

from keyframe import features, paths


def test_excluded_columns_never_in_output():
    df = pd.DataFrame(
        {
            "Compressor Filter Loss": [1.0],
            "Turbine Back Pressure": [1.0],
            "Engine room Temp.": [1.0],
            "Time": [1.0],
            "Time_abs": [1.0],
            "Time_rel": [1.0],
            "Anomaly State": [1],
            "run": ["run1"],
            "fault_type": ["Normal"],
            "label": ["Normal"],
            "t": [1.0],
            "load_bin": [40],
            "nominal_load": [40.0],
            "Shaft Power": [120.0],
            "Fuel Rack Position": [50.0],
        }
    )

    result = features.raw_sensor_columns(df)

    assert set(result).isdisjoint(features.EXCLUDED_COLUMNS)
    assert result == ["Shaft Power", "Fuel Rack Position"]


def test_non_numeric_columns_dropped():
    df = pd.DataFrame({"Shaft Power": [120.0], "fault_type": ["Normal"], "note": ["x"]})

    result = features.raw_sensor_columns(df)

    assert result == ["Shaft Power"]


@pytest.mark.data
def test_clean_parquet_columns():
    path = paths.PROCESSED / "clean.parquet"
    if not path.exists():
        pytest.skip("data/processed/clean.parquet not built")
    df = pd.read_parquet(path)

    result = features.raw_sensor_columns(df)

    assert result
    assert set(result).isdisjoint(features.EXCLUDED_COLUMNS)
    assert not df[result].isna().any().any()
