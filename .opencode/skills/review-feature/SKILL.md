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
- **Otherwise, run the same workflow yourself** -- do not re-derive a
  different checklist; read `.opencode/agent/feat-reviewer.md` for the
  authoritative checklist and report format and apply it verbatim:
  1. Load `.specmgr/feat/<id>/README.md` in full (Plan and Progress
     sections), plus `history.md` if present -- every Requirement,
     Acceptance Criterion, and Task List entry is what the diff must
     satisfy.
  2. Resolve the diff: if the current branch is named `<id>` (or a
     worktree for it), `git merge-base dev HEAD`, then
     `git log --oneline <base>..HEAD` / `git diff <base>..HEAD --stat`.
     Do not grep commit subjects for the feature id -- this repo's
     Conventional Commits scope by domain, not by feature id. If the
     branch doesn't match, ask (via your host's question mechanism) for
     an explicit `base..head` range rather than guessing.
  3. Read every changed file in full, not just diff hunks -- including
     every artifact that must move together per the Artifact consistency
     checklist item (docstrings, templates/examples, both schema copies,
     generated docs, `AGENTS.md`, `CHANGELOG.md`, `whitelist.py`).
  4. Apply `feat-reviewer`'s checklist (the Generic ISO/IEC 25010:2023
     layer plus this codebase's own conventions) against the diff and the
     plan.
  5. Report in `feat-reviewer`'s exact section order and format: Errors
     (E1, E2, ...) / Gaps (G1, ...) / Discrepancies (D1, ...) /
     Improvements (I1, ...) / Positives (P1, ...), each a
     `- [ ] <ID>: <description>` line citing a `path:line`.

If `id` is missing, ambiguous, or the branch can't be resolved to a ref
range, ask (via your host's question mechanism) rather than guessing.
Never propose fixes as a diff -- describe them in prose; the user decides
what to act on.
