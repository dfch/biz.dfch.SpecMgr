You are drafting a new Decision (DEC) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_dec` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_dec` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing decision on this topic first

Call the `list_dec` tool before creating anything. If a decision with
a similar title or topic already exists, tell the user about it and ask
(via the `question` tool) whether they want to revise that one (via the
`update_dec` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new decision.

## 1. Structure recap (body markdown only, no frontmatter block)

- `# {title}` -- H1, mandatory, free-form.
- `## Context and Problem Statement` -- mandatory prose: the situation
  and the problem the decision addresses.
- `## Decision Drivers` -- optional prose: the requirements,
  constraints, and stakeholder interests that shape the decision.
- `## Considered Options` -- optional prose: a free-form summary of
  the options that were weighed.
- `## Decision Outcome` -- mandatory: a lead paragraph naming the
  chosen option (e.g. "We chose option 1 because ..."), followed by
  optional `### Consequences` and `### Confirmation` H3 sections.
- `## Roles and Responsibilities` -- mandatory RASCI composite: every
  decision always names an accountable owner, so this whole section is
  always present (unlike SOP's own optional equivalent):
  - `### Accountable` -- mandatory; a single paragraph naming the one
    owner ultimately answerable for the decision (never a bullet list).
  - `### Responsible` -- mandatory; a bullet list with at least one item
    naming who carries out the decision or its consequences.
  - `### Support` -- optional; a bullet list that MAY be present with
    zero items (an intentional "considered, currently empty"
    placeholder, distinct from omitting the heading).
  - `### Consulted` -- optional; a bullet list, MAY be present with
    zero items.
  - `### Informed` -- optional; a bullet list, MAY be present with
    zero items.
- `## Tags` -- optional bullet list of free-form labels for
  grouping/filtering decisions.
- `## Source` -- mandatory prose: the origin/authority of this
  decision, e.g. an issue, a meeting, or a stakeholder request.
- `## Related Artifacts` -- optional container for up to four `### `
  cross-reference bullet lists: Requirements, Decisions, Goals,
  Acceptance Criteria (each `{ID}: {description}` per line).
- `## Pros and Cons` -- optional appendix of `### Option {N}: {name}`
  sections, one per weighed option (the title after the colon is
  mandatory, numbers start at 1 and are never renumbered). The H2 is
  present only if at least one option exists.
- `## More Information` -- optional freeform supplementary text.
- `## Updates` -- optional, and the last section if present: an
  optional leading HTML comment (conventionally "Newest entry first"),
  then timestamp-led `### {timestamp} ( - | : ) {title}` entries,
  newest-first, where `{timestamp}` is the full date+time form
  `yyyy-MM-dd[T ]HH:mm:ss.fff` + `Z` or `±HH:mm` (e.g. `### 2026-08-27
  14:30:00.000+02:00 - Created`), each with a mandatory lead paragraph.
  The date/time separator may be `T` or a space; a date-only timestamp
  is rejected. New entries are prepended (newest first), not appended.

Section order is binding: Context and Problem Statement -> Decision
Drivers -> Considered Options -> Decision Outcome -> Roles and
Responsibilities -> Tags -> Source -> Related Artifacts -> Pros and Cons
-> More Information -> Updates. The ADR heading
`## Pros and Cons of the Options` is not part of this schema and must
not be used.

## 2. Build a todo list, then gather the information one at a time

Build a todo list with one entry per: the mandatory `## Context and
Problem Statement`, `## Decision Outcome`, `## Roles and
Responsibilities`, and `## Source`, and each optional section (`##
Decision Drivers`, `## Considered Options`, `## Tags`, `## Related
Artifacts`, `## Pros and Cons`, `## More Information`, `## Updates`).
Then use the `question` tool to elicit the mandatory fields first --
the context, the outcome, the roles and responsibilities, and the
source -- then each optional field in turn, explicitly telling the user
they may skip any optional field they cannot or do not want to answer
yet -- a freshly created decision may have zero optional sections.

## 3. Read the RASCI role definitions before drafting `## Roles and Responsibilities`

Before filling in `## Roles and Responsibilities`, fetch the
cross-cutting `specmgr://rasci` resource and read the generic RASCI
(Responsible/Accountable/Support/Consulted/Informed) role definitions.
The `dec` schema does not duplicate those definitions here -- use the
resource as the single source of truth for what each role means, then
map the decision's actual people/teams onto the five roles following
the binding sub-section order (Accountable, Responsible, Support,
Consulted, Informed) and the structural rules in step 1 (Accountable is
a single paragraph; Responsible needs at least one bullet;
Support/Consulted/Informed may each be present with zero items). Unlike
SOP's own optional `## Roles and Responsibilities`, this section is
mandatory on every `dec` document, so this step is never skipped.

## 4. Use the template/example/schema as references

Fetch `specmgr://dec/template` or `specmgr://dec/example` as a starting
point/style reference, then check `specmgr://dec/schema` (the generated
JSON Schema) to confirm field names and constraints before drafting the
body. Do not invent field names or section headings that are not present
there.

## 5. Tool call sequence

1. Assemble the full body-only markdown per the structure above, from
   the information gathered in step 2 (and the roles content informed
   by step 3).
2. Call `create_dec(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate(type="dec", content=content, full=False)` first if you
   want to dry-run the body without writing anything -- `create_dec`
   already performs the same validation internally, so this step is
   never required, only a convenience.

## 6. Later revisions

Any later change to this decision should go through the `update_dec` prompt
(or directly through the generic `update(id, type="dec", content)`,
`set_status(id, type="dec", status)`, and
`set_classification(id, type="dec", classification)` tools), not by
re-running this prompt.
