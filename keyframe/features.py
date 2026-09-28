"""Model input columns for the raw-sensor baselines, with leakage exclusions enforced,
plus the physics features derived from a single row of the clean table.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import FunctionTransformer, PolynomialFeatures, StandardScaler

EXCLUDED_COLUMNS: frozenset[str] = frozenset(
    {
        "Compressor Filter Loss",
        "Turbine Back Pressure",
        "Engine room Temp.",
        "Time",
        "Time_abs",
        "Time_rel",
        "Anomaly State",
        "run",
        "fault_type",
        "label",
        "t",
        "load_bin",
        "nominal_load",
    }
)


DAY_MARKER_RESIDUAL_CHANNELS: tuple[str, ...] = (
    "LO Cooling Water Temp. In",
    "Charge Air IC Cooling Water Temp. In",
    "Fuel Temp.",
    "Fuel Oil Temp. Flow meter In",
)
"""Day-marker temperature channels notebook 01 recommended residualising (`Engine room
Temp.` is already excluded; `Sea Cooling Water Press.` stays raw as load-linked)."""


def raw_sensor_columns(df: pd.DataFrame) -> list[str]:
    """Return every numeric column of ``df`` not in ``EXCLUDED_COLUMNS``, in table order."""
    numeric = df.select_dtypes(include="number")
    return [column for column in numeric.columns if column not in EXCLUDED_COLUMNS]


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Elementwise division; zero or negative denominators give NaN, never inf."""
    return numerator / denominator.where(denominator > 0)


def pressure_ratio(df: pd.DataFrame) -> pd.Series:
    """Turbocharger pressure ratio proxy: gauge charge air pressure to absolute,
    against standard atmosphere (1.0332 kgf/cm²). A proxy because compressor
    inlet pressure is not measured.
    """
    return (df["Charge Air Press."] + 1.0332) / 1.0332


def cooler_effectiveness(df: pd.DataFrame) -> pd.Series:
    """(T14 - T15) / (T14 - T16): intercooler effectiveness."""
    t14 = df["Charge Air IC Air Temp. In"]
    t15 = df["Charge Air IC Air Temp. Out"]
    t16 = df["Charge Air IC Cooling Water Temp. In"]
    return _safe_divide(t14 - t15, t14 - t16)


def exhaust_temp_spread(df: pd.DataFrame) -> pd.Series:
    """Max minus min exhaust gas temperature across cylinders 1-3."""
    cylinders = df[["No.1 Exh.Gas Temp.", "No.2 Exh.Gas Temp.", "No.3 Exh.Gas Temp."]]
    return cylinders.max(axis=1) - cylinders.min(axis=1)


def exhaust_temp_deviation(df: pd.DataFrame) -> pd.DataFrame:
    """Each cylinder's exhaust gas temperature deviation from the three-cylinder mean."""
    columns = ["No.1 Exh.Gas Temp.", "No.2 Exh.Gas Temp.", "No.3 Exh.Gas Temp."]
    cylinders = df[columns]
    mean = cylinders.mean(axis=1)
    return cylinders.sub(mean, axis=0)


def pmax_spread(df: pd.DataFrame) -> pd.Series:
    """Max minus min in-cylinder peak pressure across cylinders 1-3."""
    cylinders = df[
        [
            "Max. In-Cylinder Press. No.1",
            "Max. In-Cylinder Press. No.2",
            "Max. In-Cylinder Press. No.3",
        ]
    ]
    return cylinders.max(axis=1) - cylinders.min(axis=1)


def indicated_work_spread(df: pd.DataFrame) -> pd.Series:
    """Max minus min indicated work across cylinders 1-3."""
    cylinders = df[["Indicated Work No.1", "Indicated Work No.2", "Indicated Work No.3"]]
    return cylinders.max(axis=1) - cylinders.min(axis=1)


def turbine_temp_drop(df: pd.DataFrame) -> pd.Series:
    """T4 - T5: temperature drop across the turbine."""
    return df["Exh.Gas Temp. Turbine In"] - df["Exh.Gas Temp. Turbine Out"]


def cooling_water_rise(df: pd.DataFrame) -> pd.Series:
    """Mean of T7-T9 minus T6: cooling water temperature rise across the engine."""
    outlets = df[
        [
            "Cooling Water Temp. Engine Out I",
            "Cooling Water Temp. Engine Out II",
            "Cooling Water Temp. Engine Out III",
        ]
    ]
    return outlets.mean(axis=1) - df["Cooling Water Temp. Engine In"]


def fuel_flow_per_kw(df: pd.DataFrame) -> pd.Series:
    """Fuel flow normalised by shaft power."""
    return _safe_divide(df["Fuel Flow"], df["Shaft Power"])


def exhaust_mass_flow_per_fuel(df: pd.DataFrame) -> pd.Series:
    """Exhaust gas mass flow normalised by fuel flow."""
    return _safe_divide(df["Exh. Gas Mass Flow"], df["Fuel Flow"])


def heat_exchanger_shares(df: pd.DataFrame) -> pd.DataFrame:
    """Each heat exchanger's share of the total heat balance loss."""
    total = df["Total Heat Loss in Heat Exchangers"]
    shares = {
        "cooling_water_share": df["Loss with cooling water"],
        "lo_share": df["Loss with LO"],
        "charge_air_ic_share": df["Loss in Charge Air IC"],
        "tch_lo_share": df["Loss with TCH LO"],
    }
    return pd.DataFrame({name: _safe_divide(values, total) for name, values in shares.items()})


def add_physics_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` with every ``phys_``-prefixed physics feature added."""
    result = df.copy()
    result["phys_pressure_ratio"] = pressure_ratio(df)
    result["phys_cooler_effectiveness"] = cooler_effectiveness(df)
    result["phys_exhaust_temp_spread"] = exhaust_temp_spread(df)
    deviation = exhaust_temp_deviation(df)
    result["phys_exhaust_temp_dev_1"] = deviation["No.1 Exh.Gas Temp."]
    result["phys_exhaust_temp_dev_2"] = deviation["No.2 Exh.Gas Temp."]
    result["phys_exhaust_temp_dev_3"] = deviation["No.3 Exh.Gas Temp."]
    result["phys_turbine_temp_drop"] = turbine_temp_drop(df)
    result["phys_pmax_spread"] = pmax_spread(df)
    result["phys_indicated_work_spread"] = indicated_work_spread(df)
    result["phys_fuel_flow_per_kw"] = fuel_flow_per_kw(df)
    result["phys_exhaust_mass_flow_per_fuel"] = exhaust_mass_flow_per_fuel(df)
    shares = heat_exchanger_shares(df)
    result["phys_cooling_water_share"] = shares["cooling_water_share"]
    result["phys_lo_share"] = shares["lo_share"]
    result["phys_charge_air_ic_share"] = shares["charge_air_ic_share"]
    result["phys_tch_lo_share"] = shares["tch_lo_share"]
    result["phys_cooling_water_rise"] = cooling_water_rise(df)
    return result


def _run_rolling_features(
    group: pd.DataFrame, channels: Sequence[str], windows_s: Sequence[float], stats: Sequence[str]
) -> pd.DataFrame:
    """Trailing time-based rolling features for a single run, sorted by ``t``."""
    ordered = group.sort_values("t")
    t = ordered["t"].to_numpy()
    time_index = pd.to_timedelta(t, unit="s")
    t_start = t[0]
    columns: dict[str, pd.Series] = {}

    for window in windows_s:
        warmup = ((t - t_start) < window).astype(int)
        columns[f"roll_warmup_{window}"] = pd.Series(warmup, index=ordered.index)

        t_series = pd.Series(t, index=time_index)
        roller_t = t_series.rolling(f"{window}s", min_periods=1)
        sum_t = roller_t.sum()
        sum_tt = t_series.pow(2).rolling(f"{window}s", min_periods=1).sum()
        count = roller_t.count()
        denom = count * sum_tt - sum_t.pow(2)

        for channel in channels:
            values = pd.Series(ordered[channel].to_numpy(), index=time_index)
            roller_v = values.rolling(f"{window}s", min_periods=1)
            if "mean" in stats:
                mean = roller_v.mean()
                columns[f"{channel}_roll_{window}s_mean"] = pd.Series(
                    mean.to_numpy(), index=ordered.index
                )
            if "std" in stats:
                std = roller_v.std()
                columns[f"{channel}_roll_{window}s_std"] = pd.Series(
                    std.to_numpy(), index=ordered.index
                )
            if "slope" in stats:
                sum_v = roller_v.sum()
                sum_tv = (t_series * values).rolling(f"{window}s", min_periods=1).sum()
                slope = (count * sum_tv - sum_t * sum_v) / denom.where(denom != 0)
                columns[f"{channel}_roll_{window}s_slope"] = pd.Series(
                    (slope * 60.0).to_numpy(), index=ordered.index
                )

    return pd.DataFrame(columns, index=ordered.index)


def add_rolling_features(
    df: pd.DataFrame,
    channels: Iterable[str],
    windows_s: Sequence[float] = (60, 300, 900),
    stats: Sequence[str] = ("mean", "std", "slope"),
) -> pd.DataFrame:
    """Return a copy of ``df`` with trailing time-based rolling features per run.

    Each row's window contains only rows of the same run with ``t`` in
    ``(t - window, t]``; a run's rolling state never depends on another run or
    on later rows. Slope is the least-squares slope against ``t`` in units
    per minute. ``roll_warmup_<window>`` is 1 while a run's window is still
    filling (the first ``window`` seconds of the run).
    """
    channels = list(channels)
    parts = [
        _run_rolling_features(run_df, channels, windows_s, stats)
        for _, run_df in df.groupby("run", sort=False)
    ]
    rolled = pd.concat(parts).reindex(df.index)
    return pd.concat([df, rolled], axis=1)


class HealthyEngineResiduals(BaseEstimator, TransformerMixin):
    """Add ``resid_<target>`` columns: measured minus what a healthy engine would read.

    Fits, on rows where ``y == "Normal"`` only, one polynomial ridge regression
    per target channel from ``inputs``, standardised inside. ``targets=None``
    means every raw sensor channel except the inputs. Polynomial ridge rather
    than trees because held-out loads at 40% and 85% sit at the edges of the
    training range and trees cannot extrapolate.
    """

    def __init__(
        self,
        inputs: Sequence[str] = ("Engine Speed", "Water Brake Weight", "Fuel Flow"),
        targets: Sequence[str] | None = None,
        degree: int = 2,
        alpha: float = 1.0,
    ) -> None:
        self.inputs = inputs
        self.targets = targets
        self.degree = degree
        self.alpha = alpha

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series | np.ndarray,
        extra_healthy: pd.DataFrame | None = None,
    ) -> HealthyEngineResiduals:
        y = pd.Series(np.asarray(y), index=X.index)
        healthy = X.loc[y == "Normal"]
        if extra_healthy is not None:
            healthy = pd.concat([healthy, extra_healthy])

        self.targets_ = (
            list(self.targets)
            if self.targets is not None
            else [c for c in raw_sensor_columns(X) if c not in self.inputs]
        )
        self.models_: dict[str, Pipeline] = {}
        inputs = list(self.inputs)
        for target in self.targets_:
            model = make_pipeline(
                PolynomialFeatures(degree=self.degree, include_bias=False),
                StandardScaler(),
                Ridge(alpha=self.alpha),
            )
            model.fit(healthy[inputs], healthy[target])
            self.models_[target] = model
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        inputs = list(self.inputs)
        out = X.copy()
        for target in self.targets_:
            predicted = self.models_[target].predict(X[inputs])
            out[f"resid_{target}"] = X[target].to_numpy() - predicted
        return out

    def get_feature_names_out(self, input_features=None) -> np.ndarray:
        base = list(input_features) if input_features is not None else []
        return np.asarray(base + [f"resid_{target}" for target in self.targets_])


def _physics_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.startswith("phys_")]


def _rolling_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if "_roll_" in c or c.startswith("roll_warmup_")]


def _drop_day_markers(X: pd.DataFrame) -> pd.DataFrame:
    """Post-residual pipeline step: drop the raw day-marker channels, keeping their
    ``resid_`` replacements (and every other column) added by ``HealthyEngineResiduals``.
    """
    return X.drop(columns=list(DAY_MARKER_RESIDUAL_CHANNELS))


def _feature_columns(*, physics: bool, rolling: bool) -> Callable[[pd.DataFrame], list[str]]:
    def columns(df: pd.DataFrame) -> list[str]:
        all_raw = raw_sensor_columns(df)
        phys_columns = set(_physics_columns(df))
        roll_columns = set(_rolling_columns(df))
        result = [c for c in all_raw if c not in phys_columns and c not in roll_columns]
        if physics:
            result += [c for c in all_raw if c in phys_columns]
        if rolling:
            result += [c for c in all_raw if c in roll_columns]
        return [c for c in result if c not in EXCLUDED_COLUMNS]

    return columns


@dataclass(frozen=True)
class FeatureSet:
    """One named ablation arm: the ``features`` list to pass to ``lolo_predict`` and
    whether ``build_pipeline`` should residualise the day-marker channels.
    """

    columns: Callable[[pd.DataFrame], list[str]]
    residuals: bool


FEATURE_SETS: dict[str, FeatureSet] = {
    "raw": FeatureSet(_feature_columns(physics=False, rolling=False), residuals=False),
    "raw+physics": FeatureSet(_feature_columns(physics=True, rolling=False), residuals=False),
    "residuals": FeatureSet(_feature_columns(physics=False, rolling=False), residuals=True),
    "residuals+physics": FeatureSet(_feature_columns(physics=True, rolling=False), residuals=True),
    "residuals+physics+rolling": FeatureSet(
        _feature_columns(physics=True, rolling=True), residuals=True
    ),
    "raw+physics+rolling": FeatureSet(
        _feature_columns(physics=True, rolling=True), residuals=False
    ),
}


def build_pipeline(feature_set: str, model: BaseEstimator) -> Pipeline:
    """Unfitted ``Pipeline`` for ``feature_set``, usable as a ``lolo_predict`` factory
    result: with the residuals flag set, a ``HealthyEngineResiduals`` step (targets are
    the day-marker channels) is fitted first and the raw day-marker columns are dropped
    before ``model`` sees the data; call with ``FEATURE_SETS[feature_set].columns(df)``
    as the ``features`` argument to ``lolo_predict`` so the residual step has its inputs.
    """
    spec = FEATURE_SETS[feature_set]
    if not spec.residuals:
        return Pipeline([("model", model)])
    return Pipeline(
        [
            ("residuals", HealthyEngineResiduals(targets=list(DAY_MARKER_RESIDUAL_CHANNELS))),
            ("drop_day_markers", FunctionTransformer(_drop_day_markers)),
            ("model", model),
        ]
    )
