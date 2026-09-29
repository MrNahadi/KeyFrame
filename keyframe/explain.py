"""Traces a model feature to the engine channel(s) it comes from and to a sensor group (R1-R2),
and views over SHAP arrays: rankings, grouped SHAP and single-moment waterfalls (R4)."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

WARMUP_LABEL = "window warm-up"

SENSOR_GROUPS: dict[str, str] = {
    # air path: charge air, turbocharger, exhaust gas mass flow, pressure ratio
    "Charge Air Press.": "air path",
    "Charge Air IC Air Temp. In": "air path",
    "Charge Air IC Air Temp. Out": "air path",
    "Charge Air IC Cooling Water Temp. In": "air path",
    "Charge Air IC Cooling Water Temp. Out": "air path",
    "Charge Air IC Cooling water flow": "air path",
    "Loss in Charge Air IC": "air path",
    "Exh.Gas Temp. Turbine In": "air path",
    "Exh.Gas Temp. Turbine Out": "air path",
    "Exh.Gas Vol. Flow (From Engine Speed)": "air path",
    "Exh. Gas Mass Flow": "air path",
    "Exh.Gas Total Power": "air path",
    "Exh.Gas Power": "air path",
    "TCH Power": "air path",
    # combustion and power: in-cylinder pressures, exhaust temps per cylinder, work,
    # torque, shaft power, efficiencies, engine speed, brake load
    "Engine Speed": "combustion and power",
    "Water Brake Weight": "combustion and power",
    "Max. In-Cylinder Press. No.1": "combustion and power",
    "Min. In-Cylinder Press. No.1": "combustion and power",
    "Max. In-Cylinder Press. No.2": "combustion and power",
    "Min. In-Cylinder Press. No.2": "combustion and power",
    "Max. In-Cylinder Press. No.3": "combustion and power",
    "Min. In-Cylinder Press. No.3": "combustion and power",
    "No.1 Exh.Gas Temp.": "combustion and power",
    "No.2 Exh.Gas Temp.": "combustion and power",
    "No.3 Exh.Gas Temp.": "combustion and power",
    "Indicated Work No.1": "combustion and power",
    "Indicated Work No.2": "combustion and power",
    "Indicated Work No.3": "combustion and power",
    "Total Indicated work": "combustion and power",
    "Effective Work No.1": "combustion and power",
    "Effective Work No.2": "combustion and power",
    "Effective Work No.3": "combustion and power",
    "Total Effective Work": "combustion and power",
    "Shaft Torque": "combustion and power",
    "Shaft Power": "combustion and power",
    "Mechanical Loss": "combustion and power",
    "Mechanical Efficiency": "combustion and power",
    "Indicated Efficiency": "combustion and power",
    "Effective Efficiency": "combustion and power",
    "Total Input Energy": "combustion and power",
    "Other Loss": "combustion and power",
    "Total Heat Loss in Heat Exchangers": "combustion and power",
    # fuel system: fuel flow and temperatures, fuel transfer pump, injector cooling oil
    "Fuel Flow": "fuel system",
    "Fuel Temp.": "fuel system",
    "Fuel transfer pump Press.": "fuel system",
    "Fuel Injector Cooling Oil Press.": "fuel system",
    "Fuel Oil Temp. Flow meter In": "fuel system",
    # cooling: cooling water temperatures, flows, pressures, heat rejection to water
    "Cooling Water Temp. Engine In": "cooling",
    "Cooling Water Temp. Engine Out I": "cooling",
    "Cooling Water Temp. Engine Out II": "cooling",
    "Cooling Water Temp. Engine Out III": "cooling",
    "Fresh Cooling Water Press.": "cooling",
    "Sea Cooling Water Press.": "cooling",
    "Engine Cooling water flow": "cooling",
    "Loss with cooling water": "cooling",
    # lube oil: LO temperatures, pressures, heat rejection to LO
    "LO Temp. Engine In": "lube oil",
    "LO Temp. Engine Out": "lube oil",
    "LO Cooling Water Temp. In": "lube oil",
    "LO Cooling Water Temp. Out": "lube oil",
    "LO Temp. TCH In": "lube oil",
    "LO Temp. TCH Out": "lube oil",
    "LO Circulating Pump Press.": "lube oil",
    "TCH LO pump Press.": "lube oil",
    "LO Cooling water flow": "lube oil",
    "TCH LO Cooling water flow": "lube oil",
    "Loss with LO": "lube oil",
    "Loss with TCH LO": "lube oil",
}
"""Every measured channel that can reach the feature table, to its one sensor group (R2).
`Compressor Filter Loss`, `Turbine Back Pressure` and `Engine room Temp.` are omitted: they
are in `keyframe.features.EXCLUDED_COLUMNS` and never become a feature."""

PHYSICS_SOURCE_CHANNELS: dict[str, tuple[str, ...]] = {
    "phys_pressure_ratio": ("Charge Air Press.",),
    "phys_cooler_effectiveness": (
        "Charge Air IC Air Temp. In",
        "Charge Air IC Air Temp. Out",
        "Charge Air IC Cooling Water Temp. In",
    ),
    "phys_exhaust_temp_spread": (
        "No.1 Exh.Gas Temp.",
        "No.2 Exh.Gas Temp.",
        "No.3 Exh.Gas Temp.",
    ),
    "phys_exhaust_temp_dev_1": (
        "No.1 Exh.Gas Temp.",
        "No.2 Exh.Gas Temp.",
        "No.3 Exh.Gas Temp.",
    ),
    "phys_exhaust_temp_dev_2": (
        "No.1 Exh.Gas Temp.",
        "No.2 Exh.Gas Temp.",
        "No.3 Exh.Gas Temp.",
    ),
    "phys_exhaust_temp_dev_3": (
        "No.1 Exh.Gas Temp.",
        "No.2 Exh.Gas Temp.",
        "No.3 Exh.Gas Temp.",
    ),
    "phys_turbine_temp_drop": ("Exh.Gas Temp. Turbine In", "Exh.Gas Temp. Turbine Out"),
    "phys_pmax_spread": (
        "Max. In-Cylinder Press. No.1",
        "Max. In-Cylinder Press. No.2",
        "Max. In-Cylinder Press. No.3",
    ),
    "phys_indicated_work_spread": (
        "Indicated Work No.1",
        "Indicated Work No.2",
        "Indicated Work No.3",
    ),
    "phys_fuel_flow_per_kw": ("Fuel Flow", "Shaft Power"),
    "phys_exhaust_mass_flow_per_fuel": ("Exh. Gas Mass Flow", "Fuel Flow"),
    "phys_cooling_water_share": ("Loss with cooling water", "Total Heat Loss in Heat Exchangers"),
    "phys_lo_share": ("Loss with LO", "Total Heat Loss in Heat Exchangers"),
    "phys_charge_air_ic_share": ("Loss in Charge Air IC", "Total Heat Loss in Heat Exchangers"),
    "phys_tch_lo_share": ("Loss with TCH LO", "Total Heat Loss in Heat Exchangers"),
    "phys_cooling_water_rise": (
        "Cooling Water Temp. Engine Out I",
        "Cooling Water Temp. Engine Out II",
        "Cooling Water Temp. Engine Out III",
        "Cooling Water Temp. Engine In",
    ),
}
"""Every `phys_*` feature, to the channel(s) its formula reads (R1)."""

PHYSICS_GROUPS: dict[str, str] = {
    "phys_pressure_ratio": "air path",
    "phys_cooler_effectiveness": "air path",
    "phys_exhaust_temp_spread": "combustion and power",
    "phys_exhaust_temp_dev_1": "combustion and power",
    "phys_exhaust_temp_dev_2": "combustion and power",
    "phys_exhaust_temp_dev_3": "combustion and power",
    "phys_turbine_temp_drop": "air path",
    "phys_pmax_spread": "combustion and power",
    "phys_indicated_work_spread": "combustion and power",
    "phys_fuel_flow_per_kw": "fuel system",
    "phys_exhaust_mass_flow_per_fuel": "air path",
    "phys_cooling_water_share": "cooling",
    "phys_lo_share": "lube oil",
    "phys_charge_air_ic_share": "air path",
    "phys_tch_lo_share": "lube oil",
    "phys_cooling_water_rise": "cooling",
}
"""Every `phys_*` feature, to the group of its formula's main subject (R2)."""


def source_channel(feature: str) -> tuple[str, ...]:
    """The measured channel(s) `feature` comes from: itself for a raw channel, the base
    channel for a `<channel>_roll_*` or `resid_<channel>` feature, the formula's inputs
    for a `phys_*` feature, and `("window warm-up",)` for `roll_warmup_*` (not a sensor).
    """
    if feature.startswith("roll_warmup_"):
        return (WARMUP_LABEL,)
    if "_roll_" in feature:
        return source_channel(feature.split("_roll_")[0])
    if feature.startswith("resid_"):
        return (feature.removeprefix("resid_"),)
    if feature.startswith("phys_"):
        return PHYSICS_SOURCE_CHANNELS[feature]
    return (feature,)


def group_of(feature: str) -> str:
    """The one sensor group `feature` belongs to (R2), resolving rolling and residual
    features to their base channel and physics features to their formula's main subject.
    """
    if feature.startswith("roll_warmup_"):
        return WARMUP_LABEL
    if "_roll_" in feature:
        return group_of(feature.split("_roll_")[0])
    if feature.startswith("resid_"):
        return group_of(feature.removeprefix("resid_"))
    if feature.startswith("phys_"):
        return PHYSICS_GROUPS[feature]
    return SENSOR_GROUPS[feature]


def feature_ranking(shap_values: np.ndarray, columns: Sequence[str]) -> pd.Series:
    """Mean |SHAP| per feature over the rows in `shap_values` (n_rows, n_features),
    descending. Callers pick the class slice and the rows (e.g. a class's own rows) first."""
    return pd.Series(np.abs(shap_values).mean(axis=0), index=list(columns)).sort_values(
        ascending=False
    )


def channel_ranking(shap_values: np.ndarray, columns: Sequence[str]) -> pd.Series:
    """Mean |SHAP| per source channel (R4): each feature's mean |SHAP| is added to every
    channel `source_channel` names for it, so a multi-channel `phys_*` feature counts fully
    toward each of its inputs."""
    per_feature = feature_ranking(shap_values, columns)
    channels = [channel for feature in per_feature.index for channel in source_channel(feature)]
    weights = [
        per_feature[feature] for feature in per_feature.index for _ in source_channel(feature)
    ]
    return pd.Series(weights, index=channels).groupby(level=0).sum().sort_values(ascending=False)


def grouped_shap(shap_values: np.ndarray, columns: Sequence[str]) -> pd.Series:
    """Signed SHAP summed within each sensor group, then averaged over rows (R4). Since
    `group_of` assigns each feature to exactly one group, the groups partition the features
    and this sums to the same total as the per-feature signed mean."""
    values = np.atleast_2d(shap_values)
    groups = [group_of(feature) for feature in columns]
    per_row = pd.DataFrame(values, columns=list(columns)).T.groupby(groups).sum().T
    return per_row.mean(axis=0).sort_values(key=lambda s: s.abs(), ascending=False)


DAY_DEPENDENT_CHANNELS: frozenset[str] = frozenset(
    {
        "LO Cooling Water Temp. In",
        "Fuel Temp.",
        "Fuel Oil Temp. Flow meter In",
        "Sea Cooling Water Press.",
    }
)
"""Slow, day-dependent channels a diagnosis must not lean on (checklist "Channels that
must not drive a diagnosis"; symbols T12, T18, T21, Pl_water2 in `reports/targets.md`)."""

CHECKLIST: dict[str, frozenset[str]] = {
    "AC": frozenset(
        {
            "Charge Air IC Air Temp. Out",
            "Charge Air IC Air Temp. In",
            "Charge Air IC Cooling Water Temp. In",
            "Loss in Charge Air IC",
            "Charge Air IC Cooling water flow",
            "Charge Air IC Cooling Water Temp. Out",
            "Exh.Gas Temp. Turbine In",
            "No.1 Exh.Gas Temp.",
            "No.2 Exh.Gas Temp.",
            "No.3 Exh.Gas Temp.",
        }
    ),
    "AF": frozenset(
        {
            "Charge Air Press.",
            "Exh.Gas Temp. Turbine In",
            "No.1 Exh.Gas Temp.",
            "No.2 Exh.Gas Temp.",
            "No.3 Exh.Gas Temp.",
            "Max. In-Cylinder Press. No.1",
            "Max. In-Cylinder Press. No.2",
            "Max. In-Cylinder Press. No.3",
            "TCH Power",
            "Exh. Gas Mass Flow",
        }
    ),
    "INJ": frozenset(
        {
            "No.1 Exh.Gas Temp.",
            "No.2 Exh.Gas Temp.",
            "No.3 Exh.Gas Temp.",
            "Max. In-Cylinder Press. No.1",
            "Max. In-Cylinder Press. No.2",
            "Max. In-Cylinder Press. No.3",
            "Indicated Work No.1",
            "Indicated Work No.2",
            "Indicated Work No.3",
            "Indicated Efficiency",
            "Charge Air Press.",
            "Effective Efficiency",
            "Fuel Flow",
            "Shaft Power",
        }
    ),
    "CW": frozenset(
        {
            "Fresh Cooling Water Press.",
            "Engine Cooling water flow",
            "Cooling Water Temp. Engine In",
            "Cooling Water Temp. Engine Out I",
            "Cooling Water Temp. Engine Out II",
            "Cooling Water Temp. Engine Out III",
            "Loss with cooling water",
        }
    ),
    "TD": frozenset(
        {
            "Exh.Gas Temp. Turbine Out",
            "Exh.Gas Temp. Turbine In",
            "Charge Air Press.",
            "TCH Power",
            "No.1 Exh.Gas Temp.",
            "No.2 Exh.Gas Temp.",
            "No.3 Exh.Gas Temp.",
            "Max. In-Cylinder Press. No.1",
        }
    ),
}
"""Per fault, the channels a top-5 SHAP feature must trace to for a match (R5): the
checklist's pre-registered "Expected top 5" plus any channel marked "Agree" in the
Observed section of `reports/engineering_checklist.md`, transcribed and checked against
that file by `tests/test_explain.py::test_checklist_matches_the_engineering_checklist_file`."""


def physics_check(
    shap_rank_by_class: dict[str, pd.Series], checklist: dict[str, frozenset[str]]
) -> pd.DataFrame:
    """The pre-registered physics check (R5): for each fault, the top 5 features by mean
    |SHAP| (`shap_rank_by_class[fault]`, already restricted to that class's held-out rows
    and sorted descending), each mapped to its source channel(s) via `source_channel`. A
    feature matches if any of its channels is in `checklist[fault]`. A fault passes when at
    least 3 of 5 features match and none of the top 5 traces to a day-dependent channel
    (`DAY_DEPENDENT_CHANNELS`).

    Returns one row per fault per top-5 feature, columns: fault, feature, channels, matched,
    day_dependent, match_count, day_dependent_hit, passed.
    """
    rows = []
    for fault, ranking in shap_rank_by_class.items():
        allowed = checklist[fault]
        top5 = ranking.index[:5]
        channels = [source_channel(feature) for feature in top5]
        matched = [any(ch in allowed for ch in chans) for chans in channels]
        day_dependent = [any(ch in DAY_DEPENDENT_CHANNELS for ch in chans) for chans in channels]
        match_count = sum(matched)
        day_dependent_hit = any(day_dependent)
        passed = match_count >= 3 and not day_dependent_hit
        for feature, chans, is_match, is_day in zip(
            top5, channels, matched, day_dependent, strict=True
        ):
            rows.append(
                {
                    "fault": fault,
                    "feature": feature,
                    "channels": ", ".join(chans),
                    "matched": is_match,
                    "day_dependent": is_day,
                    "match_count": match_count,
                    "day_dependent_hit": day_dependent_hit,
                    "passed": passed,
                }
            )
    return pd.DataFrame(rows)


def waterfall(
    shap_row: np.ndarray, columns: Sequence[str], top_n: int = 8
) -> tuple[pd.Series, pd.Series]:
    """A grouped waterfall for one moment (R4): signed SHAP summed per sensor group for that
    row, and the `top_n` individual features by |SHAP| within that same row."""
    grouped = grouped_shap(shap_row, columns)
    row = pd.Series(np.asarray(shap_row), index=list(columns))
    top = row.reindex(row.abs().sort_values(ascending=False).index[:top_n])
    return grouped, top
