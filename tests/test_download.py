"""The data download refuses the wrong archive and always sets the lockbox aside."""

import zipfile
from pathlib import Path

import pytest

from keyframe import download, paths


def make_zip(path: Path) -> Path:
    prefix = download.ZIP_PREFIX
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(f"{prefix}Reference_Data.csv", "a\n1\n")
        zf.writestr(f"{prefix}AC_Fouling/AC_Fouling_40_Load.csv", "a\n1\n")
        zf.writestr(f"{prefix}Injector_Nozzle/{download.LOCKBOX_FILE}", "a\n1\n")
        zf.writestr(f"{prefix}README.md", "readme")
    return path


def test_verify_rejects_a_different_archive(tmp_path: Path) -> None:
    fake = make_zip(tmp_path / "fake.zip")
    with pytest.raises(download.ChecksumError, match="does not match dataset v1.0"):
        download.verify(fake)


def test_verify_accepts_matching_digests(tmp_path: Path) -> None:
    fake = make_zip(tmp_path / "fake.zip")
    md5, sha = download.file_digests(fake)
    download.verify(fake, md5=md5, sha256=sha)


def test_extract_moves_the_lockbox_run_out_of_raw(tmp_path: Path) -> None:
    fake = make_zip(tmp_path / "fake.zip")
    raw, lockbox = tmp_path / "raw", tmp_path / "lockbox"

    written = download.extract(fake, raw, lockbox)

    assert (lockbox / download.LOCKBOX_FILE).exists()
    assert not list(raw.rglob(download.LOCKBOX_FILE))
    assert sorted(p.relative_to(raw).as_posix() for p in written) == [
        "AC_Fouling/AC_Fouling_40_Load.csv",
        "Reference_Data.csv",
    ]


def test_extract_twice_gives_the_same_tree(tmp_path: Path) -> None:
    fake = make_zip(tmp_path / "fake.zip")
    raw, lockbox = tmp_path / "raw", tmp_path / "lockbox"
    download.extract(fake, raw, lockbox)
    first = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*") if p.is_file())
    download.extract(fake, raw, lockbox)
    second = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*") if p.is_file())
    assert first == second


@pytest.mark.data
def test_real_data_folder_has_14_runs_and_the_reference() -> None:
    if not paths.RAW.exists():
        pytest.skip("dataset not downloaded")
    csvs = {p.name for p in paths.RAW.rglob("*.csv")} - {
        "dataset_index.csv",
        "variable_dictionary.csv",
    }
    assert len(csvs) == 15
    assert "Reference_Data.csv" in csvs
    assert download.LOCKBOX_FILE not in csvs
    assert (paths.LOCKBOX / download.LOCKBOX_FILE).exists()
