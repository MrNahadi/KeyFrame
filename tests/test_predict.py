import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from keyframe import explain, features, paths, predict
from keyframe.predict import KeyframeModel

LABELS = ["Normal", "AC_Fouling", "AF_Clogging"]


def _clean_run(n: int = 80, seed: int = 0, label: str = "Normal") -> pd.DataFrame:
    """A synthetic clean-table run: every known sensor channel, positive, plus t/run/label."""
    rng = np.random.default_rng(seed)
    data = {c: 50 + 10 * rng.random(n) for c in explain.SENSOR_GROUPS}
    frame = pd.DataFrame(data)
    frame["t"] = np.cumsum(rng.choice([1.0, 2.0], n))
    frame["run"] = f"run{seed}"
    frame["label"] = label
    return frame


def _fitted() -> tuple[KeyframeModel, pd.DataFrame]:
    parts = []
    for seed, label in enumerate(LABELS):
        run = _clean_run(seed=seed, label=label)
        run["Charge Air Press."] += 5 * seed
        parts.append(features.build_feature_table(run))
    table = pd.concat(parts, ignore_index=True)
    params = {"n_estimators": 8, "max_depth": 3, "learning_rate": 0.3}
    alarm = {"min_duration_s": 30.0, "min_probability": 0.5}
    return KeyframeModel.fit(table, params, alarm, git_commit="test"), table


def test_save_load_round_trip_gives_same_probabilities(tmp_path):
    model, _ = _fitted()
    run = _clean_run(seed=7)
    model.save(tmp_path)
    assert (tmp_path / "model_meta.json").exists()
    restored = KeyframeModel.load(tmp_path)
    pd.testing.assert_frame_equal(model.predict_proba(run), restored.predict_proba(run))
    assert restored.columns == model.columns
    assert restored.alarm == model.alarm


def test_explain_groups_plus_base_equal_raw_margin(tmp_path):
    model, _ = _fitted()
    model.save(tmp_path)
    restored = KeyframeModel.load(tmp_path)
    run = _clean_run(seed=9)
    out = restored.explain(run, row=60)
    assert set(out["groups"]) == {
        "air path",
        "combustion and power",
        "cooling",
        "fuel system",
        "lube oil",
    }
    total = sum(out["groups"].values()) + out["warmup"] + out["base_value"]
    assert np.isclose(total, out["margin"], atol=1e-4)
    assert len(out["top_features"]) == 8
    assert set(out["groups_all_classes"]) == set(LABELS)


@pytest.mark.data
def test_clean_session_reproduces_reference():
    if not (paths.MODELS / predict.MODEL_FILE).exists():
        pytest.skip("models/keyframe_xgboost.joblib is missing; run the export experiment")
    code = "from keyframe import predict; print(predict.reproduce_reference())"
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True, cwd=paths.ROOT
    )
    assert float(out.stdout.strip().splitlines()[-1]) < 1e-6
