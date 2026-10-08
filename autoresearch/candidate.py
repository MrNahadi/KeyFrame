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
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from keyframe.features import RESIDUAL_INPUTS, HealthyEngineResiduals, _residual_view
from keyframe.tuning import _BalancedXGBClassifier

PARAMS = {
    "max_depth": 2,
    "learning_rate": 0.1788532743297921,
    "n_estimators": 63,
    "subsample": 0.831261142176991,
    "colsample_bytree": 0.6558555380447055,
    "reg_lambda": 0.12030178871154672,
}


def add_features(run: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(index=run.index)


def select_columns(available: list[str]) -> list[str]:
    return available


class _RelativeResiduals(HealthyEngineResiduals):
    """Healthy-engine residuals as a share of the expected reading, (x - x_hat) / (|x_hat| +
    healthy sd), so a deviation means the same at 40% and at 85% load."""

    def fit(self, X, y, extra_healthy=None):
        super().fit(X, y, extra_healthy)
        healthy = X.loc[np.asarray(y) == "Normal"]
        self.scale_ = {t: float(healthy[t].std()) + 1e-9 for t in self.targets_}
        return self

    def transform(self, X):
        inputs = list(self.inputs)
        out = X.copy()
        for target in self.targets_:
            predicted = self.models_[target].predict(X[inputs])
            denominator = np.abs(predicted) + self.scale_[target]
            out[f"resid_{target}"] = (X[target].to_numpy() - predicted) / denominator
        return out


def _load_free_view(X: pd.DataFrame) -> pd.DataFrame:
    """Drop the operating-point inputs and every remaining rolling mean, so the classifier
    sees deviations from a healthy engine, spreads, ratios and trends, not load levels."""
    drop = [c for c in X.columns if c in RESIDUAL_INPUTS or c.endswith("_mean")]
    return X.drop(columns=drop)


def build_model(seed: int) -> Pipeline:
    return Pipeline(
        [
            ("residuals", _RelativeResiduals(inputs=RESIDUAL_INPUTS)),
            ("residual_view", FunctionTransformer(_residual_view)),
            ("load_free", FunctionTransformer(_load_free_view)),
            ("model", _BalancedXGBClassifier(random_state=seed, n_jobs=4, **PARAMS)),
        ]
    )
