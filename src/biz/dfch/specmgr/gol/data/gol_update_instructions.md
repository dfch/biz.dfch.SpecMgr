You are revising an existing Goal (GOL) document, id: $id

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update_gol` -- every change to the
document goes through the specmgr MCP tools listed below.

## 1. Read current state first

Call `get_gol(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. Show which sections are present and which are empty

Show the user which of the sections -- the goal `statement` (always
present), `## Source` (always present), and the optional `## Description`,
`## Priority`, `## Tags`, `## Related Artifacts`, `## More Information`,
`## Notes` -- are already present with content and which are still
absent. Use the `question` tool to ask which ones (if any) they want to
add to or revise.

## 3. Elicit the new/revised text

For each section selected in step 2, use the `question` tool to elicit
the new or revised text.

## 4. Map the requested change to the right tool

- A change to the body -- the goal statement, `description`, `priority`,
  `tags`, `source`, `related_artifacts`, `more_information`, or `notes`
  -- -> `update_gol(id, content)`. `content` is body markdown only (no
  frontmatter block) and is a **whole-body replace**: read the current
  body first (step 1) and carry forward every section you are not
  intentionally changing, or it will be dropped. `id`/`type`/`status`/
  `created`/`version` are preserved automatically regardless of what you
  submit; only `updated` changes.
- A change to `status` -> `set_status_gol(id, status)` instead --
  `update_gol` never accepts or changes `status`. `status` must be one
  of: draft, proposed, accepted, superseded, deprecated, rejected,
  implemented. Mention this as a separate, optional follow-up -- e.g.
  `implemented` once the goal has genuinely been reached, `rejected` or
  `superseded` if the goal is abandoned or replaced by another goal --
  do not call `set_status_gol` unless the user actually asks for a
  status change.

## 5. Check the schema, and validate before writing if useful

Fetch `specmgr://gol/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_gol(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update_gol` already performs the same
validation internally, so this step is never required, only a
convenience.
