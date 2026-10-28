You are drafting a new free-form text (TXT) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_txt` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_txt` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing free-form text document on this topic first

Call the `list_txt` tool before creating anything. If a free-form text
document for the same topic (or a similar title) already exists, tell
the user about it and ask (via the `question` tool) whether they want
to revise that one (via the `update_txt` prompt) instead of creating a
duplicate. Only proceed to step 1 if this is genuinely a new document.

## 1. Structure recap (body markdown only, no frontmatter block)

- `# {title}` -- H1, mandatory, free-form.
- Free-form body -- mandatory, and opaque: any markdown (paragraphs,
  lists, code blocks, H2 to H6 headings) between the H1 and the
  `## Updates` section is accepted verbatim. A free-floating
  `REQ <uuid>` reference line (or any other known tag) may appear
  anywhere in the body. The body ends at the first top-level
  `## Updates` H2: do not put a second `## Updates` in the document,
  and do not put any other H2 after it -- both are rejected.
- `## Updates` -- mandatory, and the last section of the document: an
  optional leading HTML comment (conventionally "Newest entry first"),
  then at least one timestamp-led `### {timestamp} ( - | : ) {title}`
  entry, newest-first, where `{timestamp}` is the full date+time form
  `yyyy-MM-dd[T ]HH:mm:ss.SSS` + `Z` or `±HH:mm` (e.g.
  `### 2026-08-31 07:40:12.500+02:00 - Created`), each with the entry's
  own update text directly under the H3 heading (any markdown content
  -- multiple paragraphs, lists, code blocks, block quotes, not just a
  single paragraph), which is mandatory. The date/time separator may be
  `T` or a space; a date-only timestamp is rejected. New entries are
  prepended (newest first), not appended.

Section order is binding: H1 -> free-form body -> Updates.

## 2. Build a todo list, then gather the information one at a time

Build a todo list with one entry per: the H1 title, the free-form body
content, and the `## Updates` log. Then use the `question` tool to
elicit the title, the body content, and at least one update entry in
turn. There are no optional sections in a free-form text document --
the body and the `## Updates` log are both mandatory -- so ask the user
for the body content rather than inventing it.

## 3. Use the template/example tools as references

Call the `get_txt_template` and `get_txt_example` tools as your
starting point/style reference -- one hop each. Do not invent field
names or section headings that are not present there. Call the
`get_txt_schema` tool (the generated JSON Schema) only when you are
structurally uncertain or are resolving a validation error.

## 4. Tool call sequence

1. Assemble the full body-only markdown per the structure above, from
   the information gathered in step 2.
2. Call `create_txt(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate(type="txt", content=content, full=False)`
   first if you want to dry-run the body without writing anything --
   `create_txt` already performs the same validation internally, so
   this step is never required, only a convenience.

## 5. Later revisions

Any later change to this free-form text document should go through the
`update_txt` prompt (or directly through the generic
`update(id, type="txt", content)`, `set_status(id, type="txt", status)`,
and `set_classification(id, type="txt", classification)` tools), not by
re-running this prompt.
