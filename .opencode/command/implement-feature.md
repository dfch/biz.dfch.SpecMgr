---
description: Drive a .specmgr feature plan to completion, one phase per subagent.
agent: phase-orchestrator
---

Implement the feature planned in `.specmgr/feat/$ARGUMENTS/README.md`.

Act strictly as an orchestrator: read the plan in full, build a phase-by-phase
`todowrite` list, and drive it to completion by delegating **each phase** to a
fresh `phase-implementer` subagent (one subagent per phase, in dependency
order). After each subagent returns, independently re-run that phase's quality
gate, inspect `git diff`, confirm the phase's acceptance criteria, then
commit that phase as one Conventional Commit before moving
on. Do not write or edit any file yourself; delegate all implementation.

Before delegating a phase whose design depends on an unresolved decision, ask
me first.

- Commit without asking me first, but do not push.
- Only stop when you need a decision from me, or when you hit a wall.
- After implementation completed (the feature has been at `progress` since the first implementation action), set the status `progress` -> `review`, commit, push and create a pr, but do not merge.
- If there are merge conflicts, solve them, until CI is green, but do not push.
- Then, run the review-feature agent for a post-implementation review, and follow its report with the capped review-fix loop: if it proposes a fix phase, delegate it to one more phase-implementer cycle (up to 3 cycles), resolving any [NEEDS DECISION] items with me first; set the status to `done` only after the loop exits clean (no Errors, Gaps, or Discrepancies left).
