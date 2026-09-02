You are drafting a new System Requirements Specification (SYSRS) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_sysrs` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_sysrs` builds
id/type/status/created/updated/version automatically (and always sets
`status="draft"`).

Make a todo list and use the question tool.

## 0. Check for an existing SYSRS on this topic first

Call the `list_sysrs` tool before creating anything. If a SYSRS with a
similar title or topic already exists, tell the user about it and ask
(via the `question` tool) whether they want to revise that one (via the
`update_sysrs` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new SYSRS.

## 1. Structure recap (body markdown only, no frontmatter block)

A SYSRS aggregates already-existing specmgr artifacts (`gol`, `prb`,
`qa`, `uc`, `req`, `rsk`, `dec`/`adr`, `vcr`) into one coherent,
navigable specification, rather than duplicating their content: every
cross-reference list below is a bullet list of
`<TYPE> <uuid>: <title>` lines (a literal type tag, a real 8-4-4-4-12
hex UUID, a colon, then the referenced document's title), each
optionally followed by a blank line and an indented notes paragraph
paraphrasing why it is referenced here.

- `# System Requirements Specification: {title}` -- H1, mandatory,
  must start with exactly this prefix.
- `## System Purpose` -- mandatory prose: why this system is being
  developed or modified.
- `## System Scope` -- mandatory prose: what the system will and will
  not do.
- `## Business Context and Goals` -- mandatory container:
  - `### Business Context` -- optional prose: the business situation
    driving this specification.
  - `### Goals` -- mandatory once the container is present; a
    cross-reference list to `gol` (`GOL <uuid>: <title>`), at least
    one item.
  - `### Problem Statement` -- optional; a cross-reference list to
    `prb` (`PRB <uuid>: <title>`), at least one item when present.
- `## Stakeholder Needs and Elicitation` -- optional; a
  cross-reference list to `qa` (`QA <uuid>: <title>`), at least one
  item when present.
- `## Operational Concept and Scenarios` -- optional; a
  cross-reference list to `uc` (`UC <uuid>: <title>`), at least one
  item when present.
- `## Decisions` -- optional; a cross-reference list to `dec` or `adr`
  (`DEC <uuid>: <title>` or `ADR <uuid>: <title>`), at least one item
  when present.
- `## Risks` -- optional; a cross-reference list to `rsk`
  (`RSK <uuid>: <title>`), at least one item when present.
- `## Assumptions and Dependencies` -- optional prose.
- `## System Overview` -- mandatory container:
  - `### System Context` -- mandatory once the container is present;
    prose describing major elements, human elements, and significant
    interfaces crossing the system boundary.
  - `### System Functions` -- mandatory once the container is
    present; prose describing major system capabilities, conditions,
    constraints.
  - `### User Characteristics` -- optional prose.
  - `### System Integration` -- optional prose.
- `## System Modes and States` -- optional prose.
- `## Requirements` -- mandatory container; at least one of the nine
  ISO/IEC 25010:2023 characteristic sub-sections below must be
  present, each a cross-reference list to `req`
  (`REQ <uuid>: <title>`), at least one item when present, in this
  fixed order: `### Functional Suitability`, `### Performance
  Efficiency`, `### Compatibility`, `### Interaction Capability`,
  `### Reliability`, `### Security`, `### Maintainability`,
  `### Flexibility`, `### Safety`.
- `## Other Characteristics` -- optional container (omit entirely if
  none apply); the six non-25010 requirement categories below, each a
  cross-reference list to `req` (`REQ <uuid>: <title>`), at least one
  item when present, in this fixed order: `### Physical
  Characteristics`, `### Environmental Conditions`, `### Information
  Management`, `### Policy and Regulation`, `### System Life Cycle
  Sustainment`, `### Packaging, Handling, Shipping and
  Transportation`.
- `## Verification` -- optional; a cross-reference list to `vcr`
  (`VCR <uuid>: <title>`), at least one item when present.
- `## References` -- optional; a plain bullet list of external
  standards/documents (no type tag, no uuid), at least one item when
  present.
- `## More Information` -- optional freeform supplementary text.
- `## Appendix` -- optional freeform supplementary material.
- `## Definitions and Acronyms` -- optional freeform prose.
- `## Updates` -- optional, and the last section if present: an
  optional leading HTML comment (conventionally "Newest entry first"),
  then `### {ISO8601 timestamp} ( - | : ) {title}` entries, newest-first
  (e.g. `2026-08-30 14:30:00.000+02:00 - Created`), each with a
  mandatory lead paragraph. New entries are prepended (newest first),
  not appended.

Section order is binding, exactly as listed above.

## 2. Read the ISO/IEC 25010:2023 characteristic names before filling `## Requirements`

Before filling in `## Requirements`, fetch the cross-cutting
`specmgr://iso25010` resource and read the nine canonical ISO/IEC
25010:2023 product-quality characteristic names, in their canonical
model order. `## Requirements` groups every referenced `req` under the
one characteristic sub-section named by the FIRST item of that
requirement's own `## Characteristics` section (the REQ placement
rule) -- do not invent characteristic names or reorder the nine
sub-sections.

## 3. Build a todo list, then gather the information one at a time

Build a todo list with one entry per: the mandatory `## System
Purpose`, `## System Scope`, `## Business Context and Goals`
(incl. its mandatory `### Goals`), `## System Overview` (incl. its
mandatory `### System Context`/`### System Functions`), and
`## Requirements`, plus each optional section listed in step 1. Then
use the `question` tool to elicit the mandatory fields first, then
each optional field in turn, explicitly telling the user they may skip
any optional field they cannot or do not want to answer yet.

## 4. Use the template/example/schema as references

Fetch `specmgr://sysrs/template` or `specmgr://sysrs/example` as a
starting point/style reference, then check `specmgr://sysrs/schema`
(the generated JSON Schema) to confirm field names and constraints
before drafting the body. Do not invent field names or section
headings that are not present there.

## 5. Tool call sequence

1. Assemble the full body-only markdown per the structure above, from
   the information gathered in step 3 (grouped per step 2 for
   `## Requirements`).
2. Call `create_sysrs(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically and `status` is fixed to
   `"draft"`. A structural or field validation failure raises uncaught
   and nothing is written.
3. Optionally call `validate_sysrs(content, full=False)` first if you
   want to dry-run the body without writing anything -- `create_sysrs`
   already performs the same validation internally, so this step is
   never required, only a convenience.

## 6. Later revisions

Any later change to this SYSRS should go through the `update_sysrs`
prompt (or directly through the generic `update(id, type="sysrs",
content)`, `set_status(id, type="sysrs", status)`, and
`set_classification(id, type="sysrs", classification)` tools), not by
re-running this prompt. `sysrs` has no per-domain
`update_sysrs`/`set_status_sysrs`/`set_classification_sysrs` tools --
those generic tools are the only mutation path.
