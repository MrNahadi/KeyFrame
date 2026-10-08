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
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from keyframe.features import RESIDUAL_INPUTS, HealthyEngineResiduals, _residual_view
from keyframe.tuning import _BalancedXGBClassifier

PHYSICS_CHANNELS = frozenset(
    {
        *RESIDUAL_INPUTS,
        "Max. In-Cylinder Press. No.1",
        "Max. In-Cylinder Press. No.2",
        "Max. In-Cylinder Press. No.3",
        "Charge Air Press.",
        "No.1 Exh.Gas Temp.",
        "No.2 Exh.Gas Temp.",
        "No.3 Exh.Gas Temp.",
        "Exh.Gas Temp. Turbine In",
        "Exh.Gas Temp. Turbine Out",
        "Cooling Water Temp. Engine In",
        "Cooling Water Temp. Engine Out I",
        "Cooling Water Temp. Engine Out II",
        "Cooling Water Temp. Engine Out III",
        "Charge Air IC Air Temp. In",
        "Charge Air IC Air Temp. Out",
        "Charge Air IC Cooling Water Temp. Out",
        "Fresh Cooling Water Press.",
        "Engine Cooling water flow",
        "Indicated Work No.1",
        "Indicated Work No.2",
        "Indicated Work No.3",
        "Loss with cooling water",
        "Loss in Charge Air IC",
        "Exh. Gas Mass Flow",
        "TCH Power",
        "Indicated Efficiency",
        "phys_pressure_ratio",
        "phys_cooler_effectiveness",
        "phys_exhaust_temp_spread",
        "phys_exhaust_temp_dev_1",
        "phys_exhaust_temp_dev_2",
        "phys_exhaust_temp_dev_3",
        "phys_turbine_temp_drop",
        "phys_pmax_spread",
        "phys_indicated_work_spread",
        "phys_fuel_flow_per_kw",
        "phys_exhaust_mass_flow_per_fuel",
        "phys_cooling_water_rise",
    }
)
"""The channels the engineering checklist ties to a fault mechanism, plus the
healthy-engine model's inputs; day-driven temperatures, auxiliary pumps and
heat-balance bookkeeping are left out."""

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
    return [c for c in available if c.split("_roll_")[0] in PHYSICS_CHANNELS]


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


class _RelativeRolling(BaseEstimator, TransformerMixin):
    """Rolling standard deviations and slopes as a share of the channel's rolling mean
    (plus its healthy sd, so near-zero channels stay finite), for the same reason."""

    def fit(self, X, y):
        healthy = X.loc[np.asarray(y) == "Normal"]
        self.pairs_ = []
        for column in X.columns:
            for stat in ("_std", "_slope"):
                if column.endswith(stat) and "_roll_" in column:
                    mean = column.removesuffix(stat) + "_mean"
                    source = column.split("_roll_")[0]
                    if mean in X.columns and source in X.columns:
                        scale = float(healthy[source].std()) + 1e-9
                        self.pairs_.append((column, mean, scale))
        return self

    def transform(self, X):
        out = X.copy()
        for column, mean, scale in self.pairs_:
            out[column] = X[column] / (X[mean].abs() + scale)
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
            ("relative_rolling", _RelativeRolling()),
            ("residual_view", FunctionTransformer(_residual_view)),
            ("load_free", FunctionTransformer(_load_free_view)),
            ("model", _BalancedXGBClassifier(random_state=seed, n_jobs=4, **PARAMS)),
        ]
    )
