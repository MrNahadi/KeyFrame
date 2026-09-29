"""Latency budget for /predict and /explain (feature 11, T-005, R9)."""

import json
import statistics
import time
from collections.abc import Iterator
from typing import Any

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from keyframe import paths, predict

BUDGET_MS = 300.0
CALLS = 10


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


def _median_ms(client: TestClient, path: str, rows: list[dict[str, Any]]) -> float:
    assert client.post(path, json={"rows": rows}).status_code == 200  # warm-up
    times = []
    for _ in range(CALLS):
        start = time.perf_counter()
        res = client.post(path, json={"rows": rows})
        times.append((time.perf_counter() - start) * 1000)
        assert res.status_code == 200
    return statistics.median(times)


@pytest.mark.data
def test_predict_and_explain_median_under_budget(client: TestClient) -> None:
    rows = _rows()
    results = {p: _median_ms(client, p, rows) for p in ("/predict", "/explain")}
    out = paths.RESULTS / "11_latency.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "endpoint": list(results),
            "median_ms": [round(v, 1) for v in results.values()],
            "budget_ms": BUDGET_MS,
            "calls": CALLS,
            "window_rows": len(rows),
        }
    ).to_csv(out, index=False)
    for path, ms in results.items():
        assert ms < BUDGET_MS, f"{path} median {ms:.0f} ms"


@pytest.mark.data
def test_fast_tail_features_match_training_features() -> None:
    from keyframe.predict import KeyframeModel

    model = KeyframeModel.load()
    frame = pd.DataFrame(_rows()).astype(float).sort_values("t").reset_index(drop=True)
    full = model.features(frame).tail(5)
    fast = model.features(frame, last_n=5)
    pd.testing.assert_frame_equal(fast, full, rtol=1e-6, atol=1e-6, check_dtype=False)
