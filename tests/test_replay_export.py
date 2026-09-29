"""Replay export helpers: titles, run list, reference segments and the on-disk files (R6-R7)."""

import json

import numpy as np
import pandas as pd

from keyframe import paths, replay


def test_titles_are_plain_words():
    assert replay.replay_title("Turbine_Degradation_85_Load") == "Turbine degradation at 85% load"
    assert replay.replay_title("Reference_60") == "Healthy reference at 60% load"
    assert "injector" in replay.replay_title(replay.INJECTOR_RUN).lower()


def test_run_ids_are_fourteen_runs_plus_four_references():
    runs = [f"AC_Fouling_{n}_Load" for n in (40, 60)] + [replay.INJECTOR_RUN, replay.REFERENCE_RUN]
    ids = replay.replay_run_ids(pd.DataFrame({"run": runs}))
    assert ids == [
        "AC_Fouling_40_Load",
        "AC_Fouling_60_Load",
        replay.INJECTOR_RUN,
        "Reference_40",
        "Reference_60",
        "Reference_75",
        "Reference_85",
    ]


def test_reference_segment_skips_a_broken_stretch():
    t = np.concatenate([np.arange(0, 300), np.arange(1000, 3000)]).astype(float)
    table = pd.DataFrame({"run": replay.REFERENCE_RUN, "t": t, "load_bin": 40})
    segment = replay.reference_segment(table, 40)
    assert segment["t"].min() == 1000
    assert segment["t"].max() - segment["t"].min() == replay.REFERENCE_SEGMENT_S
    assert set(segment["run"]) == {"Reference_40"}


def test_exported_files_fit_the_limits():
    directory = paths.MODELS / "replays"
    index = json.loads((directory / "index.json").read_text())
    assert len(index) == 18
    for entry in index:
        assert 0 < (directory / f"{entry['id']}.json").stat().st_size < replay.MAX_FILE_BYTES
        assert entry["title"]
    total = sum(p.stat().st_size for p in directory.glob("*.json"))
    assert total < replay.MAX_TOTAL_BYTES


def test_replays_use_each_folds_own_alarm_settings():
    """The demo must show the alarms the locked evaluation scored, not a pooled setting."""
    from keyframe import predict

    alarms = pd.read_csv(paths.RESULTS / "04_alarms.csv")
    for fold in (40, 60, 75, 85):
        row = alarms[(alarms["model"] == "xgboost") & (alarms["fold"] == fold)].iloc[0]
        assert predict.fold_alarm_settings(fold) == {
            "min_duration_s": float(row["min_duration_s"]),
            "min_probability": float(row["min_probability"]),
        }


def test_replay_alarm_delays_match_the_locked_evaluation():
    """Each replay's alarm delay equals the evaluated one, up to the 10 s frame thinning."""
    index = json.loads((paths.MODELS / "replays" / "index.json").read_text())
    delays = {r["id"]: r["alarm_delay_s"] for r in index}
    alarms = pd.read_csv(paths.RESULTS / "04_alarms.csv")
    evaluated = alarms[alarms["model"] == "xgboost"].set_index("run")["delay_s"]
    for run, delay in evaluated.items():
        if pd.isna(delay):
            assert delays[run] is None, run
        else:
            assert delays[run] is not None, run
            assert 0 <= delays[run] - delay < 10, (run, delays[run], delay)
