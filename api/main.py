"""Keyframe API: serves the trained model and the exported replays."""

import json
import os
import warnings
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from keyframe import paths
from keyframe.predict import META_FILE, MODEL_FILE, KeyframeModel

DEV_ORIGIN = "http://localhost:5173"
CREATE_MODEL_HINT = "uv run python -c 'from keyframe.predict import export_model; export_model()'"


def _cors_origins() -> list[str]:
    """Dev server plus any origins in `KEYFRAME_CORS_ORIGINS` (comma separated)."""
    extra = os.environ.get("KEYFRAME_CORS_ORIGINS", "")
    return [DEV_ORIGIN, *(o.strip() for o in extra.split(",") if o.strip())]


def create_app(models_dir: Path = paths.MODELS) -> FastAPI:
    """Build the app; the model and replay index load once at startup from `models_dir`."""
    state: dict[str, Any] = {"model": None, "version": None, "index": []}
    replays_dir = models_dir / "replays"

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if (models_dir / MODEL_FILE).exists() and (models_dir / META_FILE).exists():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                state["model"] = KeyframeModel.load(models_dir)
            meta = json.loads((models_dir / META_FILE).read_text())
            state["version"] = meta.get("git_commit")
        index = replays_dir / "index.json"
        state["index"] = json.loads(index.read_text()) if index.exists() else []
        yield

    app = FastAPI(title="Keyframe", lifespan=lifespan)
    app.state.keyframe = state
    app.add_middleware(
        CORSMiddleware, allow_origins=_cors_origins(), allow_methods=["*"], allow_headers=["*"]
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        model: KeyframeModel | None = state["model"]
        return {
            "status": "ok",
            "model_loaded": model is not None,
            "model_version": state["version"],
            "classes": model.classes if model else [],
            "replays_available": bool(state["index"]),
            "hint": None
            if model
            else f"Model files missing. Create them with: {CREATE_MODEL_HINT}",
        }

    @app.get("/runs")
    def runs() -> list[dict[str, Any]]:
        return list(state["index"])

    @app.get("/runs/{run_id}")
    def run(run_id: str) -> Any:
        if run_id not in {entry["id"] for entry in state["index"]}:
            raise HTTPException(status_code=404, detail=f"No replay called '{run_id}'.")
        return json.loads((replays_dir / f"{run_id}.json").read_text())

    return app


app = create_app()
