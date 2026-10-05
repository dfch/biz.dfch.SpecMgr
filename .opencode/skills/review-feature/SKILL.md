---
name: review-feature
description: >-
  Use when reviewing a *finished* (or claimed-finished) .specmgr feature
  implementation -- a feat-NNN-slug branch or plan -- for errors, gaps,
  discrepancies, and improvement opportunities against its own plan/
  acceptance criteria, by diffing the actual code change. Trigger on
  phrasing like "review feat-187", "is this feature ready to ship?",
  "check my implementation against the plan" -- whether surfaced by an
  explicit `/review-feature` request or organically after finishing a
  feature's implementation (e.g. before marking it done or opening a PR).
  Not for reviewing an unimplemented plan in isolation -- that's
  `refine-feature`/`feat-refiner`'s job, which never looks at a diff.
---

# Review Feature

You've been asked to review a **finished** (or claimed-finished)
`.specmgr/feat/<id>/README.md` feature implementation against its own plan
-- find errors, gaps, discrepancies, and improvement opportunities in the
actual code, not just the plan. This is read-only analysis: never edit,
write, create, or delete any file, and never commit.

## How

- **Prefer delegation.** If your host can launch subagents (a `task` tool
  is available) and the `feat-reviewer` agent is among them, delegate to
  it with the `feat-NNN-slug` id. It owns the full workflow (diff
  resolution, full-file reading, the Generic/ISO-25010 + codebase-specific
  checklist, and the TSK-compatible E/G/D/I/P report format) and reports
  its own findings.
- **`/review-feature <id>` already routes to `feat-reviewer`.** If the
  user typed it, let it run.
- **Otherwise, run the same workflow yourself.** Read
  `.opencode/agent/feat-reviewer.md` in full and follow it verbatim as
  your operating instructions for this task -- do not re-derive a
  different checklist, workflow, or report format; that file (plus, in
  this repo, `.specmgr/conventions/feat-reviewer.md` if it exists) is the
  single source of truth, and the two must not drift apart.

Never propose fixes as a diff -- describe them in prose; the user decides
what to act on.
