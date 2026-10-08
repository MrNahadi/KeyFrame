# 16 Autoresearch: trial run on fold 75

8 October 2026. Branch `autoresearch/trial-fold75` (local, not pushed). The trial ran 20 experiments under `autoresearch/program.md`, applying the keep rules by script. Its purpose was to measure run time, seed noise and keep rate, and to find out whether the protocol holds up, **not** to produce a result. `examine` was not run, and nothing here is a v2 score. Search agents must not read this file (`program.md`, "Do not read").

All scores are inner leave-one-load-out macro F1 over loads 40, 60 and 85 (load 75 is never touched), as 3-seed means.

## Part 1: before amendment 1 (scores included runs seen in training)

| Commit | Macro F1 | Seed sd | No-day F1 | Status | Change |
|---|---:|---:|---:|---|---|
| c6abdcf | 0.581 | 0.012 | 0.537 | keep | baseline (v1 fold-75 parameters) |
| 6d00c48 | 0.646 | 0.014 | 0.536 | keep | lr 0.05, 300 trees, depth 3 |
| 2dc5819 | 0.582 | 0.001 | | discard | drop 15-minute rolling features |
| 525e580 | 0.560 | 0.017 | | discard | depth 5 |
| 40ccfb1 | 0.593 | 0.017 | | discard | colsample_bytree 0.3 |
| 79c10f6 | 0.644 | 0.010 | | discard | min_child_weight 10 |

An engineer's review (ADR 0013, amendment 1) then showed that healthy readings name their run with 95 to 100% accuracy, and that the injector run and the healthy reference run each span several loads. Part 1's score rewarded recognising those runs, so the trial restarted under the corrected score.

## Part 2: after amendment 1 (unseen runs only)

Baseline ETA = max(0.01, 2 × 0.0141 × √(2/3)) = **0.023**.

| Commit | Macro F1 | Seed sd | No-day F1 | Seen-run F1 | Worst recall | Status | Change |
|---|---:|---:|---:|---:|---:|---|---|
| a07f972 | 0.532 | 0.014 | 0.444 | 0.998 | 0.18 TD | keep | baseline (v1 fold-75 parameters) |
| f2aa561 | 0.560 | 0.008 | 0.411 | 0.978 | 0.20 | **discard-day** | lr 0.05, 300 trees, depth 3 (part 1's keep) |
| f135f69 | 0.322 | 0.017 | | 0.981 | 0.00 CW | discard | healthy-engine residuals instead of raw readings |
| 86e9bf0 | 0.515 | 0.013 | | 1.000 | 0.15 AC | discard | turbocharger features (boost per exhaust temperature, TCH power share) |
| 6479158 | 0.184 | 0.024 | | 0.947 | 0.00 CW | discard | physics features only |
| 78f5835 | 0.375 | 0.033 | | 0.974 | 0.00 AF | discard | rolling means only |
| 1487925 | 0.515 | 0.024 | | 1.000 | 0.16 TD | discard | drop rolling slopes |
| d80f4bc | 0.562 | 0.001 | 0.450 | 0.993 | 0.19 | keep | reg_lambda 30 |
| 3fded48 | 0.500 | 0.020 | | 1.000 | 0.08 TD | discard | LightGBM, small trees |
| 08d8571 | 0.580 | 0.010 | | 0.981 | 0.19 TD | discard | subsample 0.5 |
| 63315b6 | 0.578 | 0.018 | | 0.989 | 0.20 TD | discard | reg_lambda 100 |
| 1d9e113 | 0.568 | 0.003 | | 0.999 | 0.18 TD | discard | min_child_weight 50 |
| 62d94d5 | **0.593** | 0.004 | **0.515** | 0.999 | **0.32** TD | keep | stumps (max_depth 1) |
| e6b64c3 | 0.585 | 0.004 | | 0.998 | 0.31 TD | discard | colsample_bytree 0.8 |
| fe713cb | 0.585 | 0.006 | | 0.999 | 0.31 TD | discard | learning rate 0.07, 160 trees |
| fda410a | 0.560 | 0.009 | | 0.995 | 0.28 AF | discard | drop lube oil channels |

The batch-effect check (`identify`) stayed at 0.865 for every kept change, because none of them changed the feature set. Final trial candidate versus the baseline: `max_depth` 2 → 1, `reg_lambda` 7.58 → 30.

## What the trial shows

1. **The machinery works.** Harness, guards and keep rule all ran without a crash. A step takes 20 s to 7 min (median about 85 s; 300-tree models are the slow ones), so 60 experiments take roughly 1.5 to 3 hours per search on 4 cores.
2. **Seed noise is real and the margin is needed.** One seed moves the score by 0.01 to 0.03. Two changes landed under the margin (subsample 0.5, +0.018; reg_lambda 100, +0.016), and under a plain keep-if-better rule both would have been kept.
3. **The corrections mattered.** Part 1's headline gain (+0.065) shrank to +0.027 once seen-run rows were excluded, and then failed the day-robust gate (no-day F1 fell by 0.033). It came from recognising sessions, and the loop would have kept it without amendment 1.
4. **Session-independent gains are modest but present.** Two keeps took the unseen-run score from 0.532 to 0.593 (+0.060, about 2.6 ETA). The no-day score rose from 0.444 to 0.515, and the worst-class recall (turbine degradation) from 0.18 to 0.32. Both kept changes *reduce* model capacity, which fits a batch-effect problem: the less the model can memorise a session, the better it transfers to a new one.
5. **Seen-run scores tell us nothing.** Rows of the injector and reference runs score 0.95 to 1.00 whatever the model does, so they cannot guide a search.
6. **Feature-only changes did not help** within 20 experiments. Removing raw readings (physics-only, rolling-means-only, residuals) collapsed the score, and the cavitation and air filter classes vanished. With every run recognisable from its healthy readings, single-session channels and cross-session signal are tangled together in the same raw columns.

## Limits of this trial

- One fold, 20 experiments, and the agent that ran it had seen v1's outer results. Its gains are not evidence for v2. They say only that gains above the noise exist on these inner folds.
- Two keeps from 15 experiments, each about 1.3 to 1.4 ETA above the previous best, can still be partly selection luck. Only `examine` on a held-out load can confirm them.

## Recommendation

**Go, with the amended protocol and modest expectations.**
- Run the four searches (`autoresearch/foldK`, K = 40, 60, 75, 85) as four fresh cloud sessions that have not seen this file, each from the `auto-research` baseline. Do not carry the trial's candidate into the fold-75 search.
- Expect zero-shot gains of a few points at most. The batch effect caps what any model can learn from 14 fault runs taken across different sessions.
- The bigger lever is probably the **calibrated** track the reviewer proposed (each run compared with its own known-healthy stretch). It needs its own spec first, including how to handle the injector run, which is faulty from its first reading.
- Ask the dataset authors for the test dates of each run. Day labels would let the harness group folds by session rather than by run, and would turn the batch-effect check into a direct test.
