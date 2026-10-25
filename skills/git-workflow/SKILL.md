# SKILL: git-workflow
- Branch per step: `git checkout -b p1-3-clean-layer`. Merge to `main` only after the DONE CHECK passes.
- Commit small and often. Message format: `P1.3: add clean.py with reason-coded drops`.
- Before each commit run `git status` and `git diff --stat`; confirm no `.env`, no `data/`, no large files.
- If a secret is ever committed: STOP, tell the student, explain they must revoke and regenerate the key at the provider; deleting it from history is not enough.
- Never force-push. Tag milestones: `v0.1-phase1`, `v0.2-phase2`.
