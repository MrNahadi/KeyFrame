"""Read a release CSV's three-row header (full name, symbol, unit) into a DataFrame.

Data start on row 4. Symbols repeat across columns (``Pmax``, ``Pmin``, ``Wi``,
``We``) so they are metadata only, never keys: the DataFrame is keyed by the
full variable names from row 1.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

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
