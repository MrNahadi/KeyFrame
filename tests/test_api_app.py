"""API skeleton: health, replay index and replay files (feature 11, T-001)."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from keyframe import paths


def _replay_dir(tmp_path: Path) -> Path:
    replays = tmp_path / "replays"
    replays.mkdir()
    (replays / "index.json").write_text(json.dumps([{"id": "Run_A", "title": "A"}]))
    (replays / "Run_A.json").write_text(json.dumps({"id": "Run_A", "t": [0, 1]}))
    (tmp_path / "secret.json").write_text("{}")
    return tmp_path


def test_health_without_model_files(tmp_path: Path) -> None:
    with TestClient(create_app(tmp_path)) as client:
        body = client.get("/health").json()
    assert body["model_loaded"] is False
    assert body["replays_available"] is False
    assert "export_model" in body["hint"]


def test_health_with_model_files() -> None:
    with TestClient(create_app(paths.MODELS)) as client:
        body = client.get("/health").json()
    assert body["model_loaded"] is True
    assert body["classes"]
    assert body["model_version"]
    assert body["replays_available"] is True


def test_runs_index_and_known_run(tmp_path: Path) -> None:
    with TestClient(create_app(_replay_dir(tmp_path))) as client:
        assert client.get("/runs").json() == [{"id": "Run_A", "title": "A"}]
        assert client.get("/runs/Run_A").json()["id"] == "Run_A"


def test_unknown_run_is_404(tmp_path: Path) -> None:
    with TestClient(create_app(_replay_dir(tmp_path))) as client:
        response = client.get("/runs/Nope")
    assert response.status_code == 404
    assert "Nope" in response.json()["detail"]


@pytest.mark.parametrize("run_id", ["..%2Fsecret", "../secret", "..%2F..%2Fsecret", "index"])
def test_path_traversal_rejected(tmp_path: Path, run_id: str) -> None:
    with TestClient(create_app(_replay_dir(tmp_path))) as client:
        assert client.get(f"/runs/{run_id}").status_code == 404


def test_runs_without_replays_is_empty(tmp_path: Path) -> None:
    with TestClient(create_app(tmp_path)) as client:
        assert client.get("/runs").json() == []


def test_cors_allows_dev_server(tmp_path: Path) -> None:
    with TestClient(create_app(tmp_path)) as client:
        response = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
