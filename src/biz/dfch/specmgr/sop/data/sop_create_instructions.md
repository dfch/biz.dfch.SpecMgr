You are drafting a new Standard Operating Procedure (SOP) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_sop` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_sop` builds
id/type/status/created/updated/version automatically (and always sets
`status="draft"`).

Make a todo list and use the question tool.

## 0. Check for an existing SOP on this topic first

Call the `list_sop` tool before creating anything. If an SOP with a
similar title or topic already exists, tell the user about it and ask
(via the `question` tool) whether they want to revise that one (via the
`update_sop` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new SOP.

## 1. Structure recap (body markdown only, no frontmatter block)

- `# {title}` -- H1, mandatory, free-form.
- `## Purpose` -- mandatory prose: why this SOP exists and the outcome
  it produces.
- `## Scope` -- optional prose: what this SOP covers (and, optionally,
  what it does not).
- `## Definitions` -- optional prose: terms-of-art used by this SOP,
  defined for the reader (loose-list style, no bold lead-ins on the
  list items).
- `## Roles and Responsibilities` -- optional RASCI composite; once
  present, `### Accountable` and `### Responsible` are both mandatory:
  - `### Accountable` -- mandatory once the container is present; a
    single paragraph naming the one owner (never a bullet list).
  - `### Responsible` -- mandatory once the container is present; a
    bullet list with at least one item naming who does the work.
  - `### Support` -- optional; a bullet list that MAY be present with
    zero items (an intentional "considered, currently empty"
    placeholder, distinct from omitting the heading).
  - `### Consulted` -- optional; a bullet list, MAY be present with
    zero items.
  - `### Informed` -- optional; a bullet list, MAY be present with
    zero items.
- `## Safety and Precautions` -- optional prose: warnings and
  precautions to read before following the procedure.
- `## Procedure` -- mandatory; an ordered set of `### Step {N}: {name}`
  entries (at least one). Numbers start at 1; leading zeros are
  accepted, gaps are allowed, duplicates are rejected.
- `## Related Artifacts` -- optional container for up to five `### `
  cross-reference bullet lists: Requirements, Decisions, Goals,
  Acceptance Criteria, Sops (each `{ID}: {description}` per line; each
  sub-list needs at least one item if present). `### Sops` is a
  self-cross-reference (related/superseding SOPs).
- `## More Information` -- optional freeform supplementary text.
- `## Updates` -- optional, and the last section if present: an
  optional leading HTML comment (conventionally "Newest entry first"),
  then `### {ISO8601 timestamp} ( - | : ) {title}` entries, newest-first
  (e.g. `2026-08-30 14:30:00.000+02:00 - Created`), each with a
  mandatory lead paragraph. The timestamp is `yyyy-MM-dd HH:mm:ss.fff`
  with an explicit UTC offset (`+02:00`, `-05:00`) or `Z`, joined to the
  title by `" - "` (space, hyphen, space) or `" : "` (space, colon,
  space) -- the em-dash separator is rejected. This is a different
  format from the frontmatter dates. New entries are prepended (newest
  first), not appended.

Section order is binding: Purpose -> Scope -> Definitions -> Roles and
Responsibilities -> Safety and Precautions -> Procedure -> Related
Artifacts -> More Information -> Updates.

## 2. Build a todo list, then gather the information one at a time

Build a todo list with one entry per: the mandatory `## Purpose` and
`## Procedure`, and each optional section (`## Scope`, `## Definitions`,
`## Roles and Responsibilities`, `## Safety and Precautions`, `## Related
Artifacts`, `## More Information`, `## Updates`). Then use the
`question` tool to elicit the mandatory fields first -- the purpose and
the procedure steps -- then each optional field in turn, explicitly
telling the user they may skip any optional field they cannot or do not
want to answer yet -- a freshly created SOP may have only `## Purpose`
and `## Procedure`.

## 3. Read the RASCI role definitions before drafting `## Roles and Responsibilities`

Before filling in `## Roles and Responsibilities`, fetch the
cross-cutting `specmgr://rasci` resource and read the generic RASCI
(Responsible/Accountable/Support/Consulted/Informed) role definitions.
The `sop` schema does not duplicate those definitions here -- use the
resource as the single source of truth for what each role means, then
map the SOP's actual people/teams onto the five roles following the
binding sub-section order (Accountable, Responsible, Support, Consulted,
Informed) and the structural rules in step 1 (Accountable is a single
paragraph; Responsible needs at least one bullet; Support/Consulted/
Informed may each be present with zero items). Skip this step only if
the SOP will not have a `## Roles and Responsibilities` section at all.

## 4. Use the template/example/schema as references

Fetch `specmgr://sop/template` or `specmgr://sop/example` as a starting
point/style reference, then check `specmgr://sop/schema` (the generated
JSON Schema) to confirm field names and constraints before drafting the
body. Do not invent field names or section headings that are not present
there.

## 5. Tool call sequence

1. Assemble the full body-only markdown per the structure above, from
   the information gathered in step 2 (and the roles content informed
   by step 3).
2. Call `create_sop(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically and `status` is fixed to
   `"draft"`. A structural or field validation failure raises uncaught
   and nothing is written.
3. Optionally call `validate(type="sop", content=content, full=False)` first if you
   want to dry-run the body without writing anything -- `create_sop`
   already performs the same validation internally, so this step is
   never required, only a convenience.

## 6. Later revisions

Any later change to this SOP should go through the `update_sop` prompt
(or directly through the generic `update(id, type="sop", content)`,
`set_status(id, type="sop", status)`, and
`set_classification(id, type="sop", classification)` tools), not by
re-running this prompt. `sop` has no per-domain
`update_sop`/`set_status_sop`/`set_classification_sop` tools -- those
generic tools are the only mutation path.
