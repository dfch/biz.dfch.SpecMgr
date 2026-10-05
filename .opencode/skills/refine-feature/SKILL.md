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
- **Otherwise, run the same workflow yourself** -- do not re-derive a
  different checklist; read `.opencode/agent/feat-refiner.md` for the
  authoritative checklist and report format and apply it verbatim:
  1. Load `.specmgr/feat/<id>/README.md` via
     `get_feat(id, raw=True, numbered=True)`, plus `history.md` if present.
  2. Walk the reference graph transitively from
     `list_references("feat", id)`: for each resolved reference, call
     `list_references` again on it, tracking every visited `(type, id)`
     pair so a cycle (two features depending on each other, a DEC citing
     the very FEAT that cites it, ...) is detected, not looped forever.
  3. Apply `feat-refiner`'s checklist (traceability, Phase/Task numbering,
     cross-reference integrity, scope coherence, status consistency,
     clarity, repo-convention consistency) against the plan and the graph.
  4. Report in `feat-refiner`'s exact section order and format: Errors
     (E1, E2, ...) / Gaps (G1, ...) / Discrepancies (D1, ...) /
     Improvements (I1, ...) / Positives (P1, ...), each a
     `- [ ] <ID>: <description>` line citing a README.md line/section,
     plus the visited-nodes appendix.

If `id` is missing, ambiguous, or not a valid `feat-NNN-slug`, ask (via
your host's question mechanism) rather than guessing. Never propose fixes
as a diff -- describe them in prose; the user decides what to act on.
