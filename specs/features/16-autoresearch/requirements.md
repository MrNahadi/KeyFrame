# 16 Autoresearch: requirements

Owner request (8 Oct 2026): improve the model with Karpathy's autoresearch method; set up the spec and a trial run on a new branch, after researching the best way to apply it here. Protocol and reasons: ADR 0013.

## Harness (fixed; the agent never edits it)

- R1. `keyframe/autoresearch.py` scores `autoresearch/candidate.py` for one outer fold K: inner leave-one-load-out macro F1 over the three loads other than K, on every 4th row of each run (`tuning.thin`), as the mean and standard deviation over seeds (42, 1, 2). Load K's rows are dropped before any fit, and `fit` and `predict` never receive them (spy test).
- R2. `score --no-day` computes the same score with every day-dependent channel, and every feature derived from one, hidden from the candidate (`features.without_day_channels`).
- R3. Candidate contract: `add_features(run)` gets one run in time order with `t` and the allowed inputs (no label, run, load bin or excluded column) and returns new `cand_*` columns with the same index; `select_columns(available)` returns a subset of `available`; `build_model(seed)` returns an unfitted classifier. Anything fitted lives inside the model.
- R4. Guards, each with a test: look-ahead features are refused (prefix test); columns outside `available` or in `EXCLUDED_COLUMNS` are refused; new columns need the `cand_` prefix; candidate source that reads files, labels or load bins, or reaches the shell, is refused.
- R5. `keep_threshold(sd)` = max(0.01, 2 × sd × √(2/3)).
- R6. `examine --outer-fold K` fits the candidate on every row of the training loads, predicts load K, writes `reports/autoresearch/v2_foldK.json` (labelled v2) and refuses to run a second time for the same fold.

## Agent program

- R7. `autoresearch/program.md` gives the loop: one branch per fold (`autoresearch/foldK`), baseline = v1's tuned parameters for that fold, ETA fixed from the baseline's seed sd, keep only if the score ≥ BEST + ETA and the no-day score ≥ BEST_NODAY − ETA, 60 experiments, a log in untracked `autoresearch/results.tsv`, files the agent must not read, and a hand-off at the end.

## Trial run

- R8. About 20 experiments on fold 75 following `program.md`, to measure run time, seed noise, the keep rate and whether the guards get in the way. Recorded in `trial-fold75.md`. The trial's candidate is reset to the baseline afterwards; nothing from it counts as a v2 result and `examine` is not run.

## Out of scope here

- The four real searches and their examinations (a later step, after the owner reads the trial report).
- Any change to v1's locked results, the exported model, the API or the demo.
