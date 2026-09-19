---
description: Review a completed .specmgr feature (feat-NNN-slug) for errors, gaps, inconsistencies, code smells, and improvements.
agent: feat-reviewer
---

Review the feature `$ARGUMENTS` (a `feat-NNN-slug` id under `.specmgr/feat/`).

1. Read `.specmgr/feat/$ARGUMENTS/README.md` in full.
2. Determine the code diff for this feature: if the current branch is named
   `$ARGUMENTS` (or a worktree for it), use `git merge-base dev HEAD` and
   review `git log <base>..HEAD` / `git diff <base>..HEAD`. If the branch
   doesn't match, use the `question` tool to ask for an explicit `base..head`
   ref range rather than guessing from commit message text -- this repo's
   Conventional Commits scope by domain, not by feature id, so grepping
   subjects for the id is unreliable.
3. Apply the full review checklist from your own agent instructions.
4. Report Errors / Gaps / Inconsistencies / Code Smells / Improvements /
   Positives with file:line citations. Do not edit, write, or commit
   anything.
