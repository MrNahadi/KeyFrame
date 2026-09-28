"""Heavy experiments run outside the notebooks: ``uv run python -m keyframe.experiments <name> ...``.

Each experiment writes its per-row LOLO predictions to
``data/processed/experiments/<name>.parquet`` and skips work whose output already
exists, unless ``--force``. Notebooks read those outputs and summarise them.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import lightgbm as lgb
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler

from keyframe import SEED, evaluate, features, paths, splits, tuning

MODELLING_FEATURE_SET = "raw+physics+rolling"

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
    return out_path


def load_modelling(
    model: str, output_dir: Path = paths.PROCESSED / "experiments"
) -> pd.DataFrame | None:
    """Modelling predictions for ``model``, or None unless the output exists."""
    out_path = output_dir / f"modelling_{model}.parquet"
    return pd.read_parquet(out_path) if out_path.exists() else None


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
    else:
        out_path = run_modelling(table, args.model, force=args.force)
    print(out_path)


if __name__ == "__main__":
    main()
