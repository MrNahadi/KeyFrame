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

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline, make_pipeline

PARAMS = {
    "n_estimators": 57,
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


def add_features(run: pd.DataFrame) -> pd.DataFrame:
    """Change since the run's first ``BASELINE_S`` seconds (expanding mean until then)."""
    early = (run["t"] - run["t"].iloc[0]) < BASELINE_S
    out = {}
    for channel in DELTA_CHANNELS:
        x = run[channel]
        ref = x.where(early).expanding().mean().ffill()
        out[f"cand_delta_{channel}"] = x - ref
    return pd.DataFrame(out, index=run.index)


def select_columns(available: list[str]) -> list[str]:
    return [c for c in available if not c.endswith(("_mean", "_slope"))]


def build_model(seed: int) -> Pipeline:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        RandomForestClassifier(class_weight="balanced", random_state=seed, n_jobs=4, **PARAMS),
    )
