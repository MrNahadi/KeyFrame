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


def add_features(run: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(index=run.index)


def select_columns(available: list[str]) -> list[str]:
    return [c for c in available if not c.endswith(("_mean", "_slope"))]


def build_model(seed: int) -> Pipeline:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        RandomForestClassifier(class_weight="balanced", random_state=seed, n_jobs=4, **PARAMS),
    )
