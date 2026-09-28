"""Read a release CSV's three-row header (full name, symbol, unit) into a DataFrame.

Data start on row 4. Symbols repeat across columns (``Pmax``, ``Pmin``, ``Wi``,
``We``) so they are metadata only, never keys: the DataFrame is keyed by the
full variable names from row 1.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from keyframe import paths, splits

RAW_VOLTAGE_UNIT = "V"
RAW_VOLTAGE_SYMBOLS = {
    "Pl_lo",
    "Pl_fuel",
    "Pl_water1",
    "Pl_water2",
    "Pl_loturb",
    "Pl_valve",
}
INT_COLUMNS = {"Anomaly State"}


class ColumnInfo:
    """Per-column metadata from header rows 2 and 3: symbol, unit and raw-voltage flag."""

    def __init__(self, frame: pd.DataFrame) -> None:
        self.frame = frame

    def __len__(self) -> int:
        return len(self.frame)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ColumnInfo):
            return NotImplemented
        return self.frame.equals(other.frame)


def _build_column_info(full_names: list[str], symbols: list[str], units: list[str]) -> ColumnInfo:
    is_raw_voltage = [
        symbol in RAW_VOLTAGE_SYMBOLS and unit == RAW_VOLTAGE_UNIT
        for symbol, unit in zip(symbols, units, strict=True)
    ]
    frame = pd.DataFrame(
        {
            "full_name": full_names,
            "symbol": symbols,
            "unit": units,
            "is_raw_voltage": is_raw_voltage,
        }
    )
    return ColumnInfo(frame)


def read_csv_with_header(path: str | Path) -> tuple[pd.DataFrame, ColumnInfo]:
    """Read a release CSV keyed by full variable names, with its ColumnInfo table."""
    header = pd.read_csv(path, header=None, nrows=3, dtype=str, keep_default_na=False)
    full_names = header.iloc[0].tolist()
    symbols = header.iloc[1].tolist()
    units = header.iloc[2].tolist()

    data = pd.read_csv(path, header=None, skiprows=3, names=full_names, na_values=[""])
    for column in data.columns:
        data[column] = data[column].astype("int64" if column in INT_COLUMNS else "float64")

    column_info = _build_column_info(full_names, symbols, units)
    return data, column_info


FAULT_CODES = {
    "AC_Fouling": "AC",
    "AF_Clogging": "AF",
    "Clogged_Injector_Nozzle": "INJ",
    "Injector_Nozzle": "INJ",
    "CW_Pump_Cavitation": "CW",
    "Pump_Cavitation": "CW",
    "Turbine_Degradation": "TD",
}


def _fault_type(path: Path) -> str:
    if path.stem == "Reference_Data":
        return "Normal"
    for candidate in (path.stem, path.parent.name):
        for prefix, code in FAULT_CODES.items():
            if candidate.startswith(prefix):
                return code
    raise ValueError(f"load_run: no fault type for {path}")


def _nominal_load(path: Path, dataset_index: pd.DataFrame) -> str | float:
    for candidate in (path.name, f"{path.parent.name}/{path.name}"):
        match = dataset_index.loc[dataset_index["file_name"] == candidate, "nominal_load"]
        if not match.empty:
            return str(match.iloc[0])
    return float("nan")


def load_run(path: str | Path, dataset_index: pd.DataFrame | None = None) -> pd.DataFrame:
    """Read one release CSV and add run/fault_type/label/t/load_bin/nominal_load."""
    path = Path(path)
    data, _ = read_csv_with_header(path)
    if dataset_index is None:
        dataset_index = pd.read_csv(paths.RAW / "dataset_index.csv")

    data = data.copy()
    data["run"] = path.stem
    data["fault_type"] = _fault_type(path)

    if path.stem == "Reference_Data":
        data["label"] = "Normal"
        data["t"] = data["Time"] - data["Time"].iloc[0]
    else:
        data["label"] = data["fault_type"].where(data["Anomaly State"] == 1, "Normal")
        data["t"] = data["Time_rel"]

    data["load_bin"] = splits.load_bin(data["Shaft Power"])
    data["nominal_load"] = _nominal_load(path, dataset_index)
    return data


def load_all(raw_dir: str | Path = paths.RAW) -> pd.DataFrame:
    """Concatenate every run listed in ``dataset_index.csv`` that is present under ``raw_dir``.

    The lockbox run (``download.LOCKBOX_FILE``) stays listed in the index but lives
    under ``data/lockbox``, not ``data/raw``, so it is skipped here.
    """
    raw_dir = Path(raw_dir)
    dataset_index = pd.read_csv(raw_dir / "dataset_index.csv")
    file_paths = sorted(
        raw_dir / name for name in dataset_index["file_name"] if (raw_dir / name).exists()
    )
    frames = [load_run(file_path, dataset_index=dataset_index) for file_path in file_paths]
    return pd.concat(frames, ignore_index=True, sort=False)
