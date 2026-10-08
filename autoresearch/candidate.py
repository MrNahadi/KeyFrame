"""The one file the autoresearch agent edits (feature 16). See autoresearch/program.md.

The harness (keyframe/autoresearch.py) calls three functions:

- ``add_features(run)``: one run, in time order, with ``t`` and the allowed sensor,
  physics and rolling columns. Return new columns only (names start with ``cand_``),
  same index, computed from the current and earlier rows only. Return an empty frame
  to add nothing.
- ``select_columns(available)``: the columns the model sees, chosen from ``available``.
- ``build_model(seed)``: an unfitted classifier with ``fit(X, y)`` and ``predict(X)``;
  ``y`` holds the class names. Anything fitted (scalers, residual models, selectors)
  belongs inside it, so it is fitted on training rows only.

Baseline: the v1 locked model for this search's outer fold (XGBoost, raw + physics +
rolling features, that fold's nested-tuned parameters from models/tuning/).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline, make_pipeline

PARAMS = {
    "n_estimators": 250,
    "max_depth": 4,
    "min_samples_leaf": 44,
    "max_features": 0.40055750587160444,
    "max_samples": 0.5832290311184182,
}


DELTA_CHANNELS = (
    "Charge Air IC Air Temp. Out",
    "phys_cooler_effectiveness",
    "Charge Air Press.",
    "Exh.Gas Temp. Turbine In",
    "Exh.Gas Temp. Turbine Out",
    "phys_turbine_temp_drop",
    "phys_exhaust_temp_spread",
    "phys_pmax_spread",
    "Engine Cooling water flow",
    "Fresh Cooling Water Press.",
    "phys_cooling_water_rise",
    "Exh. Gas Mass Flow",
    "Charge Air IC Air Temp. In",
    "Shaft Power",
    "phys_fuel_flow_per_kw",
)
BASELINE_S = 600.0
LOAD_STEP_KW = 15.0


def _load_segments(run: pd.DataFrame) -> np.ndarray:
    """Segment id per row: a new segment starts when the 60 s mean shaft power moves more
    than ``LOAD_STEP_KW`` from the current segment's mean power (causal)."""
    power = run["Shaft Power_roll_60s_mean"].to_numpy()
    segment = np.zeros(len(power), dtype=int)
    ref, n = power[0], 1
    for i in range(1, len(power)):
        if abs(power[i] - ref) > LOAD_STEP_KW:
            segment[i:] = segment[i - 1] + 1
            ref, n = power[i], 1
        else:
            n += 1
            ref += (power[i] - ref) / n
            segment[i] = segment[i - 1]
    return segment


def add_features(run: pd.DataFrame) -> pd.DataFrame:
    """Change since the first ``BASELINE_S`` seconds at the current load setpoint, in units
    of the noise over that period (expanding mean and std until then)."""
    segment = pd.Series(_load_segments(run), index=run.index)
    t0 = run["t"].groupby(segment).transform("first")
    early = (run["t"] - t0) < BASELINE_S
    out = {}
    for channel in DELTA_CHANNELS:
        x = run[channel]
        grouped = x.where(early).groupby(segment)
        ref = grouped.transform(lambda v: v.expanding().mean().ffill())
        noise = grouped.transform(lambda v: v.expanding().std().ffill())
        out[f"cand_delta_{channel}"] = (x - ref) / noise.where(noise > 0)
    return pd.DataFrame(out, index=run.index)


RAW_KEEP = (
    "Engine Speed",
    "Water Brake Weight",
    "Fuel Flow",
    "Shaft Power",
    "Charge Air IC Air Temp. Out",
    "Charge Air Press.",
    "Exh.Gas Temp. Turbine In",
    "Exh.Gas Temp. Turbine Out",
    "Exh. Gas Mass Flow",
    "Engine Cooling water flow",
    "Fresh Cooling Water Press.",
    "Sea Cooling Water Press.",
)


def select_columns(available: list[str]) -> list[str]:
    return [
        c
        for c in available
        if c.startswith("cand_")
        or (c.startswith("phys_") and "_roll_" not in c)
        or c in RAW_KEEP
    ]


NORMAL_WEIGHT = 2.0


def _class_weight(y) -> dict:
    """Balanced class weights, with Normal scaled by ``NORMAL_WEIGHT``: the healthy class
    pools many sessions (the reference run alone is half of it), so plain balancing leaves
    each healthy row too little weight against the faults."""
    classes, counts = np.unique(np.asarray(y), return_counts=True)
    weights = len(y) / (len(classes) * counts)
    return {
        c: w * (NORMAL_WEIGHT if c == "Normal" else 1.0)
        for c, w in zip(classes, weights, strict=True)
    }


class WeightedForest(Pipeline):
    def fit(self, X, y, **params):  # noqa: N803
        self.steps[-1][1].set_params(class_weight=_class_weight(y))
        return super().fit(X, y, **params)


def build_model(seed: int) -> Pipeline:
    return WeightedForest(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("forest", RandomForestClassifier(random_state=seed, n_jobs=4, **PARAMS)),
        ]
    )
