import re
from pathlib import Path

import pandas as pd
import pytest

from keyframe import experiments, lockbox

ROOT = Path(__file__).resolve().parents[1]


def test_stored_result_is_returned_without_refitting(tmp_path, monkeypatch):
    stored = pd.DataFrame({"scope": ["all"], "label": ["INJ"], "share": [0.5]})
    stored.to_csv(tmp_path / "07_lockbox.csv", index=False)

    def boom(*args, **kwargs):
        raise AssertionError("must not refit or read data")

    monkeypatch.setattr(experiments, "load_feature_table", boom)
    monkeypatch.setattr(lockbox.load, "load_run", boom)
    result = lockbox.evaluate_lockbox(force_first_run=True, results_dir=tmp_path)
    assert result["share"].tolist() == [0.5]


def test_missing_result_needs_explicit_first_run(tmp_path):
    with pytest.raises(RuntimeError):
        lockbox.evaluate_lockbox(results_dir=tmp_path)


def test_summary_has_overall_and_per_load_bin_shares():
    labels = pd.Series(["INJ", "INJ", "AF", "INJ"])
    bins = pd.Series([40, 40, 60, 60])
    out = lockbox._summarise(labels, bins, "now")
    overall = out[(out["scope"] == "all") & (out["label"] == "INJ")]
    assert overall["share"].iloc[0] == 0.75
    bin_60 = out[(out["scope"] == "load_bin") & (out["load_bin"] == 60) & (out["label"] == "AF")]
    assert bin_60["share"].iloc[0] == 0.5


def test_only_download_and_lockbox_reference_the_lockbox():
    pattern = re.compile(r"data/lockbox|paths\.LOCKBOX")
    offenders = []
    for folder in ("keyframe", "notebooks", "api"):
        for path in (ROOT / folder).rglob("*"):
            if path.suffix not in (".py", ".md") or path.name in ("download.py", "lockbox.py"):
                continue
            if pattern.search(path.read_text()):
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
