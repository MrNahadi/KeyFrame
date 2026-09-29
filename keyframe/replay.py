"""Replay JSON for one run: predictions and explanations from held-out fold models (R5)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd

from keyframe import alarm, evaluate
from keyframe.predict import KeyframeModel

FRAME_STEP_S = 10.0
SPREAD_COLUMNS = ["No.1 Exh.Gas Temp.", "No.2 Exh.Gas Temp.", "No.3 Exh.Gas Temp."]
# key: (label, source column or None for the exhaust spread, unit as in the release headers)
KEY_SENSORS: dict[str, tuple[str, str | None, str]] = {
    "charge_air_pressure": ("Charge air pressure", "Charge Air Press.", "kgf/cm2"),
    "charge_air_temp_after_cooler": (
        "Charge air temperature after cooler",
        "Charge Air IC Air Temp. Out",
        "°C",
    ),
    "turbine_in_temp": ("Turbine inlet temperature", "Exh.Gas Temp. Turbine In", "°C"),
    "turbine_out_temp": ("Turbine outlet temperature", "Exh.Gas Temp. Turbine Out", "°C"),
    "exhaust_temp_spread": ("Exhaust temperature spread (max - min, cylinders 1-3)", None, "°C"),
    "cooling_water_flow": ("Engine cooling water flow", "Engine Cooling water flow", "m3/h"),
    "fresh_cooling_water_pressure": (
        "Fresh cooling water pressure (raw sensor voltage)",
        "Fresh Cooling Water Press.",
        "V",
    ),
    "fuel_flow": ("Fuel flow", "Fuel Flow", "m3/h"),
}


def _thin_positions(t: np.ndarray, switch_on_t: float | None) -> list[int]:
    """Positions of the first row in each `FRAME_STEP_S` bucket, plus the switch-on row."""
    keep: list[int] = []
    last_bucket = None
    for i, value in enumerate(t):
        bucket = int(value // FRAME_STEP_S)
        if bucket != last_bucket:
            keep.append(i)
            last_bucket = bucket
    if switch_on_t is not None:
        keep.append(int(np.flatnonzero(t == switch_on_t)[0]))
    return sorted(set(keep))


def _fold_proba(
    run: pd.DataFrame, fold_model: KeyframeModel | Mapping[int, KeyframeModel]
) -> tuple[pd.DataFrame, list[KeyframeModel], list[int | None]]:
    """Probabilities, and per row the model and load bin that produced them."""
    models: dict[int | None, KeyframeModel]
    if isinstance(fold_model, KeyframeModel):
        models = {None: fold_model}
        bins = pd.Series([None] * len(run), index=run.index, dtype=object)
    else:
        models = {int(b): m for b, m in fold_model.items()}
        bins = run["load_bin"].astype(int)
    proba = pd.DataFrame(index=run.index, columns=next(iter(models.values())).classes, dtype=float)
    for bin_value, model in models.items():
        mask = (
            np.ones(len(run), dtype=bool) if bin_value is None else (bins == bin_value).to_numpy()
        )
        if mask.any():
            # features are causal rolling stats over the whole run, so score the whole run
            proba.loc[mask] = model.predict_proba(run).loc[mask].to_numpy()
    row_models = [models[b if b is None else int(b)] for b in bins]
    return proba, row_models, [None if b is None else int(b) for b in bins]


def build_replay(
    run: pd.DataFrame,
    fold_model: KeyframeModel | Mapping[int, KeyframeModel],
    *,
    git_commit: str | None = None,
) -> dict[str, Any]:
    """JSON-ready replay of one run of raw readings (`run`, `t`, `label`, `load_bin`, sensors).

    `fold_model` is the leave-one-load-out model that never saw the run's load, or a mapping
    from load bin to such a model, in which case each row uses the model of its own bin."""
    run = run.sort_values("t").reset_index(drop=True)
    t = run["t"].to_numpy(dtype=float)
    labels = run["label"].astype(str)
    faulty = run.loc[labels != "Normal"]
    switch_on_t = float(faulty["t"].min()) if len(faulty) else None
    fault = str(faulty["label"].iloc[0]) if len(faulty) else "Normal"

    proba, row_models, bins = _fold_proba(run, fold_model)
    first = row_models[0]
    predictions = pd.DataFrame({"run": "run", "t": t, "y_pred": proba.idxmax(axis=1)})
    for cls in proba.columns:
        predictions[f"proba_{cls}"] = proba[cls]
    alarms = alarm.sustained_alarm(
        predictions, first.alarm["min_duration_s"], first.alarm["min_probability"]
    )

    spread = run[SPREAD_COLUMNS].max(axis=1) - run[SPREAD_COLUMNS].min(axis=1)
    frames = []
    for i in _thin_positions(t, switch_on_t):
        sensors = {}
        for key, (label, column, unit) in KEY_SENSORS.items():
            value = spread.iloc[i] if column is None else run[column].iloc[i]
            sensors[key] = {"label": label, "value": float(value), "unit": unit}
        explained = row_models[i].explain(run, i)
        frames.append(
            {
                "t": float(t[i]),
                "sensors": sensors,
                "probabilities": {str(c): float(p) for c, p in proba.iloc[i].items()},
                "alarm": str(alarms.iloc[i]),
                "predicted_class": explained["predicted_class"],
                "shap_groups": explained["groups"],
                "top_features": explained["top_features"][:3],
            }
        )

    held_out = sorted({b for b in bins if b is not None})
    fold_text = ", ".join(str(b) for b in held_out) if held_out else "unknown"
    commit = git_commit if git_commit is not None else evaluate.git_commit()
    return {
        "run": str(run["run"].iloc[0]),
        "fault": fault,
        "nominal_load": int(pd.Series(bins).mode().iloc[0]) if held_out else None,
        "switch_on_t": switch_on_t,
        "sampling_note": f"frames thinned to one every {FRAME_STEP_S:g} s of t; "
        "the switch-on frame is kept exactly",
        "provenance": "predictions from the model trained without this run's load "
        f"(leave-one-load-out fold {fold_text}); git commit {commit}",
        "frames": frames,
    }
