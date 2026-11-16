You are implementing a planned Feature (FEAT) document, id: $id

This is a portable narration of the orchestrator discipline the plan's
own phase structure is built for: you drive the plan to completion,
phase by phase, and you delegate the actual implementation. The
pattern is governed by DEC
4481b1fd-26e5-46bc-8f1b-236b638385b2 (the portable MCP prompt may
narrate optional host-native subagent delegation, degrading gracefully
when absent): the delegation is narrated as optional and never assumed
present -- the text refers to "your host's task-delegation tool, if one
exists" -- and it always carries the explicit fallback below, never a
hard failure. Follow this sequence exactly.

Make a phase-by-phase `TodoWrite` list (one entry per phase of the
plan's Task List, in dependency order), and use the `question` tool
whenever a design decision the next phase depends on is unresolved --
do not delegate on top of an ambiguity.

## 1. Read the plan in full

- Call `get_feat($id)` (the parsed document) to see the frontmatter
  fields -- `id`/`type`/`status`/`created`/`updated`/`version` (plus
  `classification` when set) -- and which of the sections are present.
  If `get_feat($id)` returns a parse-failure result (`error`/`path`)
  instead of a document, report the error and stop: the plan must be
  repaired first (the `/repair` surface), not implemented.
- Call `get_feat($id, raw=True)` for the frontmatter-stripped body, and
  read it in full: every Requirement, every Acceptance Criterion, the
  phase-by-phase Task List with each phase's own gate, the
  Dependencies, and the Design Notes. Never assume prior state: the
  on-disk `.specmgr/feat/$id/README.md` file is the source of truth and
  may have been edited since you last saw it.

## 2. Delegate one phase at a time (verify before advancing)

For each phase, in the order the plan lists it:

- Delegate the phase to a fresh subagent via your host's
  task-delegation tool, if one exists (inside OpenCode that is the
  `task` tool, one phase-implementer-style subagent per phase). Give
  the subagent a self-contained prompt: the absolute path to the plan
  README and the exact phase heading, the phase's tasks verbatim, what
  the already-completed phases produced, the explicit instruction to
  run the phase-end quality gate and report concrete evidence
  (commands run + their output) back, the instruction to update the
  plan's Progress section as the phase-end task requires, and the
  instruction NOT to commit and NOT to start the next phase.
- When the subagent returns, independently verify its result BEFORE
  advancing: re-run the phase's quality gate yourself, inspect the diff
  (`git status` / `git diff`), and confirm the phase's acceptance
  criteria are met. Never take "tests pass" on trust -- run them.
- If verification fails, send the same subagent back with the specific
  failures and required fixes; if it passes, mark the phase complete in
  the `TodoWrite` list and commit the phase as one Conventional Commit
  (the plan's own per-phase commit discipline).
- Never write or edit code files yourself -- delegate all
  implementation. You read, verify, decide, and commit; the subagent
  writes the code.

## 3. Fallback: hosts without a task-delegation tool

If your host has no task-delegation tool -- the naming above is
deliberate, "your host's task-delegation tool, if one exists" -- fall
back to direct single-session implementation, phase by phase: run each
phase yourself, in the same order, with the same
verify-before-advancing discipline (re-run the phase's quality gate,
inspect the diff, confirm the phase's acceptance criteria, one
Conventional Commit per phase). This is never a hard failure: the plan
is implemented either way, and the phase's substance is unchanged by
which mode you ran it in.

## 4. The review-fix loop after the final verification phase

After the plan's final verification phase has walked the plan's
acceptance criteria with concrete evidence (the feature is then at
`review`, not yet `done`):

- Run the reviewer for the feature (the `review_feat` prompt, or your
  host's feat-reviewer-style subagent).
- If the review reports no Errors, Gaps, or Discrepancies, the loop
  exits clean: the `done` closeout happens only after a clean loop
  exit -- set the feature status `done` with the generic `set_status`
  tool (`type="feat"`) and report the final summary to the user.
- If the report contains any Errors, Gaps, or Discrepancies and the
  reviewer's conditional "Proposed Fix Phase" block is present:
  resolve any `[NEEDS DECISION]` items with the user via the `question`
  tool first (never guess at them), then delegate the fix phase to one
  more subagent cycle exactly like a normal phase -- with the
  delegation prompt instructing the implementer to first append the
  reviewer's ready-to-paste block to the plan's Task List, since you
  (the orchestrator) cannot edit files (`edit`/`write` are denied to
  you). Verify the fix phase as in step 2 and commit it as in step 2's
  own commit rule.
- Repeat until the reviewer reports no Errors, Gaps, or Discrepancies
  left, capped at 3 review-fix cycles: after the third cycle, any
  remaining findings are handed to the user instead of auto-fixed
  again.
- In step 3's single-session fallback, run the same loop yourself (the
  review, the fix phase, the repeat) -- same cap, same exit criterion,
  same `done`-only-after-a-clean-exit ordering.

## 5. Report

Return: the phases you ran (with their gate evidence and commits), the
review-fix loop's outcome (the cycles run, the findings resolved or
handed to the user), and the final feature status. Stop at `review`
until the loop exits clean -- do not set `done` early, and do not
merge a PR without the user's confirmation.
