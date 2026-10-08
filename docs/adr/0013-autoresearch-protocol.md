# 0013. Autoresearch protocol: one isolated search per held-out load, a noise margin, and a day-robust gate

Status: accepted
Decided-by: agent at the owner's request (8 Oct 2026: "set up the spec and trial run ... do more research on it before moving forward and see the best way of approaching this particular problem")
Question: How can Karpathy's autoresearch loop (an agent edits one file, runs a fixed-budget experiment, keeps the change if one metric improves, reverts otherwise, repeats about 100 times) improve Keyframe without fitting the noise in 4 loads and 14 fault runs, and without breaking the locked v1 results?

Decision:
1. **The search never sees its held-out load.** A search belongs to one outer fold K. Its keep-or-discard score is the inner leave-one-load-out macro F1 over the other three loads, computed by a fixed harness (`keyframe/autoresearch.py`) that drops load K's rows before anything is fitted. There are four searches, one per K, each on its own branch `autoresearch/foldK`, each run by a fresh agent session that reads none of the other searches' logs. Load K is scored once, by `examine`, after its search stops. The v2 score is the four examinations pooled: an estimate for the *procedure* "run autoresearch on three loads", the same reading nested cross-validation gives the v1 tuning.
2. **Every score is a 3-seed mean, and a change is kept only if it beats the best by a margin ETA** = max(0.01, 2 × seed sd × √(2/3)), fixed from the baseline before the search starts (the Ladder mechanism's idea: no credit for gains inside the noise). The trial run measured seed sd 0.0116 on fold 75, giving ETA ≈ 0.019.
3. **Day-robust gate.** A kept change must not lower the score with day-dependent channels removed (`--no-day`) by more than ETA. This stops the loop from buying F1 by recognising the test day, the main v1 weakness (cavitation recall at 60% load falls from 0.96 to 0 without those channels).
4. **A fixed budget of 60 experiments per search**, set in advance, since the Ladder's error bound grows with the number of submissions.
5. **One editable file**, `autoresearch/candidate.py` (`add_features`, `select_columns`, `build_model`). The harness refuses look-ahead features (prefix test), columns outside the allowed inputs, new columns without the `cand_` prefix, and source code that reads files, labels or load bins. Fitted steps live inside `build_model`, so they are fitted on training rows only.
6. **Results are v2, separately labelled.** v1's locked numbers (ADR 0009) stay as they are. The v2 write-up reports the number of experiments run and kept per search and the seed spread next to every score.

Basis:
- Seed noise measured here: one seed moves fold 75's inner score from 0.569 to 0.593. The v1 tuned value (0.593) is the best of the three seeds, the winner's curse in miniature. Under a plain keep-if-better rule, half of all changes that do nothing would look like gains.
- Cawley and Talbot (JMLR 2010): optimising any selection criterion over a finite sample overfits it, and the bias grows with the criterion's variance. Nested evaluation is the remedy.
- Blum and Hardt (ICML 2015), the Ladder: a leaderboard stays reliable under adaptive submissions if it only updates when a submission beats the best by a margin. Chaibub Neto et al. (2016) show the Ladder still overfits at small sample sizes, which is why a fixed experiment budget and an untouched exam fold come on top.
- Commentary on autoresearch itself: Karpathy calls the results fragile, some gains did not replicate across sessions, and one tabular XGBoost fork improved its metric without improving the model until its evaluator was hardened. AIRA-dojo (Meta FAIR / UCL, 2025) measured a 9 to 13 point gap between choosing an agent's final solution by validation and by test score.
- Tabular forks (xgboost-autoresearch by Pafka and Ariño de la Rubia; fe-autoresearch; AutoFeaTune) keep the evaluator fixed and confine the agent to one file. None uses a noise margin or an outer exam. They have 100k+ rows per split; we have 14 fault runs.

Alternatives rejected:
- *One search scored on all four loads' inner folds:* load K is an inner validation load in the other three outer folds, so the chosen candidate would have seen load K's labels and its outer score would no longer be held out.
- *Reserve one load as a final exam and search on three:* cooling water pump cavitation exists only at 60% and 85% load, and turbine degradation is absent at 75%, so any single reserved load drops classes from the exam or from training.
- *Search on the outer LOLO score as v1 reported it:* this is fitting to the test folds, which brief section 8 forbids.

Consequences:
- Four searches of about 60 experiments, each around 2 to 4 minutes, so about 3 to 4 hours of CPU per search. They can run in parallel as four cloud sessions.
- The person who wrote this protocol has seen v1's outer results (for example "turbine degradation is weakest" and ADR 0011's fold-85 diagnosis). That knowledge is not in `program.md`, and the search agents are told not to read the files that hold it, but it cannot be fully undone. The write-up says so.
- The trial run on fold 75 (`specs/features/16-autoresearch/trial-fold75.md`) measured noise and run time only. Its candidate changes are thrown away and its log is closed to the search agents.
- No deployable model changes until the four examinations are in and a separate decision picks a v2 configuration.

## Amendment 1 (8 Oct 2026): score unseen runs only, and measure the batch effect

Question: Review by a marine condition-monitoring engineer (G. W. M. Maina) raised two doubts: whether the model recognises test sessions rather than faults, and whether near-perfect injector and cavitation recall reflects run-specific information.

Checked on the data the same day:
- **Healthy rows name their run.** On healthy rows alone, a small LightGBM trained on the first 60% of each run's healthy time names the run for the last 40% with balanced accuracy 0.96 / 0.95 / 1.00 / 0.97 at 40 / 60 / 75 / 85% load (chance 0.25 / 0.20 / 0.33 / 0.20). Removing the four day-dependent channels leaves 0.80 / 0.95 / 1.00 / 0.96. The session signature is spread across most channels, so the `--no-day` gate (decision 3) is necessary but far from sufficient.
- **Two runs span several loads.** `Clogged_Injector_Nozzle1_40_60_85_Load` (the only injector training run) covers 40, 60 and 85% load, and `Reference_Data` covers all four. In every leave-one-load-out fold, the model has trained on the same run at another load, so their held-out rows test run recognition as much as fault recognition. Every other fault run sits at one load.

Decision:
1. The keep signal (`macro_f1`) counts only rows of runs absent from that fold's training loads (`unseen_run_mask`). Seen-run rows are scored separately (`seen_run_macro_f1`) and never drive a decision. The examination headline uses the same rule. In practice the scored classes are air cooler fouling, air filter clogging, cooling water pump cavitation, turbine degradation, and Normal from the fault runs' pre-fault stretches. Injector clogging is judged only by the lockbox, a different run, which v1 already scored.
2. `identify --outer-fold K` runs the batch-effect test on the candidate's columns, over the training loads. It is logged for every kept change. It is a diagnostic, not a gate: it starts near its ceiling, so a margin rule on it would decide nothing.
3. Two results, separately labelled, as the reviewer recommended: **zero-shot** (no data from the held-out run; the primary v2 result, what the loop optimises) and, later, **calibrated** (features relative to the same run's own known-healthy stretch before the fault, as commissioning data would provide). Calibrated is out of scope for this feature. It will be specified on its own, and it cannot detect the injector fault, which is present from the start of its run.
4. Trial results scored before this amendment are superseded. The trial restarts with a new baseline and a new ETA under the corrected score.

Consequences: v1's locked numbers (ADR 0009) include seen-run rows. They stay unchanged, and the v2 write-up names this as a caveat on v1. The trial's first kept change (lr 0.05, 300 trees, depth 3) is re-tested under the new score rather than carried over.

## Amendment 2 (8 Oct 2026): zero-shot features have a 15-minute memory

During the four searches, one agent tried features measured relative to the run's first 10 minutes. That is calibration: it assumes each run starts healthy, which is the separate calibrated track (ADR 0014). It does not belong in the zero-shot track.

Decision: a zero-shot feature may depend only on rows within the trailing 900 s, the longest window v1 used. `check_bounded_memory` enforces this: features computed on a run with its first 30% removed must match the whole-run values for rows more than 900 s after the cut. It runs in `search_score` and `examine`. The four running searches cloned the harness before this check existed, so they were told the rule by message. `examine` refuses any candidate that breaks it, so no search can be examined with a start-anchored feature.
