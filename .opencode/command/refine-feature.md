---
description: Refine a planned .specmgr feature (feat-NNN-slug) -- find errors, gaps, discrepancies, improvements, and positives in its plan and reference graph.
agent: feat-refiner
---

Refine the plan for feature `$ARGUMENTS` (a `feat-NNN-slug` id under `.specmgr/feat/`).

1. Read `.specmgr/feat/$ARGUMENTS/README.md` in full (Plan and Progress
   sections), plus `history.md` if present.
2. Apply the full refinement checklist from your own agent instructions.
3. Report Errors (E1, E2, ...) / Gaps (G1, G2, ...) / Discrepancies (D1,
   D2, ...) / Improvements (I1, I2, ...) / Positives (P1, P2, ...) as
   TSK-compatible checklist items (`- [ ] <ID>: <description>`), each citing
   a README.md line/section, plus the appendix of visited reference-graph
   nodes. Do not edit, write, or commit anything -- I will review the
   findings and tell you what to update.
