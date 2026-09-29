"""POST /predict from a window of raw readings (feature 11, T-002)."""

import json
from collections.abc import Iterator
from typing import Any

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from keyframe import explain, paths, predict
from keyframe.predict import KeyframeModel


def _window() -> tuple[list[dict[str, Any]], list[str]]:
    stored = json.loads((paths.MODELS / predict.REFERENCE_FILE).read_text())
    columns = [c for c in stored["columns"] if c != "run"]
    frame = pd.DataFrame(stored["rows"])[columns].tail(600)
    return frame.to_dict("records"), columns


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    if not (paths.MODELS / predict.MODEL_FILE).exists():
        pytest.skip("models/keyframe_xgboost.joblib is missing; run the export experiment")
    with TestClient(create_app()) as c:
        yield c


@pytest.mark.data
def test_predict_matches_model_for_last_row(client: TestClient) -> None:
    rows, columns = _window()
    body = client.post("/predict", json={"rows": rows}).json()
    expected = KeyframeModel.load().predict_proba(pd.DataFrame(rows)[columns]).iloc[-1]
    assert body["mode"] == "window"
    for name, value in expected.items():
        assert body["probabilities"][name] == pytest.approx(float(value), abs=1e-6)
    assert body["predicted_class"] == expected.idxmax()
    assert "alarm" in body
    assert isinstance(body["warnings"], list)


@pytest.mark.data
def test_missing_channels_422_lists_them(client: TestClient) -> None:
    rows, _ = _window()
    dropped = ["Charge Air Press.", "Fuel Flow"]
    cut = [{k: v for k, v in r.items() if k not in dropped} for r in rows]
    response = client.post("/predict", json={"rows": cut})
    assert response.status_code == 422
    for name in dropped:
        assert name in json.dumps(response.json())


@pytest.mark.data
def test_excluded_channels_ignored_and_unknown_warned(client: TestClient) -> None:
    rows, _ = _window()
    base = client.post("/predict", json={"rows": rows}).json()
    extra = [
        {**r, "Engine room Temp.": 30.0, "Turbine Back Pressure": 1.0, "mystery": 1} for r in rows
    ]
    body = client.post("/predict", json={"rows": extra}).json()
    assert body["probabilities"] == base["probabilities"]
    assert any("mystery" in w for w in body["warnings"])
    assert not any("Engine room" in w for w in body["warnings"])


def test_required_channels_exclude_dropped_ones() -> None:
    assert "Engine room Temp." not in explain.SENSOR_GROUPS
