"""Nested Optuna tuning: per-model search spaces and the inner-fold objective (R1-R3)."""

from __future__ import annotations

from collections.abc import Callable

import lightgbm as lgb
import optuna
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_sample_weight

from keyframe import SEED, evaluate

optuna.logging.set_verbosity(optuna.logging.WARNING)


def thin(df: pd.DataFrame, step: int = 4) -> pd.DataFrame:
    """Every ``step``-th row of each run, kept in time order (consecutive readings are near-duplicates)."""
    parts = [group.sort_values("t").iloc[::step] for _, group in df.groupby("run", sort=False)]
    return pd.concat(parts)


class _BalancedXGBClassifier(xgb.XGBClassifier):
    """``XGBClassifier`` with per-row balanced sample weights (it has no ``class_weight``)."""

    def fit(self, X, y, **kwargs):  # noqa: N803 (sklearn convention)
        kwargs.setdefault("sample_weight", compute_sample_weight("balanced", y))
        return super().fit(X, y, **kwargs)


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
        "num_leaves": trial.suggest_int("num_leaves", 7, 127),
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "n_estimators": trial.suggest_int("n_estimators", 50, 500),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
        "feature_fraction": trial.suggest_float("feature_fraction", 0.5, 1.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
    }


def _xgboost_space(trial: optuna.Trial) -> dict:
    return {
        "max_depth": trial.suggest_int("max_depth", 2, 10),
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "n_estimators": trial.suggest_int("n_estimators", 50, 500),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
    }


def _random_forest_space(trial: optuna.Trial) -> dict:
    return {
        "max_depth": trial.suggest_int("max_depth", 3, 30),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 50),
        "max_features": trial.suggest_float("max_features", 0.1, 1.0),
        "max_samples": trial.suggest_float("max_samples", 0.3, 1.0),
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
