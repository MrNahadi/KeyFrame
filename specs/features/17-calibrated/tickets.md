# 17 Calibrated track: tickets

## T-001: Calibrated features and variants

Status: done
Slice: `add_calibrated`, `segment_ids`, `arm_columns`, with tests.
Test seam: `tests/test_calibrated.py`
Acceptance:
- [x] Tests of R2 and R3 pass

## T-002: Inner scores for all four folds

Status: done
Blocked by: T-001
Slice: `reports/calibrated/inner_fold{40,60,75,85}.csv`
Acceptance:
- [x] Four files; each run under 10 minutes or split by fold

## T-003: Examination, once per fold

Status: done
Blocked by: T-002
Slice: `reports/calibrated/outer_fold{40,60,75,85}.json`
Acceptance:
- [x] Run once per fold, after T-002, with the primary variant read from the inner file

## T-004: Write-up

Status: done
Blocked by: T-003
Slice: `reports/calibrated/README.md`
Acceptance:
- [x] Zero-shot and calibrated side by side per fold and pooled, seed spread shown, injector limitation stated
