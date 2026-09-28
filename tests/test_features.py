"""Raw-sensor input columns exclude leakage columns and non-numeric columns."""

import time

import numpy as np
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


def _physics_input_row() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Charge Air Press.": [2.0],
            "Charge Air IC Air Temp. In": [80.0],
            "Charge Air IC Air Temp. Out": [50.0],
            "Charge Air IC Cooling Water Temp. In": [30.0],
            "No.1 Exh.Gas Temp.": [400.0],
            "No.2 Exh.Gas Temp.": [420.0],
            "No.3 Exh.Gas Temp.": [410.0],
            "Exh.Gas Temp. Turbine In": [500.0],
            "Exh.Gas Temp. Turbine Out": [350.0],
            "Max. In-Cylinder Press. No.1": [140.0],
            "Max. In-Cylinder Press. No.2": [150.0],
            "Max. In-Cylinder Press. No.3": [145.0],
            "Indicated Work No.1": [10.0],
            "Indicated Work No.2": [12.0],
            "Indicated Work No.3": [11.0],
            "Cooling Water Temp. Engine Out I": [60.0],
            "Cooling Water Temp. Engine Out II": [62.0],
            "Cooling Water Temp. Engine Out III": [61.0],
            "Cooling Water Temp. Engine In": [30.0],
            "Fuel Flow": [100.0],
            "Shaft Power": [500.0],
            "Exh. Gas Mass Flow": [2000.0],
            "Loss with cooling water": [10.0],
            "Loss with LO": [5.0],
            "Loss in Charge Air IC": [8.0],
            "Loss with TCH LO": [2.0],
            "Total Heat Loss in Heat Exchangers": [25.0],
        }
    )


def test_add_physics_features_hand_computed():
    df = _physics_input_row()

    result = features.add_physics_features(df)

    assert result["phys_pressure_ratio"].iloc[0] == pytest.approx((2.0 + 1.0332) / 1.0332)
    assert result["phys_cooler_effectiveness"].iloc[0] == pytest.approx((80 - 50) / (80 - 30))
    assert result["phys_exhaust_temp_spread"].iloc[0] == pytest.approx(420 - 400)
    mean_exh = (400 + 420 + 410) / 3
    assert result["phys_exhaust_temp_dev_1"].iloc[0] == pytest.approx(400 - mean_exh)
    assert result["phys_exhaust_temp_dev_2"].iloc[0] == pytest.approx(420 - mean_exh)
    assert result["phys_exhaust_temp_dev_3"].iloc[0] == pytest.approx(410 - mean_exh)
    assert result["phys_turbine_temp_drop"].iloc[0] == pytest.approx(500 - 350)
    assert result["phys_pmax_spread"].iloc[0] == pytest.approx(150 - 140)
    assert result["phys_indicated_work_spread"].iloc[0] == pytest.approx(12 - 10)
    assert result["phys_fuel_flow_per_kw"].iloc[0] == pytest.approx(100 / 500)
    assert result["phys_exhaust_mass_flow_per_fuel"].iloc[0] == pytest.approx(2000 / 100)
    assert result["phys_cooling_water_share"].iloc[0] == pytest.approx(10 / 25)
    assert result["phys_lo_share"].iloc[0] == pytest.approx(5 / 25)
    assert result["phys_charge_air_ic_share"].iloc[0] == pytest.approx(8 / 25)
    assert result["phys_tch_lo_share"].iloc[0] == pytest.approx(2 / 25)
    mean_cw_out = (60 + 62 + 61) / 3
    assert result["phys_cooling_water_rise"].iloc[0] == pytest.approx(mean_cw_out - 30)
    # original columns preserved, result is a copy
    assert "Fuel Flow" in result.columns
    df["Fuel Flow"] = 999.0
    assert result["Fuel Flow"].iloc[0] == 100.0


def test_add_physics_features_zero_denominator_is_nan_not_inf():
    df = _physics_input_row()
    df["Shaft Power"] = 0.0
    df["Fuel Flow"] = 0.0
    df["Total Heat Loss in Heat Exchangers"] = 0.0
    df["Charge Air IC Air Temp. In"] = 30.0
    df["Charge Air IC Cooling Water Temp. In"] = 30.0

    result = features.add_physics_features(df)

    for column in [
        "phys_fuel_flow_per_kw",
        "phys_exhaust_mass_flow_per_fuel",
        "phys_cooling_water_share",
        "phys_lo_share",
        "phys_charge_air_ic_share",
        "phys_tch_lo_share",
        "phys_cooler_effectiveness",
    ]:
        value = result[column].iloc[0]
        assert pd.isna(value)
        assert not np.isinf(value) if not pd.isna(value) else True


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


def _two_run_frame() -> pd.DataFrame:
    t = np.arange(0, 20, 1.0)
    run1 = pd.DataFrame({"run": "run1", "t": t, "value": np.linspace(10, 29, 20)})
    run2 = pd.DataFrame({"run": "run2", "t": t, "value": np.linspace(100, 300, 20)})
    return pd.concat([run1, run2], ignore_index=True)


def test_rolling_features_never_cross_run_boundary_or_look_forward():
    df = _two_run_frame()
    before = features.add_rolling_features(
        df, ["value"], windows_s=(5,), stats=("mean", "std", "slope")
    )

    mutated = df.copy()
    mutated.loc[mutated["run"] == "run2", "value"] += 1000.0
    mutated.loc[(mutated["run"] == "run1") & (mutated["t"] > 10), "value"] += 1000.0
    after = features.add_rolling_features(
        mutated, ["value"], windows_s=(5,), stats=("mean", "std", "slope")
    )

    run1_early = (df["run"] == "run1") & (df["t"] <= 10)
    for column in ["value_roll_5s_mean", "value_roll_5s_std", "value_roll_5s_slope"]:
        pd.testing.assert_series_equal(
            before.loc[run1_early, column], after.loc[run1_early, column]
        )


def test_rolling_slope_exact_and_warmup_flag():
    t = np.arange(0, 20, 1.0)
    gradient = 3.0
    df = pd.DataFrame({"run": "run1", "t": t, "value": 5.0 + gradient * t})

    result = features.add_rolling_features(df, ["value"], windows_s=(5,), stats=("slope",))

    # The very first row's window has a single point, so its slope is undefined.
    np.testing.assert_allclose(result["value_roll_5s_slope"].iloc[1:], gradient * 60.0, rtol=1e-9)
    assert (result.loc[df["t"] < 5, "roll_warmup_5"] == 1).all()
    assert (result.loc[df["t"] >= 5, "roll_warmup_5"] == 0).all()


def _synthetic_engine(n=60, fault_offset=0.0, fault_frac=0.0, seed=0):
    rng = np.random.default_rng(seed)
    speed = rng.uniform(1000, 2000, n)
    load = rng.uniform(50, 500, n)
    fuel = rng.uniform(5, 20, n)
    target = 2.0 * speed + 0.5 * load - 1.5 * fuel + 100.0
    label = np.full(n, "Normal", dtype=object)
    n_fault = int(n * fault_frac)
    if n_fault:
        label[:n_fault] = "AC"
        target[:n_fault] += fault_offset
    df = pd.DataFrame(
        {
            "Engine Speed": speed,
            "Water Brake Weight": load,
            "Fuel Flow": fuel,
            "Exhaust Temp 1": target,
        }
    )
    return df, pd.Series(label)


def test_healthy_engine_residuals_fit_ignores_fault_rows():
    df, y = _synthetic_engine(n=60, fault_offset=500.0, fault_frac=0.3, seed=1)
    healthy_only = df.loc[y == "Normal"]

    transformer = features.HealthyEngineResiduals(
        inputs=("Engine Speed", "Water Brake Weight", "Fuel Flow"),
        targets=["Exhaust Temp 1"],
    )
    transformer.fit(df, y)
    fitted_on_all = transformer.models_["Exhaust Temp 1"].predict(
        healthy_only[list(transformer.inputs)]
    )

    reference = features.HealthyEngineResiduals(
        inputs=("Engine Speed", "Water Brake Weight", "Fuel Flow"),
        targets=["Exhaust Temp 1"],
    )
    reference.fit(healthy_only, pd.Series(["Normal"] * len(healthy_only)))
    fitted_on_healthy_only = reference.models_["Exhaust Temp 1"].predict(
        healthy_only[list(reference.inputs)]
    )

    np.testing.assert_allclose(fitted_on_all, fitted_on_healthy_only, rtol=1e-8)


def test_healthy_engine_residuals_synthetic_linear_engine():
    df, y = _synthetic_engine(n=80, fault_offset=300.0, fault_frac=0.25, seed=2)

    transformer = features.HealthyEngineResiduals(
        inputs=("Engine Speed", "Water Brake Weight", "Fuel Flow"),
        targets=["Exhaust Temp 1"],
        degree=1,
    )
    transformer.fit(df, y)
    out = transformer.transform(df)

    healthy_resid = out.loc[y == "Normal", "resid_Exhaust Temp 1"]
    fault_resid = out.loc[y != "Normal", "resid_Exhaust Temp 1"]

    np.testing.assert_allclose(healthy_resid.to_numpy(), 0.0, atol=25.0)
    assert fault_resid.mean() > 250.0


def test_healthy_engine_residuals_in_pipeline_with_lolo_predict():
    from sklearn.dummy import DummyClassifier
    from sklearn.pipeline import make_pipeline

    from keyframe import evaluate

    df, y = _synthetic_engine(n=90, fault_offset=200.0, fault_frac=0.2, seed=3)
    df["label"] = y
    df["run"] = [f"run{i % 3}" for i in range(len(df))]
    df["load_bin"] = np.tile([0, 1, 2], len(df) // 3)

    def model_factory():
        return make_pipeline(
            features.HealthyEngineResiduals(
                inputs=("Engine Speed", "Water Brake Weight", "Fuel Flow"),
                targets=["Exhaust Temp 1"],
            ),
            DummyClassifier(strategy="most_frequent"),
        )

    result = evaluate.lolo_predict(
        model_factory,
        df,
        ["Engine Speed", "Water Brake Weight", "Fuel Flow", "Exhaust Temp 1"],
    )
    assert len(result) == len(df)


@pytest.mark.data
def test_rolling_features_full_table_under_two_minutes():
    path = paths.PROCESSED / "clean.parquet"
    if not path.exists():
        pytest.skip("data/processed/clean.parquet not built")
    df = pd.read_parquet(path)
    df = features.add_physics_features(df)
    channels = features.raw_sensor_columns(df)

    start = time.perf_counter()
    features.add_rolling_features(
        df, channels, windows_s=(60, 300, 900), stats=("mean", "std", "slope")
    )
    elapsed = time.perf_counter() - start

    assert elapsed < 120
