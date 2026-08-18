You are revising an existing Requirement (REQ) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update_req` -- every change to the
document goes through the specmgr MCP tools listed below.

## 1. Read current state first
Call `get_req(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified
If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Map the requested change to the right tool
- A change to the body -- the requirement statement, `description`,
  `characteristics`, `level`, `priority`, `tags`, `source`,
  `related_artifacts`, `more_information`, or `notes` -- ->
  `update_req(id, content)`. `content` is body markdown only (no
  frontmatter block) and is a **whole-body replace**: read the current
  body first (step 1) and carry forward every section you are not
  intentionally changing, or it will be dropped. `id`/`type`/`status`/
  `created`/`version` are preserved automatically regardless of what you
  submit; only `updated` changes.
- A change to `status` -> `set_status_req(id, status)` instead --
  `update_req` never accepts or changes `status`. `status` must be one
  of: draft, proposed, accepted, superseded, deprecated, rejected,
  implemented.

## 4. Check the schema, and validate before writing if useful
Fetch `specmgr://req/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_req(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update_req` already performs the same
validation internally, so this step is never required, only a
convenience.
