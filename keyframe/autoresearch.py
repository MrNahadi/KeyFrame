"""The fixed harness for the autoresearch loop (feature 16, ADR 0013).

An agent edits only ``autoresearch/candidate.py``; this module scores it. The agent's
keep-or-discard signal is the *inner* leave-one-load-out macro F1 over the training
loads of one outer fold: the outer held-out load's rows are dropped before anything is
fitted or scored, so a search for outer fold k never sees how it does on load k. The
held-out load is scored once per search, by ``examine``, after the search has stopped.

Run ``uv run python -m keyframe.autoresearch score --outer-fold 75`` for the search score,
``... score --outer-fold 75 --no-day`` for the day-robust gate, and
``... examine --outer-fold 75`` exactly once at the end of a search.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import time
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np
import pandas as pd

from keyframe import evaluate, features, paths, splits, tuning

CANDIDATE = paths.ROOT / "autoresearch" / "candidate.py"
EXAM_DIR = paths.REPORTS / "autoresearch"
SEARCH_SEEDS: tuple[int, ...] = (42, 1, 2)
"""Every score is the mean over these seeds; one seed moves the inner score by about 0.012."""
THIN_STEP = 4
"""Search scores fit and score on every 4th row of each run, as the v1 tuning did (R3 of 06)."""
NEW_PREFIX = "cand_"
"""Columns the candidate adds must start with this, so the day filter and audits can find them."""

_FORBIDDEN_SOURCE = re.compile(
    r"read_parquet|read_csv|read_pickle|open\(|Path\(|paths\.|lockbox|load_bin|"
    r"\blabel\b|Anomaly State|subprocess|\bos\.|\bsys\.|importlib|__import__|eval\(|exec\("
)
"""Things candidate code has no business touching: files, labels, load bins, the shell."""


@dataclass(frozen=True)
class Score:
    """One search score: the mean and spread over seeds of inner-LOLO macro F1."""

    outer_fold: int
    no_day: bool
    macro_f1: float
    macro_f1_sd: float
    per_seed: tuple[float, ...]
    worst_recall: float
    worst_recall_class: str
    n_features: int
    seconds: float


class CandidateError(ValueError):
    """The candidate broke a harness rule; the experiment counts as a crash."""


def load_candidate(path: Path = CANDIDATE) -> ModuleType:
    """Import ``candidate.py`` after a static check that it reads no files and no labels."""
    source = path.read_text()
    match = _FORBIDDEN_SOURCE.search(source)
    if match:
        raise CandidateError(f"candidate.py uses a forbidden name: {match.group(0)!r}")
    spec = importlib.util.spec_from_file_location("autoresearch_candidate", path)
    if spec is None or spec.loader is None:
        raise CandidateError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("add_features", "select_columns", "build_model"):
        if not callable(getattr(module, name, None)):
            raise CandidateError(f"candidate.py must define {name}()")
    return module


def model_inputs(table: pd.DataFrame, no_day: bool) -> list[str]:
    """The columns a candidate may see: every model-safe column, minus day-dependent ones
    (and everything derived from them) when ``no_day``."""
    columns = features.raw_sensor_columns(table)
    return features.without_day_channels(columns) if no_day else columns


def candidate_table(candidate: ModuleType, table: pd.DataFrame, no_day: bool) -> pd.DataFrame:
    """``table`` plus the candidate's own features, computed run by run.

    Each call to ``add_features`` sees one run, in time order, with ``t`` and the allowed
    inputs only: no label, run name or load bin, and never another run's rows.
    """
    inputs = ["t", *model_inputs(table, no_day)]
    parts = []
    for _, run in table.groupby("run", sort=False):
        run = run.sort_values("t")
        added = candidate.add_features(run[inputs].copy())
        if added is None or added.empty:
            continue
        _check_added(added, run.index)
        parts.append(added)
    if not parts:
        return table
    return pd.concat([table, pd.concat(parts).loc[table.index]], axis=1)


def _check_added(added: pd.DataFrame, index: pd.Index) -> None:
    bad = [c for c in added.columns if not str(c).startswith(NEW_PREFIX)]
    if bad:
        raise CandidateError(f"new columns must start with {NEW_PREFIX!r}: {bad[:5]}")
    if not added.index.sort_values().equals(index.sort_values()):
        raise CandidateError("add_features must return one row per input row, same index")


def check_causal(candidate: ModuleType, table: pd.DataFrame, no_day: bool) -> None:
    """Fail if the candidate's features look ahead in time: features computed on the first
    part of a run must equal the same rows computed on the whole run."""
    inputs = ["t", *model_inputs(table, no_day)]
    sizes = table.groupby("run").size()
    run = table[table["run"] == sizes.idxmin()].sort_values("t")[inputs]
    full = candidate.add_features(run.copy())
    if full is None or full.empty:
        return
    for share in (0.3, 0.7):
        cut = int(len(run) * share)
        prefix = candidate.add_features(run.iloc[:cut].copy())
        left = full.loc[prefix.index, prefix.columns].to_numpy(dtype=float)
        right = prefix.to_numpy(dtype=float)
        if not np.allclose(left, right, equal_nan=True, rtol=1e-6, atol=1e-9):
            raise CandidateError("add_features looks ahead: a prefix of a run gives other values")


def select_checked(candidate: ModuleType, available: Sequence[str]) -> list[str]:
    """The candidate's chosen columns, refused if any is not an allowed input."""
    chosen = list(candidate.select_columns(list(available)))
    allowed = set(available)
    outside = [c for c in chosen if c not in allowed or c in features.EXCLUDED_COLUMNS]
    if outside:
        raise CandidateError(f"select_columns chose columns it may not use: {outside[:5]}")
    if not chosen:
        raise CandidateError("select_columns chose no columns")
    return chosen


def _available(base: pd.DataFrame, full: pd.DataFrame, no_day: bool) -> list[str]:
    """The allowed inputs plus every column the candidate added."""
    added = [str(c) for c in full.columns if str(c).startswith(NEW_PREFIX)]
    return [*model_inputs(base, no_day), *added]


def development_rows(table: pd.DataFrame, outer_fold: int) -> pd.DataFrame:
    """The rows a search for ``outer_fold`` may use: every load except the held-out one."""
    if outer_fold not in splits.LOAD_BINS:
        raise ValueError(f"outer fold must be one of {splits.LOAD_BINS}, got {outer_fold}")
    return table[table["load_bin"] != outer_fold]


def search_score(
    outer_fold: int,
    *,
    no_day: bool = False,
    seeds: Sequence[int] = SEARCH_SEEDS,
    thin_step: int = THIN_STEP,
    candidate: ModuleType | None = None,
    table: pd.DataFrame | None = None,
) -> Score:
    """Mean inner-LOLO macro F1 over ``seeds`` on the training loads of ``outer_fold``."""
    started = time.monotonic()
    candidate = candidate or load_candidate()
    base = table if table is not None else _feature_table()
    check_causal(candidate, base, no_day)
    full = candidate_table(candidate, base, no_day)
    dev = development_rows(full, outer_fold)
    available = _available(base, full, no_day)
    columns = select_checked(candidate, available)
    thinned = tuning.thin(dev, thin_step)

    per_seed: list[float] = []
    pooled: list[pd.DataFrame] = []
    for seed in seeds:
        predictions = evaluate.lolo_predict(partial(candidate.build_model, seed), thinned, columns)
        per_seed.append(evaluate.macro_f1(predictions["y_true"], predictions["y_pred"]))
        pooled.append(predictions)
    everything = pd.concat(pooled)
    recall = evaluate.per_class_recall(everything["y_true"], everything["y_pred"])
    return Score(
        outer_fold=outer_fold,
        no_day=no_day,
        macro_f1=float(np.mean(per_seed)),
        macro_f1_sd=float(np.std(per_seed, ddof=1)) if len(per_seed) > 1 else 0.0,
        per_seed=tuple(per_seed),
        worst_recall=float(recall.min()),
        worst_recall_class=str(recall.idxmin()),
        n_features=len(columns),
        seconds=time.monotonic() - started,
    )


def keep_threshold(seed_sd: float, n_seeds: int = len(SEARCH_SEEDS)) -> float:
    """The margin a candidate must beat the current best by (ladder-style, ADR 0013):
    two standard deviations of the difference of two ``n_seeds``-seed means, and never
    below 0.01."""
    return max(0.01, 2.0 * seed_sd * float(np.sqrt(2.0 / n_seeds)))


def examine(
    outer_fold: int,
    *,
    seeds: Sequence[int] = SEARCH_SEEDS,
    candidate: ModuleType | None = None,
    table: pd.DataFrame | None = None,
    exam_dir: Path = EXAM_DIR,
) -> dict[str, Any]:
    """Score the finished search's candidate on its held-out load, once.

    Fits on every row of the training loads (not thinned, like the v1 refit) and predicts
    every held-out row. Refuses to run twice for one fold: the result file is the record.
    """
    out_path = exam_dir / f"v2_fold{outer_fold}.json"
    if out_path.exists():
        raise RuntimeError(f"{out_path} exists: fold {outer_fold} has already been examined")
    candidate = candidate or load_candidate()
    base = table if table is not None else _feature_table()
    full = candidate_table(candidate, base, no_day=False)
    available = _available(base, full, no_day=False)
    columns = select_checked(candidate, available)
    per_seed = []
    for seed in seeds:
        predictions = evaluate.lolo_predict(
            partial(candidate.build_model, seed), full, columns, only_folds=[outer_fold]
        )
        summary = evaluate.summarise(predictions).iloc[0].to_dict()
        per_seed.append({"seed": seed, **summary})
    result = {
        "outer_fold": outer_fold,
        "label": "v2 (autoresearch), separately labelled; v1 locked results unchanged",
        "macro_f1_mean": float(np.mean([r["macro_f1"] for r in per_seed])),
        "per_seed": per_seed,
        "git_commit": evaluate.git_commit(),
    }
    exam_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=str) + "\n")
    return result


def _feature_table() -> pd.DataFrame:
    from keyframe import experiments

    return experiments.load_feature_table()


def _print_score(score: Score) -> None:
    print("---")
    for key, value in asdict(score).items():
        if isinstance(value, float):
            value = f"{value:.6f}"
        elif isinstance(value, tuple):
            value = " ".join(f"{v:.6f}" for v in value)
        print(f"{key}: {value}")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m keyframe.autoresearch")
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="Inner-LOLO search score of autoresearch/candidate.py.")
    score.add_argument("--outer-fold", type=int, required=True, choices=splits.LOAD_BINS)
    score.add_argument("--no-day", action="store_true", help="Day-robust gate: no day channels.")
    exam = sub.add_parser("examine", help="Score the held-out load once, after the search.")
    exam.add_argument("--outer-fold", type=int, required=True, choices=splits.LOAD_BINS)
    args = parser.parse_args(argv)
    if args.command == "score":
        _print_score(search_score(args.outer_fold, no_day=args.no_day))
    else:
        print(json.dumps(examine(args.outer_fold), indent=2, default=str))


if __name__ == "__main__":
    main()
