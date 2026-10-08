"""Numbers for the v2 write-up (feature 16, T-007): v1 reference against each search's
examination, with the search logs' experiment counts. Writes
``reports/autoresearch/summary.md``; the narrative lives in ``reports/autoresearch/README.md``.

Run ``uv run python -m keyframe.v2report``. Folds without an examination yet are listed as
pending, so the summary can be rebuilt as searches finish.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from keyframe import paths, splits

EXAM_DIR = paths.REPORTS / "autoresearch"


def search_summary(log_path: Path, examined_commit: str | None = None) -> dict[str, Any]:
    """Experiments run and kept in one search log (tab-separated, ``status`` and
    ``macro_f1`` columns, first row the baseline). ``inner_examined`` is the inner score of
    the commit that was examined (ADR 0013, amendment 3), or of the last keep if not given."""
    log = pd.read_csv(log_path, sep="\t")
    status = log["status"].astype(str).str.strip()
    experiments = log.iloc[1:]
    kept = status.iloc[1:] == "keep"
    keeps = log[status == "keep"]
    return {
        "experiments": len(experiments),
        "kept": int(kept.sum()),
        "crashed": int((status.iloc[1:] == "crash").sum()),
        "inner_baseline": float(log["macro_f1"].iloc[0]),
        "inner_final": float(keeps["macro_f1"].iloc[-1]),
        "inner_examined": float(
            keeps.loc[keeps["commit"].astype(str).str.startswith(examined_commit), "macro_f1"].iloc[
                0
            ]
            if examined_commit
            else keeps["macro_f1"].iloc[-1]
        ),
    }


def _exam(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    result = json.loads(path.read_text())
    per_seed = result["per_seed"]
    f1 = [r["macro_f1"] for r in per_seed]
    return {
        "mean": float(np.mean(f1)),
        "sd": float(np.std(f1, ddof=1)) if len(f1) > 1 else 0.0,
        "worst_recall": float(np.mean([r["worst_recall"] for r in per_seed])),
        "worst_class": per_seed[0]["worst_recall_class"],
        "false_alarm_rate": float(np.mean([r["false_alarm_rate"] for r in per_seed])),
    }


def summary_table(exam_dir: Path = EXAM_DIR) -> pd.DataFrame:
    """One row per held-out load: v1 reference, v2 examination and the search's log."""
    examined_path = exam_dir / "examined.json"
    examined = json.loads(examined_path.read_text()) if examined_path.exists() else {}
    rows = []
    for fold in splits.LOAD_BINS:
        v1 = _exam(exam_dir / f"v1_unseen_fold{fold}.json")
        v2 = _exam(exam_dir / f"v2_fold{fold}.json")
        log_path = exam_dir / f"fold{fold}_results.tsv"
        log = search_summary(log_path, examined.get(str(fold))) if log_path.exists() else {}
        row: dict[str, Any] = {"held_out_load": fold}
        for tag, exam in (("v1", v1), ("v2", v2)):
            for key in ("mean", "sd", "worst_recall", "worst_class", "false_alarm_rate"):
                row[f"{tag}_{key}"] = exam[key] if exam else None
        row["delta"] = v2["mean"] - v1["mean"] if v1 and v2 else None
        row.update(log)
        rows.append(row)
    return pd.DataFrame(rows)


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):  # pending fold
        return "pending"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _count(value: Any) -> str:
    return str(int(value)) if value is not None and pd.notna(value) else "pending"


def render(table: pd.DataFrame) -> str:
    """Markdown summary: per-load scores, mean over loads, search effort."""
    lines = [
        "# v2 summary (generated)",
        "",
        "Built by `uv run python -m keyframe.v2report` from `reports/autoresearch/*.json` and",
        "`*_results.tsv`. Macro F1 on each held-out load, rows of unseen runs only, mean ± sd",
        "over 3 seeds. v1 is re-scored under the same rule. Its locked numbers (ADR 0009) are",
        "unchanged.",
        "",
        "| Held-out load | v1 | v2 | v2 − v1 | v2 worst recall | v2 false alarms"
        " | Experiments | Kept | Inner F1 (baseline → examined) |",
        "|---|---:|---:|---:|---|---:|---:|---:|---|",
    ]
    for _, r in table.iterrows():
        v1 = f"{_fmt(r['v1_mean'])} ± {_fmt(r['v1_sd'])}" if pd.notna(r["v1_mean"]) else "pending"
        v2 = f"{_fmt(r['v2_mean'])} ± {_fmt(r['v2_sd'])}" if pd.notna(r["v2_mean"]) else "pending"
        worst = (
            f"{_fmt(r['v2_worst_recall'], 2)} {r['v2_worst_class']}"
            if pd.notna(r["v2_worst_recall"])
            else "pending"
        )
        inner = (
            f"{_fmt(r.get('inner_baseline'))} → {_fmt(r.get('inner_examined'))}"
            if "inner_baseline" in r and pd.notna(r.get("inner_baseline"))
            else "pending"
        )
        experiments = r.get("experiments")  # NaN while a search is running
        lines.append(
            f"| {r['held_out_load']}% | {v1} | {v2} | {_fmt(r['delta'])} | {worst}"
            f" | {_fmt(r['v2_false_alarm_rate'])}"
            f" | {_count(experiments)} | {_count(r.get('kept'))} | {inner} |"
        )
    done = table.dropna(subset=["v1_mean", "v2_mean"])
    if len(done):
        lines += [
            "",
            f"Mean over the {len(done)} examined loads: v1 {done['v1_mean'].mean():.3f},"
            f" v2 {done['v2_mean'].mean():.3f} (difference {done['delta'].mean():+.3f}).",
        ]
    return "\n".join(lines) + "\n"


def main() -> None:
    table = summary_table()
    out = EXAM_DIR / "summary.md"
    out.write_text(render(table))
    print(out.read_text())


if __name__ == "__main__":
    main()
