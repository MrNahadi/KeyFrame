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
from sklearn.preprocessing import FunctionTransformer

from keyframe.features import (
    RESIDUAL_INPUTS,
    HealthyEngineResiduals,
    _residual_view,
    without_day_channels,
)
from keyframe.tuning import _BalancedXGBClassifier

PARAMS = {
    "max_depth": 7,
    "learning_rate": 0.0033572967053517922,
    "n_estimators": 59,
    "subsample": 0.5917022549267169,
    "colsample_bytree": 0.6521211214797689,
    "reg_lambda": 0.12561043700013558,
}


def add_features(run: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(index=run.index)


def select_columns(available: list[str]) -> list[str]:
    """No day-dependent channels nor anything derived from them."""
    return without_day_channels(available)


COOLANT_IN = "Charge Air IC Cooling Water Temp. In"
"""Cooling water supply temperature: set by the day, it shifts every engine temperature, so
the healthy-engine model takes it as an input and the classifier never sees it."""


def _drop_coolant(X: pd.DataFrame) -> pd.DataFrame:
    return X.drop(columns=[c for c in X.columns if c.split("_roll_")[0] == COOLANT_IN])


def build_model(seed: int) -> Pipeline:
    return Pipeline(
        [
            ("residuals", HealthyEngineResiduals(inputs=(*RESIDUAL_INPUTS, COOLANT_IN))),
            ("residual_view", FunctionTransformer(_residual_view)),
            ("drop_coolant", FunctionTransformer(_drop_coolant)),
            ("model", _BalancedXGBClassifier(random_state=seed, n_jobs=4, **PARAMS)),
        ]
    )
