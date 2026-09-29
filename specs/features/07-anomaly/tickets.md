# 07 Anomaly detection: tickets

## T-001: Detector interface and Isolation Forest

Status: done
Blocked by:
Slice: A healthy-only detector interface with Isolation Forest behind it.
Test seam: `keyframe.anomaly.IsolationForestDetector` (`fit`, `score`)
Context: requirements R1-R3; `grep -n '^def \|^class ' keyframe/features.py | head -30`
Acceptance:
- [x] Synthetic test: points far from a healthy cloud score higher than points inside it
- [x] Standardisation and imputation use training healthy rows only (test)
Notes:

## T-002: PCA with Hotelling T² and Q

Status: done
Blocked by: T-001
Slice: A PCA detector that reports T², Q and their combined score.
Test seam: `keyframe.anomaly.PCADetector`
Context: requirements R2; `grep -n 'class IsolationForestDetector' -A40 keyframe/anomaly.py`
Acceptance:
- [x] Synthetic test: a shift along a retained component raises T²; a shift orthogonal to them raises Q
- [x] Combined score normalised by training 99th percentiles (test)
Notes:

## T-003: Autoencoder detector

Status: done
Blocked by: T-001
Slice: A small MLP autoencoder that scores reconstruction error.
Test seam: `keyframe.anomaly.AutoencoderDetector`
Context: requirements R2; `grep -n 'class IsolationForestDetector' -A40 keyframe/anomaly.py`
Acceptance:
- [x] Synthetic test: off-manifold points reconstruct worse than healthy ones; seeded fit is reproducible
Notes:

## T-004: Anomaly experiment and all runs

Status: done
Blocked by: T-002, T-003
Slice: Per-row held-out scores for every detector and fold, fitted on training healthy rows only.
Test seam: `uv run python -m keyframe.experiments anomaly --detector <d> --fold <bin>`
Context: requirements R3-R5; `grep -n 'def run_ablation\|def load_ablation\|add_parser' keyframe/experiments.py`
Acceptance:
- [x] Spy test: `fit` sees no fault row and no held-out-load row
- [x] 12 score files written (one foreground command each, each under 9 minutes)
- [x] `reports/results/05_anomaly.csv` with pooled and per-fold AUROC per detector, and per-class AUROC
Notes:

## T-008: Residual input arm for the detectors

Status: done
Blocked by: T-004
Slice: Every detector can run on load-normalised inputs; all 12 residual runs exist and the AUROC table covers both arms.
Test seam: `keyframe.anomaly.detector_inputs(df, arm)`; `uv run python -m keyframe.experiments anomaly --detector <d> --fold <bin> --inputs residual`
Context: requirements R1b, R4-R5; `docs/adr/0008-anomaly-detector-inputs.md`; `grep -n 'class HealthyEngineResiduals' -A12 keyframe/features.py`; `grep -n 'def run_anomaly' -A45 keyframe/experiments.py`
Acceptance:
- [x] Test: the residual arm's columns contain no raw level, no rolling mean and none of the three residual inputs; the residual model is fitted on training-fold healthy rows only (spy)
- [x] 12 residual score files written (one foreground command each, under 9 minutes)
- [x] `reports/results/05_anomaly.csv` has an `inputs` column with rows for both arms
Notes:

## T-005: Thresholds, alarms and detection delay

Status: open
Blocked by: T-008
Slice: For both input arms (residual primary), each detector's scores become sustained alarms with a 2% training-fold false alarm budget, giving detection delay per run.
Test seam: `keyframe.anomaly.threshold_for_far`, alarm helpers from `keyframe.alarm`
Context: requirements R6; `grep -n '^def ' keyframe/alarm.py`
Acceptance:
- [ ] Threshold chosen from training healthy rows only (test)
- [ ] `reports/results/05_alarms.csv`: per detector, per run delay, alarm-level false alarm rate
Notes:
- Parked stash: T-005 parked (work started on the raw arm only before T-008 was added; pop it, then extend to both arms)

## T-006: Notebook 05 and findings

Status: open
Blocked by: T-005
Slice: Notebook 05 leads with the residual arm and presents AUROC, per-class results, delays and score traces, against the brief's targets.
Test seam: executing `notebooks/05_anomaly_detection.py`
Context: requirements R7; `grep -n '^# %%' notebooks/04_modelling.py`; `head -3 reports/results/05_anomaly.csv reports/results/05_alarms.csv`
Acceptance:
- [ ] `05_roc.png`, `05_detection_delay.png`, `05_scores_switch_on.png`
- [ ] Targets marked met / not met; comparison with notebook 04's classifier delays
- [ ] Executes under 5 minutes; committed
- [ ] Diagnostic section (selects nothing, changes no score): AUROC per detector and arm with "healthy" restricted to reference-file rows (steady running) versus with "healthy" restricted to pre-fault segments, plus score distributions by source (reference, pre-fault, faulty) per fold (`05_scores_by_source.png`)
Notes:
- Planner: both arms land near chance (pooled AUROC raw 0.50-0.56, residual 0.42-0.53) and several per-class AUROCs are below 0.5 (AF, CW), i.e. faulty rows look more normal than healthy ones. Hypothesis to test in the diagnostic: the healthy rows at the held-out load include pre-fault warm-up segments that are not at steady state (see `reports/figures/00_switch_on.png`), and the detectors correctly flag that non-steady running. Report the outcome either way; ADR 0008's pre-declared primary arm (residual) stays primary regardless of which scores better. State the brief's AUROC target (0.95) as not met if it is not met.
