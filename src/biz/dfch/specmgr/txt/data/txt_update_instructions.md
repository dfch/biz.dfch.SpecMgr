You are revising an existing free-form text (TXT) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update` or `edit` -- every change to the
document goes through the specmgr MCP tools listed below.

## 1. Read current state first

Call `get_txt(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified

If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Show what the document currently holds

Show the user the document's current free-form body (including any H2
to H6 headings inside it) and its `## Updates` log entries. Use the
`question` tool to ask what they want to add to or revise.

## 4. Map the requested change to the right tool

- A change to the body -- the free-form body text (a paragraph, a
  heading, a list, a code block), or the `updates` entries -- -> the
  generic `update` tool called with `type="txt"`: a **line-range
  replace** for a localized change, or a **whole-body replace**
  otherwise. `content` is body markdown only (no frontmatter block) in
  both cases.
  - **Line-range replace** (a localized change -- one paragraph,
    heading, or update entry): first call
    `get_txt(id, raw=True, numbered=True)` to see the exact body text --
    every line prefixed with its 1-based body-line number, so no manual
    counting is needed and a number seen can be fed straight back into
    `update`'s `offset` -- identify the
    1-based line to start at and how many lines to replace -- `offset`
    is the first body line, `limit` the number of lines
    (`offset`..`offset+limit-1`); `limit` omitted replaces through
    the last body line, `limit=0` is a pure insert, and the `N+1`
    position is end-of-body: `offset = N+1` appends after the last line
    -- and call
    `update(id, type="txt", content, offset=..., limit=...)` passing only
    the replacement lines. The server splices the fragment into the
    current on-disk body and validates the result as a whole document
    before writing anything, so every out-of-range line stays
    byte-identical. Adding a new `## Updates` entry is typically a
    line-range insert directly below the section's optional leading
    comment (or directly below the `## Updates` heading if no comment
    is present) -- new entries go first, since the section is
    newest-first, enforced. Each entry's heading is
    `### {timestamp} ( - | : ) {title}`, where `{timestamp}` is the full
    date+time form `yyyy-MM-dd[T ]HH:mm:ss.SSS` + `Z` or `±HH:mm` (the
    date/time separator may be `T` or a space; a date-only timestamp is
    rejected), followed by the entry's own update text directly under
    the H3 heading (any markdown content -- multiple paragraphs, lists,
    code blocks, block quotes, not just a single paragraph), which is
    mandatory. `offset`/`limit` address the frontmatter-stripped body,
    never the raw on-disk `.md` file: the YAML frontmatter block is
    variable-length, so a raw file read's line numbers are never the
    same as body-line coordinates -- and never feed the `numbered=True`
    output back verbatim as `content`: strip the `"<n>: "` prefix from
    each line first.
  - **Whole-body replace** (a multi-section change, or whenever you are
    uncertain about the line range): call `update(id, type="txt", content)`
    with no `offset`/`limit` -- `content` is then the full replacement
    body: read the current body first (step 1) and carry forward the
    free-form body content and the `## Updates` section you are not
    intentionally changing, or it will be dropped.
    `id`/`type`/`status`/`created`/`version` are preserved automatically
    regardless of what you submit; only `updated` changes.
  - The body ends at the first top-level `## Updates` H2: do not
    introduce a second `## Updates`, and do not add any other H2 after
    it -- both fail validation and nothing is written.
- A small, exact-match string replacement in the body -> the generic
  `edit` tool called with `type="txt"`:
  `edit(id, type="txt", old_str, new_str)` -- `old_str` must match the
  on-disk body byte-exactly and must be unique (unless
  `replace_all=True`), and the edited body must still validate as a
  whole document; nothing is written if either check fails. Read the
  current body via `get_txt(id, raw=True)` first to copy the exact text.
- A change to `status` -> `set_status(id, type="txt", status)` instead
  -- `update` never accepts or changes `status`. `status` must be one
  of: draft, progress, done. Mention this as a separate, optional
  follow-up -- e.g. `progress` while the text is being actively worked
  on, `done` once it is final -- do not call `set_status` unless the
  user actually asks for a status change.
- A change to `classification` ->
  `set_classification(id, type="txt", classification)` instead --
  `update` never accepts or changes `classification`. Fully free-text;
  a blank or whitespace-only value clears it back to `None`/absent.

## 5. Check the schema only for structural changes, and validate before writing if useful

Call the `get_txt_schema` tool (the generated JSON Schema) only for a
whole-body rewrite or a structural change -- to confirm field names and
constraints. Skip the schema fetch for a local splice (a line-range
replace or an `edit`), where the raw body is already in context:
`update` and `edit` both validate the result as a whole document before
writing anything, so the skip is safe. Optionally call
`validate(type="txt", content=content, full=False)` beforehand to dry-run the
new body without writing anything -- `update` already performs the same
validation internally, so this step is never required, only a
convenience.
