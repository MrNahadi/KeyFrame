#!/usr/bin/env bash
# Rebuild every result in the README from a fresh clone, in the order they were made.
#
#   bash scripts/reproduce.sh                  # everything (several hours on a laptop)
#   bash scripts/reproduce.sh --experiments    # only the heavy experiments
#   bash scripts/reproduce.sh --notebooks      # only re-execute the notebooks
#
# Each experiment skips work whose output already exists (add --force by hand to redo one).
# The tuned hyperparameters are committed in models/tuning/, so tuning is skipped and the
# locked results are rebuilt from the same parameters. Tuning runs on a 7-minute budget per
# fold, so rerunning it (delete models/tuning/) on different hardware can change the trial
# count and the result; see ADR 0011.
set -euo pipefail

cd "$(dirname "$0")/.."
run() { echo "+ $*"; "$@"; }
exp() { run uv run python -m keyframe.experiments "$@"; }

LOADS=(40 60 75 85)
MODELS=(logreg random_forest lightgbm xgboost)
DETECTORS=(pca iforest autoencoder)

experiments() {
  run uv run python -m keyframe.download

  # 03: feature ablation (every feature set x two model families) and pruning.
  for set in raw raw+physics raw+physics+rolling residuals residuals+physics residuals+physics+rolling; do
    for model in logreg lightgbm; do
      for load in "${LOADS[@]}"; do exp ablation --feature-set "$set" --model "$model" --fold "$load"; done
    done
  done
  for load in "${LOADS[@]}"; do exp ablation --feature-set residuals+physics --model logreg --shop-test --fold "$load"; done
  for load in "${LOADS[@]}"; do exp pruning --feature-set raw+physics+rolling --model lightgbm --fold "$load"; done

  # 04: nested tuning (skipped: parameters committed), refit per fold, alarm logic.
  for model in "${MODELS[@]}"; do
    for load in "${LOADS[@]}"; do exp tuning --model "$model" --outer-fold "$load"; done
    exp modelling --model "$model"
    exp alarm --model "$model"
  done

  # 05: healthy-only anomaly detectors, on raw readings and on healthy-engine residuals.
  for detector in "${DETECTORS[@]}"; do
    for inputs in raw residual; do
      for load in "${LOADS[@]}"; do exp anomaly --detector "$detector" --inputs "$inputs" --fold "$load"; done
      exp anomaly-alarm --detector "$detector" --inputs "$inputs"
    done
  done

  # 06: SHAP per held-out load, and the permutation-importance cross-check.
  for load in "${LOADS[@]}"; do exp shap --fold "$load"; done
  exp crosscheck

  # 07: calibration, per-run errors, the day-channel sensitivity check, the lockbox (once).
  for load in "${LOADS[@]}"; do exp calibration --fold "$load"; done
  exp runs
  for load in "${LOADS[@]}"; do exp sensitivity --fold "$load"; done
  exp lockbox

  # 08: the exported model, what-if baselines and replay files for the demo.
  exp export
  exp whatif
  exp replay
}

notebooks() {
  for nb in notebooks/0*.py; do
    run uv run jupytext --set-kernel python3 --to ipynb --execute "$nb"
  done
}

case "${1:-all}" in
  --experiments) experiments ;;
  --notebooks) notebooks ;;
  all) experiments && notebooks ;;
  *) echo "usage: $0 [--experiments | --notebooks]" >&2; exit 2 ;;
esac
