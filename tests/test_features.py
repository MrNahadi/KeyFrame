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


def _synthetic_feature_table(n=40, seed=4):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(
        {
            "Engine Speed": rng.uniform(1000, 2000, n),
            "Water Brake Weight": rng.uniform(50, 500, n),
            "Fuel Flow": rng.uniform(5, 20, n),
            "LO Cooling Water Temp. In": rng.uniform(10, 20, n),
            "Charge Air IC Cooling Water Temp. In": rng.uniform(10, 20, n),
            "Fuel Temp.": rng.uniform(10, 20, n),
            "Fuel Oil Temp. Flow meter In": rng.uniform(10, 20, n),
            "Sea Cooling Water Press.": rng.uniform(1, 3, n),
            "Engine room Temp.": rng.uniform(15, 35, n),
            "phys_pressure_ratio": rng.uniform(1, 2, n),
            "Exhaust Temp 1_roll_60s_mean": rng.uniform(300, 400, n),
            "roll_warmup_60": np.zeros(n),
            "Time": np.arange(n),
            "run": [f"run{i % 4}" for i in range(n)],
            "label": np.where(rng.random(n) < 0.2, "AC", "Normal"),
        }
    )
    return df


def test_every_feature_set_excludes_excluded_columns():
    df = _synthetic_feature_table()
    for name, spec in features.FEATURE_SETS.items():
        cols = spec.columns(df)
        assert not (set(cols) & features.EXCLUDED_COLUMNS), name


def test_residual_feature_sets_replace_day_markers_with_residual_columns():
    from sklearn.dummy import DummyClassifier

    df = _synthetic_feature_table()
    y = df["label"]
    for name in ["residuals", "residuals+physics", "residuals+physics+rolling"]:
        spec = features.FEATURE_SETS[name]
        assert spec.residuals
        cols = spec.columns(df)
        assert set(features.DAY_MARKER_RESIDUAL_CHANNELS) <= set(cols), name

        pipeline = features.build_pipeline(name, DummyClassifier(strategy="most_frequent"))
        transformed = pipeline[:-1].fit_transform(df[cols], y)
        assert not (set(transformed.columns) & set(features.DAY_MARKER_RESIDUAL_CHANNELS)), name
        assert {f"resid_{c}" for c in features.DAY_MARKER_RESIDUAL_CHANNELS} <= set(
            transformed.columns
        )

    for name in ["raw", "raw+physics", "raw+physics+rolling"]:
        spec = features.FEATURE_SETS[name]
        cols = spec.columns(df)
        assert set(features.DAY_MARKER_RESIDUAL_CHANNELS) <= set(cols), name
        assert not spec.residuals


def test_build_pipeline_unfitted_and_usable_with_lolo_predict():
    from sklearn.dummy import DummyClassifier

    from keyframe import evaluate

    df = _synthetic_feature_table()
    df["load_bin"] = np.tile([0, 1, 2, 3], len(df) // 4)
    feature_set = "residuals"
    spec = features.FEATURE_SETS[feature_set]
    training_columns = spec.columns(df)

    def model_factory():
        return features.build_pipeline(feature_set, DummyClassifier(strategy="most_frequent"))

    pipeline = model_factory()
    assert isinstance(pipeline, features.Pipeline)
    from sklearn.exceptions import NotFittedError

    with pytest.raises(NotFittedError):
        pipeline.predict(df[training_columns])

    result = evaluate.lolo_predict(model_factory, df, training_columns)
    assert len(result) == len(df)


def _synthetic_table_with_derived_columns() -> pd.DataFrame:
    """The synthetic table (already carrying a stand-in physics and rolling column) plus a
    real trailing rolling mean of one sensor channel."""
    table = _synthetic_feature_table()
    table["t"] = table.groupby("run").cumcount() * 2.0
    return features.add_rolling_features(table, ["Fuel Temp."], windows_s=(120,))


def test_feature_sets_differ_once_physics_and_rolling_columns_exist():
    """Regression: every set used to collapse to raw sensors when the table lacked
    physics and rolling columns, so the ablation compared identical inputs."""
    table = _synthetic_table_with_derived_columns()
    raw = features.FEATURE_SETS["raw"].columns(table)
    with_physics = features.FEATURE_SETS["raw+physics"].columns(table)
    with_rolling = features.FEATURE_SETS["raw+physics+rolling"].columns(table)
    assert set(raw) < set(with_physics) < set(with_rolling)
    assert all(c.startswith("phys_") for c in set(with_physics) - set(raw))
    assert not any("_roll_" in c for c in with_physics)
    assert not any(c.startswith("phys_") or "_roll_" in c for c in raw)


def test_residual_view_keeps_load_inputs_and_drops_every_raw_reading():
    from sklearn.dummy import DummyClassifier

    table = _synthetic_table_with_derived_columns()
    cols = features.FEATURE_SETS["residuals+physics+rolling"].columns(table)
    pipeline = features.build_pipeline(
        "residuals+physics+rolling", DummyClassifier(strategy="most_frequent")
    )
    seen = set(pipeline[:-1].fit_transform(table[cols], table["label"]).columns)

    sensors = features.sensor_channels(table)
    targets = [c for c in sensors if c not in features.RESIDUAL_INPUTS]
    assert set(features.RESIDUAL_INPUTS) & set(sensors) <= seen
    assert not (set(targets) & seen)
    assert {f"resid_{c}" for c in targets} <= seen
    assert not any(c.endswith("_mean") and c.split("_roll_")[0] in targets for c in seen)
    assert any(c.startswith("phys_") for c in seen)


def test_prune_correlated_drops_one_of_a_perfect_pair_keeps_uncorrelated():
    rng = np.random.default_rng(0)
    base = rng.normal(size=200)
    df = pd.DataFrame(
        {
            "a": base,
            "a_twin": base * 2 + 1,  # perfectly correlated with a
            "b": rng.normal(size=200),  # uncorrelated
        }
    )

    kept = features.prune_correlated(df, ["a", "a_twin", "b"], threshold=0.98)

    assert kept == ["a", "b"]


def test_inner_permutation_importance_only_uses_inner_fold_rows():
    from sklearn.dummy import DummyClassifier

    train_df = pd.DataFrame(
        {
            "Engine Speed": np.linspace(0, 1, 60),
            "Fuel Flow": np.linspace(1, 2, 60),
            "label": ["Normal"] * 60,
            "load_bin": np.tile([40, 60, 75], 20),
        }
    )
    seen_indices: set = set()

    class SpyClassifier(DummyClassifier):
        def fit(self, X, y, **kwargs):
            seen_indices.update(X.index)
            return super().fit(X, y, **kwargs)

    def factory():
        return SpyClassifier(strategy="most_frequent")

    importance = features.inner_permutation_importance(
        factory, train_df, ["Engine Speed", "Fuel Flow"], n_repeats=1
    )

    assert seen_indices == set(train_df.index)  # inner folds together cover all training rows
    assert set(importance["feature"]) == {"Engine Speed", "Fuel Flow"}
    assert set(importance["fold"]) == {40, 60, 75}


def test_stratified_subsample_keeps_class_shares_and_is_seeded():
    labels = pd.Series(["Normal"] * 800 + ["AC"] * 200)
    first = features._stratified_subsample(labels, 100, np.random.default_rng(0))
    again = features._stratified_subsample(labels, 100, np.random.default_rng(0))
    assert list(first) == list(again)
    assert labels[first].value_counts().to_dict() == {"Normal": 80, "AC": 20}
    assert features._stratified_subsample(labels, None, np.random.default_rng(0)).equals(
        labels.index
    )
