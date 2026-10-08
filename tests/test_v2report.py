"""Tests for the v2 summary builder (feature 16, T-007)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from keyframe import v2report


def _exam(path: Path, f1s: list[float]) -> None:
    per_seed = [
        {"macro_f1": f, "worst_recall": 0.2, "worst_recall_class": "TD", "false_alarm_rate": 0.1}
        for f in f1s
    ]
    path.write_text(json.dumps({"per_seed": per_seed}))


def test_summary_pairs_v1_and_v2_per_load_and_counts_the_search(tmp_path: Path):
    _exam(tmp_path / "v1_unseen_fold40.json", [0.40, 0.42, 0.44])
    _exam(tmp_path / "v2_fold40.json", [0.50, 0.52, 0.54])
    _exam(tmp_path / "v1_unseen_fold60.json", [0.8, 0.8, 0.8])
    (tmp_path / "fold40_results.tsv").write_text(
        "commit\tmacro_f1\tstatus\tdescription\n"
        "a\t0.30\tkeep\tbaseline\n"
        "b\t0.31\tdiscard\tx\n"
        "c\t0.35\tkeep\ty\n"
        "d\t0\tcrash\tz\n"
    )
    table = v2report.summary_table(tmp_path).set_index("held_out_load")
    assert table.loc[40, "delta"] == pytest.approx(0.10)
    assert table.loc[40, "experiments"] == 3
    assert table.loc[40, "kept"] == 1
    assert table.loc[40, "crashed"] == 1
    assert table.loc[40, "inner_final"] == pytest.approx(0.35)
    assert pd.isna(table.loc[60, "v2_mean"])
    text = v2report.render(table.reset_index())
    assert "pending" in text
    assert "Mean over the 1 examined loads" in text
