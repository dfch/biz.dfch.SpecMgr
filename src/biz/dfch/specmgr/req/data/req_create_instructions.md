You are drafting a new Requirement (REQ) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_req` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_req` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing requirement on this topic first
Call the `list_req` tool before creating anything. If a
requirement with a similar title or topic already exists, tell the user
about it and ask whether they want to revise that one (via the
`update_req` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new requirement.

## 1. Structure recap (body markdown only, no frontmatter block)
- `# {title}` -- H1, mandatory, free-form.
- Lead paragraph directly under the H1 -- the requirement statement
  itself, mandatory. Obligation is carried by the statement's phrasing,
  not by a field: `shall` expresses an obligation, `should` a
  recommendation whose deviation must be justified. Read `specmgr://ears`
  before phrasing the statement.
- `## Description` -- optional prose giving context/rationale.
- `## Characteristics` -- mandatory bullet list of ISO 25010:2023 quality
  attributes (e.g. "Functional Suitability", "Performance Efficiency",
  "Compatibility", "Interaction Capability", "Reliability", "Security",
  "Maintainability", "Flexibility", "Safety"); at least one item.
- `## Level` -- mandatory single-line ISO 29148 requirement
  specification kind: one of BRS / StRS / SyRS / SRS (the
  ISO/IEC/IEEE 29148:2018 §3.2 abbreviations). Fetch the
  `specmgr://iso29148` resource before filling this in (step 3) to
  confirm what each kind means and which one applies.
- `## Priority` -- optional single-line value, 0-99 (lower means more
  important). Default: 50.
- `## Tags` -- optional bullet list of free-form labels.
- `## Source` -- mandatory single-line value naming the origin/authority
  of this requirement.
- `## Related Artifacts` -- optional container for up to four `### `
  cross-reference bullet lists: Requirements, Decisions, Goals, Risks
  (each bullet MUST match `<TAG> <uuid>: <title>` -- a space-separated
  tag, a lowercase 8-4-4-4-12 hex UUID, and a title, e.g.
  `REQ 550e8400-e29b-41d4-a716-446655440000: <title>`; `Decisions`
  accepts only the `DEC` tag).
- `## More Information` -- optional freeform supplementary text.
- `## Notes` -- optional freeform remarks.

## 2. Gather information before calling any tool
Elicit (asking the user if not already given): the requirement statement,
its characteristics, its ISO 29148 requirement specification kind
(`## Level`), and source, and optionally priority, tags, related
artifacts, description, and notes.

## 3. Read the ISO 29148 requirement specifications before drafting `## Level`
Before filling in `## Level`, fetch the cross-cutting
`specmgr://iso29148` resource and read the four requirement
specifications (BRS, StRS, SyRS, SRS) and the "When to use each"
guidance. The `req` schema does not duplicate those definitions here --
use the resource as the single source of truth for what each kind
means, then ask the user (via the `question` tool) which of the four
kinds this requirement is.

## 4. Use the template/example tools as references
Call the `get_req_template` and `get_req_example` tools as your
starting point/style reference -- one hop each. Do not invent field
names or section headings that are not present there. Call the
`get_req_schema` tool (the generated JSON Schema) only when you are
structurally uncertain or are resolving a validation error.

## 5. Tool call sequence
1. Draft the body-only markdown per the structure above.
2. Call `create_req(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate(type="req", content=content, full=False)` first if you want
   to dry-run the body without writing anything -- `create_req` already
   performs the same validation internally, so this step is never
   required, only a convenience.

## 6. Later revisions
Any later change to this requirement should go through the `update_req` prompt
(or directly through the generic `update(id, type="req", content)`,
`set_status(id, type="req", status)`, and
`set_classification(id, type="req", classification)` tools), not by
re-running this prompt.
