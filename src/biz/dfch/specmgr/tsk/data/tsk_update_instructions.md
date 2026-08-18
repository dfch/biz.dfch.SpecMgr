You are revising an existing Task List (TSK) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update_tsk` -- every change to the
document goes through the specmgr MCP tools listed below.

## 1. Read current state first
Call `get_tsk(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified
If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Map the requested change to the right tool
- A change to the body -- the checklist items, the leading comment, or
  adding a new `## Recent Updates` entry -- -> `update_tsk(id, content)`.
  `content` is body markdown only (no frontmatter block) and is a
  **whole-body replace**: read the current body first (step 1) and carry
  forward every section you are not intentionally changing, or it will
  be dropped. `id`/`type`/`status`/`created`/`version` are preserved
  automatically regardless of what you submit; only `updated` changes.
  In particular, `## Recent Updates` requires at least one entry at all
  times -- if you are not adding a new one, carry forward every existing
  entry; removing the last remaining entry would fail validation
  (`RecentUpdates.updates` requires `min_length>=1`).
- A change to `status` -> `set_status_tsk(id, status)` instead --
  `update_tsk` never accepts or changes `status`. `status` must be one
  of: draft, active, done, cancelled.

## 4. Check the schema, and validate before writing if useful
Fetch `specmgr://tsk/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_tsk(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update_tsk` already performs the same
validation internally, so this step is never required, only a
convenience.

To actually work through the checklist items themselves (marking them
done, asking clarifying questions), use the `implement_task` prompt
instead of this one.
