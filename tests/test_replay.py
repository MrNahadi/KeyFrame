import numpy as np
import pandas as pd

from keyframe import explain
from keyframe.predict import KeyframeModel
from keyframe.replay import KEY_SENSORS, build_replay
from tests.test_predict import LABELS, _clean_run, _fitted

GROUPS = set(explain.SENSOR_GROUPS.values()) - {"lube oil", "unassigned"}


def _run(n: int = 120, bins=(40,)) -> pd.DataFrame:
    run = _clean_run(n=n, seed=5)
    run["label"] = ["Normal"] * (n // 2) + [LABELS[1]] * (n - n // 2)
    for column in ("No.1 Exh.Gas Temp.", "No.2 Exh.Gas Temp.", "No.3 Exh.Gas Temp."):
        run[column] = 400 + 10 * np.arange(n) % 7
    run["load_bin"] = np.resize(np.array(bins), n)
    return run


def test_frames_ordered_include_switch_on_and_probabilities_sum_to_one():
    model, _ = _fitted()
    run = _run()
    replay = build_replay(run, model, git_commit="abc")
    times = [f["t"] for f in replay["frames"]]
    assert times == sorted(times)
    assert replay["switch_on_t"] in times
    assert replay["switch_on_t"] == float(run["t"].iloc[60])
    assert len(times) < len(run)
    for frame in replay["frames"]:
        assert abs(sum(frame["probabilities"].values()) - 1) < 1e-6
        assert set(frame["sensors"]) == set(KEY_SENSORS)
        assert len(frame["top_features"]) == 3


def test_grouped_shap_has_five_groups():
    model, _ = _fitted()
    replay = build_replay(_run(), model, git_commit="abc")
    for frame in replay["frames"]:
        assert len(frame["shap_groups"]) == 5


def test_provenance_names_held_out_fold_and_commit():
    model, _ = _fitted()
    replay = build_replay(_run(bins=(60,)), {60: model}, git_commit="abc")
    assert "leave-one-load-out fold 60" in replay["provenance"]
    assert "abc" in replay["provenance"]
    assert replay["nominal_load"] == 60
    assert replay["fault"] == LABELS[1]


def test_mixed_bin_run_uses_each_rows_own_fold_model():
    model_a, table = _fitted()
    model_b = KeyframeModel.fit(
        table, {"n_estimators": 2, "max_depth": 1, "learning_rate": 0.5}, model_a.alarm
    )
    run = _run(bins=(40, 60)).sort_values("t").reset_index(drop=True)
    replay = build_replay(run, {40: model_a, 60: model_b}, git_commit="x")
    assert "40, 60" in replay["provenance"]
    expected = {40: model_a.predict_proba(run), 60: model_b.predict_proba(run)}
    assert not np.allclose(expected[40], expected[60])
    by_t = {float(t): i for i, t in enumerate(run["t"])}
    for frame in replay["frames"]:
        i = by_t[frame["t"]]
        want = expected[int(run["load_bin"].iloc[i])].iloc[i]
        assert np.allclose(list(frame["probabilities"].values()), want.to_numpy())


def test_to_strict_json_turns_nan_into_null() -> None:
    import json
    import math

    from keyframe.replay import to_strict_json

    text = to_strict_json({"a": math.nan, "b": [1.0, math.inf], "c": {"d": -math.inf}})
    assert json.loads(text) == {"a": None, "b": [1.0, None], "c": {"d": None}}


def test_committed_replay_files_are_strict_json() -> None:
    import json
    from pathlib import Path

    replays = Path(__file__).resolve().parents[1] / "models" / "replays"

    def reject(token: str) -> None:
        raise ValueError(f"contains {token}")

    for path in replays.glob("*.json"):
        json.loads(path.read_text(), parse_constant=reject)
