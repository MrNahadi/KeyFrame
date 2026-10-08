"""The calibrated track (feature 17, ADR 0014): readings relative to a known-healthy baseline.

A real installation can record its own engine running healthy at each operating point
(commissioning, after an overhaul). Here every run's first ``BASELINE_S`` seconds at a
load stand in for that record: ``cal_<column>`` is the reading minus its mean over the
baseline window of the same run and load segment. Rows are monitored only once their
baseline is complete, and a segment whose baseline window is not all healthy (the
injector run, faulty from its first reading) has no usable baseline and is left out,
because a calibrated system cannot detect a fault already present when it was calibrated.

Every fault run in the dataset switches on at least 28 minutes in, so a 20-minute
baseline never contains the fault.

Commands (each one fold, under 10 minutes):
``uv run python -m keyframe.calibrated inner --outer-fold K`` scores the arms on the inner
folds of K's training loads only; ``... examine --outer-fold K`` scores load K, once.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from keyframe import autoresearch, evaluate, features, paths, splits, tuning

BASELINE_S = 1200.0
"""The known-healthy stretch at the start of each run and load segment (20 minutes)."""
SEEDS: tuple[int, ...] = (42, 1, 2)
LOAD_INPUTS: tuple[str, ...] = features.RESIDUAL_INPUTS
"""Operating-point channels kept as absolute values in the calibrated arm (speed, brake
load, fuel flow): they say where the engine is running, not which session it is."""
ARMS: tuple[str, ...] = ("zero_shot", "calibrated", "raw+calibrated")


def segment_ids(table: pd.DataFrame) -> pd.Series:
    """``<run>#<n>`` per row: a new segment starts each time a run changes load bin."""
    out = pd.Series(index=table.index, dtype=object)
    for run, rows in table.groupby("run", sort=False):
        rows = rows.sort_values("t")
        changes = (rows["load_bin"] != rows["load_bin"].shift()).cumsum()
        out.loc[rows.index] = [f"{run}#{n}" for n in changes]
    return out


def _level_columns(table: pd.DataFrame) -> list[str]:
    """Columns whose level depends on the session: raw readings, physics features and
    their rolling means (rolling std and slope are already level-free)."""
    base = features.sensor_channels(table) + features._physics_columns(table)
    rolled = [c for c in table.columns if "_roll_" in c and c.endswith("_mean")]
    return [c for c in base + rolled if c not in features.EXCLUDED_COLUMNS]


def _source(column: str) -> str:
    return column.split("_roll_")[0] if "_roll_" in column else column


def add_calibrated(
    table: pd.DataFrame, baseline_s: float = BASELINE_S
) -> tuple[pd.DataFrame, pd.Series]:
    """``table`` plus ``cal_*`` columns, and a mask of rows that may be monitored.

    For each run and load segment, the baseline of a reading is its mean over the first
    ``baseline_s`` seconds; a rolling mean is compared with the baseline of the reading
    it averages. ``ready`` is true for rows after a complete, all-healthy baseline.
    Labels are used only to decide which segments have a healthy baseline, never as
    feature values.
    """
    levels = _level_columns(table)
    sources = sorted({_source(c) for c in levels})
    segments = segment_ids(table)
    ready = pd.Series(False, index=table.index)
    baselines = pd.DataFrame(np.nan, index=table.index, columns=sources)
    for _, rows in table.groupby(segments, sort=False):
        rows = rows.sort_values("t")
        since = rows["t"] - rows["t"].iloc[0]
        window = rows[since < baseline_s]
        if since.iloc[-1] < baseline_s or (window["label"] != "Normal").any():
            continue
        baselines.loc[rows.index, sources] = window[sources].mean().to_numpy()
        ready.loc[rows.index] = (since >= baseline_s).to_numpy()
    cal = pd.DataFrame(
        {f"cal_{c}": table[c] - baselines[_source(c)] for c in levels}, index=table.index
    )
    return pd.concat([table, cal], axis=1), ready


def arm_columns(table: pd.DataFrame, arm: str) -> list[str]:
    """Model inputs for one arm. ``zero_shot`` is v1's set; ``calibrated`` keeps only
    deviations from the baseline, level-free rolling stats and the operating point;
    ``raw+calibrated`` is v1's set plus the deviations."""
    cal = [c for c in table.columns if c.startswith("cal_")]
    v1 = [c for c in features.FEATURE_SETS["raw+physics+rolling"].columns(table) if c not in cal]
    if arm == "zero_shot":
        return v1
    if arm == "raw+calibrated":
        return v1 + cal
    if arm == "calibrated":
        level_free = [c for c in v1 if "_roll_" in c and not c.endswith("_mean")]
        return [*LOAD_INPUTS, *level_free, *cal]
    raise ValueError(f"unknown arm {arm!r}; expected one of {ARMS}")


def _model(params: dict, seed: int) -> Any:
    return tuning._BalancedXGBClassifier(random_state=seed, n_jobs=4, **params)


def _calibrated_table() -> tuple[pd.DataFrame, pd.Series]:
    from keyframe import experiments

    return add_calibrated(experiments.load_feature_table())


def inner_scores(
    outer_fold: int,
    *,
    table: pd.DataFrame | None = None,
    ready: pd.Series | None = None,
    params: dict | None = None,
    seeds: Sequence[int] = SEEDS,
    thin_step: int = autoresearch.THIN_STEP,
) -> pd.DataFrame:
    """Every arm on the inner folds of ``outer_fold``'s training loads, on the same rows:
    monitored rows of runs unseen in each inner fold's training loads. One row per arm."""
    if table is None or ready is None:
        table, ready = _calibrated_table()
    if params is None:
        from keyframe import experiments

        params = experiments.load_tuned_params("xgboost", outer_fold)
    dev = autoresearch.development_rows(table[ready], outer_fold)
    thinned = tuning.thin(dev, thin_step)
    rows = []
    for arm in ARMS:
        columns = arm_columns(thinned, arm)
        per_seed, recalls = [], []
        for seed in seeds:
            predictions = evaluate.lolo_predict(partial(_model, params, seed), thinned, columns)
            scored = predictions[autoresearch.unseen_run_mask(predictions, thinned)]
            per_seed.append(evaluate.macro_f1(scored["y_true"], scored["y_pred"]))
            recalls.append(evaluate.per_class_recall(scored["y_true"], scored["y_pred"]))
        recall = pd.concat(recalls, axis=1).mean(axis=1)
        rows.append(
            {
                "outer_fold": outer_fold,
                "arm": arm,
                "macro_f1": float(np.mean(per_seed)),
                "macro_f1_sd": float(np.std(per_seed, ddof=1)) if len(per_seed) > 1 else 0.0,
                "n_features": len(columns),
                **{f"recall_{c}": float(v) for c, v in recall.items()},
            }
        )
    return pd.DataFrame(rows)


def identifiability(outer_fold: int, arm: str, table: pd.DataFrame, ready: pd.Series) -> float:
    """Mean over training loads of how well ``arm``'s columns name the run from monitored
    healthy rows alone (ADR 0013 amendment 1's batch-effect test)."""
    rows = tuning.thin(autoresearch.development_rows(table[ready], outer_fold))
    scores = autoresearch.identify_runs(rows[rows["label"] == "Normal"], arm_columns(rows, arm))
    return float(np.mean(list(scores.values())))


def examine(
    outer_fold: int,
    *,
    table: pd.DataFrame | None = None,
    ready: pd.Series | None = None,
    params: dict | None = None,
    seeds: Sequence[int] = SEEDS,
    out_dir: Path = paths.REPORTS / "calibrated",
) -> dict[str, Any]:
    """Score every arm on held-out load ``outer_fold``, once (monitored rows of unseen runs).

    The primary arm for the fold is the one with the best inner score, chosen before this
    runs and stored with the result. Refuses to run twice for one fold.
    """
    out_path = out_dir / f"outer_fold{outer_fold}.json"
    if out_path.exists():
        raise RuntimeError(f"{out_path} exists: fold {outer_fold} has already been examined")
    if table is None or ready is None:
        table, ready = _calibrated_table()
    if params is None:
        from keyframe import experiments

        params = experiments.load_tuned_params("xgboost", outer_fold)
    inner_path = out_dir / f"inner_fold{outer_fold}.csv"
    inner = pd.read_csv(inner_path) if inner_path.exists() else None
    calibrated_arms = ["calibrated", "raw+calibrated"]
    primary = (
        str(inner[inner["arm"].isin(calibrated_arms)].sort_values("macro_f1").iloc[-1]["arm"])
        if inner is not None
        else None
    )
    monitored = table[ready]
    arms: dict[str, Any] = {}
    for arm in ARMS:
        columns = arm_columns(monitored, arm)
        per_seed = []
        for seed in seeds:
            predictions = evaluate.lolo_predict(
                partial(_model, params, seed), monitored, columns, only_folds=[outer_fold]
            )
            scored = predictions[autoresearch.unseen_run_mask(predictions, monitored)]
            per_seed.append({"seed": seed, **evaluate.summarise(scored).iloc[0].to_dict()})
        arms[arm] = {
            "macro_f1_mean": float(np.mean([r["macro_f1"] for r in per_seed])),
            "per_seed": per_seed,
        }
    result = {
        "outer_fold": outer_fold,
        "label": "calibrated track (feature 17), separately labelled; v1 locked results unchanged",
        "primary_arm": primary,
        "arms": arms,
        "git_commit": evaluate.git_commit(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=str) + "\n")
    return result


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m keyframe.calibrated")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("inner", "examine"):
        command = sub.add_parser(name)
        command.add_argument("--outer-fold", type=int, required=True, choices=splits.LOAD_BINS)
    args = parser.parse_args(argv)
    out_dir = paths.REPORTS / "calibrated"
    if args.command == "inner":
        table, ready = _calibrated_table()
        scores = inner_scores(args.outer_fold, table=table, ready=ready)
        scores["identify"] = [
            identifiability(args.outer_fold, arm, table, ready) for arm in scores["arm"]
        ]
        out_dir.mkdir(parents=True, exist_ok=True)
        scores.to_csv(out_dir / f"inner_fold{args.outer_fold}.csv", index=False)
        print(scores.to_string(index=False))
    else:
        print(json.dumps(examine(args.outer_fold), indent=2, default=str))


if __name__ == "__main__":
    main()
