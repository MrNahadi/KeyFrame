import pandas as pd

from keyframe import audit


def test_sampling_intervals_reports_gap():
    df = pd.DataFrame(
        {
            "run": ["r1"] * 5,
            "t": [0, 1, 2, 9, 10],
        }
    )
    result = audit.sampling_intervals(df).set_index("run").loc["r1"]
    assert result["max_gap_s"] == 7.0
    assert result["gaps_s"] == [7.0]


def test_missing_by_channel_reports_all_empty_channel():
    df = pd.DataFrame(
        {
            "run": ["r1", "r1", "r2", "r2"],
            "Foo": [1.0, 2.0, 3.0, 4.0],
            "Bar": [float("nan"), float("nan"), 5.0, 6.0],
        }
    )
    result = audit.missing_by_channel(df)
    row = result[(result["run"] == "r1") & (result["channel"] == "Bar")].iloc[0]
    assert row["missing_share"] == 1.0
    assert result[(result["run"] == "r2") & (result["channel"] == "Bar")].empty


def test_switch_on_points_reports_none_for_injector_run():
    df = pd.DataFrame(
        {
            "run": ["inj"] * 4,
            "t": [0.0, 1.0, 2.0, 3.0],
            "Time_abs": [100.0, 101.0, 102.0, 103.0],
            "Anomaly State": [1, 1, 1, 1],
        }
    )
    result = audit.switch_on_points(df).set_index("run").loc["inj"]
    assert result["row_index"] is None
    assert result["healthy_rows"] == 0
    assert result["faulty_rows"] == 4


def test_switch_on_points_finds_first_anomaly_row():
    df = pd.DataFrame(
        {
            "run": ["r1"] * 5,
            "t": [0.0, 60.0, 120.0, 180.0, 240.0],
            "Time_abs": [0.0, 60.0, 120.0, 180.0, 240.0],
            "Anomaly State": [0, 0, 0, 1, 1],
        }
    )
    result = audit.switch_on_points(df).set_index("run").loc["r1"]
    assert result["row_index"] == 3
    assert result["t"] == 180.0
    assert result["healthy_rows"] == 3
    assert result["faulty_rows"] == 2


def test_load_bin_agreement_is_one_for_run_fully_inside_bin():
    df = pd.DataFrame(
        {
            "run": ["r1"] * 3,
            "load_bin": [40, 40, 40],
            "nominal_load": ["40%", "40%", "40%"],
        }
    )
    result = audit.load_bin_agreement(df).set_index("run").loc["r1"]
    assert bool(result["fixed_load"]) is True
    assert result["agreement_share"] == 1.0


def test_load_bin_agreement_reports_bin_counts_for_stepped_run():
    df = pd.DataFrame(
        {
            "run": ["r1"] * 3,
            "load_bin": [40, 60, 60],
            "nominal_load": ["load program (~40-85%)"] * 3,
        }
    )
    result = audit.load_bin_agreement(df).set_index("run").loc["r1"]
    assert bool(result["fixed_load"]) is False
    assert result["bin_counts"] == {40: 1, 60: 2}


def test_write_clean_table_round_trips_dtypes(tmp_path):
    df = pd.DataFrame(
        {"run": ["r1", "r1"], "Anomaly State": pd.array([0, 1], dtype="int64"), "t": [0.0, 1.0]}
    )
    path = audit.write_clean_table(df, path=tmp_path / "clean.parquet")
    assert path.exists()
    loaded = pd.read_parquet(path)
    pd.testing.assert_frame_equal(loaded, df)
