"""Healthy-only anomaly detectors: ``fit`` sees healthy rows only, ``score`` returns
higher-is-more-anomalous values for any input.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from keyframe import SEED, features

RAW_FEATURE_SET = "raw+physics+rolling"


def detector_inputs(
    df: pd.DataFrame, arm: str
) -> tuple[list[str], Callable[[pd.DataFrame, pd.Series], Callable[[pd.DataFrame], pd.DataFrame]]]:
    """Column list for input ``arm`` (``"raw"`` or ``"residual"``, ADR 0008) and a function
    that fits the arm's view on training rows and returns a projector for any frame.

    ``raw`` selects ``FEATURE_SETS["raw+physics+rolling"]`` unchanged. ``residual`` fits
    ``HealthyEngineResiduals`` on the training frame's healthy rows (it filters internally)
    and keeps every ``resid_`` column, every ``phys_`` column and every rolling ``_std``/
    ``_slope`` column; raw levels, rolling means and the residual inputs themselves never
    appear.
    """
    if arm == "raw":
        columns = features.FEATURE_SETS[RAW_FEATURE_SET].columns(df)

        def fit_raw_view(train_df: pd.DataFrame, train_labels: pd.Series) -> Callable:
            return lambda X: X[columns]

        return columns, fit_raw_view

    if arm == "residual":
        targets = [c for c in features.sensor_channels(df) if c not in features.RESIDUAL_INPUTS]
        phys_columns = [c for c in df.columns if c.startswith("phys_") and "_roll_" not in c]
        rolling_columns = [
            c for c in df.columns if "_roll_" in c and ("_std" in c or "_slope" in c)
        ]
        columns = [f"resid_{target}" for target in targets] + phys_columns + rolling_columns

        def fit_residual_view(train_df: pd.DataFrame, train_labels: pd.Series) -> Callable:
            residualiser = features.HealthyEngineResiduals(
                inputs=features.RESIDUAL_INPUTS, targets=targets
            ).fit(train_df, train_labels)
            return lambda X: residualiser.transform(X)[columns]

        return columns, fit_residual_view

    raise ValueError(f"unknown detector input arm: {arm!r}")


class IsolationForestDetector:
    """Isolation Forest over standardised, median-imputed inputs.

    Imputation medians and standardisation statistics come from the healthy rows
    passed to ``fit`` only, so scoring later data never changes what the detector
    learned as "healthy".
    """

    def __init__(self, n_estimators: int = 300, max_samples: int = 8192) -> None:
        self.n_estimators = n_estimators
        self.max_samples = max_samples

    def fit(self, X_healthy: pd.DataFrame) -> IsolationForestDetector:
        self.imputer_ = SimpleImputer(strategy="median").fit(X_healthy)
        scaled_healthy = self._prepare(X_healthy, fit_scaler=True)
        self.model_ = IsolationForest(
            n_estimators=self.n_estimators,
            max_samples=min(self.max_samples, len(X_healthy)),
            random_state=SEED,
        ).fit(scaled_healthy)
        return self

    def score(self, X: pd.DataFrame) -> np.ndarray:
        scaled = self._prepare(X, fit_scaler=False)
        return -self.model_.score_samples(scaled)

    def _prepare(self, X: pd.DataFrame, *, fit_scaler: bool) -> np.ndarray:
        imputed = self.imputer_.transform(X)
        if fit_scaler:
            self.scaler_ = StandardScaler().fit(imputed)
        return self.scaler_.transform(imputed)


class AutoencoderDetector:
    """Bottlenecked MLP autoencoder over standardised, median-imputed inputs.

    Score is the mean squared reconstruction error, so rows the network cannot
    compress and rebuild from the healthy manifold score higher.
    """

    def __init__(self, hidden_layer_sizes: tuple[int, ...] = (64, 16, 64)) -> None:
        self.hidden_layer_sizes = hidden_layer_sizes

    def fit(self, X_healthy: pd.DataFrame) -> AutoencoderDetector:
        self.imputer_ = SimpleImputer(strategy="median").fit(X_healthy)
        scaled_healthy = self._prepare(X_healthy, fit_scaler=True)
        self.model_ = MLPRegressor(
            hidden_layer_sizes=self.hidden_layer_sizes,
            early_stopping=True,
            random_state=SEED,
        ).fit(scaled_healthy, scaled_healthy)
        return self

    def score(self, X: pd.DataFrame) -> np.ndarray:
        scaled = self._prepare(X, fit_scaler=False)
        reconstructed = self.model_.predict(scaled)
        return np.mean((scaled - reconstructed) ** 2, axis=1)

    def _prepare(self, X: pd.DataFrame, *, fit_scaler: bool) -> np.ndarray:
        imputed = self.imputer_.transform(X)
        if fit_scaler:
            self.scaler_ = StandardScaler().fit(imputed)
        return self.scaler_.transform(imputed)


class PCADetector:
    """PCA over standardised, median-imputed inputs.

    Score is the max of Hotelling T² and reconstruction error Q, each divided by
    its own 99th percentile on the training healthy rows, so the two parts are
    comparable before being combined.
    """

    def __init__(self, variance_ratio: float = 0.95) -> None:
        self.variance_ratio = variance_ratio

    def fit(self, X_healthy: pd.DataFrame) -> PCADetector:
        self.imputer_ = SimpleImputer(strategy="median").fit(X_healthy)
        scaled_healthy = self._prepare(X_healthy, fit_scaler=True)
        self.pca_ = PCA(n_components=self.variance_ratio, svd_solver="full", random_state=SEED).fit(
            scaled_healthy
        )
        t2, q = self._t2_q(scaled_healthy)
        self.t2_p99_ = np.percentile(t2, 99)
        self.q_p99_ = np.percentile(q, 99)
        return self

    def score_parts(self, X: pd.DataFrame) -> pd.DataFrame:
        scaled = self._prepare(X, fit_scaler=False)
        t2, q = self._t2_q(scaled)
        combined = np.maximum(t2 / self.t2_p99_, q / self.q_p99_)
        return pd.DataFrame({"t2": t2, "q": q, "score": combined}, index=X.index)

    def score(self, X: pd.DataFrame) -> np.ndarray:
        return self.score_parts(X)["score"].to_numpy()

    def _t2_q(self, scaled: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        projected = self.pca_.transform(scaled)
        t2 = np.sum((projected**2) / self.pca_.explained_variance_, axis=1)
        reconstructed = self.pca_.inverse_transform(projected)
        q = np.sum((scaled - reconstructed) ** 2, axis=1)
        return t2, q

    def _prepare(self, X: pd.DataFrame, *, fit_scaler: bool) -> np.ndarray:
        imputed = self.imputer_.transform(X)
        if fit_scaler:
            self.scaler_ = StandardScaler().fit(imputed)
        return self.scaler_.transform(imputed)
