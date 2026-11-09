---
description: Refine a planned .specmgr feature (feat-NNN-slug) for implementation readiness and apply the user-approved fixes to its plan in place -- $1 is the feature id.
agent: feat-planner
---

Refine the plan for feature `$1` (a `feat-NNN-slug` id under
`.specmgr/feat/`).

1. Parse my input. If `$1` is missing or is not a well-formed
   `feat-NNN-slug` (e.g. `feat-36-delete`), ask me for a clean id with
   the `question` tool rather than guessing.
2. Apply your own workflow (read the plan, assess it against the
   readiness checklist, ask which findings to apply, apply the approved
   fixes with the generic `update` tool's line-range edits, and re-check
   with the generic `validate` tool, `full=True`) to this id.
3. Report the findings, the edits you applied (the line before and after
   per finding), and the final re-check outcome. Do not commit, and do
   not touch any file other than the plan's README.
