"""Every model feature traces to a source channel and to exactly one sensor group (R1-R2)."""

import pandas as pd
import pytest

from keyframe import explain, features, paths


def test_raw_channel_maps_to_itself():
    assert explain.source_channel("Fuel Flow") == ("Fuel Flow",)
    assert explain.group_of("Fuel Flow") == "fuel system"


def test_rolling_feature_maps_to_its_base_channel():
    assert explain.source_channel("Fuel Flow_roll_60s_mean") == ("Fuel Flow",)
    assert explain.group_of("Fuel Flow_roll_60s_mean") == "fuel system"


def test_residual_feature_maps_to_its_base_channel():
    assert explain.source_channel("resid_Fuel Temp.") == ("Fuel Temp.",)
    assert explain.group_of("resid_Fuel Temp.") == "fuel system"


def test_residual_rolling_feature_maps_to_its_base_channel():
    assert explain.source_channel("resid_Fuel Temp._roll_60s_std") == ("Fuel Temp.",)
    assert explain.group_of("resid_Fuel Temp._roll_60s_std") == "fuel system"


def test_warmup_feature_is_not_a_sensor():
    assert explain.source_channel("roll_warmup_60s") == (explain.WARMUP_LABEL,)
    assert explain.group_of("roll_warmup_60s") == explain.WARMUP_LABEL


@pytest.mark.parametrize(
    "feature,channels,group",
    [
        ("phys_pressure_ratio", ("Charge Air Press.",), "air path"),
        (
            "phys_turbine_temp_drop",
            ("Exh.Gas Temp. Turbine In", "Exh.Gas Temp. Turbine Out"),
            "air path",
        ),
        (
            "phys_pmax_spread",
            (
                "Max. In-Cylinder Press. No.1",
                "Max. In-Cylinder Press. No.2",
                "Max. In-Cylinder Press. No.3",
            ),
            "combustion and power",
        ),
        ("phys_fuel_flow_per_kw", ("Fuel Flow", "Shaft Power"), "fuel system"),
        ("phys_cooling_water_share", None, "cooling"),
        ("phys_lo_share", None, "lube oil"),
    ],
)
def test_physics_feature_maps_to_its_formula_channels(feature, channels, group):
    if channels is not None:
        assert explain.source_channel(feature) == channels
    assert explain.group_of(feature) == group


def test_physics_rolling_feature_resolves_through_its_base_physics_feature():
    assert explain.source_channel("phys_pressure_ratio_roll_60s_mean") == ("Charge Air Press.",)
    assert explain.group_of("phys_pressure_ratio_roll_60s_mean") == "air path"


def test_every_physics_feature_covered():
    df = pd.DataFrame(
        {
            "Charge Air Press.": [1.0],
            "Charge Air IC Air Temp. In": [1.0],
            "Charge Air IC Air Temp. Out": [1.0],
            "Charge Air IC Cooling Water Temp. In": [1.0],
            "No.1 Exh.Gas Temp.": [1.0],
            "No.2 Exh.Gas Temp.": [1.0],
            "No.3 Exh.Gas Temp.": [1.0],
            "Exh.Gas Temp. Turbine In": [1.0],
            "Exh.Gas Temp. Turbine Out": [1.0],
            "Max. In-Cylinder Press. No.1": [1.0],
            "Max. In-Cylinder Press. No.2": [1.0],
            "Max. In-Cylinder Press. No.3": [1.0],
            "Indicated Work No.1": [1.0],
            "Indicated Work No.2": [1.0],
            "Indicated Work No.3": [1.0],
            "Fuel Flow": [1.0],
            "Shaft Power": [1.0],
            "Exh. Gas Mass Flow": [1.0],
            "Loss with cooling water": [1.0],
            "Loss with LO": [1.0],
            "Loss in Charge Air IC": [1.0],
            "Loss with TCH LO": [1.0],
            "Total Heat Loss in Heat Exchangers": [1.0],
            "Cooling Water Temp. Engine Out I": [1.0],
            "Cooling Water Temp. Engine Out II": [1.0],
            "Cooling Water Temp. Engine Out III": [1.0],
            "Cooling Water Temp. Engine In": [1.0],
        }
    )
    physics = features.add_physics_features(df)
    physics_columns = [c for c in physics.columns if c.startswith("phys_")]

    for column in physics_columns:
        assert explain.source_channel(column)
        assert explain.group_of(column) in {
            "air path",
            "combustion and power",
            "fuel system",
            "cooling",
            "lube oil",
        }


@pytest.mark.data
def test_every_sensor_channel_in_the_feature_table_has_exactly_one_group():
    clean_path = paths.PROCESSED / "clean.parquet"
    if not clean_path.exists():
        pytest.skip("clean.parquet not built")
    clean = pd.read_parquet(clean_path)
    table = features.build_feature_table(clean)

    for channel in features.sensor_channels(table):
        assert channel in explain.SENSOR_GROUPS, channel
