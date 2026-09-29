"""The paper's generated numbers, tables and plot data match the locked results (roadmap 15)."""

import importlib.util

import pytest

from keyframe import paths

PAPER = paths.ROOT / "paper"
NEEDED = [
    paths.PROCESSED / "clean.parquet",
    paths.PROCESSED / "experiments" / "modelling_xgboost.parquet",
]


def _make_data():
    spec = importlib.util.spec_from_file_location("make_data", PAPER / "make_data.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.skipif(
    not all(p.exists() for p in NEEDED), reason="needs the dataset and the saved predictions"
)
def test_committed_paper_data_matches_a_fresh_run(tmp_path):
    written = _make_data().build(tmp_path, counts=False)
    assert written
    for fresh in written:
        committed = PAPER / "data" / fresh.name
        assert committed.exists(), f"{fresh.name} is not committed; run paper/make_data.py"
        assert committed.read_text() == fresh.read_text(), (
            f"paper/data/{fresh.name} is stale; run `uv run python paper/make_data.py`"
        )


def test_macro_names_are_letters_only():
    macros = _make_data().Macros()
    macros["FineName"] = "1"
    with pytest.raises(ValueError):
        macros["Bad1Name"] = "2"
    with pytest.raises(ValueError):
        macros["FineName"] = "3"
