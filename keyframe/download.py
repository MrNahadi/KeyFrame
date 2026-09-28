"""Fetch the Marine Engine Fault Dataset v1.0 from Zenodo and set the lockbox aside.

Run from the repo root:

    uv run python -m keyframe.download            # download from Zenodo
    uv run python -m keyframe.download --zip PATH # use a zip you already have

The zip is checked against the pinned MD5 (published by Zenodo) and SHA-256 before
anything is extracted. The two-hole injector run goes to ``data/lockbox/``, never
``data/raw/``, so no notebook can train on it by accident.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from keyframe import paths

RECORD_URL = "https://zenodo.org/records/19857425"
ZIP_NAME = "Marine_Engine_Fault_Data_v1.zip"
ZIP_URL = f"https://zenodo.org/records/19857425/files/{ZIP_NAME}?download=1"
ZIP_MD5 = "f4d246c1bb46e05b26e56221acc2606c"
ZIP_SHA256 = "3fba7aa0c288ae1bc05383fb54bf67cbde209d61b26e3e811d4bc2f22f97442b"
ZIP_PREFIX = "Marine_Engine_Fault_Data/"
LOCKBOX_FILE = "Clogged_Injector_Nozzle2_LoadProgram.csv"


class ChecksumError(RuntimeError):
    """The archive does not match the pinned dataset version."""


def file_digests(path: Path) -> tuple[str, str]:
    """Return the (md5, sha256) hex digests of a file."""
    md5, sha = hashlib.md5(), hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            md5.update(chunk)
            sha.update(chunk)
    return md5.hexdigest(), sha.hexdigest()


def verify(path: Path, md5: str = ZIP_MD5, sha256: str = ZIP_SHA256) -> None:
    """Raise ChecksumError unless the file matches both pinned digests."""
    got_md5, got_sha = file_digests(path)
    if got_md5 != md5 or got_sha != sha256:
        raise ChecksumError(
            f"{path.name} does not match dataset v1.0 "
            f"(md5 {got_md5}, expected {md5}; sha256 {got_sha}, expected {sha256}). "
            f"Delete it and download again from {RECORD_URL}."
        )


def fetch(url: str, dest: Path) -> Path:
    """Download url to dest, streaming to disk."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as resp, dest.open("wb") as out:
        shutil.copyfileobj(resp, out)
    return dest


def extract(zip_path: Path, raw_dir: Path, lockbox_dir: Path) -> list[Path]:
    """Extract the release into raw_dir, moving the lockbox run into lockbox_dir.

    Returns the CSV files written to raw_dir. Existing files are replaced, so running
    twice gives the same result.
    """
    written: list[Path] = []
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir() or not info.filename.startswith(ZIP_PREFIX):
                continue
            rel = Path(info.filename[len(ZIP_PREFIX) :])
            if ".." in rel.parts:
                raise ValueError(f"Unsafe path in archive: {info.filename}")
            target = lockbox_dir / rel.name if rel.name == LOCKBOX_FILE else raw_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            if target.suffix == ".csv" and target.parent != lockbox_dir:
                written.append(target)
    return written


def build(zip_path: Path | None = None, data_dir: Path = paths.DATA) -> None:
    """Rebuild data/raw and data/lockbox from Zenodo (or a local copy of the zip)."""
    raw_dir, lockbox_dir = data_dir / "raw", data_dir / "lockbox"
    with tempfile.TemporaryDirectory() as tmp:
        if zip_path is None:
            print(f"Downloading {ZIP_NAME} from Zenodo…")
            zip_path = fetch(ZIP_URL, Path(tmp) / ZIP_NAME)
        verify(zip_path)
        print("Checksum OK (dataset v1.0).")
        for d in (raw_dir, lockbox_dir):
            if d.exists():
                shutil.rmtree(d)
        csvs = extract(zip_path, raw_dir, lockbox_dir)
    runs = [p for p in csvs if p.name not in {"dataset_index.csv", "variable_dictionary.csv"}]
    print(f"Wrote {len(runs)} data files to {raw_dir} and 1 lockbox file to {lockbox_dir}.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--zip", type=Path, help="use a local copy of the dataset zip")
    args = parser.parse_args(argv)
    try:
        build(args.zip)
    except ChecksumError as err:
        print(err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
