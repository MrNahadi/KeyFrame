"""The lockbox: one two-hole injector run, scored once (R5).

This module and ``download.py`` are the only code that touches ``data/lockbox``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from keyframe import download, evaluate, experiments, features, load, paths, splits, tuning

MODEL = "xgboost"
INTEGER_PARAMS = ("n_estimators", "max_depth")
RESULT_NAME = "07_lockbox"


def median_params(model: str = MODEL, tuning_dir: Path = paths.MODELS / "tuning") -> dict:
    """Median of the per-fold tuned params; integer-valued params are rounded back to int."""
    per_fold = pd.DataFrame(
        [experiments.load_tuned_params(model, fold, tuning_dir) for fold in splits.LOAD_BINS]
    )
    medians = per_fold.median()
    return {
        name: int(round(value)) if name in INTEGER_PARAMS else float(value)
        for name, value in medians.items()
    }


def _summarise(labels: pd.Series, load_bins: pd.Series, timestamp: str) -> pd.DataFrame:
    classes = sorted(labels.unique())
    groups = [("all", np.nan, labels)]
    groups += [("load_bin", b, labels[load_bins == b]) for b in sorted(load_bins.unique())]
    rows = []
    for scope, bin_value, group in groups:
        counts = group.value_counts()
        for label in classes:
            rows.append(
                {
                    "scope": scope,
                    "load_bin": bin_value,
                    "label": label,
                    "n_rows": int(counts.get(label, 0)),
                    "share": counts.get(label, 0) / len(group),
                    "timestamp": timestamp,
                }
            )
    return pd.DataFrame(rows)


def evaluate_lockbox(
    force_first_run: bool = False,
    *,
    results_dir: Path = paths.RESULTS,
    tuning_dir: Path = paths.MODELS / "tuning",
) -> pd.DataFrame:
    """Score the lockbox run once and store it; afterwards only return the stored result.

    A stored ``07_lockbox.csv`` is returned untouched and nothing is fitted. When it is
    missing, the run happens only if ``force_first_run`` is True, so a casual call cannot
    spend the lockbox. The model is the best one (XGBoost) with the median of its per-fold
    tuned params, fitted on every row of the clean feature table (all loads).
    """
    out_path = results_dir / f"{RESULT_NAME}.csv"
    if out_path.exists():
        return pd.read_csv(out_path)
    if not force_first_run:
        raise RuntimeError(f"{out_path} is missing; pass force_first_run=True to spend the lockbox")

    train = experiments.load_feature_table()
    columns = features.FEATURE_SETS[experiments.MODELLING_FEATURE_SET].columns(train)
    model: Any = tuning.MODEL_BUILDERS[MODEL](median_params(MODEL, tuning_dir))
    model.fit(train[columns], train["label"])

    run = load.load_run(paths.LOCKBOX / download.LOCKBOX_FILE)
    table = features.build_feature_table(run)
    predicted = pd.Series(model.predict(table[columns]), index=table.index)

    timestamp = datetime.now(UTC).isoformat(timespec="seconds")
    summary = _summarise(predicted, table["load_bin"], timestamp)
    evaluate.log_results(RESULT_NAME, summary, results_dir=results_dir)
    return pd.read_csv(out_path)
