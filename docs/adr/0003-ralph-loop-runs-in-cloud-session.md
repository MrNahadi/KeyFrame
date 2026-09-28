# 0003. The Ralph loop runs in the owner's cloud session, fully automatic

Status: accepted
Decided-by: owner, 28 Sep 2026
Question: Where does the loop run and which gates need the owner?
Decision: `.ralph/ralph.sh` runs as a background process in the Claude Code cloud session that set the project up. Every gate is automatic. When a question can't be settled from the brief, the answerer researches it at xhigh effort and decides, recording an ADR. The agent may merge to main after validating each feature.
Basis: Owner's answers on 28 Sep 2026: "Here, in this cloud session"; "Full automatic but in case of a question launch an answerer agent on xhigh to do research and decide the best way forward"; "I have given you permission to do everything, including committing and merging any form of changes to main."
Consequences: ADRs with `Decided-by: answerer (inferred)` are where drift can hide; each feature report lists them for the owner to review later. Only a conflict with a brief non-negotiable stops the work.
