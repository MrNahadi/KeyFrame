# Milestone 4 gate: targets review

The brief allows the target table to be revised once, after the EDA, with
the reason written down (`specs/brief.md`, Goals and success metrics).
This is that one review. It uses EDA evidence only, never model results.

## Target table (unchanged)

| Metric | Baseline, 28 Sep 2026 | Target | Stretch |
| --- | --- | --- | --- |
| Macro F1, held-out loads | 0.52 raw / 0.60 residuals | 0.80 | 0.90 |
| Lowest per-class recall | 0.00 (turbine degradation, raw) | 0.70 | 0.85 |
| False alarm rate | 29.8% raw / 13.4% residuals | 5% | 2% |
| Fault detection AUROC | not measured | 0.95 | 0.98 |
| Detection delay | not measured | 10 min | 5 min |
| Expected calibration error | not measured | 0.05 | 0.03 |
| Unseen severity | not measured | 90% | 97% |
| Physics check on explanations | not done | 4 of 5 faults | 5 of 5 faults |
| Demo response time | not built | 300 ms | 100 ms |

## EDA evidence per target

- **Macro F1 / lowest per-class recall**: coverage by fault x load
  (`reports/results/01_coverage.csv`) has gaps — CW has 0 rows at 40% and
  75% load, TD has 0 rows at 75% load, INJ has only 61 rows at 75% load
  (vs. thousands elsewhere). The brief's validation protocol already
  accounts for this: per-fold scores cover only the classes present, and
  the headline metrics pool predictions across folds. Pooled, every fault
  has at least 6,492 rows, so the targets stay reachable. Every fault also
  shows a strong signature in the notebook (AC's Charge Air IC Air Temp.
  Out shift +29.8 SD, TD's whole exhaust chain moving together, AF's
  Charge Air Press. shift -1.62, INJ's 2.5 SD cylinder-to-cylinder spread,
  CW's rolling-std jump at switch-on) — nothing suggests the targets are
  out of reach or should be raised.
- **False alarm rate, AUROC, detection delay, ECE, unseen severity,
  demo response time**: no EDA evidence bears on these directly; the
  coverage and separability findings above give no reason to move them.
- **Physics check on explanations**: AF's predicted exhaust-temperature
  rise did not appear in the data (Disagree in
  `reports/engineering_checklist.md`'s Observed section) while its boost
  loss did — this is the one miss that "4 of 5 faults" already allows.
  CW's signature is a rolling-std variance shift rather than a mean-level
  shift, but this was pre-registered in the checklist's Expected top 5
  for CW (rolling std of Pl_water1 and Qw_eng), so the target still holds
  as written.

## Decision

No target or stretch value is revised. The scoring rules for two metrics
are made precise (without changing any number), so evaluation is honest
and reproducible before modelling starts:

1. **Lowest per-class recall** is taken over the five fault classes on
   pooled leave-one-load-out predictions. Per-fold recall is reported with
   its row count; a fold with no rows of a class shows "n/a", not 0. INJ
   at 75% load (61 rows) is reported but flagged as high-variance.
2. **Physics check** compares each fault's top-5 mean-|SHAP| features
   against `reports/engineering_checklist.md` as committed at the end of
   the EDA (Expected top 5 plus channels marked "Agree" in Observed). A
   fault matches if at least 3 of its top 5 map to those channels; derived
   features (residual, rolling mean or std, cylinder spread, ratio) count
   as the channels they are built from. None of the top 5 may be a
   day-dependent channel (T12, T18, T21, Pl_water2).

Decided by the answerer sub-agent on EDA evidence alone. See
`docs/adr/0005-targets-kept-after-eda.md`.

Targets final as of 2026-09-28.
