---
description: Drive a .specmgr feature plan to completion, one phase per subagent.
agent: phase-orchestrator
---

Implement the feature planned in `.specmgr/feat/$ARGUMENTS/README.md`.

Act strictly as an orchestrator: read the plan in full, build a phase-by-phase
`todowrite` list, and drive it to completion by delegating **each phase** to a
fresh `phase-implementer` subagent (one subagent per phase, in dependency
order). After each subagent returns, independently re-run that phase's quality
gate, inspect `git diff`, confirm the phase's acceptance criteria, then — with
my confirmation — commit that phase as one Conventional Commit before moving
on. Do not write or edit any file yourself; delegate all implementation.

Before delegating a phase whose design depends on an unresolved decision, ask
me first.
