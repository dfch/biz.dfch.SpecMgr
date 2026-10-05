# Schema Audit -- specmgr://<domain>/schema Resources (feat-128, Task 100.110)

Audit of the 12 whole-body domains' generated JSON Schema resources
(`specmgr://<domain>/schema`) for correctness and completeness as
agent-facing authoring guidance, including each resource's agent-facing
title/description metadata, the create/update prompts' own
title/description metadata, and the per-domain closed-vocabulary baseline
verification (Design Notes (a) of the feature README).

- **Audit target:** the worktree's own generated schemas. `uv run --frozen specmgr schema` reports all 12 `docs/<domain>_schema.json` files
  **unchanged** (exit 0), so `docs/` is the current generated output.
- **Packaged-vs-docs drift check:** all 12 packaged copies
  (`src/biz/dfch/specmgr/<domain>/data/<domain>_schema.json`) are
  **byte-identical** to the `docs/` copies (`cmp` on each pair) -- no
  drift.
- **Published-surface note:** the agent-facing surface of the Phase 100
  runs is the **published** `biz-dfch-specmgr[mcp, similarity]` 0.34.0
  (the global opencode config runs the server via `uvx`), not the
  worktree. The published version string equals the worktree's
  `pyproject.toml` version (both `0.34.0`), but the worktree is **33
  commits past the `v0.34.0` tag** with 99 changed `src/` files -- the
  live agent surface lags the repo. See "Published-vs-worktree surface
  diff" below for the material differences.

## Finding (question 2, explicit): adr has no schema resource

`adr` is the one domain without a `specmgr://<domain>/schema` resource,
which is why the audit set is 12, not 13:

- `src/biz/dfch/specmgr/commands/schema.py`, lines 305-318: the
  `_GENERATORS` dict registers exactly 12 types -- `dec`, `feat`, `gol`,
  `prb`, `qa`, `req`, `rsk`, `sop`, `sysrs`, `tsk`, `uc`, `vcr` -- and no
  `adr` entry, so `specmgr schema` can not generate an `adr_schema.json`.
- `src/biz/dfch/specmgr/adr/resources/` contains only `adr_get.py`
  (the `specmgr://adr/{id}` resource template); there is no
  `adr_schema.py`, so no `@mcp.resource("specmgr://adr/schema")` is
  registered.
- Confirmed on the live surface: a `list_resources()` probe against the
  published 0.34.0 server returns 44 resources, including
  `specmgr://<d>/schema` for exactly the 12 whole-body domains and
  nothing adr-related.

Consequence for agents: an ADR-authoring flow has no machine-readable
schema to fetch at all; the ADR's `create_adr`/`update_adr` prompts and
tool docstrings are the only structured guidance.

## Per-domain baseline verification (Design Notes (a))

Verified per domain on the worktree-generated `docs/<domain>_schema.json`
(JSON 2020-12, Pydantic v2 native): **all 12 schemas carry zero `enum`
keywords anywhere**, and the **only** `pattern` keywords in each schema
are the two feat-94 frontmatter timestamp patterns on
`<Domain>Frontmatter.properties.created` and `.updated` (e.g.
`$.$defs.TskFrontmatter.properties.created`). Every markdown leaf
(`MarkdownParagraph`, `MarkdownListItem`, `MarkdownComment`,
`MarkdownBlockQuote`, and the opaque content-blob leaves such as
prb's `Summary`/`Question1..7`, dec/sop/tsk's `UpdateEntryContent`)
renders as `properties: {}` -- a closed object with no declared
properties, so the schema conveys nothing about the content the agent
must author there.

Empty-`properties` leaf counts per domain ($defs level): req 6, uc 2,
tsk 3, qa 6, prb 15, gol 5, rsk 10, dec 11, sop 10, feat 16, vcr 5,
sysrs 16.

Schema payload sizes (bytes, `docs/<domain>_schema.json`; KB in
parentheses): tsk 12,607 (12.3), prb 15,574 (15.2), gol 16,172 (15.8),
rsk 18,722 (18.3), req 19,986 (19.5), vcr 21,318 (20.8), uc 23,096
(22.6), qa 25,406 (24.8), feat 28,859 (28.2), sop 33,039 (32.3), dec
35,296 (34.5), sysrs 53,024 (51.8). Total for all 12: 314,014 bytes
(~306.7 KB) -- the "perceived cost" of a schema fetch scales with this,
and half of it (the docstring-derived descriptions) describes the
*parser's* internal mechanics rather than authoring rules.

## Closed-vocabulary absence, per domain

Each domain's closed vocabularies are absent from the schemas as
constraints (no `enum`, no heading `pattern`), appearing at most as
prose in `description` strings:

- **req** -- `Level.value` (RFC 2119 obligation strength): the node is
  `{"$ref": "#/$defs/MarkdownParagraph", "description": "...(e.g. \"MUST\")"}`; the full set (`MUST`/`SHALL`/`SHOULD`/`MAY`/`MUST NOT`,
  `req/models/v1` Level validator) appears nowhere -- 0 occurrences of
  `shall`/`must not` in the whole file, and the single `e.g. "MUST"`
  prose example. Status set (`draft`/`proposed`/`accepted`/
  `rejected`/`implemented`/`deprecated`/`superseded`): prose-only in the
  `ReqFrontmatter` description; the `status` node itself is
  `{"default": "draft", "type": "string"}`.
- **uc** -- status set (`draft`/`proposed`/`accepted`/`deprecated`/
  `superseded`): prose-only; `status` node `{"default": "draft", "type": "string"}`.
- **tsk** -- checkbox markers: `TaskItem`'s description carries the
  `- [ ]`/`- [x]` forms in prose; the node has no pattern enforcing a
  well-formed checkbox (enforcement is code-level `AssertionError` in
  `TaskItem.checked`/`.description`). Status set (`draft`/`active`/
  `done`/`cancelled`): prose-only in the `TskFrontmatter` description.
  Recent-updates H3 timestamp form (`### {timestamp} ( - | : ) {title}`): prose-only in `UpdateEntry`'s description.
- **qa** -- the 10 Q&A-holding category headings (ISO/IEC 25010:2023
  names + `Elicitation Context`): prose-only; the bold question-number
  prefix `**<d>.<NNNN>**: ` (feat-156): prose-only in the `QaQuestion`
  description. Status set = TSK's (`draft`/`active`/`done`/`cancelled`):
  prose-only.
- **prb** -- the mandatory lead-sentence template (`[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].`): prose-only (the `is causing` template text appears in the
  `ProblemStatement`/`Summary`-adjacent descriptions); code-level
  `field_validator` rejects deviations, but the schema carries no
  `pattern`. The 7 fixed 5W2H H3 headings: prose-only in the
  `Question1..7` descriptions. Status set (`draft`/`active`/
  `resolved`/`cancelled`): prose-only.
- **gol** -- status set (`draft`/`proposed`/`accepted`/`rejected`/
  `implemented`/`deprecated`/`superseded`): prose-only.
- **rsk** -- TARA strategy set (`transfer`/`accept`/`reduce`/`avoid`):
  prose-only in `StrategyItem`/`Strategy` descriptions; the 5x5
  `### Probability {1..5}` / `### Impact {1..5}` heading values:
  prose-only (the regex `@alias` is code-level); status set
  (`open`/`mitigating`/`occurred`/`closed`/`accepted`/`dropped`):
  prose-only, `status` node `{"default": "open", "type": "string"}`.
- **dec** -- option numbering (`### Option N: ...`), RASCI H3 set
  (`Accountable`/`Responsible`/`Support`/`Consulted`/`Informed`):
  prose-only; status set (`draft`/`proposed`/`accepted`/`rejected`/
  `deprecated`/`superseded`): prose-only.
- **sop** -- the RASCI H3 set and the approval/effectivity lifecycle
  values: prose-only; status set (`draft`/`review`/`approved`/`active`/
  `retired`): prose-only.
- **feat** -- the `feat-NNN-slug` id shape and the
  Phase/Task numbering scheme: prose-only; status set
  (`planning`/`progress`/`review`/`done`): prose-only, `status` node
  `{"default": "planning", "type": "string"}`.
- **vcr** -- DTAIS method set (`Demonstration`/`Test`/`Analysis`/
  `Inspection`/`Special`): **not even fully in prose** -- `Test` occurs
  only inside one `e.g. AC-001 (Test): ...` heading example in
  `AcceptanceCriterion`'s description; `Demonstration`, `Analysis`,
  `Inspection`, `Special` have 0 occurrences in the whole file (the
  `specmgr://dtais` general resource is the only place an agent can
  learn the set). The `AC-NNN` 3-digit number + method heading regex:
  prose-only. `## Coverage` set (`full`/`partial`/`none`): prose-only.
  Status set (`draft`/`progress`/`complete`/`approved`): prose-only.
- **sysrs** -- the per-sub-list type-tagged reference vocabulary
  (`GOL`/`PRB`/`QA`/`UC`/`REQ`/`RSK`/`DEC`/`ADR`/`VCR` bullets):
  prose-only; status set (`draft`/`review`/`approved`/`active`/
  `retired`): prose-only.

## Gap list (ACC-002 format: domain, section, problem, proposed fix)

The schemas are **not** complete as agent-facing authoring guidance; the
gap list is below. "Section" names the JSON location (dot path into
`docs/<domain>_schema.json`).

01. **domain** adr, **section** (whole resource), **problem** no
    `specmgr://adr/schema` resource and no `commands/schema.py`
    `_GENERATORS` entry, so ADR-authoring flows have no machine-readable
    schema at all, **proposed fix** add an `adr` generator entry (the
    `models/adr/v1` Pydantic models already exist) plus the matching
    `adr/resources/adr_schema.py` resource, or document the deliberate
    exclusion.
02. **domain** all 12, **section** `<Domain>Frontmatter.properties.status`,
    **problem** the closed status vocabulary (domain-specific 4-7 value
    sets) is a plain `{"type": "string", "default": ...}` with the values
    only in the class description prose, so an agent cannot see the
    allowed values as constraints and cannot validate its own choice
    against the schema, **proposed fix** emit `enum` for `status` in each
    domain's frontmatter model (Pydantic `Literal` or an explicit
    `json_schema_extra`), or at minimum a `pattern` enumerating the set.
03. **domain** all 12, **section** every `properties: {}` markdown leaf
    (6/2/3/6/15/5/10/11/10/16/5/16 per domain), **problem** the schema
    says nothing about what content the leaf must carry (prose paragraph,
    bullet list, fixed template, cross-reference bullet shape); the
    authoring rules live only in the descriptions' prose or not at all,
    **proposed fix** demote the schema to constraint discovery and move
    markdown-level authoring guidance to the template/example resources
    (which already carry it), or add per-leaf `content` hints (e.g.
    `format`/`$comment`-style annotations) without breaking the
    parsed-JSON contract.
04. **domain** req, **section** `$defs.Level.properties.value`,
    **problem** the RFC 2119 obligation-strength set is absent (0
    `shall`/`must not` occurrences; one `e.g. "MUST"` prose example),
    **proposed fix** `enum` on `Level.value` (single-line, so an enum of
    the 5 RFC 2119 words is directly expressible) or a `pattern`.
05. **domain** tsk, **section** `$defs.TaskItem`, **problem** the
    checkbox well-formedness (`- [ ]`/`- [x]`) is code-level
    `AssertionError` only; the schema node carries the forms in prose,
    **proposed fix** a `pattern` annotation on the item's text view or an
    explicit `format` hint, since TSK's whole body is checkbox lines.
06. **domain** tsk, **section** `$defs.UpdateEntry`, **problem** the H3
    timestamp form (`### {timestamp} ( - | : ) {title}`, full date+time,
    `-`/`:` separator, em-dash rejected) is prose-only,
    **proposed fix** a heading-shape `pattern` or a structured
    `{timestamp, title}` hint (the model already computes both).
07. **domain** qa, **section** `$defs.QaQuestion` (and the 10 category
    headings), **problem** the bold question-number prefix
    `**<d>.<NNNN>**: ` and the fixed ISO/IEC 25010:2023 category heading
    set are prose-only, **proposed fix** a `pattern` for the question
    prefix and an `enum`/list annotation for the category heading set.
08. **domain** prb, **section** the lead-sentence field (Problem
    Statement lead paragraph) and `$defs.Question1..7`, **problem** the
    mandatory fixed lead-sentence template and the 7 verbatim 5W2H
    headings are prose-only (code-level `field_validator` enforces the
    template), **proposed fix** a `pattern` for the lead-sentence frame
    (the 4 blanks make a regex feasible) and the 7 headings as a fixed
    list annotation.
09. **domain** rsk, **section** `$defs.StrategyItem` and the
    Probability/Impact H3 nodes, **problem** the TARA set
    (`transfer`/`accept`/`reduce`/`avoid`) and the 5x5 `### Probability {1..5}`/`### Impact {1..5}` heading values are prose-only (regex
    `@alias` is code-level), **proposed fix** `enum` on the strategy
    value and heading-value `pattern`s (both are single-line closed
    sets).
10. **domain** vcr, **section** `$defs.AcceptanceCriterion` and
    `$defs.Coverage`, **problem** the DTAIS method set is absent even as
    prose (only `Test` occurs, inside one example heading;
    `Demonstration`/`Analysis`/`Inspection`/`Special` never occur), the
    `AC-NNN (Method):` heading regex and the `full`/`partial`/`none`
    coverage set are prose-only, **proposed fix** `enum` on the method
    word and the coverage value (both single-line closed sets), a
    heading `pattern` for `AC-NNN`, and reference the
    `specmgr://dtais` resource from the schema description.
11. **domain** all 12, **section** resource metadata
    (`@mcp.resource()` title/description), **problem** the wording is
    provenance-oriented (how the file is generated and kept current)
    rather than usage-oriented (what an agent should do with it before
    authoring a body), see the verbatim strings below, **proposed fix**
    reword each resource description to a usage directive ("Fetch this
    before drafting a <domain> body; it lists the mandatory sections,
    closed vocabularies, and heading shapes") while keeping the
    provenance sentence.
12. **domain** all 12, **section** create/update prompt metadata
    (`@mcp.prompt()` title/description), **problem** the 24 prompt
    titles/descriptions are silent about the schema/template/example
    resources, so an agent choosing among prompts/resources from the
    listing gets no hint that the schema exists, see the verbatim strings
    below, **proposed fix** add one clause to each create/update prompt
    description naming the `specmgr://<domain>/schema` (and
    template/example) resources as the authoritative structure
    reference.
13. **domain** all 12, **section** `create_<d>`/generic `update` tool
    descriptions (agent-visible `tools/list` metadata), **problem** none
    of the create/update/get/list/validate tool descriptions mention the
    schema/template/example resources (verified verbatim below and on
    the live published surface), so tool-direct flows that never invoke a
    prompt get zero pointers to the schema, **proposed fix** add a
    short "structure reference: `specmgr://<domain>/schema` (also
    `/template`, `/example`)" clause to each `create_<d>` description and
    to the generic `update`/`validate` descriptions.
14. **domain** all 12, **section** top-level `description` and
    docstring-derived `$defs` descriptions, **problem** large parts of
    the payload describe the *parser's* internal mechanics (`_value`,
    `get_extent`, `from_text`, computed-property derivation,
    `model_dump`) rather than authoring rules -- e.g.
    `MarkdownParagraph`'s description explains leaf-vs-composite parsing
    internals, and every fetch pays for it (12.3 KB for tsk up to 51.8
    KB for sysrs), **proposed fix** split the schema into an
    authoring-facing view (sections, required/optional, closed sets,
    heading shapes) and keep the implementation view in the code
    docstrings only.
15. **domain** all 12, **section** `frontmatter` block of the document
    schema, **problem** the schemas describe the *parsed JSON* shape
    (property names like `statement`, `characteristics`, `frontmatter`,
    `body`) while the agent authors *markdown*; the prompts' "confirm
    field names" instruction conflates the two artifact layers (Design
    Notes (d)), **proposed fix** accompany the schema with (or render
    into it) a markdown-shape summary -- the template resource already
    is one; the schema description should say explicitly that it is the
    parsed-JSON view and point at the template for the markdown view.
16. **domain** tsk (live surface), **section** published-vs-worktree
    schema, **problem** the published 0.34.0 `tsk_schema.json` differs
    from the worktree's by 12 lines (`UpdateEntry.content` is
    `MarkdownParagraph` in 0.34.0 but the opaque `UpdateEntryContent`
    blob in the worktree); agents on the live surface fetch the older
    schema, **proposed fix** release cadence (ship the worktree state)
    plus, in the follow-up, make the schema `$comment` layout marker
    visible to agents so a shape-change is detectable from the resource
    itself.

## Agent-facing metadata audit (verbatim)

### Schema resources (all 12, uniform template)

Every `specmgr://<domain>/schema` resource in
`src/biz/dfch/specmgr/<domain>/resources/<domain>_schema.py` (decorator
lines 49-59, varying only in the domain word) carries:

- `name="<domain>_schema"`, `title="<Domain> (<XXX>) JSON Schema"` (e.g.
  `title="Task List (TSK) JSON Schema"`, `title="Problem Statement (PRB) JSON Schema"`).
- `description="The generated <XXX> JSON Schema (2020-12 dialect), generated by `specmgr schema`and kept current by a pre-commit hook/CI step. Includes a`$comment` schema-layout version marker for detecting a shape change without diffing the whole document."` (the
  full 12 are recorded in the evidence manifest; all are the same three
  sentences with the domain word substituted).

Classification: **provenance-oriented** -- all three sentences describe
how the file is produced and kept current (generation command,
hook/CI maintenance, `$comment` marker). Zero sentences tell an agent
*when* to fetch it (before authoring a body) or *what for* (structure,
required/optional sections, closed vocabularies, heading shapes).

### Create/update prompts (24; tsk and prb verbatim, pattern uniform)

The `@mcp.prompt()` decorator metadata for the 24 whole-body
create/update prompts is uniform in shape and **silent about the
schema** in every case:

- `create_task` (tsk): `title="Create a task list"`,
  `description="Guides the LLM through checking for an existing similar task list, gathering the required information, and driving create_tsk/validate to author a new TSK document."`
- `update_task` (tsk): `title="Update a task list"`,
  `description="Guides the LLM through revising an existing task list by id: reading current state, applying the requested change with the right tool, and validating."`
- `create_prb`: `title="Create a problem statement"`,
  `description="Guides the LLM through checking for an existing similar problem statement, optionally carrying over already-answered 5W2H questions from a linked QA document (qa_id), interviewing the user for whichever 5W2H current-state questions remain, synthesizing the Summary and Gap, composing the mandatory Problem Statement lead sentence, and driving create_prb/validate to author a new PRB document."`
- `update_prb`: `title="Update a problem statement"`,
  `description="Guides the LLM through revising an existing problem statement by id: reading current state (recovering an old-shape document missing the mandatory lead sentence via a raw re-read if needed), showing which of the 7 5W2H questions are answered, eliciting revisions, re-synthesizing Summary/Gap, applying the change with the right tool, and validating."`

The other 20 (req/uc/qa/gol/rsk/dec/sop/feat/vcr/sysrs) follow the same
two-sentence pattern ("checking for an existing similar X ... driving
create_X/validate to author a new X document." / "revising an existing X
by id: reading current state, applying the requested change with the
right tool, and validating."), recorded in the evidence manifest.
Classification: **task-flow-oriented, schema-silent** -- none of the 24
mentions `specmgr://<domain>/schema`, `/template`, or `/example`, so the
prompt *listing* gives no hint that a schema resource exists; the schema
pointer appears only *inside* the prompt body (create step 3/4/10,
update step 4/5/6/9 -- Design Notes (b)), which an agent never reads
without invoking the prompt.

### Tool descriptions (live published surface, verbatim in the manifest)

Captured from the published 0.34.0 server's `tools/list`: `create_tsk`,
`create_prb`, `get_tsk`, `get_prb`, `list_tsk`, `list_prb`, `update`,
`validate` -- **none** mention the schema/template/example resources.
The only resource-adjacent pointers are "use the corresponding `get_<d>`
tool to fetch the full document afterward" (create tools) and the
`validate_adr` cross-reference in `validate`. This confirms Design Notes
(c) on the live surface: tool-direct flows get zero schema pointers.

## Published-vs-worktree surface diff (agent-facing)

- **Version string:** published 0.34.0 == worktree `pyproject.toml`
  0.34.0 (no version-level divergence), but the worktree is
  `v0.34.0-33-g27cbe27` (33 commits past the release tag; 99 changed
  `src/` files). The live agent surface therefore lags the repo.
- **`get_<d>` tools:** published lacks the feat-153 `numbered`
  parameter (verified on the live `get_tsk` input schema: `id`/`raw`/
  `offset`/`limit` only; the worktree adds `numbered`).
- **`update` tool:** published returns the frontmatter-only shape and
  its description says so; the worktree returns the `UpdateResult`
  wrapper with `snippet` (description updated accordingly).
- **Instruction files (prompt bodies):** the published tsk/prb
  update instructions direct `get_<d>(id, raw=True)` with manual line
  counting; the worktree directs `get_<d>(id, raw=True, numbered=True)`.
  The published tsk create instructions describe Recent Updates entry
  content as "a short paragraph"; the worktree allows "any markdown
  content". The prb create instructions are unchanged.
- **Schemas:** prb/uc/qa/rsk are byte-identical between published 0.34.0
  and the worktree; tsk (+12 lines, `UpdateEntryContent`), vcr (+12),
  sysrs (+12), feat (+24), req (+82), gol (+88), dec (+94), sop (+122)
  differ (the latter four mainly the issue #135 `### Risks` sub-list
  additions). The Phase 100 runs' prb observations therefore apply
  directly to the audited schemas; the tsk observations apply to the
  older published tsk schema, which differs from the audited one only in
  the `UpdateEntryContent` leaf (gap entry 16).
- **Registration counts (live published surface):** 84 tools, 25
  prompts, 44 resources (probe output in the evidence manifest).
