You are drafting a new Task List (TSK) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_tsk` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_tsk` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing task list on this topic first
Call the `list_tsk` tool before creating anything. If a
task list with a similar title or topic already exists, tell the user
about it and ask whether they want to revise that one (via the
`update_task` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new task list.

## 1. Structure recap (body markdown only, no frontmatter block)
- `# {title}` -- H1, mandatory, free-form.
- `<!-- optional leading comment -->` -- optional HTML comment right
  after the H1, giving context for the task list as a whole.
- A flat checklist, one `- [ ] ...`/`- [x] ...` entry per line --
  mandatory, at least one item. No phases, no per-item `depends on`/
  `status` metadata -- this is a deliberately lightweight, flat list.
- `## Recent Updates` -- mandatory H2 section, an optional leading HTML
  comment (e.g. an ordering hint) followed by at least one
  `### {timestamp} ( - | : ) {title}` entry, newest-first (e.g.
  `### 2026-08-19 - Created` or the full date+time variant
  `2026-08-19 05:42:00.000+02:00`), each followed by a short paragraph
  of update text. A freshly drafted task list must include at least
  one Recent Updates entry describing why this list was made --
  `RecentUpdates.updates` requires `min_length>=1`, so an empty section
  (or omitting it) will fail validation. `create_tsk` does not seed
  this entry automatically; you must include it yourself.

## 2. Gather information before calling any tool
Elicit (asking the user if not already given): the checklist items to
track, and a short description of why this task list is being created
for the first `## Recent Updates` entry.

## 3. Use the template/example/schema as references
Fetch `specmgr://tsk/template` or `specmgr://tsk/example` as a starting
point/style reference, then check `specmgr://tsk/schema` (the generated
JSON Schema) to confirm field names and constraints before drafting the
body. Do not invent field names or section headings that are not present
there.

## 4. Tool call sequence
1. Draft the body-only markdown per the structure above, including at
   least one checklist item and at least one `## Recent Updates` entry.
2. Call `create_tsk(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_tsk(content, full=False)` first if you want
   to dry-run the body without writing anything -- `create_tsk` already
   performs the same validation internally, so this step is never
   required, only a convenience.

## 5. Later revisions
Any later change to this task list should go through the `update_task`
prompt (or directly through the generic `update(id, type="tsk", content)`
and `set_status(id, type="tsk", status)` tools), not by re-running this
prompt. To work through the checklist itself, use the `implement_task`
prompt instead.
