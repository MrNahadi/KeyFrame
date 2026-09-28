"""Shared fixtures for writing synthetic three-row-header CSVs."""

from pathlib import Path

import pytest


@pytest.fixture
def write_three_row_csv(tmp_path: Path):
    """Write a CSV with full-name/symbol/unit header rows and return its path."""

    def _write(
        full_names: list[str], symbols: list[str], units: list[str], rows: list[list[str]]
    ) -> Path:
        path = tmp_path / "scenario.csv"
        lines = [
            ",".join(full_names),
            ",".join(symbols),
            ",".join(units),
            *(",".join(row) for row in rows),
        ]
        path.write_text("\n".join(lines) + "\n")
        return path

    return _write
