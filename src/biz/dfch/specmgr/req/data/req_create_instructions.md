You are drafting a new Requirement (REQ) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_req` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_req` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing requirement on this topic first
Read the `specmgr://req/list` resource before creating anything. If a
requirement with a similar title or topic already exists, tell the user
about it and ask whether they want to revise that one (via the
`update_req` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new requirement.

## 1. Structure recap (body markdown only, no frontmatter block)
- `# {title}` -- H1, mandatory, free-form.
- Lead paragraph directly under the H1 -- the requirement statement
  itself, mandatory.
- `## Description` -- optional prose giving context/rationale.
- `## Characteristics` -- mandatory bullet list of ISO 25010:2023 quality
  attributes (e.g. "Functional Suitability", "Performance Efficiency",
  "Compatibility", "Interaction Capability", "Reliability", "Security",
  "Maintainability", "Flexibility", "Safety"); at least one item.
- `## Level` -- mandatory single-line obligation strength: one of
  MUST / SHOULD / MUST NOT / SHOULD NOT / MAY (RFC 2119 keywords).
- `## Priority` -- optional single-line value, 0-99 (lower means more
  important). Default: 50.
- `## Tags` -- optional bullet list of free-form labels.
- `## Source` -- mandatory single-line value naming the origin/authority
  of this requirement.
- `## Related Artifacts` -- optional container for up to four `### `
  cross-reference bullet lists: Requirements, Decisions, Goals,
  Acceptance Criteria (each `{ID}: {description}` per line).
- `## More Information` -- optional freeform supplementary text.
- `## Notes` -- optional freeform remarks.

## 2. Gather information before calling any tool
Elicit (asking the user if not already given): the requirement statement,
its characteristics, obligation level, and source, and optionally
priority, tags, related artifacts, description, and notes.

## 3. Use the template/example/schema as references
Fetch `specmgr://req/template` or `specmgr://req/example` as a starting
point/style reference, then check `specmgr://req/schema` (the generated
JSON Schema) to confirm field names and constraints before drafting the
body. Do not invent field names or section headings that are not present
there.

## 4. Tool call sequence
1. Draft the body-only markdown per the structure above.
2. Call `create_req(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_req(content, full=False)` first if you want
   to dry-run the body without writing anything -- `create_req` already
   performs the same validation internally, so this step is never
   required, only a convenience.

## 5. Later revisions
Any later change to this requirement should go through the `update_req`
prompt (or directly through `update_req`/`set_status_req`), not by
re-running this prompt.
