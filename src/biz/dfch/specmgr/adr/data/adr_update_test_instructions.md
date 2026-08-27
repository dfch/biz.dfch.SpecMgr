[STRICT STEP-GATED VARIANT -- for A/B comparison against the `update_adr` prompt]

You are revising an existing Architecture Decision Record (ADR), id: $id

Requested change: $instructions

You MUST follow the numbered gates below IN ORDER. A gate is a hard stop:
you may not perform any action described in a later gate until the
current gate's exit condition is explicitly satisfied. Never fabricate a
value in order to pass a gate. Do not write raw markdown yourself --
every change to the document goes through the specmgr MCP tools named
below.

## GATE 0 -- Read current state (mandatory, no exceptions)
Action: call `get_adr(id)` (or read the `specmgr://adr/{id}` resource).
Exit condition: you have the document's actual current frontmatter,
body, and options in hand. Never assume prior state from earlier in this
conversation -- the on-disk file is always the source of truth and may
have been hand-edited since you last saw it.
Do not call any write tool before this gate passes, even for a
seemingly-obvious change.

## GATE 1 -- Confirm the requested change
If "Requested change" above literally says "(not given)": stop here, ask
the user what they want to change, and wait for their reply before
continuing. Do not guess a plausible-sounding change and proceed anyway.
Exit condition: you have an explicit, user-stated change to make.

## GATE 2 -- Map the change to exactly one tool family
Pick the single right tool for the confirmed change -- do not call a
broader set of tools than the confirmed change actually implicates:
- A change to prose in `context_and_problem_statement`,
  `decision_drivers`, `considered_options`, `decision_outcome`,
  `consequences`, `confirmation`, `more_information`, or `title` ->
  `update_section(id, key, value)`. A blank string or the literal
  `"REMOVE"` clears an *optional* section; this is rejected with an
  error for a *mandatory* one (`title`/`context_and_problem_statement`/
  `considered_options`/`decision_outcome`).
- A change to `status` (e.g. accepting/rejecting/deprecating the
  decision, or marking it superseded) -> the generic status-change tool:
  `set_status(id, type="adr", status, superseded_by=...)`, always called
  with `type="adr"` for an ADR (`superseded_by` composes the status as
  `"superseded by {superseded_by}"`). Never use `update_frontmatter`
  for a status-only change.
- Any other frontmatter change (`date`, `decision_makers`, `consulted`,
  `informed`) -> `update_frontmatter(id, frontmatter)`. This is a
  **whole-object replace**: you MUST carry forward every field from
  GATE 0's read that you are not intentionally changing, or it is
  silently dropped. `id` itself is always preserved automatically by the
  tool regardless of what you submit.
- Adding a new considered option's pros/cons write-up ->
  `option_create(id, partial_title, value)`.
- Revising an existing option's content -> `option_update(id,
  full_title, value)`.
- Removing an option entirely -> `option_delete(id, full_title)`. This
  never renumbers or reorders the remaining options -- deleting one
  leaves a permanent gap in the numbering.
Exit condition: exactly the tool call(s) implied by the confirmed change
have been made -- nothing broader, nothing skipped.

## GATE 3 -- Validate before reporting success
Action: call `validate_adr(id)`.
Exit condition: it returns successfully. If it raises, fix the
offending change (re-enter GATE 2 with corrected input) before telling
the user anything succeeded.
Do not report success to the user until this gate passes.
