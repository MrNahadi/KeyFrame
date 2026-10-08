# 0015. One pre-registered test: does an untuned default model beat v1's tuned one?

Status: accepted
Decided-by: agent, under the owner's standing brief of 8 Oct 2026, after the v2 examinations of folds 40, 60 and 85 (ADR 0013)
Question: The autoresearch searches raised their inner scores (fold 40: 0.540 → 0.603, fold 60: 0.196 → 0.381, fold 85: 0.243 → 0.332), yet scored far below v1 on their held-out loads (0.254 / 0.299 / 0.158 against 0.404 / 0.818 / 0.517). Even v1's inner score barely tracks its held-out score (fold 60: 0.196 inner against 0.818 held out). An inner fold trains on two loads and extrapolates to a third, so with four loads it measures a different task from the real one. v1's Optuna tuning used the same signal, and that is how fold 85 ended up with a learning rate of 0.0034 (ADR 0011). If selecting on this signal hurts, a model with no selection at all should do at least as well.

Decision: one comparison, fixed before it runs, with nothing chosen by any score:
- Model: XGBoost with the library's default settings (`_BalancedXGBClassifier(random_state=seed)`, xgboost 3.4.1 defaults: 100 trees, learning rate 0.3, depth 6, no subsampling, L2 1.0) and balanced class weights, as in v1.
- Features: v1's `raw+physics+rolling` set, unchanged.
- Evaluation: `examine` for each held-out load (rows of unseen runs only, every training row, seeds 42/1/2), tag `default`, compared with `v1_unseen_foldK.json`.
- Reading: the default model "beats" v1 only if its mean over the four loads is higher **and** it is higher on at least three of the four loads. Either way, the result is reported and no further variant is tried on these held-out loads.

Consequences: if the default wins, the honest recommendation is to stop tuning on this dataset, and the deployable model should use default settings. If it loses, v1's tuned model stands, and the write-up says that no change tested on 8 October beat it.
