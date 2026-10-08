"""Synthetic tests for the autoresearch harness (feature 16, ADR 0013)."""

from __future__ import annotations

import types
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier

from keyframe import autoresearch

LOADS = (40, 60, 75, 85)


def _table() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    for load in LOADS:
        for run in ("healthy", "fault"):
            for i in range(24):
                faulty = run == "fault" and i >= 8
                rows.append(
                    {
                        "run": f"{run}_{load}",
                        "load_bin": load,
                        "t": float(i),
                        "label": "AC" if faulty else "Normal",
                        "Engine Speed": rng.normal() + (2.0 if faulty else 0.0),
                        "Fuel Temp.": rng.normal(),
                    }
                )
    return pd.DataFrame(rows)


class _Spy(DummyClassifier):
    """Records every row index it is fitted on or asked to predict."""

    seen: list[pd.Index] = []

    def fit(self, X, y, **kwargs):  # noqa: N803
        _Spy.seen.append(X.index)
        return super().fit(X, y)

    def predict(self, X):  # noqa: N803
        _Spy.seen.append(X.index)
        return super().predict(X)


def _candidate(**overrides) -> types.ModuleType:
    module = types.ModuleType("candidate")
    module.add_features = lambda run: pd.DataFrame(index=run.index)
    module.select_columns = lambda available: available
    module.build_model = lambda seed: _Spy(strategy="most_frequent")
    for name, value in overrides.items():
        setattr(module, name, value)
    return module


def test_search_never_touches_the_held_out_load():
    table = _table()
    _Spy.seen = []
    autoresearch.search_score(75, candidate=_candidate(), table=table, seeds=(1,), thin_step=1)
    held_out = set(table.index[table["load_bin"] == 75])
    assert _Spy.seen
    assert all(held_out.isdisjoint(index) for index in _Spy.seen)


def test_no_day_hides_day_channels_from_the_candidate():
    table = _table()
    seen: list[list[str]] = []

    def add_features(run: pd.DataFrame) -> pd.DataFrame:
        seen.append(list(run.columns))
        return pd.DataFrame(index=run.index)

    autoresearch.search_score(
        60,
        no_day=True,
        candidate=_candidate(add_features=add_features),
        table=table,
        seeds=(1,),
        thin_step=1,
    )
    assert seen
    assert all("Fuel Temp." not in columns and "label" not in columns for columns in seen)


def test_look_ahead_features_are_refused():
    def future(run: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({"cand_next": run["Engine Speed"].shift(-1)}, index=run.index)

    with pytest.raises(autoresearch.CandidateError, match="looks ahead"):
        autoresearch.check_causal(_candidate(add_features=future), _table(), no_day=False)


def test_causal_rolling_features_pass():
    def trailing(run: pd.DataFrame) -> pd.DataFrame:
        mean = run["Engine Speed"].rolling(3, min_periods=1).mean()
        return pd.DataFrame({"cand_mean3": mean}, index=run.index)

    autoresearch.check_causal(_candidate(add_features=trailing), _table(), no_day=False)


@pytest.mark.parametrize("column", ["label", "load_bin", "Turbine Back Pressure", "made_up"])
def test_select_columns_cannot_reach_outside_the_inputs(column):
    candidate = _candidate(select_columns=lambda available: [*available, column])
    with pytest.raises(autoresearch.CandidateError, match="may not use"):
        autoresearch.select_checked(candidate, ["Engine Speed"])


def test_new_columns_need_the_prefix():
    def unprefixed(run: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({"speed2": run["Engine Speed"] ** 2}, index=run.index)

    with pytest.raises(autoresearch.CandidateError, match="cand_"):
        autoresearch.candidate_table(_candidate(add_features=unprefixed), _table(), no_day=False)


def test_candidate_source_may_not_read_files(tmp_path: Path):
    path = tmp_path / "candidate.py"
    path.write_text("import pandas as pd\nX = pd.read_parquet('data/processed/clean.parquet')\n")
    with pytest.raises(autoresearch.CandidateError, match="forbidden"):
        autoresearch.load_candidate(path)


def test_the_shipped_candidate_loads():
    module = autoresearch.load_candidate()
    assert callable(module.build_model)


def test_keep_threshold_has_a_floor_and_grows_with_noise():
    assert autoresearch.keep_threshold(0.0) == 0.01
    assert autoresearch.keep_threshold(0.012) == pytest.approx(2 * 0.012 * np.sqrt(2 / 3))


def test_examine_runs_once_per_fold(tmp_path: Path):
    table = _table()
    candidate = _candidate()
    result = autoresearch.examine(
        40, candidate=candidate, table=table, seeds=(1,), exam_dir=tmp_path
    )
    assert result["outer_fold"] == 40
    assert (tmp_path / "v2_fold40.json").exists()
    with pytest.raises(RuntimeError, match="already been examined"):
        autoresearch.examine(40, candidate=candidate, table=table, seeds=(1,), exam_dir=tmp_path)


def test_rows_of_runs_seen_at_a_training_load_are_not_scored():
    predictions = pd.DataFrame(
        {
            "run": ["spans", "spans", "single", "other"],
            "fold": [40, 60, 40, 60],
        }
    )
    table = pd.DataFrame(
        {"run": ["spans", "spans", "single", "other"], "load_bin": [40, 60, 40, 60]}
    )
    mask = autoresearch.unseen_run_mask(predictions, table)
    assert mask.tolist() == [False, False, True, True]


def test_search_score_reports_seen_runs_apart():
    table = _table()
    shared = table["run"].isin(["healthy_40", "healthy_60"])
    table.loc[shared, "run"] = "reference"
    score = autoresearch.search_score(
        75, candidate=_candidate(), table=table, seeds=(1,), thin_step=1
    )
    dev = table[table["load_bin"] != 75]
    assert score.n_scored_rows == len(dev) - shared.sum()
    assert not np.isnan(score.seen_run_macro_f1)


def test_run_identifiability_scores_each_training_load():
    scores = autoresearch.run_identifiability(
        60, candidate=_candidate(), table=_table(), thin_step=1
    )
    assert set(scores) == {40, 75, 85}
    assert all(0.0 <= v <= 1.0 for v in scores.values())
