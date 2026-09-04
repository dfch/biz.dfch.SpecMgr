You are revising an existing Requirement (REQ) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update` -- every change to the document
goes through the specmgr MCP tools listed below.

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
  `related_artifacts`, `more_information`, or `notes` -- -> the
  generic `update` tool called with `type="req"`: a **line-range replace**
  for a localized change, or a **whole-body replace** otherwise.
  `content` is body markdown only (no frontmatter block) in both cases.
  - **Line-range replace** (a localized change -- one paragraph, field,
    or section): first call `get_req(id, raw=True)` to see the exact
    body text, identify the 1-based line to start at and how many lines
    to replace -- `offset` is the first body line, `limit` the number of
    lines (`offset`..`offset+limit-1`); `limit` omitted replaces through
    the last body line, `limit=0` is a pure insert, and the `N+1`
    position is end-of-body: `offset = N+1` appends after the last line
    -- and call `update(id, type="req", content, offset=..., limit=...)`
    passing only the replacement lines. The server splices the fragment
    into the current on-disk body and validates the result as a whole
    document before writing anything, so every out-of-range line stays
    byte-identical.
  - **Whole-body replace** (a multi-section change, or whenever you are
    uncertain about the line range): call `update(id, type="req", content)`
    with no `offset`/`limit` -- `content` is then the full replacement body:
    read the current body first (step 1) and carry forward every section
    you are not intentionally changing, or it will be dropped.
    `id`/`type`/`status`/`created`/`version` are preserved automatically
    regardless of what you submit; only `updated` changes.
- A change to `status` -> `set_status(id, type="req", status)` instead
  -- `update` never accepts or changes `status`. `status` must be one
  of: draft, proposed, accepted, superseded, deprecated, rejected,
  implemented.
- A change to `classification` ->
  `set_classification(id, type="req", classification)` instead --
  `update` never accepts or changes `classification`. Fully free-text;
  a blank or whitespace-only value clears it back to `None`/absent.

## 4. Check the schema, and validate before writing if useful
Fetch `specmgr://req/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate(type="req", content=content, full=False)` beforehand to dry-run the new body
without writing anything -- `update` already performs the same
validation internally, so this step is never required, only a
convenience.
