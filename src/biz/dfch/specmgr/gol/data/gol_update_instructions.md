You are revising an existing Goal (GOL) document, id: $id

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update` -- every change to the document
goes through the specmgr MCP tools listed below.

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
  -- -> the generic `update` tool called with `type="gol"`: a
  **line-range replace** for a localized change, or a **whole-body replace**
  otherwise. `content` is body markdown only (no frontmatter block) in
  both cases.
  - **Line-range replace** (a localized change -- one paragraph, field,
    or section): first call `get_gol(id, raw=True)` to see the exact
    body text, identify the 1-based line to start at and how many lines
    to replace -- `offset` is the first body line, `limit` the number of
    lines (`offset`..`offset+limit-1`); `limit` omitted replaces through
    the last body line, `limit=0` is a pure insert, and the `N+1`
    position is end-of-body: `offset = N+1` appends after the last line
    -- and call `update(id, type="gol", content, offset=..., limit=...)`
    passing only the replacement lines. The server splices the fragment
    into the current on-disk body and validates the result as a whole
    document before writing anything, so every out-of-range line stays
    byte-identical.
  - **Whole-body replace** (a multi-section change, or whenever you are
    uncertain about the line range): call `update(id, type="gol", content)`
    with no `offset`/`limit` -- `content` is then the full replacement body:
    read the current body first (step 1) and carry forward every section
    you are not intentionally changing, or it will be dropped.
    `id`/`type`/`status`/`created`/`version` are preserved automatically
    regardless of what you submit; only `updated` changes.
- A change to `status` -> `set_status(id, type="gol", status)` instead
  -- `update` never accepts or changes `status`. `status` must be one
  of: draft, proposed, accepted, superseded, deprecated, rejected,
  implemented. Mention this as a separate, optional follow-up -- e.g.
  `implemented` once the goal has genuinely been reached, `rejected` or
  `superseded` if the goal is abandoned or replaced by another goal --
  do not call `set_status` unless the user actually asks for a status
  change.
- A change to `classification` ->
  `set_classification(id, type="gol", classification)` instead --
  `update` never accepts or changes `classification`. Fully free-text;
  a blank or whitespace-only value clears it back to `None`/absent.

## 5. Check the schema, and validate before writing if useful

Fetch `specmgr://gol/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_gol(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update` already performs the same
validation internally, so this step is never required, only a
convenience.
