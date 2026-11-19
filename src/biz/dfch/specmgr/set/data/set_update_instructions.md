You are revising an existing set (SET) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update` or `edit` -- every change to the
document goes through the specmgr MCP tools listed below.

## 1. Read current state first

Call `get_set(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified

If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Show what the document currently holds

Show the user the document's current `## Description` content and its
`## Items` list. A set is a convenience bundle: the listed items remain
the source of truth for their own content, and nothing in an item ever
points back to the set -- revising the set means adding, removing, or
rewording bundle entries, never editing the referenced artifacts (those
go through their own domains' tools). Use the `question` tool to ask
what they want to add to or revise.

## 4. Map the requested change to the right tool

- A change to the body -- the `## Description` text, or an `## Items`
  bullet (add, remove, or reword a `<TAG> <uuid>: <title>` line, or its
  notes paragraph) -- -> the generic `update` tool called with
  `type="set"`: a **line-range replace** for a localized change, or a
  **whole-body replace** otherwise. `content` is body markdown only (no
  frontmatter block) in both cases.
  - **Line-range replace** (a localized change -- one description
    paragraph, or one bullet): first call
    `get_set(id, raw=True, numbered=True)` to see the exact body text --
    every line prefixed with its 1-based body-line number, so no manual
    counting is needed and a number seen can be fed straight back into
    `update`'s `offset` -- identify the 1-based line to start at and how many
    lines to replace -- `offset` is the first body line, `limit`
    the number of lines (`offset`..`offset+limit-1`); `limit` omitted
    replaces through the last body line, `limit=0` is a pure insert, and
    the `N+1` position is end-of-body: `offset = N+1` appends after the
    last line -- and call `update(id, type="set", content, offset=..., limit=...)`
    passing only the replacement lines. The server splices
    the fragment into the current on-disk body and validates the result
    as a whole document before writing anything, so every out-of-range
    line stays byte-identical. Each `## Items` bullet stays one physical
    line in the form `<TAG> <uuid>: <title>` (the `FEAT` tag carries a
    `feat-NNN-slug` or bare `feat-NNN` id); an optional notes paragraph
    goes after a blank line, indented under the bullet. Two bullets with
    the same `<TAG>` and the same id are a duplicate and are rejected.
    `offset`/`limit` address the frontmatter-stripped body, never the
    raw on-disk `.md` file: the YAML frontmatter block is
    variable-length, so a raw file read's line numbers are never the same
    as body-line coordinates -- and never feed the `numbered=True`
    output back verbatim as `content`: strip the `"<n>: "` prefix from
    each line first.
  - **Whole-body replace** (a multi-section change, or whenever you are
    uncertain about the line range): call `update(id, type="set", content)`
    with no `offset`/`limit` -- `content` is then the full replacement
    body: read the current body first (step 1) and carry forward the
    `## Description` and `## Items` sections you are not intentionally
    changing, or they will be dropped. `id`/`type`/`status`/`created`/
    `version` are preserved automatically regardless of what you submit;
    only `updated` changes.
  - The body holds exactly two H2 sections: `## Description` then
    `## Items` -- do not introduce any other H2 (no `## Owner`, no
    `## Source`, no `## Tags`) or reorder the two: both fail validation
    and nothing is written.
- A small, exact-match string replacement in the body -> the generic
  `edit` tool called with `type="set"`:
  `edit(id, type="set", old_str, new_str)` -- `old_str` must match the
  on-disk body byte-exactly and must be unique (unless
  `replace_all=True`), and the edited body must still validate as a
  whole document; nothing is written if either check fails. Read the
  current body via `get_set(id, raw=True)` first to copy the exact text.
- A change to `status` -> `set_status(id, type="set", status)` instead
  -- `update` never accepts or changes `status`. `status` must be one
  of: draft, progress, done, review. Mention this as a separate, optional
  follow-up -- e.g. `progress` while the bundle is being assembled, `review`
  once it is proposed for sign-off, `done` once it is final -- do not call
  `set_status` unless the user actually asks for a status change.
- A change to `classification` ->
  `set_classification(id, type="set", classification)` instead --
  `update` never accepts or changes `classification`. Fully free-text;
  a blank or whitespace-only value clears it back to `None`/absent.
- Removing the last bullet of `## Items` (or an empty list) is not a
  valid document: `## Items` requires at least one item. If the user
  wants to empty the bundle, ask (via the `question` tool) whether they
  mean to delete the set itself (the generic `delete` tool,
  `type="set"`) instead.

## 5. Check the schema only for structural changes, and validate before writing if useful

Call the `get_set_schema` tool (the generated JSON Schema) only for a
whole-body rewrite or a structural change -- to confirm field names and
constraints. Skip the schema fetch for a local splice (a line-range
replace or an `edit`), where the raw body is already in context:
`update` and `edit` both validate the result as a whole document before
writing anything, so the skip is safe. Optionally call
`validate(type="set", content=content, full=False)` beforehand to
dry-run the new body without writing anything -- `update` already
performs the same validation internally, so this step is never
required, only a convenience.
