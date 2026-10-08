# v2: what Karpathy-style autoresearch did for Keyframe

8 October 2026. Feature 16 (autoresearch) with feature 17 (calibrated track) and ADR 0015 (untuned defaults). Protocol: ADR 0013 and its three amendments. The numbers come from `summary.md` (`uv run python -m keyframe.v2report`) and the JSON and TSV files beside it. v1's locked results (ADR 0009) are unchanged.

## The short answer

**Nothing tested today beats v1 on loads it has not seen, and that is the finding.** Four autonomous searches ran 60 experiments each, under a protocol built to stop them fooling themselves. They raised their own development scores, and those gains reversed on the held-out loads. With 4 engine loads and 14 fault runs, this dataset cannot tell a better model from a luckier one through any score computed inside it. The protocol made that visible instead of hiding it.

Along the way, the work produced a more honest view of v1 itself, driven by an outside engineer's review:

- **Every run can be recognised from its healthy readings alone**: 95–100% balanced accuracy, and still 80–100% without the four day-dependent channels.
- **The injector run and the healthy reference run each span several loads**, so v1 had always trained on part of each before being "tested" on another part. Scored on runs it has never seen, v1's macro F1 is **0.404 / 0.818 / 0.500 / 0.517** at 40 / 60 / 75 / 85% load (mean 0.560). The locked mean per load is 0.679.
- **At 75% load, v1 raises an alarm on healthy running from sessions it has not seen**: its false alarm rate there is 0.64 on all healthy rows of unseen runs, and 1.0 after each run's first 20 minutes. Its locked 25% was measured mostly on the reference run.

## What was run

| Step | What | Result |
|---|---|---|
| Trial (fold 75) | 20 experiments, to measure noise and run time | Seed noise ±0.012 to 0.03. The protocol caught a "gain" that was session recognition. |
| Four searches | One fresh cloud session per held-out load, 60 experiments each, keep only gains ≥ noise margin and not worse without day channels | Inner scores rose (below). |
| Examinations | Each search's candidate scored once on its held-out load | v2 far below v1 (below). |
| Calibrated track (feature 17) | Readings compared with each run's own first 20 healthy minutes | No gain (`reports/calibrated/README.md`). |
| Untuned defaults (ADR 0015) | XGBoost library defaults, one pre-registered test | No gain: 0.518 against v1's 0.560. |

## v2 against v1 on held-out loads

Macro F1 on rows of runs unseen in training, mean of 3 seeds:

| Held-out load | v1 | v2 | Search inner score: baseline → examined | Experiments / kept |
|---|---:|---:|---|---|
| 40% | 0.404 | 0.254 | 0.540 → 0.603 | 60 / 7 |
| 60% | 0.818 | 0.299 | 0.196 → 0.381 | 60 / 5 |
| 75% | 0.500 | *pending* | *pending* | *pending* |
| 85% | 0.517 | 0.158 | 0.243 → 0.332 | 60 / 2 |

Fold 40's search kept features measured from each run's start from its fourth keep onward. That breaks the zero-shot rule (ADR 0013, amendment 2), so its v2 candidate is the last compliant keep. Its non-compliant final candidate (inner 0.717) scored 0.325 when examined, still below v1.

## Why the searches failed

1. **The development score measures a different task.** Inside a search, each inner fold trains on two loads and predicts a third. The real task trains on three loads. With so few loads, the two tasks behave differently. v1's own inner and held-out scores disagree (fold 60: 0.196 inner, 0.818 held out), so "better inside" carries little information about "better outside".
2. **The noise margin guards against seed luck, not against a misleading target.** The margin (about 0.02) stopped the loop from keeping changes that only shuffled random seeds. It cannot stop a loop that reliably improves the wrong number.
3. **The searches leaned towards what the inner folds reward.** Folds 60 and 85 moved to healthy-engine residuals and load-free views, which travel well between two training loads. On the held-out load they lost whole classes: cavitation at 60% and air filter clogging at 85% fell to zero recall.
4. **Session recognition is part of every score on this dataset.** Every run is identifiable from healthy data, and each fault type has at most four runs, so any model partly learns sessions. Neither more searching nor calibrating against the run's start removed that.

## What this means for the model

- **Keep v1 as the deployed model.** Report its unseen-run scores (mean 0.560) next to the locked ones, and state its 75% load false alarm problem plainly.
- **Stop optimising against this dataset's internal scores.** More tuning, more features or more search will not give trustworthy gains with 4 loads and 14 fault runs. That covers Optuna, autoresearch and manual work alike.
- **The next real improvement needs new data, not new models.** In order of value:
  1. Repeat runs of each fault on different days. This breaks the link between session and fault and is the only way to measure generalisation honestly.
  2. Test dates for the existing runs, so evaluation can group by day (ask the dataset authors).
  3. A healthy recording made separately from each fault run, to test calibration properly.
  4. More than one injector run, and injector and reference runs that do not span loads.

## Caveats

- The protocol author had seen v1's held-out results before designing the protocol (ADR 0013).
- The search agents worked unattended and were told by message about the 15-minute rule while they ran. One search broke it, and the harness caught it at examination.
- Each examination is one held-out load with at most five fault runs, and seed spread is shown in `summary.md`. Differences of a few points between models are not meaningful here. The gaps above (0.15 to 0.52) are.
