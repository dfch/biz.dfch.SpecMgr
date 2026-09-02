You are drafting a new Feature (FEAT) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_feat` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_feat` builds
id/type/status/created/updated/version automatically -- a fresh
`feat-NNN-slug` id, `status="planning"` always (never caller-supplied on
create), and the current date+time timestamp for `created`/`updated`.

Make a todo list and use the question tool.

## 0. Check for an existing feature on this topic first

Call the `list_feat` tool before creating anything. If a feature with a
similar title or topic already exists, tell the user about it and ask
(via the `question` tool) whether they want to revise that one (via the
`update_feat` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new feature.

## 1. Structure recap (body markdown only, no frontmatter block)

- `# Feature: {title}` -- H1, mandatory, free-form title after the fixed
  `Feature: ` prefix.
- `## Plan` -- mandatory container, no own text:
  - `### Overview` -- mandatory prose: what this feature is and why it
    exists.
  - `### Requirements` -- mandatory bullet list, at least one item, each
    line `REQ-NNN: {text}`.
  - `### Acceptance Criteria` -- mandatory checklist, at least one item,
    each line `- [ ] ACC-NNN: {text}` (or `- [x] ...` once verified).
  - `### Scope` -- mandatory container, no own text, holding two
    mandatory leaves: `#### Included` and `#### Explicitly Out Of Scope`.
  - `### Dependencies` -- optional container, no own text, holding two
    independently optional leaves: `#### Depends On` and `#### Blocks`.
  - `### Design Notes` -- optional prose.
  - `### Related Decisions` -- optional bullet list of related ADR/DEC
    ids with a short description each.
  - `### Task List` -- mandatory container, no own text, holding at
    least one `#### Phase N: {title}` entry (unpadded phase number, e.g.
    "Phase 1"), each with its own flat checklist of at least one
    `- [ ] .../- [x] ...` task item.
- `## Progress` -- mandatory container, no own text:
  - `### Current Status` -- mandatory prose: where things stand today.
  - `### Blockers` -- optional prose/list of open blockers.
  - `### Updates` -- mandatory, an optional leading HTML comment (e.g. an
    ordering hint) followed by at least one
    `#### {timestamp} ( - | : ) {title}` entry, newest-first, where
    `{timestamp}` is `yyyy-MM-dd HH:mm:ss.fff±HH:mm` (or `Z` for UTC) and
    the separator is `" - "` or `" : "` (the em-dash separator is
    rejected), each with a lead paragraph.
  - `### Decisions Made` -- optional, same shape as `### Updates` (same
    timestamp format, same newest-first ordering, at least one entry once
    the section is present at all).
  - `### Related PRs / Commits` -- optional freeform list.
  - `### More Information` -- optional freeform supplementary text.

Section order is binding, exactly as listed above. There is no
`update_feat`/`set_status_feat` tool of its own -- later changes go
through the generic `update`/`set_status` tools with `type="feat"` (see
step 5).

## 2. Build a todo list, then gather the information one at a time

Build a todo list with one entry per: the mandatory `Overview`,
`Requirements`, `Acceptance Criteria`, `Scope` (both `Included` and
`Explicitly Out Of Scope`), `Task List`, `Current Status`, `Updates`, and
each optional section (`Dependencies`, `Design Notes`,
`Related Decisions`, `Blockers`, `Decisions Made`,
`Related PRs / Commits`, `More Information`). Then use the `question`
tool to elicit the mandatory fields first, then each optional field in
turn, explicitly telling the user they may skip any optional field they
cannot or do not want to answer yet.

## 3. Use the template/example/schema as references

Fetch `specmgr://feat/template` or `specmgr://feat/example` as a
starting point/style reference, then check `specmgr://feat/schema` (the
generated JSON Schema) to confirm field names and constraints before
drafting the body. Do not invent field names or section headings that
are not present there.

## 4. Tool call sequence

1. Assemble the full body-only markdown per the structure above, from
   the information gathered in step 2.
2. Call `create_feat(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically, including the
   `feat-NNN-slug` id derived from the H1 title. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_feat(content, full=False)` first if you
   want to dry-run the body without writing anything -- `create_feat`
   already performs the same validation internally, so this step is
   never required, only a convenience.

## 5. Later revisions

Any later change to this feature should go through the `update_feat`
prompt (or directly through the generic `update(id, type="feat", content)`
and `set_status(id, type="feat", status)` tools), not by re-running this
prompt.
