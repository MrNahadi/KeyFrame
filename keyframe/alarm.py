"""Row predictions turned into sustained per-run alarms, and their detection metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def sustained_alarm(
    predictions: pd.DataFrame, min_duration_s: float, min_probability: float
) -> pd.Series:
    """Per-run, causal alarm: a fault class is active once every prediction over the
    trailing ``min_duration_s`` seconds of that run is that class with probability
    at least ``min_probability``. Never crosses a run boundary or looks ahead.

    Expects ``run``, ``t``, ``y_pred`` and one ``proba_<class>`` column per class.
    Returns an ``alarm`` series (``Normal`` or a fault class) aligned to ``predictions``.
    """
    alarm = pd.Series("Normal", index=predictions.index, name="alarm")
    for _, group in predictions.groupby("run", sort=False):
        group = group.sort_values("t")
        classes = group["y_pred"].to_numpy()
        times = group["t"].to_numpy(dtype=float)
        own_proba = np.array(
            [
                group[f"proba_{cls}"].iat[i] if f"proba_{cls}" in group.columns else np.nan
                for i, cls in enumerate(classes)
            ]
        )
        confident = own_proba >= min_probability

        streak_start: int | None = None
        streak_class: str | None = None
        for i, idx in enumerate(group.index):
            if confident[i]:
                if streak_class != classes[i]:
                    streak_start = i
                    streak_class = classes[i]
            else:
                streak_start = None
                streak_class = None
            if (
                streak_start is not None
                and streak_class != "Normal"
                and times[i] - times[streak_start] >= min_duration_s
            ):
                alarm.at[idx] = streak_class
    return alarm


MIN_DURATIONS_S: tuple[float, ...] = (30, 60, 120, 300)
MIN_PROBABILITIES: tuple[float, ...] = (0.5, 0.6, 0.7, 0.8)
MAX_FALSE_ALARM_RATE = 0.05


def choose_alarm_params(predictions: pd.DataFrame, switch_on: pd.DataFrame) -> dict:
    """Grid search (R10) over ``MIN_DURATIONS_S`` x ``MIN_PROBABILITIES`` on ``predictions``.

    Picks the combination with the lowest median detection delay among those whose
    false alarm rate is at most ``MAX_FALSE_ALARM_RATE``, falling back to the lowest
    false alarm rate if none qualifies. ``predictions`` should be inner-fold-only
    (never the outer test rows) so the outer fold never chooses its own parameters.
    Returns a dict with ``min_duration_s``, ``min_probability`` and that combination's
    metrics from :func:`alarm_metrics`.
    """
    qualifying: dict | None = None
    fallback: dict | None = None
    for min_duration_s in MIN_DURATIONS_S:
        for min_probability in MIN_PROBABILITIES:
            alarms = predictions.assign(
                alarm=sustained_alarm(predictions, min_duration_s, min_probability)
            )
            metrics = alarm_metrics(alarms, switch_on)
            candidate = {
                "min_duration_s": min_duration_s,
                "min_probability": min_probability,
                **metrics.to_dict(),
            }
            if fallback is None or candidate["false_alarm_rate"] < fallback["false_alarm_rate"]:
                fallback = candidate
            if candidate["false_alarm_rate"] <= MAX_FALSE_ALARM_RATE and (
                qualifying is None or _delay_key(candidate) < _delay_key(qualifying)
            ):
                qualifying = candidate
    assert fallback is not None  # MIN_DURATIONS_S x MIN_PROBABILITIES is never empty
    return qualifying if qualifying is not None else fallback


def _delay_key(candidate: dict) -> float:
    delay = candidate["median_detection_delay_s"]
    return float("inf") if pd.isna(delay) else delay


def detection_delay(alarms: pd.DataFrame, switch_on: pd.DataFrame) -> pd.DataFrame:
    """Per run with a switch-on: time from switch-on to the first fault alarm that
    starts (transitions from a different alarm state) at or after switch-on, and its
    class. ``delay_s`` is NaN and ``class`` is None if no such alarm ever starts.

    Expects ``alarms`` with ``run``, ``t``, ``alarm``; ``switch_on`` with ``run``, ``t``
    (NaN ``t`` for runs without a switch-on, which are skipped).
    """
    rows: list[dict[str, object]] = []
    for run, t0 in zip(switch_on["run"], switch_on["t"], strict=True):
        if pd.isna(t0):
            continue
        run_alarms = alarms.loc[alarms["run"] == run].sort_values("t")
        previous = run_alarms["alarm"].shift(1, fill_value="Normal")
        is_onset = (run_alarms["alarm"] != "Normal") & (run_alarms["alarm"] != previous)
        onsets = run_alarms.loc[is_onset & (run_alarms["t"] >= t0)]
        if onsets.empty:
            rows.append({"run": run, "delay_s": float("nan"), "class": None})
        else:
            first = onsets.iloc[0]
            rows.append({"run": run, "delay_s": float(first["t"] - t0), "class": first["alarm"]})
    return pd.DataFrame(rows, columns=["run", "delay_s", "class"])


def alarm_metrics(alarms: pd.DataFrame, switch_on: pd.DataFrame) -> pd.Series:
    """Alarm-level summary: false alarm rate (share of healthy rows under an active
    alarm), median detection delay over runs, share of runs detected, and correct-class
    share of first alarms.

    Expects ``alarms`` with ``run``, ``t``, ``y_true``, ``alarm``; ``switch_on`` as for
    :func:`detection_delay`.
    """
    healthy = alarms["y_true"] == "Normal"
    false_alarm_rate = (
        float((alarms.loc[healthy, "alarm"] != "Normal").mean()) if healthy.any() else float("nan")
    )

    delays = detection_delay(alarms, switch_on)
    detected = delays["delay_s"].notna()
    share_detected = float(detected.mean()) if len(delays) else float("nan")
    median_delay = (
        float(delays.loc[detected, "delay_s"].median()) if detected.any() else float("nan")
    )

    correct = []
    for _, row in delays.loc[detected].iterrows():
        run_true = alarms.loc[
            (alarms["run"] == row["run"]) & (alarms["y_true"] != "Normal"), "y_true"
        ]
        correct.append(bool(len(run_true)) and row["class"] == run_true.mode().iat[0])
    correct_class_share = float(np.mean(correct)) if correct else float("nan")

    return pd.Series(
        {
            "false_alarm_rate": false_alarm_rate,
            "median_detection_delay_s": median_delay,
            "share_detected": share_detected,
            "correct_class_share": correct_class_share,
        }
    )
