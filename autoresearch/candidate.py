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
from sklearn.pipeline import Pipeline

from keyframe.features import HealthyEngineResiduals
from keyframe.tuning import _BalancedXGBClassifier

PARAMS = {
    "max_depth": 1,
    "learning_rate": 0.13983740016490973,
    "n_estimators": 200,
    "subsample": 0.8540362888980227,
    "colsample_bytree": 0.2,
    "reg_lambda": 7.579479953348009,
}


IMBALANCE = (
    "phys_exhaust_temp_spread",
    "phys_exhaust_temp_dev_1",
    "phys_exhaust_temp_dev_2",
    "phys_exhaust_temp_dev_3",
    "phys_pmax_spread",
    "phys_indicated_work_spread",
)
"""Cylinder imbalance; a healthy engine's grows with load, so it reaches the model only as
a residual from what a healthy engine shows at the same load."""

CHECKLIST_CHANNELS = (
    "Charge Air IC Air Temp. Out",
    "Charge Air IC Air Temp. In",
    "Charge Air IC Cooling Water Temp. Out",
    "Charge Air Press.",
    "Exh.Gas Temp. Turbine In",
    "Exh.Gas Temp. Turbine Out",
    "No.1 Exh.Gas Temp.",
    "No.2 Exh.Gas Temp.",
    "No.3 Exh.Gas Temp.",
    "Max. In-Cylinder Press. No.1",
    "Max. In-Cylinder Press. No.2",
    "Max. In-Cylinder Press. No.3",
    "TCH Power",
    "Exh. Gas Mass Flow",
    "Fresh Cooling Water Press.",
    "Engine Cooling water flow",
    "phys_cooler_effectiveness",
    "phys_turbine_temp_drop",
    "phys_pressure_ratio",
    "phys_cooling_water_rise",
    *IMBALANCE,
)
"""The channels the engineering checklist says the faults move."""

LOAD_INPUTS = ("Engine Speed", "Water Brake Weight")
"""The operating point; fuel flow is left out because the governor adds fuel under a fault."""


def add_features(run: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(index=run.index)


LUBE_OIL = ("LO ", "TCH LO", "Loss with LO", "Loss with TCH LO", "phys_lo_share", "phys_tch_lo_share")
"""The lube oil system: no fault in the checklist acts on it, so it can only tell sessions apart."""


def select_columns(available: list[str]) -> list[str]:
    return [
        c
        for c in available
        if (not c.startswith(IMBALANCE) or c in RESIDUAL_SOURCES) and not c.startswith(LUBE_OIL)
    ]


SMOOTH = "_roll_300s_mean"
RESIDUAL_SOURCES = {c + SMOOTH for c in IMBALANCE}


def build_model(seed: int) -> Pipeline:
    smooth = SMOOTH
    residuals = HealthyEngineResiduals(
        inputs=[c + smooth for c in LOAD_INPUTS],
        targets=[c + smooth for c in CHECKLIST_CHANNELS],
        degree=1,
    )
    return Pipeline(
        [
            ("residuals", residuals),
            ("model", _BalancedXGBClassifier(random_state=seed, n_jobs=4, **PARAMS)),
        ]
    )
