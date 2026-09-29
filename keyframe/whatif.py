"""What-if baselines: typical healthy readings per load and slider ranges (feature 11, R7)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from keyframe import explain, paths, splits

BASELINES_FILE = "whatif_baselines.json"
SLIDER_CHANNELS: dict[str, str] = {
    "Charge Air Press.": "Charge air pressure",
    "Charge Air IC Air Temp. Out": "Charge air temperature after cooler",
    "Exh.Gas Temp. Turbine In": "Turbine inlet temperature",
    "Exh.Gas Temp. Turbine Out": "Turbine outlet temperature",
    "No.1 Exh.Gas Temp.": "Cylinder 1 exhaust temperature",
    "No.2 Exh.Gas Temp.": "Cylinder 2 exhaust temperature",
    "No.3 Exh.Gas Temp.": "Cylinder 3 exhaust temperature",
    "Fresh Cooling Water Press.": "Fresh cooling water pressure",
    "Engine Cooling water flow": "Engine cooling water flow",
    "Fuel Flow": "Fuel flow",
}


def build_baselines(clean: pd.DataFrame) -> dict:
    """Per load bin: median healthy reading of every model input, plus slider ranges
    (5th to 95th percentile over all rows, healthy and faulty, at that load)."""
    inputs = list(explain.SENSOR_GROUPS)
    loads: dict[str, dict] = {}
    for load in splits.LOAD_BINS:
        at_load = clean[clean["load_bin"] == load]
        healthy = at_load[at_load["label"] == "Normal"]
        loads[str(load)] = {
            "reading": {c: float(healthy[c].median()) for c in inputs},
            "sliders": {
                c: {
                    "label": label,
                    "min": float(at_load[c].quantile(0.05)),
                    "max": float(at_load[c].quantile(0.95)),
                }
                for c, label in SLIDER_CHANNELS.items()
            },
        }
    return {"load_bins": list(splits.LOAD_BINS), "loads": loads}


def export_baselines(directory: Path = paths.MODELS) -> Path:
    """Write `whatif_baselines.json` from the clean table."""
    clean = pd.read_parquet(paths.PROCESSED / "clean.parquet")
    out = directory / BASELINES_FILE
    directory.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_baselines(clean), indent=1))
    return out
