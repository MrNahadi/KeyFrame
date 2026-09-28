"""Heavy experiments run outside the notebooks: ``uv run python -m keyframe.experiments <name> ...``.

Each experiment writes its per-row LOLO predictions to
``data/processed/experiments/<name>.parquet`` and skips work whose output already
exists, unless ``--force``. Notebooks read those outputs and summarise them.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import lightgbm as lgb
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler

from keyframe import SEED, evaluate, features, paths

MODEL_FACTORIES = {
    "logreg": lambda: make_pipeline(
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
    output_dir: Path = paths.PROCESSED / "experiments",
) -> Path:
    """Score one feature-set x model combination via LOLO and write the predictions.

    Skips the run and returns the existing path if the output is already there,
    unless ``force``. ``shop_test`` requires a residualising feature set (R9):
    it feeds the held-out load's reference rows to the residual step only.
    """
    suffix = "_shop_test" if shop_test else ""
    out_path = output_dir / f"ablation_{feature_set}_{model}{suffix}.parquet"
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

    predictions = evaluate.lolo_predict(factory, df, columns, extra_healthy=extra_healthy)
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_parquet(out_path)
    return out_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m keyframe.experiments")
    subparsers = parser.add_subparsers(dest="experiment", required=True)

    ablation = subparsers.add_parser("ablation", help="Score one feature set x model combination.")
    ablation.add_argument("--feature-set", required=True, choices=sorted(features.FEATURE_SETS))
    ablation.add_argument("--model", required=True, choices=sorted(MODEL_FACTORIES))
    ablation.add_argument("--shop-test", action="store_true")
    ablation.add_argument("--force", action="store_true")

    args = parser.parse_args(argv)

    table = load_feature_table()
    out_path = run_ablation(
        table, args.feature_set, args.model, shop_test=args.shop_test, force=args.force
    )
    print(out_path)


if __name__ == "__main__":
    main()
