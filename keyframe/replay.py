"""Replay JSON for one run: predictions and explanations from held-out fold models (R5)."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from keyframe import alarm, evaluate, experiments, explain, lockbox, paths, predict, splits
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


def _finite_or_none(value: Any) -> Any:
    """Recursively replace NaN and infinities with None (JSON null)."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: _finite_or_none(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_finite_or_none(v) for v in value]
    return value


def to_strict_json(value: Any, indent: int | None = None) -> str:
    """JSON that browsers can parse: NaN and infinities become null (Python's default
    writer emits bare NaN, which is not valid JSON)."""
    separators = (",", ":") if indent is None else None
    return json.dumps(_finite_or_none(value), separators=separators, indent=indent, allow_nan=False)


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
    feature_frames: dict[int, pd.DataFrame] = {}
    for i in _thin_positions(t, switch_on_t):
        sensors = {}
        for key, (label, column, unit) in KEY_SENSORS.items():
            value = spread.iloc[i] if column is None else run[column].iloc[i]
            sensors[key] = {"label": label, "value": float(value), "unit": unit}
        model = row_models[i]
        if id(model) not in feature_frames:
            feature_frames[id(model)] = model.features(run)
        explained = model.explain(run, i, feature_frame=feature_frames[id(model)])
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


REFERENCE_SEGMENT_S = 1800.0
MAX_FILE_BYTES = 2_000_000
MAX_TOTAL_BYTES = 30_000_000
FAULT_NAMES = {
    "AC_Fouling": "Air cooler fouling",
    "AF_Clogging": "Air filter clogging",
    "CW_Pump_Cavitation": "Cooling water pump cavitation",
    "Turbine_Degradation": "Turbine degradation",
}
INJECTOR_RUN = "Clogged_Injector_Nozzle1_40_60_85_Load"
REFERENCE_RUN = "Reference_Data"


def replay_title(run_id: str) -> str:
    """Plain-words title for a run id such as `Turbine_Degradation_40_Load` or `Reference_60`."""
    if run_id == INJECTOR_RUN:
        return "Clogged injector nozzle 1 with the load stepped through 40%, 60% and 85%"
    if run_id.startswith("Reference_"):
        return f"Healthy reference at {run_id.rsplit('_', 1)[1]}% load"
    stem, load = run_id.removesuffix("_Load").rsplit("_", 1)
    return f"{FAULT_NAMES[stem]} at {load}% load"


def replay_run_ids(table: pd.DataFrame) -> list[str]:
    """Every exported run id: the fixed-load fault runs, the injector run, one reference per bin."""
    faults = sorted(r for r in table["run"].unique() if r not in (INJECTOR_RUN, REFERENCE_RUN))
    return [*faults, INJECTOR_RUN, *(f"Reference_{b}" for b in splits.LOAD_BINS)]


def reference_segment(table: pd.DataFrame, load: int) -> pd.DataFrame:
    """First 30 minutes of the healthy run spent in one load bin, named `Reference_<load>`."""
    ref = table[(table["run"] == REFERENCE_RUN) & (table["load_bin"] == load)].sort_values("t")
    times = ref["t"].to_numpy(dtype=float)
    stretch_start = previous = times[0]
    for value in times:
        if value - previous > 60:  # a gap: another load bin sat in between
            stretch_start = value
        previous = value
        if value - stretch_start >= REFERENCE_SEGMENT_S:
            segment = ref[(ref["t"] >= stretch_start) & (ref["t"] <= value)]
            return segment.assign(run=f"Reference_{load}")
    raise ValueError(f"no {REFERENCE_SEGMENT_S:g} s stretch at load {load}")


def fold_models(table: pd.DataFrame, bins: list[int]) -> dict[int, KeyframeModel]:
    """Leave-one-load-out XGBoost models for the given bins, each with its outer fold's tuned
    params and the alarm settings chosen for that fold, as in the locked evaluation."""
    models = {}
    for bin_value, train_index, _ in splits.lolo_folds(table):
        if int(bin_value) in bins:
            params = experiments.load_tuned_params(lockbox.MODEL, bin_value)
            models[int(bin_value)] = KeyframeModel.fit(
                table.loc[train_index], params, predict.fold_alarm_settings(int(bin_value))
            )
    return models


def alarm_delay_s(replay: dict[str, Any]) -> float | None:
    """Seconds from switch-on to the first alarm frame; None if healthy or never alarmed."""
    switch_on = replay["switch_on_t"]
    if switch_on is None:
        return None
    for frame in replay["frames"]:
        if frame["t"] >= switch_on and frame["alarm"] != "Normal":
            return frame["t"] - switch_on
    return None


def export_replays(
    table: pd.DataFrame,
    run_ids: list[str] | None = None,
    directory: Path = paths.MODELS / "replays",
) -> Path:
    """Write `<run>.json` per run and merge its entry into `index.json`; enforce size limits."""
    directory.mkdir(parents=True, exist_ok=True)
    columns = list(dict.fromkeys(["run", "t", "label", "load_bin", *explain.SENSOR_GROUPS]))
    index_path = directory / "index.json"
    index = {e["id"]: e for e in json.loads(index_path.read_text())} if index_path.exists() else {}
    for run_id in run_ids or replay_run_ids(table):
        if run_id.startswith("Reference_"):
            run = reference_segment(table, int(run_id.rsplit("_", 1)[1]))
        else:
            run = table[table["run"] == run_id]
        run = run[columns].reset_index(drop=True)
        bins = sorted(int(b) for b in run["load_bin"].unique())
        replay = build_replay(run, fold_models(table, bins))
        text = to_strict_json(replay)
        if len(text.encode()) > MAX_FILE_BYTES:
            raise ValueError(f"{run_id} replay is {len(text)} bytes, over {MAX_FILE_BYTES}")
        (directory / f"{run_id}.json").write_text(text)
        index[run_id] = {
            "id": run_id,
            "title": replay_title(run_id),
            "duration_s": float(run["t"].max() - run["t"].min()),
            "switch_on_t": replay["switch_on_t"],
            "alarm_delay_s": alarm_delay_s(replay),
        }
    index_path.write_text(to_strict_json(list(index.values()), indent=1))
    total = sum(p.stat().st_size for p in directory.glob("*.json"))
    if total > MAX_TOTAL_BYTES:
        raise ValueError(f"replays total {total} bytes, over {MAX_TOTAL_BYTES}")
    return index_path
