"""POST /explain: grouped SHAP for the last row of a window (feature 11, T-003)."""

import json
from collections.abc import Iterator
from typing import Any

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from keyframe import explain, paths, predict


def _rows() -> list[dict[str, Any]]:
    stored = json.loads((paths.MODELS / predict.REFERENCE_FILE).read_text())
    columns = [c for c in stored["columns"] if c != "run"]
    return pd.DataFrame(stored["rows"])[columns].tail(600).to_dict("records")


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    if not (paths.MODELS / predict.MODEL_FILE).exists():
        pytest.skip("models/keyframe_xgboost.joblib is missing; run the export experiment")
    with TestClient(create_app()) as c:
        yield c


@pytest.mark.data
def test_explain_is_additive_with_five_groups_and_top_features(client: TestClient) -> None:
    res = client.post("/explain", json={"rows": _rows()})
    assert res.status_code == 200
    body = res.json()
    assert len(body["groups"]) == 5
    total = sum(body["groups"].values()) + body["warmup"] + body["base_value"]
    assert total == pytest.approx(body["margin"], abs=1e-4)
    for by_class in body["groups_all_classes"].values():
        assert len(by_class) == 5
    assert body["predicted_class"] in body["probabilities"]
    top = body["top_features"]
    assert len(top) == 8
    for item in top:
        assert {"feature", "value", "shap", "source_channels", "group"} <= item.keys()
        assert item["group"] == explain.group_of(item["feature"])
        assert item["source_channels"] == list(explain.source_channel(item["feature"]))


@pytest.mark.data
def test_explain_missing_channels_422(client: TestClient) -> None:
    rows = [{k: v for k, v in r.items() if k != "t"} for r in _rows()[:5]]
    assert client.post("/explain", json={"rows": rows}).status_code == 422
