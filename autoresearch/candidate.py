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

from keyframe.tuning import _BalancedXGBClassifier

PARAMS = {
    "max_depth": 1,
    "learning_rate": 0.13983740016490973,
    "n_estimators": 200,
    "subsample": 0.8540362888980227,
    "colsample_bytree": 0.5102922471479012,
    "reg_lambda": 7.579479953348009,
}


def add_features(run: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(index=run.index)


def select_columns(available: list[str]) -> list[str]:
    return available


def build_model(seed: int) -> _BalancedXGBClassifier:
    return _BalancedXGBClassifier(random_state=seed, n_jobs=4, **PARAMS)
