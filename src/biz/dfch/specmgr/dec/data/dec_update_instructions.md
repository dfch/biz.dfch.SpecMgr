You are revising an existing Decision (DEC) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update` -- every change to the document
goes through the specmgr MCP tools listed below.

## 1. Read current state first

Call `get_dec(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified

If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Show which sections are present and which are empty

Show the user which of the sections -- the mandatory `## Context and
Problem Statement` and `## Decision Outcome` (always present), and the
optional `## Decision Drivers`, `## Considered Options`, `## Related
Artifacts`, `## Pros and Cons`, `## More Information`, `## Updates` --
are already present with content and which are still absent. Use the
`question` tool to ask which ones (if any) they want to add to or
revise.

## 4. Map the requested change to the right tool

- A change to the body -- the `context`, `drivers`, `considered`,
  `outcome` (lead paragraph, `### Consequences`, `### Confirmation`),
  `related_artifacts`, `pros_and_cons` options, `more_information`, or
  `updates` entries -- -> the generic `update` tool called with
  `type="dec"`: a **line-range replace** for a localized change, or a
  **whole-body replace** otherwise. `content` is body markdown only (no
  frontmatter block) in both cases.
  - **Line-range replace** (a localized change -- one paragraph, field,
    or section): first call `get_dec(id, raw=True)` to see the exact
    body text, identify the 1-based line to start at and how many lines
    to replace -- `offset` is the first body line, `limit` the number of
    lines (`offset`..`offset+limit-1`); `limit` omitted replaces through
    the last body line, `limit=0` is a pure insert, and the `N+1`
    position is end-of-body: `offset = N+1` appends after the last line
    -- and call `update(id, type="dec", content, offset=..., limit=...)`
    passing only the replacement lines. The server splices the fragment
    into the current on-disk body and validates the result as a whole
    document before writing anything, so every out-of-range line stays
    byte-identical. Adding a new `## Updates` entry is typically a
    line-range insert directly below the section's optional leading
    comment (or directly below the `## Updates` heading if no comment
    is present) -- new entries go first, since the section is
    newest-first, enforced.
  - **Whole-body replace** (a multi-section change, or whenever you are
    uncertain about the line range): call `update(id, type="dec", content)`
    with no `offset`/`limit` -- `content` is then the full replacement body:
    read the current body first (step 1) and carry forward every section
    you are not intentionally changing, or it will be dropped.
    `id`/`type`/`status`/`created`/`version` are preserved automatically
    regardless of what you submit; only `updated` changes.
- A change to `status` -> `set_status(id, type="dec", status)` instead
  -- `update` never accepts or changes `status`. `status` must be one
  of: draft, proposed, accepted, rejected, superseded, deprecated.
  Mention this as a separate, optional follow-up -- e.g. `accepted`
  once the decision has genuinely been agreed to, `rejected` or
  `superseded` if the decision was not adopted or is replaced by
  another one -- do not call `set_status` unless the user actually
  asks for a status change.

## 5. Check the schema, and validate before writing if useful

Fetch `specmgr://dec/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_dec(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update` already performs the same
validation internally, so this step is never required, only a
convenience.
