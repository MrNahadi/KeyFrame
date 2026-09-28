"""Healthy-only anomaly detectors: ``fit`` sees healthy rows only, ``score`` returns
higher-is-more-anomalous values for any input.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
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
