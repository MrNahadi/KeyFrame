# v2 summary (generated)

Built by `uv run python -m keyframe.v2report` from `reports/autoresearch/*.json` and
`*_results.tsv`. Macro F1 on each held-out load, rows of unseen runs only, mean ± sd
over 3 seeds. v1 is re-scored under the same rule. Its locked numbers (ADR 0009) are
unchanged.

| Held-out load | v1 | v2 | v2 − v1 | v2 worst recall | v2 false alarms | Experiments | Kept | Inner F1 (baseline → examined) |
|---|---:|---:|---:|---|---:|---:|---:|---|
| 40% | 0.404 ± 0.058 | 0.254 ± 0.033 | -0.150 | 0.00 AF | 0.389 | 60 | 7 | 0.540 → 0.603 |
| 60% | 0.818 ± 0.026 | 0.299 ± 0.004 | -0.519 | 0.00 CW | 0.014 | 60 | 5 | 0.196 → 0.381 |
| 75% | 0.500 ± 0.009 | pending | pending | pending | pending | pending | pending | pending |
| 85% | 0.517 ± 0.005 | 0.158 ± 0.001 | -0.359 | 0.00 AF | 0.004 | 60 | 2 | 0.243 → 0.332 |

Mean over the 3 examined loads: v1 0.580, v2 0.237 (difference -0.343).
