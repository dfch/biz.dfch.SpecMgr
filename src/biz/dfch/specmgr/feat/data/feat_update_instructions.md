You are revising an existing Feature (FEAT) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update` -- every change to the document
goes through the specmgr MCP tools listed below. There is no
`update_feat`/`set_status_feat` tool of its own -- `feat` uses the
generic `update`/`set_status` tools with `type="feat"` from day one.

## 1. Read current state first

Call `get_feat(id)` to load the document's current frontmatter and
body. Never assume prior state -- the on-disk `README.md` file is
always the source of truth and may have been hand-edited since you last
saw it -- direct hand/agent editing of `.specmgr/feat/<id>/README.md` is
the normal, sanctioned workflow for this domain, not just an MCP-tool
convenience.

## 2. If no change was specified

If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Show which sections are present and which are empty

Show the user which of the sections -- the mandatory `Overview`,
`Requirements`, `Acceptance Criteria`, `Scope` (`Included` and
`Explicitly Out Of Scope`), `Task List`, `Current Status`, and `Updates`
(always present), and the optional `Dependencies` (`Depends On`/
`Blocks`), `Design Notes`, `Related Decisions`, `Blockers`,
`Decisions Made`, `Related PRs / Commits`, and `More Information` --
are already present with content and which are still absent. Use the
`question` tool to ask which ones (if any) they want to add to or
revise.

## 4. Map the requested change to the right tool

- A change to the body -- any of the sections listed in step 3 -- ->
  the generic `update` tool called with `type="feat"`: a
  **line-range replace** for a localized change, or a **whole-body replace**
  otherwise. `content` is body markdown only (no frontmatter block) in
  both cases.
  - **Line-range replace** (a localized change -- one paragraph, list
    item, or section): first call `get_feat(id, raw=True)` to see the
    exact body text, identify the 1-based line to start at and how many
    lines to replace -- `offset` is the first body line, `limit` the
    number of lines (`offset`..`offset+limit-1`); `limit` omitted
    replaces through the last body line, `limit=0` is a pure insert,
    and the `N+1` position is end-of-body: `offset = N+1` appends after
    the last line -- and call `update(id, type="feat", content, offset=..., limit=...)`
    passing only the replacement lines. The server splices the fragment
    into the current on-disk body and validates the result as a whole
    document before writing anything, so every out-of-range line stays
    byte-identical. Adding a new `### Updates`/`### Decisions Made` entry
    is typically a line-range insert directly below the section's
    optional leading comment (or directly below the `### Updates`/
    `### Decisions Made` heading if no comment is present) -- new entries
    go first, since both sections are newest-first, enforced.
  - **Whole-body replace** (a multi-section change, or whenever you are
    uncertain about the line range): call `update(id, type="feat", content)`
    with no `offset`/`limit` -- `content` is then the full replacement body:
    read the current body first (step 1) and carry forward every section
    you are not intentionally changing, or it will be dropped.
    `id`/`type`/`created`/`version` are preserved automatically
    regardless of what you submit; only `updated` changes (the current
    date+time timestamp, same as every other domain).
- A change to `status` -> `set_status(id, type="feat", status)` instead
  -- `update` never accepts or changes `status`. `status` must be one
  of: planning, progress, review, done (no hyphens -- `progress`, not
  `in-progress`). Mention this as a separate, optional follow-up -- e.g.
  `progress` once implementation starts, `review` once implementation is
  done and pending verification, `done` once shipped -- do not call
  `set_status` unless the user actually asks for a status change.

## 5. Check the schema, and validate before writing if useful

Fetch `specmgr://feat/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_feat(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update` already performs the same
validation internally, so this step is never required, only a
convenience.
