You are revising an existing Architecture Decision Record (ADR), id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself -- every
change to the document goes through the specmgr MCP tools listed below.

## 1. Read current state first
Call `get_adr(id)` (or read the `specmgr://adr/{id}` resource) to load
the document's current frontmatter, body, and options. Never assume prior
state -- the on-disk file is always the source of truth and may have been
hand-edited since you last saw it.

## 2. If no change was specified
If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Map the requested change to the right tool
- A change to prose in `context_and_problem_statement`, `decision_drivers`,
  `considered_options`, `decision_outcome`, `consequences`, `confirmation`,
  or `more_information` -> `update_section(id, key, value)`. Submitting a
  blank string or the literal `"REMOVE"` clears an *optional* section;
  this is rejected with an error for a *mandatory* one
  (`title`/`context_and_problem_statement`/`considered_options`/
  `decision_outcome`).
- A change to `title` -> also `update_section(id, "title", value)`.
- A change to `status` (e.g. accepting/rejecting/deprecating the
  decision, or marking it superseded) -> the generic status-change tool:
  `set_status(id, type="adr", status, superseded_by=...)`, always called
  with `type="adr"` for an ADR (`superseded_by` is accepted only for
  `type="adr"`, composing the status as `"superseded by
  {superseded_by}"`) -- prefer it over `update_frontmatter` for
  status-only changes.
- Any other frontmatter change (`date`, `decision_makers`, `consulted`,
  `informed`) -> `update_frontmatter(id, frontmatter)`. This is a
  **whole-object replace**: read the current frontmatter first (step 1)
  and carry forward every field you are not intentionally changing, or
  they will be dropped. `id` itself is always preserved automatically by
  the tool regardless of what you submit.
- Adding a new considered option's pros/cons write-up ->
  `option_create(id, partial_title, value)`.
- Revising an existing option's content -> `option_update(id, full_title,
  value)`.
- Removing an option entirely -> `option_delete(id, full_title)`. This
  never renumbers or reorders the remaining options -- deleting one
  leaves a permanent gap in the numbering.

## 4. Always finish with validation
Call `validate_adr(id)` last, to self-correct before reporting success
back to the user.
