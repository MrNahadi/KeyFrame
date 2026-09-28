# 0002. Use the xgboost-cpu wheel

Status: accepted
Decided-by: agent (planning, owner present), 28 Sep 2026
Question: The default `xgboost` wheel on Linux pulls in a 291 MB NVIDIA NCCL library. Is that needed?
Decision: Depend on `xgboost-cpu` (same `import xgboost` API, no GPU libraries).
Basis: The dataset is about 140,000 rows; GPU training brings nothing. Smaller installs make a fresh clone faster to rebuild (brief non-negotiable on reproducibility).
Consequences: No GPU training. Switching back later is a one-line dependency change.
