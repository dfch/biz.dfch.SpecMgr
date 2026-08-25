You are revising an existing Risk (RSK) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update_rsk` -- every change to the
document goes through the specmgr MCP tools listed below.

## 1. Read current state first
Call `get_rsk(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified
If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Map the requested change to the right tool
- A change to the body -- the `cause`, `trigger`, `consequence`,
  `scope` entries, the `### Probability`/`### Impact` heading values of
  either assessment, the `strategy` TARA word, the `mitigation`, or any
  of the optional `owner`/`tags`/`more_information` sections -- ->
  `update_rsk(id, content)`. `content` is body markdown only (no
  frontmatter block) and is a **whole-body replace**: read the current
  body first (step 1) and carry forward every section you are not
  intentionally changing, or it will be dropped. `id`/`type`/`status`/
  `created`/`version` are preserved automatically regardless of what you
  submit; only `updated` changes. Keep both assessments in their
  mandated shape (`### Probability {1..5}` then `### Impact {1..5}`
  under each H2, values in 1..5) and the strategy one of the four TARA
  words, or the replace fails validation.
- A change to `status` -> `set_status_rsk(id, status)` instead --
  `update_rsk` never accepts or changes `status`. `status` must be one
  of: open, mitigating, accepted, occurred, closed, dropped.

## 4. Check the schema, and validate before writing if useful
Fetch `specmgr://rsk/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_rsk(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update_rsk` already performs the same
validation internally, so this step is never required, only a
convenience.
