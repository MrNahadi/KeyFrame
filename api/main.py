"""Keyframe API: serves the trained model and the exported replays."""

import json
import os
import warnings
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from keyframe import explain, paths
from keyframe.alarm import sustained_alarm
from keyframe.features import EXCLUDED_COLUMNS
from keyframe.predict import META_FILE, MODEL_FILE, KeyframeModel

WINDOW_S = 900.0
DEV_ORIGIN = "http://localhost:5173"
CREATE_MODEL_HINT = "uv run python -c 'from keyframe.predict import export_model; export_model()'"


class PredictRequest(BaseModel):
    """A time-ordered window of raw readings (channel name → value, plus `t` in seconds)."""

    rows: list[dict[str, float]] = Field(min_length=1)


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

    @app.post("/predict")
    def predict(body: PredictRequest) -> dict[str, Any]:
        model: KeyframeModel | None = state["model"]
        if model is None:
            raise HTTPException(status_code=503, detail="Model files missing.")
        frame = pd.DataFrame(body.rows)
        required = list(explain.SENSOR_GROUPS)
        missing = [c for c in required if c not in frame.columns]
        if missing:
            raise HTTPException(
                status_code=422, detail=f"Missing required channels: {', '.join(missing)}"
            )
        if "t" not in frame.columns:
            raise HTTPException(status_code=422, detail="Each row needs a time `t` in seconds.")
        warns = [
            f"Ignored unknown channel '{c}'."
            for c in frame.columns
            if c not in explain.SENSOR_GROUPS and c not in EXCLUDED_COLUMNS
        ]
        frame = frame[[*required, "t"]].astype(float).sort_values("t").reset_index(drop=True)
        span = float(frame["t"].iloc[-1] - frame["t"].iloc[0])
        if span < WINDOW_S:
            warns.append(
                f"Window covers {span / 60:.1f} min, shorter than 15 min: "
                "long-window features are still warming up."
            )
        proba = model.predict_proba(frame)
        preds = proba.add_prefix("proba_").assign(
            run="run", t=frame["t"], y_pred=proba.idxmax(axis=1)
        )
        alarms = sustained_alarm(
            preds, model.alarm["min_duration_s"], model.alarm["min_probability"]
        )
        last = proba.iloc[-1]
        return {
            "mode": "window",
            "probabilities": {k: float(v) for k, v in last.items()},
            "predicted_class": str(last.idxmax()),
            "alarm": str(alarms.iloc[-1]),
            "alarm_settings": model.alarm,
            "warnings": warns,
        }

    return app


app = create_app()
