# 07 Anomaly detection: tickets

## T-001: Detector interface and Isolation Forest

Status: open
Blocked by:
Slice: A healthy-only detector interface with Isolation Forest behind it.
Test seam: `keyframe.anomaly.IsolationForestDetector` (`fit`, `score`)
Context: requirements R1-R3; `grep -n '^def \|^class ' keyframe/features.py | head -30`
Acceptance:
- [ ] Synthetic test: points far from a healthy cloud score higher than points inside it
- [ ] Standardisation and imputation use training healthy rows only (test)
Notes:

## T-002: PCA with Hotelling T² and Q

Status: open
Blocked by: T-001
Slice: A PCA detector that reports T², Q and their combined score.
Test seam: `keyframe.anomaly.PCADetector`
Context: requirements R2; `grep -n 'class IsolationForestDetector' -A40 keyframe/anomaly.py`
Acceptance:
- [ ] Synthetic test: a shift along a retained component raises T²; a shift orthogonal to them raises Q
- [ ] Combined score normalised by training 99th percentiles (test)
Notes:

## T-003: Autoencoder detector

Status: open
Blocked by: T-001
Slice: A small MLP autoencoder that scores reconstruction error.
Test seam: `keyframe.anomaly.AutoencoderDetector`
Context: requirements R2; `grep -n 'class IsolationForestDetector' -A40 keyframe/anomaly.py`
Acceptance:
- [ ] Synthetic test: off-manifold points reconstruct worse than healthy ones; seeded fit is reproducible
Notes:

## T-004: Anomaly experiment and all runs

Status: open
Blocked by: T-002, T-003
Slice: Per-row held-out scores for every detector and fold, fitted on training healthy rows only.
Test seam: `uv run python -m keyframe.experiments anomaly --detector <d> --fold <bin>`
Context: requirements R3-R5; `grep -n 'def run_ablation\|def load_ablation\|add_parser' keyframe/experiments.py`
Acceptance:
- [ ] Spy test: `fit` sees no fault row and no held-out-load row
- [ ] 12 score files written (one foreground command each, each under 9 minutes)
- [ ] `reports/results/05_anomaly.csv` with pooled and per-fold AUROC per detector, and per-class AUROC
Notes:

## T-005: Thresholds, alarms and detection delay

Status: open
Blocked by: T-004
Slice: Each detector's scores become sustained alarms with a 2% training-fold false alarm budget, giving detection delay per run.
Test seam: `keyframe.anomaly.threshold_for_far`, alarm helpers from `keyframe.alarm`
Context: requirements R6; `grep -n '^def ' keyframe/alarm.py`
Acceptance:
- [ ] Threshold chosen from training healthy rows only (test)
- [ ] `reports/results/05_alarms.csv`: per detector, per run delay, alarm-level false alarm rate
Notes:

## T-006: Notebook 05 and findings

Status: open
Blocked by: T-005
Slice: Notebook 05 presents AUROC, per-class results, delays and score traces, against the brief's targets.
Test seam: executing `notebooks/05_anomaly_detection.py`
Context: requirements R7; `grep -n '^# %%' notebooks/04_modelling.py`; `head -3 reports/results/05_anomaly.csv reports/results/05_alarms.csv`
Acceptance:
- [ ] `05_roc.png`, `05_detection_delay.png`, `05_scores_switch_on.png`
- [ ] Targets marked met / not met; comparison with notebook 04's classifier delays
- [ ] Executes under 5 minutes; committed
Notes:
