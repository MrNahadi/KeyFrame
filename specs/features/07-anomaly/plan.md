# 07 Anomaly detection: plan

Roadmap item 7 (brief milestone 8). Done when AUROC and detection delay are measured for detectors trained on healthy data only.

## Approach

Three detectors fitted only on healthy rows of the training loads (LOLO, so the held-out load's healthy rows are never seen): Isolation Forest, PCA with Hotelling T² plus the squared prediction error (Q), and a small autoencoder (scikit-learn `MLPRegressor` trained to reproduce its standardised input). Each gives a per-row anomaly score. Scores are compared by AUROC (healthy vs any fault) on held-out loads, and turned into alarms with a threshold chosen on training-fold healthy rows (a fixed false alarm budget), then the sustained-alarm logic from feature 06 measures detection delay. A detector that flags an unseen fault type is the fallback when the classifier meets something new, so the notebook also scores each fault class on its own.

## Modules touched

- `keyframe/anomaly.py` (new): the three detectors with a shared interface
- `keyframe/experiments.py`: `anomaly` experiment (per detector, per fold)
- `tests/test_anomaly.py`
- `notebooks/05_anomaly_detection.py` + executed `.ipynb`; `reports/results/05_*.csv`; `reports/figures/05_*.png`

## Order of work

T-001 detector interface and Isolation Forest → T-002 PCA T²/Q → T-003 autoencoder → T-004 experiment and runs → T-005 thresholds, alarms and delay → T-006 notebook and findings.

## New dependencies

None.
