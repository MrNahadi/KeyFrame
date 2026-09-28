"""Healthy-only anomaly detectors: ``fit`` sees healthy rows only, ``score`` returns
higher-is-more-anomalous values for any input.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from keyframe import SEED


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
