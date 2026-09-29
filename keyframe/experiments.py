"""Heavy experiments run outside the notebooks: ``uv run python -m keyframe.experiments <name> ...``.

Each experiment writes its per-row LOLO predictions to
``data/processed/experiments/<name>.parquet`` and skips work whose output already
exists, unless ``--force``. Notebooks read those outputs and summarise them.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import lightgbm as lgb
import numpy as np
import pandas as pd
import shap
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler

from keyframe import (
    SEED,
    alarm,
    anomaly,
    audit,
    calibration,
    evaluate,
    features,
    paths,
    splits,
    tuning,
)

MODELLING_FEATURE_SET = "raw+physics+rolling"

FAULT_CLASSES = [c for c in evaluate.CLASS_ORDER if c != "Normal"]

DETECTOR_FACTORIES: dict[str, Callable[[], Any]] = {
    "iforest": lambda: anomaly.IsolationForestDetector(),
    "pca": lambda: anomaly.PCADetector(),
    "autoencoder": lambda: anomaly.AutoencoderDetector(),
}

MODEL_FACTORIES = {
    # The imputer fills the rare NaNs (a rolling std or slope over a run's first row,
    # a physics ratio with a zero denominator); it is fitted per fold like the scaler.
    # LightGBM handles NaN natively.
    "logreg": lambda: make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(class_weight="balanced", max_iter=2000, random_state=SEED),
    ),
    "lightgbm": lambda: lgb.LGBMClassifier(class_weight="balanced", random_state=SEED, verbose=-1),
}


FEATURE_TABLE = paths.PROCESSED / "features.parquet"


def load_feature_table(force: bool = False) -> pd.DataFrame:
    """The clean table with physics and rolling features, built once and cached as Parquet."""
    if FEATURE_TABLE.exists() and not force:
        return pd.read_parquet(FEATURE_TABLE)
    table = features.build_feature_table(pd.read_parquet(paths.PROCESSED / "clean.parquet"))
    FEATURE_TABLE.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(FEATURE_TABLE)
    return table


def _extra_healthy(df: pd.DataFrame, held_out_bin: object) -> pd.DataFrame:
    """Reference-file rows of ``held_out_bin``, for the shop-test residual fit (R9)."""
    reference = df[df["run"] == "Reference_Data"]
    return reference[reference["load_bin"] == held_out_bin]


def run_ablation(
    df: pd.DataFrame,
    feature_set: str,
    model: str,
    *,
    shop_test: bool = False,
    force: bool = False,
    fold: int | None = None,
    output_dir: Path = paths.PROCESSED / "experiments",
) -> Path:
    """Score one feature-set x model combination via LOLO and write the predictions.

    Skips the run and returns the existing path if the output is already there,
    unless ``force``. ``shop_test`` requires a residualising feature set (R9):
    it feeds the held-out load's reference rows to the residual step only.
    """
    out_path = output_dir / _ablation_name(feature_set, model, shop_test, fold)
    if out_path.exists() and not force:
        return out_path

    spec = features.FEATURE_SETS[feature_set]
    columns = spec.columns(df)

    def factory() -> Pipeline:
        return features.build_pipeline(feature_set, MODEL_FACTORIES[model]())

    extra_healthy = None
    if shop_test:
        if not spec.residuals:
            raise ValueError(f"--shop-test needs a residualising feature set, got {feature_set!r}")

        def extra_healthy(held_out_bin: object) -> pd.DataFrame:
            return _extra_healthy(df, held_out_bin)

    predictions = evaluate.lolo_predict(
        factory,
        df,
        columns,
        extra_healthy=extra_healthy,
        only_folds=None if fold is None else [fold],
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_parquet(out_path)
    return out_path


def _ablation_name(feature_set: str, model: str, shop_test: bool, fold: int | None) -> str:
    suffix = "_shop_test" if shop_test else ""
    fold_part = "" if fold is None else f"_fold{fold}"
    return f"ablation_{feature_set}_{model}{suffix}{fold_part}.parquet"


def run_pruning(
    df: pd.DataFrame,
    feature_set: str,
    model: str,
    fold: int,
    *,
    force: bool = False,
    output_dir: Path = paths.PROCESSED / "experiments",
) -> Path:
    """Prune ``feature_set``'s columns inside one outer LOLO fold's training set only
    (correlation, then grouped permutation importance on inner folds; R13), then score
    the pruned set on that outer fold. Writes predictions plus the dropped-feature list.
    """
    out_path = output_dir / _pruning_name(feature_set, model, fold)
    if out_path.exists() and not force:
        return out_path

    spec = features.FEATURE_SETS[feature_set]
    all_columns = spec.columns(df)
    train_df = df[df["load_bin"] != fold]
    healthy = train_df[train_df["label"] == "Normal"]
    # The residual model's inputs (speed, brake load, fuel flow) are never pruned: residual
    # feature sets need them, and they tell every model the operating point.
    protected = [c for c in all_columns if c in features.RESIDUAL_INPUTS]
    corr_kept = features.prune_correlated(healthy, all_columns)
    corr_kept = protected + [c for c in corr_kept if c not in protected]

    def factory() -> Pipeline:
        return features.build_pipeline(feature_set, MODEL_FACTORIES[model]())

    importance = features.inner_permutation_importance(factory, train_df, corr_kept)
    mean_importance = importance.groupby("feature")["importance"].mean()
    pruned_columns = [c for c in corr_kept if c in protected or mean_importance.get(c, 0.0) > 0]
    dropped = sorted(set(all_columns) - set(pruned_columns))

    predictions = evaluate.lolo_predict(factory, df, pruned_columns, only_folds=[fold])
    predictions["dropped_feature"] = ",".join(dropped)

    output_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_parquet(out_path)
    return out_path


def _pruning_name(feature_set: str, model: str, fold: int) -> str:
    return f"pruning_{feature_set}_{model}_fold{fold}.parquet"


def load_pruning(
    feature_set: str,
    model: str,
    output_dir: Path = paths.PROCESSED / "experiments",
) -> pd.DataFrame | None:
    """Pruning predictions stitched over every outer fold, or None unless all are cached."""
    parts = [output_dir / _pruning_name(feature_set, model, fold) for fold in splits.LOAD_BINS]
    if not all(part.exists() for part in parts):
        return None
    return pd.concat(pd.read_parquet(part) for part in parts).sort_index()


def load_ablation(
    feature_set: str,
    model: str,
    *,
    shop_test: bool = False,
    output_dir: Path = paths.PROCESSED / "experiments",
) -> pd.DataFrame | None:
    """Predictions for one ablation arm: the whole-run file if present, else the per-fold
    files stitched together. Returns None unless every load bin is covered."""
    whole = output_dir / _ablation_name(feature_set, model, shop_test, None)
    if whole.exists():
        return pd.read_parquet(whole)
    parts = [
        output_dir / _ablation_name(feature_set, model, shop_test, fold)
        for fold in splits.LOAD_BINS
    ]
    if not all(part.exists() for part in parts):
        return None
    return pd.concat(pd.read_parquet(part) for part in parts).sort_index()


def _tuning_path(model: str, fold: object, output_dir: Path) -> Path:
    return output_dir / f"{model}_fold{fold}.json"


def run_tuning(
    df: pd.DataFrame,
    model: str,
    fold: int,
    *,
    n_trials: int = 30,
    timeout_s: float | None = 420,
    force: bool = False,
    output_dir: Path = paths.MODELS / "tuning",
) -> Path:
    """Tune ``model`` on the outer training rows for one held-out load (R4)."""
    out_path = _tuning_path(model, fold, output_dir)
    if out_path.exists() and not force:
        return out_path

    train_df = df[df["load_bin"] != fold]
    columns = features.FEATURE_SETS[MODELLING_FEATURE_SET].columns(df)
    best_params, trials = tuning.tune(
        model, train_df, columns, n_trials=n_trials, timeout_s=timeout_s
    )
    payload = {
        "model": model,
        "fold": fold,
        "best_params": best_params,
        "best_inner_score": float(trials["value"].max()),
        "n_trials": int(len(trials)),
        "git_commit": evaluate.git_commit(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2))
    return out_path


def load_tuned_params(model: str, fold: object, output_dir: Path = paths.MODELS / "tuning") -> dict:
    """Best params tuned for ``model`` on the fold held out of training, per R4's JSON."""
    return json.loads(_tuning_path(model, fold, output_dir).read_text())["best_params"]


def run_modelling(
    df: pd.DataFrame,
    model: str,
    *,
    force: bool = False,
    tuning_dir: Path = paths.MODELS / "tuning",
    output_dir: Path = paths.PROCESSED / "experiments",
    results_dir: Path = paths.RESULTS,
) -> Path:
    """Refit ``model`` per outer fold with that fold's tuned params, predicting the
    held-out rows (R5). Every outer fold's tuned-params JSON must already exist."""
    out_path = output_dir / f"modelling_{model}.parquet"
    if out_path.exists() and not force:
        return out_path

    columns = features.FEATURE_SETS[MODELLING_FEATURE_SET].columns(df)
    parts = []
    for fold in splits.LOAD_BINS:
        params = load_tuned_params(model, fold, tuning_dir)

        def factory(params=params) -> object:
            return tuning.MODEL_BUILDERS[model](params)

        parts.append(evaluate.lolo_predict(factory, df, columns, only_folds=[fold]))

    predictions = pd.concat(parts).loc[df.index]
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_parquet(out_path)
    _log_modelling_summary(model, predictions, results_dir)
    return out_path


def _log_modelling_summary(
    model: str, predictions: pd.DataFrame, results_dir: Path = paths.RESULTS
) -> None:
    """Merge ``model``'s summary into ``reports/results/04_models.csv`` (R5).

    Each CLI invocation tunes/fits one model, so the row for that model is replaced
    in place rather than the whole file, keeping earlier models' rows.
    """
    summary = evaluate.summarise(predictions)
    summary.insert(0, "model", model)
    results_path = results_dir / "04_models.csv"
    if results_path.exists():
        existing = pd.read_csv(results_path)
        existing = existing[existing["model"] != model]
        summary = pd.concat([existing.drop(columns=["experiment", "date", "git_commit"]), summary])
    evaluate.log_results("04_models", summary, results_dir=results_dir)


def _stratified_sample(labels: pd.Series, n: int, seed: int) -> pd.Index:
    """Up to ``n`` of ``labels``' index, sampled proportionally per class."""
    if len(labels) <= n:
        return labels.index
    rng = np.random.default_rng(seed)
    frac = n / len(labels)
    parts = []
    for _, group in labels.groupby(labels):
        take = min(len(group), max(1, round(len(group) * frac)))
        parts.append(rng.choice(group.index.to_numpy(), size=take, replace=False))
    return pd.Index(np.concatenate(parts)).unique()


def _switch_on_window_rows(df: pd.DataFrame, test_index: pd.Index, window_s: float) -> pd.Index:
    """``test_index`` rows within ``window_s`` seconds of their run's switch-on time,
    where switch-on is the first non-``Normal`` row of the run anywhere in ``df``."""
    switch_t = df.loc[df["label"] != "Normal"].groupby("run")["t"].min()
    test_df = df.loc[test_index, ["run", "t"]].join(switch_t.rename("t_switch"), on="run")
    test_df = test_df.dropna(subset=["t_switch"])
    within = test_df[(test_df["t"] - test_df["t_switch"]).abs() <= window_s]
    return within.index


def run_shap(
    df: pd.DataFrame,
    fold: int,
    *,
    model: str = "xgboost",
    sample_size: int = 3000,
    window_s: float = 600.0,
    force: bool = False,
    tuning_dir: Path = paths.MODELS / "tuning",
    output_dir: Path = paths.PROCESSED / "experiments",
) -> Path:
    """SHAP TreeExplainer values for ``model`` refit on ``fold``'s training rows (R3).

    Scores a seeded, label-stratified sample of up to ``sample_size`` held-out rows,
    plus every held-out row within ``window_s`` seconds of a switch-on in that fold.
    Writes row metadata to ``shap_fold<fold>.parquet`` and the SHAP arrays (values,
    base values, classes, row index) to ``shap_fold<fold>.npz`` alongside it.
    """
    out_path = output_dir / f"shap_fold{fold}.parquet"
    npz_path = output_dir / f"shap_fold{fold}.npz"
    if out_path.exists() and npz_path.exists() and not force:
        return out_path

    columns = features.FEATURE_SETS[MODELLING_FEATURE_SET].columns(df)
    params = load_tuned_params(model, fold, tuning_dir)
    train_df = df[df["load_bin"] != fold]
    test_index = df.index[df["load_bin"] == fold]

    fitted = cast(tuning._BalancedXGBClassifier, tuning.MODEL_BUILDERS[model](params))
    fitted.fit(train_df[columns], train_df["label"])

    sampled = _stratified_sample(df.loc[test_index, "label"], sample_size, SEED)
    switch_on = _switch_on_window_rows(df, test_index, window_s)
    selected = sampled.union(switch_on)

    X = df.loc[selected, columns]
    explanation = shap.TreeExplainer(fitted.model_)(X)

    metadata = pd.DataFrame(
        {
            "run": df.loc[selected, "run"],
            "load_bin": df.loc[selected, "load_bin"],
            "t": df.loc[selected, "t"],
            "y_true": df.loc[selected, "label"],
            "y_pred": fitted.predict(X),
        },
        index=selected,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    np.savez(
        npz_path,
        shap_values=explanation.values,
        base_values=explanation.base_values,
        classes=np.asarray(fitted.classes_),
        row_index=selected.to_numpy(),
    )
    metadata.to_parquet(out_path)
    return out_path


def run_crosscheck(
    df: pd.DataFrame,
    *,
    model: str = "xgboost",
    force: bool = False,
    tuning_dir: Path = paths.MODELS / "tuning",
    shap_dir: Path = paths.PROCESSED / "experiments",
    results_dir: Path = paths.RESULTS,
) -> Path:
    """Grouped permutation importance vs. the SHAP ranking, per outer fold (R7).

    Each fold's SHAP output (`run_shap`) must already exist. Refits ``model`` on that
    fold's training rows, then runs `features.outer_permutation_importance` on the exact
    rows `run_shap` scored, and rank-correlates it (Spearman) against those rows'
    mean total |SHAP| per source group.
    """
    out_path = results_dir / "06_crosscheck.csv"
    if out_path.exists() and not force:
        return out_path

    columns = features.FEATURE_SETS[MODELLING_FEATURE_SET].columns(df)
    groups = features.group_columns_by_source(columns)

    rows = []
    for fold in splits.LOAD_BINS:
        npz = np.load(shap_dir / f"shap_fold{fold}.npz", allow_pickle=True)
        selected = pd.Index(npz["row_index"])

        params = load_tuned_params(model, fold, tuning_dir)
        train_df = df[df["load_bin"] != fold]
        fitted = cast(tuning._BalancedXGBClassifier, tuning.MODEL_BUILDERS[model](params))
        fitted.fit(train_df[columns], train_df["label"])

        X_test = df.loc[selected, columns]
        y_test = df.loc[selected, "label"]
        perm_importance = features.outer_permutation_importance(
            fitted, X_test, y_test, columns, random_state=SEED
        )

        per_feature_shap = pd.Series(
            np.abs(npz["shap_values"]).sum(axis=-1).mean(axis=0), index=columns
        )
        shap_importance = pd.Series(
            {group: per_feature_shap[cols].sum() for group, cols in groups.items()}
        )

        common = perm_importance.index
        rho = perm_importance.corr(shap_importance.reindex(common), method="spearman")
        rows.append({"fold": fold, "n_groups": len(common), "spearman_r": rho})

    table = pd.DataFrame(rows)
    evaluate.log_results("06_crosscheck", table, results_dir=results_dir)
    return out_path


def run_alarm(
    df: pd.DataFrame,
    model: str,
    *,
    force: bool = False,
    tuning_dir: Path = paths.MODELS / "tuning",
    modelling_dir: Path = paths.PROCESSED / "experiments",
    results_dir: Path = paths.RESULTS,
) -> Path:
    """Alarm params chosen per outer fold from that fold's inner-fold predictions only,
    then scored on the fold's held-out predictions (R10). ``model`` must already have
    tuned params (``run_tuning``) and modelling predictions (``run_modelling``)."""
    out_path = results_dir / "04_alarms.csv"
    if out_path.exists() and not force and model in pd.read_csv(out_path)["model"].unique():
        return out_path

    columns = features.FEATURE_SETS[MODELLING_FEATURE_SET].columns(df)
    outer_predictions = pd.read_parquet(modelling_dir / f"modelling_{model}.parquet")

    fold_tables = []
    for fold in splits.LOAD_BINS:
        train_df = df[df["load_bin"] != fold]
        params = load_tuned_params(model, fold, tuning_dir)

        def factory(params=params) -> object:
            return tuning.MODEL_BUILDERS[model](params)

        inner_predictions = evaluate.lolo_predict(factory, train_df, columns)
        inner_predictions = inner_predictions.assign(t=train_df.loc[inner_predictions.index, "t"])
        inner_switch_on = audit.switch_on_points(train_df)
        chosen = alarm.choose_alarm_params(inner_predictions, inner_switch_on)

        fold_predictions = outer_predictions.loc[outer_predictions["fold"] == fold].copy()
        fold_predictions["t"] = df.loc[fold_predictions.index, "t"]
        fold_switch_on = audit.switch_on_points(df.loc[fold_predictions.index])
        alarms = fold_predictions.assign(
            alarm=alarm.sustained_alarm(
                fold_predictions, chosen["min_duration_s"], chosen["min_probability"]
            )
        )
        metrics = alarm.alarm_metrics(alarms, fold_switch_on)
        delays = alarm.detection_delay(alarms, fold_switch_on)
        delays["model"] = model
        delays["fold"] = fold
        delays["min_duration_s"] = chosen["min_duration_s"]
        delays["min_probability"] = chosen["min_probability"]
        delays["false_alarm_rate"] = metrics["false_alarm_rate"]
        fold_tables.append(delays)

    summary = pd.concat(fold_tables, ignore_index=True)
    _log_alarm_summary(model, summary, out_path)
    return out_path


ECE_RECALIBRATION_THRESHOLD = 0.05


def _proba_columns(predictions: pd.DataFrame) -> tuple[list[str], list[str]]:
    columns = [c for c in predictions.columns if c.startswith("proba_")]
    return columns, [c.removeprefix("proba_") for c in columns]


def run_calibration(
    df: pd.DataFrame,
    fold: int,
    model: str = "xgboost",
    *,
    force: bool = False,
    tuning_dir: Path = paths.MODELS / "tuning",
    modelling_dir: Path = paths.PROCESSED / "experiments",
    results_dir: Path = paths.RESULTS,
    inner_predict: Callable[..., pd.DataFrame] = evaluate.lolo_predict,
    fit: Callable[..., Any] | None = None,
) -> Path:
    """ECE and macro F1 before/after recalibrating one outer fold (R3).

    Recalibration happens only if the pooled ECE over every outer fold exceeds 0.05.
    The calibrator is fitted on the outer training rows' inner-fold predictions
    (``train_df`` excludes the fold), never on the fold's own rows.
    """
    out_path = results_dir / "07_calibration.csv"
    if out_path.exists() and not force and fold in pd.read_csv(out_path)["fold"].unique():
        return out_path

    fit = fit or calibration.fit_calibrator
    outer = pd.read_parquet(modelling_dir / f"modelling_{model}.parquet")
    proba_columns, classes = _proba_columns(outer)
    pooled_ece = calibration.expected_calibration_error(
        outer["y_true"], outer[proba_columns].to_numpy(), classes
    )
    held_out = outer[outer["fold"] == fold]
    proba = held_out[proba_columns].to_numpy()
    ece_before = calibration.expected_calibration_error(held_out["y_true"], proba, classes)
    f1_before = evaluate.macro_f1(held_out["y_true"], held_out["y_pred"])

    row: dict[str, object] = {
        "model": model,
        "fold": fold,
        "pooled_ece_before": pooled_ece,
        "recalibrated": pooled_ece > ECE_RECALIBRATION_THRESHOLD,
        "temperature": 1.0,
        "ece_before": ece_before,
        "ece_after": ece_before,
        "macro_f1_before": f1_before,
        "macro_f1_after": f1_before,
    }
    if row["recalibrated"]:
        columns = features.FEATURE_SETS[MODELLING_FEATURE_SET].columns(df)
        train_df = df[df["load_bin"] != fold]
        params = load_tuned_params(model, fold, tuning_dir)
        inner = inner_predict(lambda: tuning.MODEL_BUILDERS[model](params), train_df, columns)
        inner_columns, inner_classes = _proba_columns(inner)
        calibrator = fit(inner["y_true"], inner[inner_columns].to_numpy(), inner_classes)
        recalibrated = calibrator.transform(proba)
        after_pred = pd.Series(
            np.asarray(classes)[recalibrated.argmax(axis=1)], index=held_out.index
        )
        row["temperature"] = calibrator.temperature
        row["ece_after"] = calibration.expected_calibration_error(
            held_out["y_true"], recalibrated, classes
        )
        row["macro_f1_after"] = evaluate.macro_f1(held_out["y_true"], after_pred)

    summary = pd.DataFrame([row])
    if out_path.exists():
        existing = pd.read_csv(out_path)
        existing = existing[existing["fold"] != fold]
        summary = pd.concat([existing.drop(columns=["experiment", "date", "git_commit"]), summary])
    evaluate.log_results("07_calibration", summary.sort_values("fold"), results_dir=results_dir)
    return out_path


def run_sensitivity(
    df: pd.DataFrame,
    fold: int,
    model: str = "xgboost",
    *,
    force: bool = False,
    tuning_dir: Path = paths.MODELS / "tuning",
    modelling_dir: Path = paths.PROCESSED / "experiments",
    results_dir: Path = paths.RESULTS,
) -> Path:
    """Re-score ``model`` on one held-out load without day-dependent channels (R4b).

    Same tuned params and training rows as the headline; only the columns differ. Writes
    headline vs no-day-channel macro F1 and per-class recall to ``07_sensitivity.csv``.
    """
    out_path = results_dir / "07_sensitivity.csv"
    if out_path.exists() and not force and fold in pd.read_csv(out_path)["fold"].unique():
        return out_path

    all_columns = features.FEATURE_SETS[MODELLING_FEATURE_SET].columns(df)
    columns = features.without_day_channels(all_columns)
    params = load_tuned_params(model, fold, tuning_dir)
    reduced = evaluate.lolo_predict(
        lambda: tuning.MODEL_BUILDERS[model](params), df, columns, only_folds=[fold]
    )
    headline = pd.read_parquet(modelling_dir / f"modelling_{model}.parquet")
    headline = headline[headline["fold"] == fold]
    reduced = reduced[reduced["fold"] == fold]

    recall_head = evaluate.per_class_recall(headline["y_true"], headline["y_pred"])
    recall_red = evaluate.per_class_recall(reduced["y_true"], reduced["y_pred"])
    scores = {
        "macro_f1": (
            evaluate.macro_f1(headline["y_true"], headline["y_pred"]),
            evaluate.macro_f1(reduced["y_true"], reduced["y_pred"]),
        ),
        **{
            f"recall_{cls}": (recall_head[cls], recall_red.get(cls, float("nan")))
            for cls in recall_head.index
        },
    }
    summary = pd.DataFrame(
        {
            "model": model,
            "fold": fold,
            "metric": metric,
            "headline": head,
            "no_day_channels": red,
            "n_features_dropped": len(all_columns) - len(columns),
        }
        for metric, (head, red) in scores.items()
    )
    if out_path.exists():
        existing = pd.read_csv(out_path)
        existing = existing[existing["fold"] != fold]
        summary = pd.concat([existing.drop(columns=["experiment", "date", "git_commit"]), summary])
    evaluate.log_results(
        "07_sensitivity", summary.sort_values("fold", kind="stable"), results_dir=results_dir
    )
    return out_path


def _log_alarm_summary(model: str, summary: pd.DataFrame, out_path: Path) -> None:
    """Merge ``model``'s per-run alarm rows into ``reports/results/04_alarms.csv`` (R10).

    Each CLI invocation scores one model, so that model's rows are replaced in place,
    keeping earlier models' rows (mirrors ``_log_modelling_summary``).
    """
    if out_path.exists():
        existing = pd.read_csv(out_path)
        existing = existing[existing["model"] != model]
        summary = pd.concat([existing.drop(columns=["experiment", "date", "git_commit"]), summary])
    evaluate.log_results("04_alarms", summary, results_dir=out_path.parent)


def run_anomaly(
    df: pd.DataFrame,
    detector: str,
    fold: int,
    *,
    inputs: str = "raw",
    force: bool = False,
    output_dir: Path = paths.PROCESSED / "experiments",
    results_dir: Path = paths.RESULTS,
) -> Path:
    """Fit one healthy-only detector on the training loads' Normal rows and score the
    held-out load, including its fault rows (R3-R5). ``inputs`` selects the arm
    (``raw`` or ``residual``, R1b/ADR 0008); the residual view is fitted once on the
    training fold before scoring either the thinned fit rows or the held-out fold."""
    suffix = "" if inputs == "raw" else f"_{inputs}"
    out_path = output_dir / f"anomaly_{detector}{suffix}_fold{fold}.parquet"
    if out_path.exists() and not force:
        return out_path

    _, fit_view = anomaly.detector_inputs(df, inputs)
    train_df = df[df["load_bin"] != fold]
    healthy = train_df[train_df["label"] == "Normal"]
    thinned = healthy.groupby("run", group_keys=False).apply(lambda g: g.iloc[::2])
    view = fit_view(train_df, train_df["label"])

    model = DETECTOR_FACTORIES[detector]().fit(view(thinned))

    test_index = df.index[df["load_bin"] == fold]
    X_test = view(df.loc[test_index])
    result = pd.DataFrame(
        {
            "run": df.loc[test_index, "run"],
            "load_bin": df.loc[test_index, "load_bin"],
            "label": df.loc[test_index, "label"],
            "t": df.loc[test_index, "t"],
        },
        index=test_index,
    )
    if detector == "pca":
        parts = model.score_parts(X_test)
        result["score"] = parts["score"]
        result["t2"] = parts["t2"]
        result["q"] = parts["q"]
    else:
        result["score"] = model.score(X_test)

    output_dir.mkdir(parents=True, exist_ok=True)
    result.to_parquet(out_path)
    _log_anomaly_summary(detector, inputs, output_dir, results_dir)
    return out_path


def run_anomaly_alarms(
    df: pd.DataFrame,
    detector: str,
    *,
    inputs: str = "raw",
    far: float = 0.02,
    force: bool = False,
    output_dir: Path = paths.PROCESSED / "experiments",
    results_dir: Path = paths.RESULTS,
) -> Path:
    """Threshold ``detector`` on the ``inputs`` arm (``raw`` or ``residual``, R1b/ADR 0008)
    at a 2% false alarm rate on each fold's training healthy rows (R6), pick a
    sustained-alarm duration from the training fold's own runs at a 2% alarm-level
    false alarm budget, then score detection delay and false alarm rate on the
    held-out fold. Requires that fold's ``run_anomaly`` score file to exist."""
    out_path = results_dir / "05_alarms.csv"
    if out_path.exists() and not force:
        existing = pd.read_csv(out_path)
        if ((existing["detector"] == detector) & (existing["inputs"] == inputs)).any():
            return out_path

    suffix = "" if inputs == "raw" else f"_{inputs}"
    _, fit_view = anomaly.detector_inputs(df, inputs)
    fold_tables = []
    for fold in splits.LOAD_BINS:
        train_df = df[df["load_bin"] != fold]
        healthy = train_df[train_df["label"] == "Normal"]
        thinned = healthy.groupby("run", group_keys=False).apply(lambda g: g.iloc[::2])
        view = fit_view(train_df, train_df["label"])
        model = DETECTOR_FACTORIES[detector]().fit(view(thinned))

        threshold = anomaly.threshold_for_far(model.score(view(healthy)), far)

        train_scores = model.score(view(train_df))
        train_predictions = pd.DataFrame(
            {
                "run": train_df["run"],
                "t": train_df["t"],
                "y_pred": np.where(train_scores >= threshold, "Anomaly", "Normal"),
                "y_true": train_df["label"],
                "proba_Anomaly": 1.0,
            },
            index=train_df.index,
        )
        train_switch_on = audit.switch_on_points(train_df)
        chosen = alarm.choose_alarm_params(train_predictions, train_switch_on)

        test_scores = pd.read_parquet(output_dir / f"anomaly_{detector}{suffix}_fold{fold}.parquet")
        test_alarms = test_scores.assign(
            y_pred=np.where(test_scores["score"] >= threshold, "Anomaly", "Normal"),
            proba_Anomaly=1.0,
            y_true=test_scores["label"],
        )
        test_alarms["alarm"] = alarm.sustained_alarm(test_alarms, chosen["min_duration_s"], 0.5)
        test_switch_on = audit.switch_on_points(df.loc[test_scores.index])
        metrics = alarm.alarm_metrics(test_alarms, test_switch_on)
        delays = alarm.detection_delay(test_alarms, test_switch_on)
        delays["fold"] = fold
        delays["threshold"] = threshold
        delays["min_duration_s"] = chosen["min_duration_s"]
        delays["false_alarm_rate"] = metrics["false_alarm_rate"]
        fold_tables.append(delays)

    summary = pd.concat(fold_tables, ignore_index=True)
    summary.insert(0, "inputs", inputs)
    summary.insert(0, "detector", detector)
    _log_anomaly_alarm_summary(detector, inputs, summary, out_path)
    return out_path


def _log_anomaly_alarm_summary(
    detector: str, inputs: str, summary: pd.DataFrame, out_path: Path
) -> None:
    """Merge ``detector``/``inputs``' per-run alarm rows into ``reports/results/05_alarms.csv``
    (R6), keeping other detectors' and arms' rows (mirrors ``_log_alarm_summary``)."""
    if out_path.exists():
        existing = pd.read_csv(out_path)
        existing = existing[~((existing["detector"] == detector) & (existing["inputs"] == inputs))]
        summary = pd.concat([existing.drop(columns=["experiment", "date", "git_commit"]), summary])
    evaluate.log_results("05_alarms", summary, results_dir=out_path.parent)


def _anomaly_auroc(labels: pd.Series, scores: pd.Series) -> float:
    y = (labels != "Normal").astype(int)
    if y.nunique() < 2:
        return float("nan")
    return float(roc_auc_score(y, scores))


def _anomaly_per_class_auroc(labels: pd.Series, scores: pd.Series) -> dict[str, float]:
    result = {}
    for fault_class in FAULT_CLASSES:
        mask = labels.isin(["Normal", fault_class])
        y = labels[mask] == fault_class
        result[f"auroc_{fault_class}"] = (
            float(roc_auc_score(y, scores[mask])) if y.nunique() >= 2 else float("nan")
        )
    return result


def _anomaly_slice(fold: object, labels: pd.Series, scores: pd.Series) -> dict[str, object]:
    row = {"fold": fold, "auroc": _anomaly_auroc(labels, scores)}
    row.update(_anomaly_per_class_auroc(labels, scores))
    return row


def _log_anomaly_summary(
    detector: str, inputs: str, output_dir: Path, results_dir: Path = paths.RESULTS
) -> None:
    """Merge ``detector``'s AUROC summary for input arm ``inputs`` into
    ``reports/results/05_anomaly.csv`` (R5), once every held-out load's score file for
    that detector/arm pair exists."""
    suffix = "" if inputs == "raw" else f"_{inputs}"
    parts = [
        output_dir / f"anomaly_{detector}{suffix}_fold{fold}.parquet" for fold in splits.LOAD_BINS
    ]
    if not all(part.exists() for part in parts):
        return

    predictions = pd.concat(pd.read_parquet(part) for part in parts)
    rows = [_anomaly_slice("pooled", predictions["label"], predictions["score"])]
    for fold in sorted(predictions["load_bin"].unique()):
        mask = predictions["load_bin"] == fold
        rows.append(
            _anomaly_slice(fold, predictions.loc[mask, "label"], predictions.loc[mask, "score"])
        )
    summary = pd.DataFrame(rows)
    summary.insert(0, "inputs", inputs)
    summary.insert(0, "detector", detector)

    results_path = results_dir / "05_anomaly.csv"
    if results_path.exists():
        existing = pd.read_csv(results_path)
        if "inputs" not in existing.columns:
            existing["inputs"] = "raw"
        existing = existing[~((existing["detector"] == detector) & (existing["inputs"] == inputs))]
        summary = pd.concat([existing.drop(columns=["experiment", "date", "git_commit"]), summary])
    evaluate.log_results("05_anomaly", summary, results_dir=results_dir)


def load_modelling(
    model: str, output_dir: Path = paths.PROCESSED / "experiments"
) -> pd.DataFrame | None:
    """Modelling predictions for ``model``, or None unless the output exists."""
    out_path = output_dir / f"modelling_{model}.parquet"
    return pd.read_parquet(out_path) if out_path.exists() else None


def run_runs(
    model: str = "xgboost",
    *,
    force: bool = False,
    modelling_dir: Path = paths.PROCESSED / "experiments",
    results_dir: Path = paths.RESULTS,
) -> Path:
    """Per-run error table for ``model`` (R4), from its saved LOLO predictions."""
    out_path = results_dir / "07_runs.csv"
    if out_path.exists() and not force:
        return out_path
    predictions = pd.read_parquet(modelling_dir / f"modelling_{model}.parquet")
    predictions["t"] = pd.read_parquet(paths.PROCESSED / "clean.parquet", columns=["t"])["t"]
    switch_on = pd.read_csv(results_dir / "00_switch_on_points.csv")
    alarms = pd.read_csv(results_dir / "04_alarms.csv")
    table = evaluate.per_run_errors(predictions, switch_on, alarms[alarms["model"] == model])
    return evaluate.log_results("07_runs", table, results_dir=results_dir)


def run_lockbox(results_dir: Path = paths.RESULTS) -> Path:
    """The one lockbox evaluation (R6); a stored result is returned without refitting."""
    from keyframe import lockbox

    lockbox.evaluate_lockbox(force_first_run=True, results_dir=results_dir)
    return results_dir / "07_lockbox.csv"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m keyframe.experiments")
    subparsers = parser.add_subparsers(dest="experiment", required=True)

    ablation = subparsers.add_parser("ablation", help="Score one feature set x model combination.")
    ablation.add_argument("--feature-set", required=True, choices=sorted(features.FEATURE_SETS))
    ablation.add_argument("--model", required=True, choices=sorted(MODEL_FACTORIES))
    ablation.add_argument("--shop-test", action="store_true")
    ablation.add_argument("--force", action="store_true")
    ablation.add_argument(
        "--fold", type=int, choices=splits.LOAD_BINS, help="run one held-out load only"
    )

    pruning = subparsers.add_parser(
        "pruning", help="Prune one feature set inside a training fold, then score it."
    )
    pruning.add_argument("--feature-set", required=True, choices=sorted(features.FEATURE_SETS))
    pruning.add_argument("--model", required=True, choices=sorted(MODEL_FACTORIES))
    pruning.add_argument("--fold", type=int, required=True, choices=splits.LOAD_BINS)
    pruning.add_argument("--force", action="store_true")

    tuning_parser = subparsers.add_parser(
        "tuning", help="Tune one model's hyperparameters for one outer held-out load."
    )
    tuning_parser.add_argument("--model", required=True, choices=sorted(tuning.MODEL_BUILDERS))
    tuning_parser.add_argument("--outer-fold", type=int, required=True, choices=splits.LOAD_BINS)
    tuning_parser.add_argument("--n-trials", type=int, default=30)
    tuning_parser.add_argument("--timeout-s", type=float, default=420)
    tuning_parser.add_argument("--force", action="store_true")

    modelling = subparsers.add_parser(
        "modelling", help="Refit one model per outer fold with its tuned params."
    )
    modelling.add_argument("--model", required=True, choices=sorted(tuning.MODEL_BUILDERS))
    modelling.add_argument("--force", action="store_true")

    alarm_parser = subparsers.add_parser(
        "alarm", help="Choose alarm params per outer fold from its inner folds, then score them."
    )
    alarm_parser.add_argument("--model", required=True, choices=sorted(tuning.MODEL_BUILDERS))
    alarm_parser.add_argument("--force", action="store_true")

    anomaly_parser = subparsers.add_parser(
        "anomaly", help="Score one healthy-only detector for one held-out load."
    )
    anomaly_parser.add_argument("--detector", required=True, choices=sorted(DETECTOR_FACTORIES))
    anomaly_parser.add_argument("--fold", type=int, required=True, choices=splits.LOAD_BINS)
    anomaly_parser.add_argument("--inputs", choices=["raw", "residual"], default="raw")
    anomaly_parser.add_argument("--force", action="store_true")

    calibration_parser = subparsers.add_parser(
        "calibration", help="ECE and macro F1 before/after recalibrating one outer fold."
    )
    calibration_parser.add_argument("--fold", type=int, required=True, choices=splits.LOAD_BINS)
    calibration_parser.add_argument("--force", action="store_true")

    subparsers.add_parser("lockbox", help="Score the lockbox run once (refuses to run twice).")

    runs_parser = subparsers.add_parser("runs", help="Per-run error table for XGBoost.")
    runs_parser.add_argument("--force", action="store_true")

    sensitivity_parser = subparsers.add_parser(
        "sensitivity", help="Best model on one held-out load without day-dependent channels."
    )
    sensitivity_parser.add_argument("--fold", type=int, required=True, choices=splits.LOAD_BINS)
    sensitivity_parser.add_argument("--force", action="store_true")

    shap_parser = subparsers.add_parser(
        "shap", help="SHAP TreeExplainer values for the best model on one held-out load."
    )
    shap_parser.add_argument("--fold", type=int, required=True, choices=splits.LOAD_BINS)
    shap_parser.add_argument("--force", action="store_true")

    crosscheck_parser = subparsers.add_parser(
        "crosscheck", help="Permutation importance vs. SHAP ranking, per outer fold."
    )
    crosscheck_parser.add_argument(
        "--model", default="xgboost", choices=sorted(tuning.MODEL_BUILDERS)
    )
    crosscheck_parser.add_argument("--force", action="store_true")

    anomaly_alarm_parser = subparsers.add_parser(
        "anomaly-alarm", help="Threshold one detector and score its detection delay."
    )
    anomaly_alarm_parser.add_argument(
        "--detector", required=True, choices=sorted(DETECTOR_FACTORIES)
    )
    anomaly_alarm_parser.add_argument("--inputs", choices=["raw", "residual"], default="raw")
    anomaly_alarm_parser.add_argument("--force", action="store_true")

    args = parser.parse_args(argv)

    table = load_feature_table()
    if args.experiment == "ablation":
        out_path = run_ablation(
            table,
            args.feature_set,
            args.model,
            shop_test=args.shop_test,
            force=args.force,
            fold=args.fold,
        )
    elif args.experiment == "pruning":
        out_path = run_pruning(
            table,
            args.feature_set,
            args.model,
            args.fold,
            force=args.force,
        )
    elif args.experiment == "tuning":
        out_path = run_tuning(
            table,
            args.model,
            args.outer_fold,
            n_trials=args.n_trials,
            timeout_s=args.timeout_s,
            force=args.force,
        )
    elif args.experiment == "modelling":
        out_path = run_modelling(table, args.model, force=args.force)
    elif args.experiment == "alarm":
        out_path = run_alarm(table, args.model, force=args.force)
    elif args.experiment == "anomaly":
        out_path = run_anomaly(
            table, args.detector, args.fold, inputs=args.inputs, force=args.force
        )
    elif args.experiment == "calibration":
        out_path = run_calibration(table, args.fold, force=args.force)
    elif args.experiment == "lockbox":
        out_path = run_lockbox()
    elif args.experiment == "runs":
        out_path = run_runs(force=args.force)
    elif args.experiment == "sensitivity":
        out_path = run_sensitivity(table, args.fold, force=args.force)
    elif args.experiment == "shap":
        out_path = run_shap(table, args.fold, force=args.force)
    elif args.experiment == "crosscheck":
        out_path = run_crosscheck(table, model=args.model, force=args.force)
    else:
        out_path = run_anomaly_alarms(table, args.detector, inputs=args.inputs, force=args.force)
    print(out_path)


if __name__ == "__main__":
    main()
