You are drafting a new Goal (GOL) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_gol` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_gol` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing goal on this topic first

Call the `list_gol` tool before creating anything. If a goal with a
similar title or topic already exists, tell the user about it and ask
(via the `question` tool) whether they want to revise that one (via the
`update_gol` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new goal.

## 1. Structure recap (body markdown only, no frontmatter block)

- `# {title}` -- H1, mandatory, free-form.
- Lead paragraph directly under the H1 -- the goal statement itself,
  mandatory.
- `## Description` -- optional prose giving context/rationale.
- `## Priority` -- optional single-line value, 0-99 (lower means more
  important).
- `## Tags` -- optional bullet list of free-form labels.
- `## Source` -- mandatory single-line value naming the origin/authority
  of this goal.
- `## Related Artifacts` -- optional container for up to four `### `
  cross-reference bullet lists: Requirements, Decisions, Goals,
  Acceptance Criteria (each `{ID}: {description}` per line).
- `## More Information` -- optional freeform supplementary text.
- `## Notes` -- optional freeform remarks.

No `## Characteristics` section exists in this schema, and none should be
added: ISO 25010:2023 quality characteristics grade requirements, not
goals. Likewise no `## Level` section -- a goal is implicitly always a
MUST; RFC 2119 obligation strength applies to the requirements below it.

## 2. Build a todo list, then gather the information one at a time

Build a todo list with one entry per: the goal `statement`, `Source`,
and each optional section (`Description`, `Priority`, `Tags`,
`Related Artifacts`, `More Information`, `Notes`). Then use the
`question` tool to elicit the mandatory fields first -- the goal
statement and the source -- then each optional field in turn,
explicitly telling the user they may skip any optional field they
cannot or do not want to answer yet -- a freshly created goal may
have zero optional sections.

## 3. Use the template/example/schema as references

Fetch `specmgr://gol/template` or `specmgr://gol/example` as a starting
point/style reference, then check `specmgr://gol/schema` (the generated
JSON Schema) to confirm field names and constraints before drafting the
body. Do not invent field names or section headings that are not present
there.

## 4. Tool call sequence

1. Assemble the full body-only markdown per the structure above, from
   the information gathered in step 2.
2. Call `create_gol(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_gol(content, full=False)` first if you
   want to dry-run the body without writing anything -- `create_gol`
   already performs the same validation internally, so this step is
   never required, only a convenience.

## 5. Later revisions

Any later change to this goal should go through the `update_gol` prompt
(or directly through the generic `update(id, type="gol", content)` and
`set_status(id, type="gol", status)` tools), not by re-running this
prompt.
