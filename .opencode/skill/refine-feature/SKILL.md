---
name: refine-feature
description: >-
  Use when sanity-checking or refining a *planned* .specmgr feature's
  README.md plan -- before implementation starts, mid-implementation, or
  whenever asked to find errors/gaps/discrepancies/improvements in a
  feat-NNN-slug plan (e.g. "is this feature plan solid?", "check
  feat-187 for gaps before I build it") -- whether surfaced by an explicit
  `/refine-feature` request or organically while working with a feature
  plan. Not for reviewing finished implementations against a plan -- that
  is `review-feature`/`feat-reviewer`'s job, which diffs code, not a plan.
---

# Refine Feature

You've been asked to sanity-check a **planned** (not-yet, or partially,
implemented) `.specmgr/feat/<id>/README.md` feature -- find errors, gaps,
discrepancies, improvements, and positive items in the plan itself and its
reference graph. This is read-only analysis: never edit, write, create, or
delete any document, and never commit.

## How

- **Prefer delegation.** If your host can launch subagents (a `task` tool
  is available) and the `feat-refiner` agent is among them, delegate to it
  with the `feat-NNN-slug` id. It owns the full workflow (transitive
  reference-graph walk with cycle protection, the plan-quality checklist,
  and the TSK-compatible E/G/D/I/P report format) and reports its own
  findings.
- **`/refine-feature <id>` already routes to `feat-refiner`.** If the user
  typed it, let it run.
- **Otherwise, run the same workflow yourself.** Read
  `.opencode/agent/feat-refiner.md` in full and follow it verbatim as your
  operating instructions for this task -- do not re-derive a different
  checklist, workflow, or report format; that file (plus, in this repo,
  `.specmgr/conventions/feat-refiner.md` if it exists) is the single
  source of truth, and the two must not drift apart.

Never propose fixes as a diff -- describe them in prose; the user decides
what to act on.
