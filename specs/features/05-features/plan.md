# 05 Feature engineering: plan

Roadmap item 5 (brief milestone 6). Done when the ablation table shows which feature sets earn their place on held-out loads.

## Approach

Three feature families, each a tested building block that plugs into the LOLO machinery from feature 04 without leaking:

1. **Physics features** are stateless functions of one row, so they can be computed once on the whole table.
2. **Rolling windows** are causal (trailing only) and computed per run in seconds of `t`, so they are also stateless and computed once. Causal matters twice: no row sees its future, and the demo can replay them live.
3. **Healthy-engine residuals** are fitted, so they live in an sklearn transformer inside the pipeline and are refitted on each training fold's healthy rows only.

Then notebook 03 runs the ablation one family at a time with two fixed models (logistic regression and LightGBM at defaults, as in notebook 02), and prunes near-duplicates and useless features with statistics computed inside the training folds only.

## Modules touched

- `keyframe/features.py`: physics functions, rolling features, `HealthyEngineResiduals` transformer, feature-set registry
- `keyframe/eda.py`: import physics functions from `features.py` instead of defining them (no behaviour change)
- `keyframe/evaluate.py`: `lolo_predict` gains an optional `extra_healthy` hook for the shop-test score
- `tests/test_features.py` (extend), `tests/test_evaluate.py` (extend)
- `notebooks/03_feature_engineering.py` + executed `.ipynb`; `reports/results/03_*.csv`; `reports/figures/03_*.png`; `docs/adr/` for the chosen feature set

## Order of work

T-001 physics → T-002 rolling → T-003 residuals → T-004 shop-test hook → T-005 feature-set registry → T-006 ablation notebook → T-007 pruning → T-008 findings and decision.

## New dependencies

None.
