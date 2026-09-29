"""What-if baselines and steady-state predict (feature 11, T-004)."""

from collections.abc import Iterator

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.main import STEADY_WARNING, create_app
from keyframe import explain, paths, predict, splits, whatif


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    if not (paths.MODELS / predict.MODEL_FILE).exists():
        pytest.skip("models/keyframe_xgboost.joblib is missing; run the export experiment")
    if not (paths.MODELS / whatif.BASELINES_FILE).exists():
        pytest.skip("models/whatif_baselines.json is missing; run the whatif experiment")
    with TestClient(create_app()) as c:
        yield c


def test_build_baselines_uses_healthy_medians_and_all_row_ranges() -> None:
    cols = list(explain.SENSOR_GROUPS)
    rows = []
    for load in splits.LOAD_BINS:
        for label, value in [("Normal", 1.0), ("Normal", 3.0), ("Normal", 5.0), ("AC", 100.0)]:
            rows.append({**dict.fromkeys(cols, value), "load_bin": load, "label": label})
    out = whatif.build_baselines(pd.DataFrame(rows))
    assert out["load_bins"] == list(splits.LOAD_BINS)
    entry = out["loads"]["40"]
    assert entry["reading"]["Fuel Flow"] == 3.0
    slider = entry["sliders"]["Fuel Flow"]
    assert slider["min"] < 3.0 < slider["max"] <= 100.0


def test_reading_and_rows_together_are_rejected(client: TestClient) -> None:
    response = client.post("/predict", json={"reading": {}, "rows": [{"t": 0.0}]})
    assert response.status_code == 422
    assert client.post("/predict", json={}).status_code == 422


@pytest.mark.data
def test_baselines_endpoint_lists_every_load(client: TestClient) -> None:
    body = client.get("/whatif/baselines").json()
    assert body["load_bins"] == list(splits.LOAD_BINS)
    for load in splits.LOAD_BINS:
        entry = body["loads"][str(load)]
        assert set(entry["reading"]) == set(explain.SENSOR_GROUPS)
        assert len(entry["sliders"]) == len(whatif.SLIDER_CHANNELS)


@pytest.mark.data
def test_steady_state_prediction_for_each_baseline(client: TestClient) -> None:
    baselines = client.get("/whatif/baselines").json()
    rows = []
    for load in splits.LOAD_BINS:
        reading = baselines["loads"][str(load)]["reading"]
        response = client.post("/predict", json={"reading": reading, "load_percent": load})
        assert response.status_code == 200
        body = response.json()
        assert body["mode"] == "steady-state"
        assert STEADY_WARNING in body["warnings"]
        assert sum(body["probabilities"].values()) == pytest.approx(1.0, abs=1e-4)
        rows.append({"load_percent": load, "predicted_class": body["predicted_class"]})
    paths.RESULTS.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(paths.RESULTS / "11_whatif_baselines.csv", index=False)
