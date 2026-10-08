# autoresearch: program

You are improving Keyframe's fault classifier on your own, one experiment at a time, the way Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) improves a small language model. The rules below exist because this dataset is tiny: 4 engine loads and 14 fault runs. A loop that keeps every lucky score would end up fitting the noise, so follow them exactly. The reasons are in `docs/adr/0013-autoresearch-protocol.md`.

## Your search

Each search belongs to one **outer fold** `K` (40, 60, 75 or 85), the engine load that is held out. The human starting you gives you `K`. You work on branch `autoresearch/foldK`, created from `auto-research`.

The harness scores your candidate on the **other three loads only** (inner leave-one-load-out, mean over 3 seeds). Load `K`'s rows are dropped before anything is fitted, and you never see a score for them. A separate step scores load `K` once, after you stop.

`macro_f1` counts only rows of runs the model has not trained on. The injector run and the healthy reference run each span several loads, so their rows are scored apart as `seen_run_macro_f1`. That number is shown for information and never decides anything. Every run is recognisable from its healthy readings alone (ADR 0013, amendment 1), so a gain that comes from telling sessions apart is not a gain. Prefer features that compare readings with what a healthy engine does at the same load.

## Files

- `autoresearch/candidate.py` is the **only file you edit**. It defines `add_features(run)`, `select_columns(available)` and `build_model(seed)`; its docstring gives the contract.
- `keyframe/autoresearch.py` is the harness. Read it, never edit it. The same goes for everything else in `keyframe/`, `tests/` and `data/`.
- `autoresearch/results.tsv` is your log. It is untracked, so `git reset` never erases it.

## Do not read

To keep the held-out load unseen, do not open `README.md`, `reports/`, `paper/`, `docs/adr/` (except 0013), `notebooks/*.ipynb`, `specs/features/16-autoresearch/trial-*`, or any other search's branch or log. They contain held-out scores from v1 or from other searches. You may read `keyframe/`, `specs/brief.md`, `CONTEXT.md` and `reports/engineering_checklist.md` (the physics: what each fault should do to which sensor).

## Setup

0. `uv sync`, then `uv run python -m keyframe.autoresearch prepare` (downloads the dataset and builds the feature table; about 2 minutes, once).
1. `git checkout -b autoresearch/foldK auto-research`
2. Put this fold's v1 parameters in `PARAMS` in `candidate.py`: copy `best_params` from `models/tuning/xgboost_foldK.json`. That file holds only inner scores. Commit it as `baseline`.
3. Create `autoresearch/results.tsv` with the header `commit	macro_f1	sd	noday_f1	identify	worst_recall	status	description` (tab-separated).
4. Score the baseline: `uv run python -m keyframe.autoresearch score --outer-fold K > run.log 2>&1`, then `uv run python -m keyframe.autoresearch score --outer-fold K --no-day >> run.log 2>&1`. Run `identify` too. Log it with status `keep`. Its `macro_f1` is **BEST** and its `noday` score is **BEST_NODAY**.
5. Set the keep margin **ETA** = max(0.01, 2 × sd × √(2/3)), using the baseline's `macro_f1_sd`. You can run `uv run python -c "from keyframe.autoresearch import keep_threshold; print(keep_threshold(SD))"`. Write ETA at the top of your notes and never change it.

## The loop

Repeat until you have logged **60 experiments**. Do not stop to ask whether to continue.

1. Pick one idea and edit `candidate.py`. Commit it with a one-line message saying what it tries.
2. `uv run python -m keyframe.autoresearch score --outer-fold K > run.log 2>&1`, then read the `macro_f1` and `macro_f1_sd` lines. If it crashed, read `tail -n 40 run.log`. Fix a typo and rerun; if the idea itself is broken, log `crash` and `git reset --hard HEAD~1`. A `CandidateError` means you broke a harness rule: undo the idea, never work around the rule.
3. **Keep or discard.** Two tests, run in order:
   - **Improves:** `macro_f1` ≥ BEST + ETA. If it fails, log `discard` and `git reset --hard HEAD~1`.
   - **Does not lean on the test day:** run the score again with `--no-day`. If that score is below BEST_NODAY − ETA, log `discard-day` and reset.
   - If both pass, log `keep`. Update BEST and BEST_NODAY to the new scores and leave the commit in place. Then run `uv run python -m keyframe.autoresearch identify --outer-fold K` and log its `identify_mean` (the batch-effect check: lower means your features depend less on the session).
4. Append one line to `results.tsv` for every experiment, including crashes and discards.

A single experiment should finish in under 10 minutes. Kill anything slower and log it as a crash.

## What to try

Anything that keeps to the contract. For example:
- Model settings: learning rate against number of trees (a very low learning rate with few trees cannot converge), depth, regularisation, class weights.
- Model family: LightGBM, random forest and logistic regression are installed. Do not add packages.
- Features, physics first: the engineering checklist names the sensors each fault should move. Build features that follow it, such as differences, ratios, exhaust temperature spread, or trends over trailing windows. Only causal features: the current row and earlier rows of the same run.
- Fewer features: dropping a noisy group that scores the same or better is a win.
- Steps fitted inside `build_model` (scaling, selection, healthy-engine residuals via `keyframe.features.HealthyEngineResiduals`) are fitted on training rows only. Use them freely.

**Simplicity:** a gain just above ETA that adds a lot of code is not worth keeping. Removing code at equal score is.

## Never

- Edit anything except `candidate.py`, or change ETA, the seeds or the thinning.
- Read the files listed under "Do not read", or run `examine`. The human runs it, once, after your 60 experiments.
- Use labels, run names, load bins, file reads or the time stamp as a feature. The harness refuses most of these; the rest are on you.
- Keep a change because it "nearly" passed, or re-run a seed hoping for a better number.

## When you finish

Leave the branch at the last kept commit. Copy `results.tsv` to `reports/autoresearch/foldK_results.tsv`, commit it, and push the branch. Then report how many experiments you ran, how many you kept, and the final BEST and BEST_NODAY.
