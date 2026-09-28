"""Nested Optuna tuning: per-model search spaces and the inner-fold objective (R1-R3)."""

from __future__ import annotations

from collections.abc import Callable

import lightgbm as lgb
import optuna
import pandas as pd
import xgboost as xgb
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.utils.class_weight import compute_sample_weight

from keyframe import SEED, evaluate

optuna.logging.set_verbosity(optuna.logging.WARNING)


def thin(df: pd.DataFrame, step: int = 4) -> pd.DataFrame:
    """Every ``step``-th row of each run, kept in time order (consecutive readings are near-duplicates)."""
    parts = [group.sort_values("t").iloc[::step] for _, group in df.groupby("run", sort=False)]
    return pd.concat(parts)


class _BalancedXGBClassifier(ClassifierMixin, BaseEstimator):
    """XGBoost with balanced per-row sample weights and string class labels.

    ``XGBClassifier`` has no ``class_weight`` and only accepts labels 0..k-1, so this
    wrapper encodes the labels present in ``y`` for fitting and decodes predictions;
    ``classes_`` holds the original labels, in the order of ``predict_proba``'s columns.
    """

    def __init__(self, random_state: int = SEED, **params: object) -> None:
        self.random_state = random_state
        self.params = params

    def get_params(self, deep: bool = True) -> dict:
        return {"random_state": self.random_state, **self.params}

    def set_params(self, **params: object) -> _BalancedXGBClassifier:
        if "random_state" in params:
            self.random_state = params.pop("random_state")  # type: ignore[assignment]
        self.params.update(params)
        return self

    def fit(self, X, y, **kwargs):  # noqa: N803 (sklearn convention)
        self.encoder_ = LabelEncoder().fit(y)
        self.classes_ = self.encoder_.classes_
        encoded = self.encoder_.transform(y)
        kwargs.setdefault("sample_weight", compute_sample_weight("balanced", encoded))
        self.model_ = xgb.XGBClassifier(random_state=self.random_state, **self.params)
        self.model_.fit(X, encoded, **kwargs)
        return self

    def predict_proba(self, X):  # noqa: N803
        return self.model_.predict_proba(X)

    def predict(self, X):  # noqa: N803
        return self.encoder_.inverse_transform(self.model_.predict(X).astype(int))


def _logreg_builder(params: dict) -> object:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(class_weight="balanced", max_iter=2000, random_state=SEED, **params),
    )


def _lightgbm_builder(params: dict) -> object:
    return lgb.LGBMClassifier(class_weight="balanced", random_state=SEED, verbose=-1, **params)


def _random_forest_builder(params: dict) -> object:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        RandomForestClassifier(class_weight="balanced", random_state=SEED, **params),
    )


def _xgboost_builder(params: dict) -> object:
    return _BalancedXGBClassifier(random_state=SEED, **params)


MODEL_BUILDERS: dict[str, Callable[[dict], object]] = {
    "logreg": _logreg_builder,
    "lightgbm": _lightgbm_builder,
    "random_forest": _random_forest_builder,
    "xgboost": _xgboost_builder,
}


def _logreg_space(trial: optuna.Trial) -> dict:
    # penalty l2 (R2) is sklearn's default; passing it explicitly is deprecated since 1.8.
    return {"C": trial.suggest_float("C", 1e-3, 1e2, log=True)}


def _lightgbm_space(trial: optuna.Trial) -> dict:
    return {
        "num_leaves": trial.suggest_int("num_leaves", 7, 31),
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "n_estimators": trial.suggest_int("n_estimators", 50, 100),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
        "feature_fraction": trial.suggest_float("feature_fraction", 0.5, 1.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
    }


def _xgboost_space(trial: optuna.Trial) -> dict:
    return {
        "max_depth": trial.suggest_int("max_depth", 2, 8),
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "n_estimators": trial.suggest_int("n_estimators", 50, 100),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
    }


def _random_forest_space(trial: optuna.Trial) -> dict:
    return {
        "n_estimators": trial.suggest_int("n_estimators", 50, 100),
        "max_depth": trial.suggest_int("max_depth", 3, 20),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 50),
        "max_features": trial.suggest_float("max_features", 0.1, 0.6),
        "max_samples": trial.suggest_float("max_samples", 0.3, 0.7),
    }


SEARCH_SPACES: dict[str, Callable[[optuna.Trial], dict]] = {
    "logreg": _logreg_space,
    "lightgbm": _lightgbm_space,
    "xgboost": _xgboost_space,
    "random_forest": _random_forest_space,
}


def tune(
    model_name: str,
    train_df: pd.DataFrame,
    features: list[str],
    n_trials: int = 30,
    timeout_s: float | None = None,
) -> tuple[dict, pd.DataFrame]:
    """Optuna study (TPE, seeded) maximising pooled macro F1 over ``inner_lolo_folds``.

    Trials fit and score on ``thin(train_df)`` only, never on rows outside
    ``train_df`` (R3). Returns ``(study.best_params, study.trials_dataframe())``.
    """
    thinned = thin(train_df)
    space = SEARCH_SPACES[model_name]
    builder = MODEL_BUILDERS[model_name]

    def objective(trial: optuna.Trial) -> float:
        params = space(trial)

        def factory() -> object:
            return builder(params)

        predictions = evaluate.lolo_predict(factory, thinned, features)
        return evaluate.macro_f1(predictions["y_true"], predictions["y_pred"])

    sampler = optuna.samplers.TPESampler(seed=SEED)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    study.optimize(objective, n_trials=n_trials, timeout=timeout_s)
    return study.best_params, study.trials_dataframe()
