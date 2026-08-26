---
created: 2026-08-25
id: feat-18-goal
status: in-progress
updated: 2026-08-26
version: 1.0.0
---

# Feature: Add artifact type Goal (gol)

## Plan

### Overview

Add a new markdown artifact type, `Goal` (abbreviation `gol`), for capturing
high-level business goals — the strategic "what the organization wants to
achieve" level that sits above individual requirements. `gol` follows the
domain-first hierarchy and MCP surface already established by `req`/`prb`
(ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and mirrors `req`'s body schema
with exactly two deliberate omissions: no `## Characteristics` section (ISO
25010:2023 quality characteristics are a requirement-level attribute — a
business goal stays deliberately free of them) and no `## Level` section
(RFC 2119 obligation strength is implicit — a goal is always a MUST). `req`
already anticipates this artifact type: its `## Related Artifacts` →
`### Goals` cross-reference sub-list (exercised in `req_example.md` as
`GOL-0007: Competitive Engines in Consumer Vehicles`) points at documents
of exactly this shape, and `gol_example.md` will be that very goal so the
two packaged examples read coherently side by side. `gol` reuses `req`'s
whole-body update convention (not ADR's granular `update_section`
mechanism) and `req`'s 7-value frontmatter status set.

### Requirements

- REQ-001: Define the `gol` markdown schema — frontmatter (`type="gol"`,
  7-value status set `draft`/`proposed`/`accepted`/`superseded`/
  `deprecated`/`rejected`/`implemented`, `req`'s exact set) and body (H1
  title, mandatory `statement` lead paragraph, optional `## Description`,
  optional `## Priority`, optional `## Tags`, mandatory `## Source`,
  optional `## Related Artifacts` holding four optional, fixed-heading
  `### ` cross-reference sub-lists — `Requirements`/`Decisions`/`Goals`/
  `Acceptance Criteria` — optional `## More Information`, optional
  `## Notes`). No `## Characteristics` and no `## Level` (see Design
  Notes).
- REQ-002: Pydantic models under `gol/models/v1/` (frontmatter, body,
  document, parser, summary), domain-first, mirroring `req`/`prb`'s exact
  file shapes. No `models/md` engine changes are needed — every field is
  buildable with the existing declarative heading-mapped parser.
- REQ-003: Parse/validate `gol` documents from markdown, mirroring
  `parse_req`/`parse_prb`'s two-error-channel convention
  (`AssertionError` for structural problems, `pydantic.ValidationError`
  for field-level problems).
- REQ-004: MCP tools mirroring REQ/PRB's lifecycle surface, **plus**
  `list_gol` as a paged tool from day one (per ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 — new domains must not add a
  `specmgr://gol/list` resource and convert it later): `parse_gol`,
  `create_gol`, `update_gol`, `set_status_gol`, `delete_gol` (stub),
  `validate_gol`, `get_gol`, `get_gol_example`, `get_gol_template`,
  `list_gol`.
- REQ-005: MCP resources: `specmgr://gol/schema`, `/example`, `/template`
  (no `/list` — REQ-004 covers listing as a tool; no `/{id}` — id-based
  reads are `get_gol`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
- REQ-006: MCP prompts `create_gol`/`update_gol` — narrated,
  `TodoWrite` + `question`-tool-driven interview flows reusing the
  dedup-check-first pattern from `req/prompts/create_req.py` and the
  `TodoWrite`/`question`-tool narration pattern from
  `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use
  their own packaged instructions data file (`gol_create_instructions.md`/
  `gol_update_instructions.md` under `gol/data/`), not an inline string.
- REQ-007: Packaged example/template/schema data (`gol/data/`) via the
  existing generic `general/tools/_packaged_data.py`, with the matching
  `pyproject.toml` package-data entry, pre-commit hook, and CI step.
- REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema` (new
  `gol` entry in the doc-type registry, `commands/schema.py`),
  `specmgr mcp-docs`, all kept drift-free via pre-commit/CI; `AGENTS.md`
  updated to eight domain/cross-cutting packages.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — schema documented (`docs/gol_schema.json`,
  `specmgr://gol/schema`); a reference `gol_reference.md` exercising every
  field (`statement`, `Source` plus all optional sections present,
  `Related Artifacts` with all four sub-lists) round-trips through the
  parser.
- [ ] ACC-002: Verifies REQ-002 — Pydantic models validate mandatory
  (`statement`, `Source`) vs. optional (`Description`, `Priority`, `Tags`,
  `Related Artifacts` and each of its four sub-lists, `More Information`,
  `Notes`) fields correctly; `GolFrontmatter.status` rejects any value
  outside the seven-value set.
- [ ] ACC-003: Verifies REQ-003 — parser produces a valid object tree for a
  well-formed document; missing the `statement` lead paragraph or the
  `Source` section raises `AssertionError`; an invalid field value (e.g. a
  `Priority` outside 0–99, an out-of-set `status`) raises
  `pydantic.ValidationError`.
- [ ] ACC-004: Verifies REQ-004 — every listed tool is implemented,
  registered, and callable; `list_gol` returns a `PagedResult[GolSummary]`
  with default page size 25 / cap 100, mirroring the other five domains'
  `list_<d>` tools exactly (no resource-first-then-converted history for
  this domain).
- [ ] ACC-005: Verifies REQ-005 — every listed resource is implemented and
  registered (no `/{id}`, no `/list`, as designed).
- [ ] ACC-006: Verifies REQ-006 — `create_gol`/`update_gol` prompts narrate:
  (a) a duplicate/similar-document check via `list_gol` first, (b) building
  a `TodoWrite` list covering `statement` + `Source` + each optional
  section, (c) using the `question` tool to elicit each field (explicitly
  allowing skip for optional ones), (d) calling `create_gol(content)`/
  `update_gol(id, content)` (whole-body) at the end — verified live by
  reading both packaged instruction files in full and manually walking the
  narrated flows end to end against a real document, not just asserting
  their static text.
- [ ] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a
  real, non-editable install (`uv build --wheel` + scratch-venv install),
  mirroring feat-16's ACC-007 verification.
- [ ] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/
  `specmgr mcp-docs` all report no drift after implementation; `AGENTS.md`
  reflects eight domain/cross-cutting packages.

### Scope

**Included in this feature:**

- The `gol` markdown schema, Pydantic models, parser, and summary under
  `gol/models/v1/`.
- Full MCP surface (tools/resources/prompts/packaged data), including
  `list_gol` as a tool (not a resource) from the start.
- The interactive `create_gol`/`update_gol` prompt behavior (`TodoWrite` +
  `question`-tool-driven interview).
- Tests mirroring `tests/req/`/`tests/prb/`'s layout and coverage depth.
- Cross-cutting registration (`server.py`, `pyproject.toml`,
  `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`).

**Explicitly out of scope:**

- A `## Characteristics` section (ISO 25010:2023 quality attributes).
  Quality characteristics are a requirement-level attribute — a business
  goal states *what* to achieve, not *which quality dimension* it loads
  (user decision, planning session 2026-08-25).
- A `## Level` section (RFC 2119 obligation strength). A goal is
  implicitly always a MUST — obligation grading applies to requirements
  below it, not to the goal itself (user decision, planning session
  2026-08-25).
- Structured cross-referencing/validation of the `Related Artifacts`
  sub-lists (typed id validation, `GOL-NNNN:`-style format checks,
  existence checks against the other domains' base directories) — v1 keeps
  all four sub-lists as opaque free text, matching `req`'s own precedent.
  Revisit only if a concrete need emerges.
- ADR-style granular `update_section`/option-style per-field mutation
  tools — `update_gol` is a single whole-body replace tool, like
  `update_req`/`update_prb`. Individual sections stay addressable by their
  fixed heading text within the markdown body itself, not via a dedicated
  tool per section.
- Real implementation of `delete_gol` — a stub raising
  `NotImplementedError`, matching the other five domains' `delete_*` stubs
  (a shared, cross-domain decision deferred to future work).
- Any changes to `req`'s schema, data, or tools — REQ's existing
  `### Goals` cross-reference sub-list already anticipates this artifact
  type and needs no modification.
- A `specmgr gol-toc`-equivalent generation command or dedicated CI/
  pre-commit drift check beyond what `specmgr docs`/`specmgr mcp-docs`/
  `specmgr schema` already provide generically.

### Dependencies

- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
  `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614
  (tool-only id-based reads, no `specmgr://gol/{id}` resource), ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 (`list_<domain>` as a paged tool,
  not a resource — `list_gol` must follow this from day one), the existing
  `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py` and
  `general/models/{DocSummary,PagedResult}` infrastructure, and the
  existing `models/md` engine (`MarkdownSection1`, `MarkdownSection2`,
  `MarkdownSection2WithComment`, `MarkdownSection3`, `MarkdownParagraph`,
  `MarkdownListItem`, `@alias`) — reused as-is, no engine changes
  anticipated.
- Blocks: None identified yet.
- Related, but explicitly out of scope here: issue #15 "Add artifact type
  Risk" (open) — a sibling domain that will follow the same pattern
  independently.

### Design Notes

**Schema:**

```
GolFrontmatter(MarkdownFrontmatter): type: Literal["gol"];
  status in {draft, proposed, accepted, superseded, deprecated, rejected, implemented}
  (req's exact 7-value set -- goals are business-level requirements, so
   requirement-lifecycle semantics apply)

Goal(MarkdownSection1)                          # H1, free-form title (@alias ".+" REGEX)
├── statement: MarkdownParagraph                # mandatory lead paragraph (the goal statement itself)
├── description: Description | None             # optional H2 "Description", opaque free text leaf
├── priority: Priority | None                   # optional H2 "Priority", 0-99 single-line value + optional comment
├── tags: Tags | None                           # optional H2 "Tags", bullet list
├── source: Source                              # mandatory H2 "Source", single-line value
├── related_artifacts: RelatedArtifacts | None  # optional H2 "Related Artifacts"
│   ├── requirements: Requirements | None       # optional H3, bullet list of cross-refs (e.g. "REQ-9687: ...")
│   ├── decisions: Decisions | None             # optional H3, bullet list of cross-refs (e.g. "DEC-2703: ...")
│   ├── goals: Goals | None                     # optional H3, bullet list of cross-refs (e.g. "GOL-0007: ...")
│   └── acceptance_criteria: AcceptanceCriteria | None  # optional H3, bullet list (e.g. "ACC-1234: ...")
├── more_information: MoreInformation | None    # optional H2 "More Information", opaque free text leaf
└── notes: Notes | None                         # optional H2 "Notes", opaque free text leaf
```

**No `Characteristics`, no `Level`** (see Scope: Explicitly out of scope) —
both are deliberate, domain-driven omissions, not oversights: ISO 25010
quality characteristics grade *requirements*, and RFC 2119 obligation
strength is implicit (a goal is always a MUST). Consequently the only
mandatory body fields are `statement` and `Source`; a freshly created
`gol` document may have zero optional sections yet (all deferred to a later
`update_gol` call) but must always carry the goal statement and its source.

**`Priority` keeps `req`'s `MarkdownSection2WithComment` +
`field_validator`-on-`value.text` pattern** (0–99, no leading zeros other
than "0" itself), re-declared in `gol/models/v1/body.py` — domain packages
never import model classes from each other (verified: no cross-domain
imports exist in `src/`), so `req`'s `Priority`/`Level` classes are
*pattern* precedents, not shared code. `Description`/`Source`/
`MoreInformation`/`Notes` are bare opaque leaf subclasses with no further
declared fields — the same pattern verified for REQ's `MoreInformation`/
`Notes` and PRB's leaves.

**The four `RelatedArtifacts` sub-lists are 1:1 re-declarations of REQ's
own four classes**: `MarkdownSection3` with
`items: list[MarkdownListItem] = Field(min_length=1)`; heading text
("Requirements"/"Decisions"/"Goals"/"Acceptance Criteria") derives
implicitly via the `AliasType.SPACE_SEPARATED` convention (multi-word
`AcceptanceCriteria` → "Acceptance Criteria"), so no explicit `@alias` is
needed — exactly as in `req/models/v1/body.py`. All four sub-lists are
optional, as is `Related Artifacts` as a whole, and no consistency check
is enforced between them (REQ precedent). Cross-reference id formats
(`GOL-0007:`, `REQ-9687:`, `DEC-2703:`, `ACC-1234:`) are conventional text
only — not validated in v1. The `### Goals` sub-list includes goals for
cross-referencing peer/superseding goals (self-referencing is allowed; the
parser does not special-case a document's own id).

**Update mechanism: whole-body `update_gol(id, content)`**, not an
ADR-style `update_section`. The generic `adr/tools/update_section.py`
mechanism (ADR 71fd95d7-07f2-466f-81aa-d29b7e3ef34c) is currently
ADR-specific code, not a shared cross-domain component — the same decision
as feat-16's for `prb`. Individual sections stay addressable by grepping/
editing their fixed heading text within the whole-body markdown.

**`list_gol` is a paged tool from day one** (`@mcp.tool(name="list_gol")`
returning `PagedResult[GolSummary]`, via `general/tools/_paging.py`'s
`paginate`/`normalize_paging`, default page size 25 / cap 100), not a
`specmgr://gol/list` resource — GOL is a new domain built *after* ADR
ec9f5262 was accepted, so it must not repeat the resource-then-convert
history of REQ/UC/TSK/QA/PRB (feat-13). `GolSummary` subclasses
`general/models/summary.py::DocSummary` (`id`/`title`/`status`/`ref`),
like `ReqSummary`/`PrbSummary`; `title` is the body's H1 text.

**Prompts are narrated instructions only** (return a string, auto-wrapped
as a `UserMessage` by the MCP SDK) — `create_gol`/`update_gol` never call
`TodoWrite`/`question`/`get_gol`/`create_gol`/`update_gol` themselves; they
only narrate that the calling LLM should. This is the same contract every
existing prompt in this codebase already follows
(`tsk/prompts/implement_task.py`, `req/prompts/create_req.py`).

- `create_gol(topic: str) -> str`: instructs the LLM to (1) call `list_gol`
  first to check for an existing, similar goal (mirrors `create_req`'s
  dedup-check pattern) and ask the user via `question` if a near-duplicate
  is found; (2) build a `TodoWrite` list with one entry per `statement` +
  `Source` + each optional section (`Description`/`Priority`/`Tags`/
  `Related Artifacts`/`More Information`/`Notes`); (3) use the `question`
  tool to elicit the goal statement (mandatory) and the source (mandatory)
  plus each optional field in turn, explicitly allowing the user to skip
  any optional one; (4) reference the packaged
  `specmgr://gol/template`/`specmgr://gol/example`/`specmgr://gol/schema`
  for the fixed structure; (5) assemble the full body markdown per the
  schema above and call `create_gol(content)`.
- `update_gol(id: str) -> str`: instructs the LLM to (1) call
  `get_gol(id)` first (never assume prior state); (2) show the user which
  sections are already present and which are empty, and ask via
  `question` which ones (if any) they want to add or revise; (3) for each
  selected section, elicit the new/revised text via `question`; (4) call
  `update_gol(id, content)` (whole-body replace, carrying forward every
  unchanged section); (5) mention `set_status_gol` as a separate, optional
  follow-up (e.g. `implemented` once the goal has genuinely been reached,
  `rejected`/`superseded` if abandoned or replaced).

Both prompts' instructional text lives in packaged data files
(`gol/data/gol_create_instructions.md`/`gol_update_instructions.md`, read
via `general.tools._packaged_data.read_packaged_text`, `string.Template`
substitution), matching `req_create_instructions.md`/
`prb_create_instructions.md`'s precedent — not an inline Python string.

**Frontmatter status** is REQ's exact 7-value closed set
(`draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/
`implemented`), re-declared as `GolFrontmatter`'s own `_ALLOWED_STATUSES`
frozenset (each domain declares its own set — `ReqFrontmatter`,
`TskFrontmatter`, `PrbFrontmatter` all do), with goal-specific semantics:
`draft` = still being written; `proposed` = under consideration;
`accepted` = agreed to be pursued; `implemented` = the goal has genuinely
been reached; `superseded` = replaced by another goal; `deprecated` = no
longer pursued, kept for reference; `rejected` = considered and not
pursued.

**Example/template documents:** `gol_example.md` is drafted as
`GOL-0007: Competitive Engines in Consumer Vehicles` — the exact goal
`req_example.md`'s `### Goals` sub-list already cross-references — so the
two packaged examples read coherently side by side; it reuses
`gol_reference.md`'s content verbatim (feat-16's own precedent:
`prb_example.md` reuses `prb_reference.md`). `gol_template.md` mirrors
`req_template.md` minus the `Characteristics` and `Level` sections, with
goal-oriented placeholder prose.

### Related ADRs

- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for
  markdown document types
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based reads as a tool
  (`get_gol`), not a resource
- ec9f5262-9912-49d0-903f-fcfb54f28c13: Expose `<domain>_list` as a paged
  MCP tool (`list_gol`), not a resource — must be followed from the start
  for this new domain, not retrofitted later
- 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` — reviewed
  and explicitly *not* reused for `gol` (see Design Notes)

No new ADR is anticipated for this feature — every schema/tooling decision
either follows an existing ADR's precedent directly or is scoped enough to
log only in this file's own Decisions Made.

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself. Each phase ends with a mandatory phase-end task (tests, full
quality gate, README Progress update), mirroring feat-16's per-phase
commit discipline, since implementation is likely to span multiple
sessions.

#### Phase 1: Specification

- [x] Task 1.1: Write a full reference `gol_reference.md`
  (`.specmgr/feat/feat-18-goal/gol_reference.md`) exercising every field
  (`statement`, `Source`, plus all optional sections present:
  `Description`/`Priority`/`Tags`/`Related Artifacts` with all four
  sub-lists/`More Information`/`Notes`) — depends on: none — status:
  completed
- [x] Task 1.2: Define `gol` frontmatter (`gol/models/v1/frontmatter.py` —
  `GolFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["gol"]`,
  7-value status set identical to `ReqFrontmatter`'s) — depends on: none —
  status: completed
- [x] Task 1.3: Define `gol` body structure (`gol/models/v1/body.py`) —
  `Goal(MarkdownSection1)` with `@alias(value=".+", type=AliasType.REGEX)`,
  mandatory `statement: MarkdownParagraph` + `source: Source`, optional
  `description`/`priority`/`tags`/`related_artifacts`/`more_information`/
  `notes`; `Priority` re-declares REQ's `MarkdownSection2WithComment` +
  `field_validator` pattern (0–99); `RelatedArtifacts(MarkdownSection2)`
  with four optional `MarkdownSection3` sub-lists (see Design Notes) —
  depends on: Task 1.2 — status: completed
- [x] Task 1.4: `tests/gol/models/v1/test_frontmatter.py`, `test_body.py` —
  structural + validation tests mirroring `tests/req/models/v1/`/
  `tests/prb/models/v1/`, explicit coverage of mandatory-vs-optional field
   combinations (each optional section individually absent/present; each of
   the four `Related Artifacts` sub-lists individually absent/present) —
  depends on: Task 1.3 — status: completed
- [x] Task 1.5: Phase-end quality gate — run the full pre-commit/quality
  gate (ruff format/check, vulture, full `unittest` suite); confirm
  `gol_reference.md` is `specmgr mdformat`-clean; add any new
  vulture-invisible Pydantic field names to `whitelist.py` if needed;
  update this README's Progress section — depends on: Task 1.1, Task 1.4 —
  status: completed

#### Phase 2: Pydantic Models, Parser & Schema

- [x] Task 2.1: `gol/models/v1/document.py` (`GolDocument(frontmatter, body)`, mirroring `ReqDocument`) — depends on: Task 1.3 — status:
  completed
- [x] Task 2.2: Implement `parse_gol(text: str) -> GolDocument` (model-layer
  function, mirrors `parse_req`) — depends on: Task 2.1 — status:
  completed
- [x] Task 2.3: `gol/models/v1/summary.py` (`GolSummary(DocSummary)`,
  subclassing `general/models/summary.py::DocSummary`, for `list_gol`) —
  depends on: Task 2.1 — status: completed
- [x] Task 2.4: Field-level `Field(description=...)` on every scalar/
  optional field (schema-quality parity with REQ/PRB) — depends on:
  Task 2.1 — status: completed
- [x] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`
  (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`),
  and register `"gol"` in the `specmgr schema` doc-type generator registry
  (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —
  status: completed
- [x] Task 2.6: `tests/gol/models/v1/test_parser.py` — mirrors
  `TestParseReq`'s shape (minimal doc, full reference-doc round-trip,
  defaults-when-absent, invalid status, missing-mandatory-field
  `AssertionError` cases (`statement`, `Source`), invalid-field
  `ValidationError` (e.g. `Priority` out of 0–99 range, invalid `type`
  field)) — depends on: Task 2.2, Task 2.5 — status: completed
- [x] Task 2.7: Phase-end quality gate — full pre-commit/quality gate
  including Task 2.6's new tests; update this README's Progress section —
  depends on: Task 2.5, Task 2.6 — status: completed

#### Phase 3: MCP Surface

- [x] Task 3.1: `gol/tools/_paths.py`/`_io.py`/`_write.py`/`_lock.py`, thin
  wrappers over `general/tools/_doc_paths.py` (mirrors `req/tools/`/
  `prb/tools/` exactly) — depends on: Task 2.2 — status: completed
- [x] Task 3.2: `parse_gol(path: str) -> GolDocument` tool wrapper
  (`gol/tools/parse_gol.py`) — depends on: Task 3.1 — status: completed
- [x] Task 3.3: `create_gol(content: str) -> GolDocument` tool (body-only
  content; MCP builds frontmatter: `id`, `type="gol"`, `status="draft"`,
  `created=updated=now`, `version`) — depends on: Task 3.1 — status:
  completed
- [x] Task 3.4: `update_gol(id, content) -> GolDocument` tool (whole-body
  replace, preserves `id`/`type`/`status`/`created`/`version`, bumps
  `updated`) — depends on: Task 3.1 — status: completed
- [x] Task 3.5: `set_status_gol(id, status) -> GolDocument` tool (only path
  that changes `status`; reconstructs `GolFrontmatter` via its own
  constructor so the 7-value validator runs, mirroring `set_status_req`) —
  depends on: Task 3.1 — status: completed
- [x] Task 3.6: `delete_gol(id) -> NoReturn` stub tool — depends on: Task
  3.1 — status: completed
- [x] Task 3.7: `validate_gol(content, full=False) -> bool` tool — depends
  on: none — status: completed
- [x] Task 3.8: `get_gol(id) -> GolDocument` tool (id-based single-document
  read; tool, not resource) — depends on: Task 3.1 — status: completed
- [x] Task 3.9: `list_gol(max_results=None, offset=None) -> PagedResult[GolSummary]`
  tool, via `general/tools/_paging.py`'s `paginate`/`normalize_paging`
  (default page size 25, cap 100), preserving the standard skip-malformed-
  file scan behavior — depends on: Task 2.3, Task 3.1 — status: completed
- [x] Task 3.10: `get_gol_example`/`get_gol_template` tools + packaged data
  (`gol/data/gol_example.md` — drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` per Design Notes, `gol/data/gol_template.md` —
  `req_template.md` mirrored minus `Characteristics`/`Level`) via
  `general/tools/_packaged_data.py` — depends on: Task 1.1 — status:
  completed
- [x] Task 3.11: `gol/resources/{gol_schema,gol_example,gol_template}.py`
  — `specmgr://gol/schema` (packaged `gol/data/gol_schema.json`, mirroring
  `specmgr://req/schema`), `specmgr://gol/example`, `specmgr://gol/template`
  (no `/list`, no `/{id}`) — depends on: Task 2.5, Task 3.10 — status:
  completed
- [x] Task 3.12: `pyproject.toml` package-data entry for
  `biz.dfch.specmgr.gol` (`data/*.md`, `data/*.json`); `.pre-commit-config.yaml`
  — widen the shared schema-hook glob to include `gol/models/v1`, add a
  `specmgr-schema-gol-package` hook — depends on: Task 2.5 — status: completed
- [x] Task 3.13: `.github/workflows/ci.yml` — add the `docs/gol_schema.json`
  check + packaged-copy check steps — depends on: Task 2.5 — status:
  completed
- [x] Task 3.14: `gol/data/gol_create_instructions.md` +
  `gol/prompts/create_gol.py` (`@mcp.prompt()`, `string.Template`
  substitution, narrates the full interview flow — see Design Notes) —
  depends on: Tasks 3.3, 3.9 — status: completed
- [x] Task 3.15: `gol/data/gol_update_instructions.md` +
  `gol/prompts/update_gol.py` — depends on: Tasks 3.4, 3.5, 3.8 — status:
  completed
- [x] Task 3.16: `gol/__init__.py` (docstring + `from . import prompts, resources, tools`), add `gol` to `server.py`'s bottom-of-file domain
  import line (alphabetical: `adr, general, gol, prb, qa, req, tsk, uc`)
  and update its module docstring (Tools/Resources/Prompts sections) —
  depends on: Tasks 3.2-3.15 — status: completed
- [x] Task 3.17: `tests/gol/tools/...`, `tests/gol/resources/...`,
  `tests/gol/prompts/...` mirroring `tests/req/`/`tests/prb/`'s layout,
  including live end-to-end coverage of `create_gol`/`update_gol`'s
  narrated `TodoWrite`/`question`-tool flow (ACC-006) and `list_gol`'s
  paging behavior (default page size, `max_results` clamping, `offset`
  paging, `truncated` boundary) — depends on: Tasks 3.1-3.16 — status:
  completed
- [x] Task 3.18: Phase-end quality gate — full pre-commit/quality gate
  including Task 3.17's new tests; update this README's Progress section —
  depends on: Task 3.17 — status: completed

#### Phase 4: Cross-cutting registration

- [x] Task 4.1: `AGENTS.md` — update heading to "eight domain/cross-cutting
  packages implemented (ADR, REQ, UC, TSK, QA, PRB, GOL, general)"; add a
  `gol/` bullet (chronological order, after `prb/`); update the "Still
  genuinely missing" list (`validate_gol` not enforced via pre-commit/CI,
  `delete_gol` stub) and the closing domain-enumeration paragraphs —
  depends on: Phase 3 complete — status: completed
- [x] Task 4.2: `specmgr docs` / `specmgr mcp-docs` / `specmgr schema`
  regeneration — confirm `gol` appears correctly and all three commands
  report zero drift — depends on: Task 4.1 — status: completed
- [x] Task 4.3: Phase-end quality gate — full pre-commit/quality gate;
  update this README's Progress section — depends on: Task 4.2 — status:
  completed

#### Phase 5: Final cross-cutting verification

- [ ] Task 5.1: Final verification pass — walk every ACC-001..008 and
  confirm each is satisfied with concrete evidence (including a live
  `create_gol`→`update_gol`→`set_status_gol` run, not just unit tests);
  run the full quality gate (ruff format/check, pylint advisory, vulture,
  unittest, `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` drift
  checks) end to end; set feature status to `done` — depends on: Phase
  1-4 complete — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in
place; rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-26**: Phase 4 (Cross-cutting registration) complete —
`AGENTS.md` updated to eight domain/cross-cutting packages (heading,
opening count, new `gol/` bullet after `prb/`, "Still genuinely missing"
list, closing domain enumeration, server-import enumeration); all three
doc-generation commands re-run and confirmed zero drift (`gol` appears
correctly in `docs/MCP.md`, `docs/GENERATED.md`, `docs/api/`, and
`docs/gol_schema.json`); full quality gate green (1609 tests, coverage
98%). GitHub issue #18 ("Add artifact type Goal (GOL)") is filed and
open. Phase 5 (Final cross-cutting verification — ACC-001..008 walk,
live lifecycle run, status → `done`) is next.

### Blockers

None.

### Recent Updates

#### Update 2026-08-26 (Phase 4)

- Completed: Phase 4 (Cross-cutting registration), Tasks 4.1–4.3.
  - Task 4.1: `AGENTS.md` updated, scoped exactly to the plan — heading
    "seven → eight domain/cross-cutting packages implemented (ADR, REQ,
    UC, TSK, QA, PRB, GOL, general)"; opening sentence "Six → Seven
    document-type domains plus one cross-cutting package"; new
    `**gol/**` (Goal) bullet in chronological position (after `prb/`,
    before `general/`) mirroring the `prb/` bullet's shape and density
    (all ten tools with the `delete_gol` stub noted, the three resources
    with the no-`specmgr://gol/{id}` (ADR ddfb1109) / no-
    `specmgr://gol/list` (`list_gol` paged tool from day one, ADR
    ec9f5262) references, the narrated `TodoWrite` + `question`-tool
    prompts with the `create_gol` dedup-check-first note, schema at
    `gol/models/v1/` inside the domain package, the REQ-mirrored-minus-
    `Characteristics`/`Level` body note, whole-body `update_gol`); "Still
    genuinely missing" list gains `validate_gol` (first bullet's
    parenthetical) and `delete_gol` (stubs bullet); the closing
    "Don't assume any other domain package exists beyond …" enumeration
    gains `gol` (alphabetical, between `general` and `prb`). Two further
    domain-set enumerations updated per the task's item-5 rule (see
    Decisions Made): the "Still genuinely missing" bullet that lists
    which domains register `tools`/`resources`/`prompts`
    (`req`/`tsk`/`qa`/`prb` → `req`/`tsk`/`qa`/`prb`/`gol`), and the
    "MCP server (`server.py`)" section's list of the domain packages
    `server.py`'s bottom import line pulls in (now includes `gol`,
    matching the actual line since Phase 3). Left untouched, deliberately:
    the "Models location" paragraph's historical "REQ, UC, and TSK were
    built *after* that refactor" enumeration (already stale pre-GOL — it
    omits QA/PRB; fixing it is a pre-existing-staleness edit outside this
    task, reported to the orchestrator) and the "Existing feature
    folders" paragraph (explicitly out of scope per the task).
  - Task 4.2: zero-drift confirmation — `specmgr docs` (exit 0;
    `git diff --exit-code -- docs/` exit 0 — no changes), `specmgr
    mcp-docs` (exit 0; `git diff --exit-code -- docs/MCP.md` exit 0),
    `specmgr schema` (exit 0; all six types "unchanged"). `gol` appears
    correctly: `docs/MCP.md` header line `20 resource(s), 1 resource
    template(s), 74 tool(s), 17 prompt(s)` with exactly 10 `### Tool:
    *gol` entries, 3 `### Resource: gol_*` entries, 2 `### Prompt: *gol`
    entries; `docs/GENERATED.md` carries the full 30-line `gol/` module
    section (package + `models/v1` 7 + prompts 3 + resources 4 + tools
    15); `docs/api/` holds 23 `biz.dfch.specmgr.gol*` pages (the package
    page `biz.dfch.specmgr.gol.md` + the 22 sub-module pages: 15 tools
    incl. `tools.md`, 4 resources incl. `resources.md`, 3 prompts incl.
    `prompts.md`); `docs/gol_schema.json` present with
    `$comment: "v1"`, 2020-12 dialect, top-level
    `required: ["frontmatter", "body"]`.
  - Task 4.3: quality gate green — see below.
- Next: Phase 5 (Final cross-cutting verification) — walk every
  ACC-001..008 with concrete evidence (incl. the live
  `create_gol`→`update_gol`→`set_status_gol` run and ACC-007's
  scratch-venv install), full quality gate end to end, set feature
  status to `done`.
- Notes:
  - Quality gate: `ruff format --check` (1011 files already formatted),
    `ruff check` (all passed), `pylint` (advisory; exit 30, 8.92/10 —
    identical to the Phase-3 baseline by construction: this phase
    changes no `.py` file, and `git status` confirms only `AGENTS.md` +
    this README are modified; 112 of the pre-existing findings reference
    committed `gol` files, e.g. `tests/gol/models/v1/test_body.py`,
    none introduced here), `vulture` (exit 0, no output), full unittest
    suite (1609 tests, all OK, 55s), `specmgr coverage-badge` (98%,
    `docs/coverage.svg` byte-unchanged), `specmgr adr-toc` (no change to
    `docs/adr/README.md`), `specmgr docs`/`mcp-docs`/`schema` (zero
    drift, per Task 4.2 above). Final `git status`: only `AGENTS.md` and
    `.specmgr/feat/feat-18-goal/README.md` modified.
  - ACC-008 (this phase's acceptance criterion) is satisfied by the
    Task 4.2 zero-drift evidence plus the `AGENTS.md` update: `specmgr
    docs`/`schema`/`mcp-docs` all report no drift after implementation,
    and `AGENTS.md` now reflects eight domain/cross-cutting packages.
    The final ACC walk over all of ACC-001..008 is Phase 5's Task 5.1.

#### Update 2026-08-26 (Phase 3)

- Completed: Phase 3 (MCP Surface), Tasks 3.1–3.18.
  - Task 3.1: `gol/tools/_paths.py` (`gol_base_dir`/
    `ensure_gol_base_dir`/`iter_gol_paths`/`find_gol_path`/
    `GolNotFoundError`/`GOL_TYPE_NAME`), `_io.py` (`read_gol`/
    `load_by_id`), `_write.py` (`write_gol_file`), `_lock.py`
    (`gol_lock`) — thin wrappers over `general/tools/_doc_paths.py`,
    mirroring `prb/tools/` file-for-file (REQ's same shape).
  - Tasks 3.2–3.9: all eight lifecycle tools — `parse_gol` (path-based
    disk read), `create_gol` (body-only content; tool builds the full
    `GolFrontmatter`: fresh `uuid4` id, `type="gol"`, `status="draft"`,
    `created=updated=now` with `timespec="microseconds"`,
    `version=CURRENT_SCHEMA_VERSION`; filename
    `gol-<uuid>-<slug>.md`), `update_gol` (whole-body replace, preserves
    `id`/`type`/`status`/`created`/`version`, bumps `updated`),
    `set_status_gol` (sole status path; reconstructs `GolFrontmatter` via
    its own constructor so the 7-value validator runs), `delete_gol`
    (stub, `structured_output=False`), `validate_gol` (disk-free dry run,
    `full` flag with symmetric `ValueError`s), `get_gol` (tool-only id
    read, ADR ddfb1109), `list_gol` (`PagedResult[GolSummary]` via
    `paginate`/`normalize_paging`, skip-malformed-file scan, `title` =
    body H1, ADR ec9f5262 paged-from-day-one wording).
  - Task 3.10: `get_gol_example`/`get_gol_template` tools + packaged data —
    `gol_example.md` is a **byte-identical copy of `gol_reference.md`**
    (`diff` empty, verified); `gol_template.md` = `req_template.md` minus
    `## Characteristics`/`## Level` with goal-oriented placeholders
    (dead-UUID `id: deaddead-goal-goal-goal-deaddeadgoal`, plain
    `2026-08-26` dates) — verified parseable by `parse_gol` (same
    guarantee `tests/prb/tools/test_integration.py` gives PRB's
    template); `gol_schema.json` generated via `specmgr schema --type gol
    --output-dir src/biz/dfch/specmgr/gol/data` (byte-identical to
    `docs/gol_schema.json`, generator exits 0).
  - Task 3.11: `gol/resources/` — `specmgr://gol/schema` (reads the
    packaged JSON via `read_packaged_text`, mirroring `req_schema.py`),
    `specmgr://gol/example`, `specmgr://gol/template`; no `/list`, no
    `/{id}`.
  - Tasks 3.12/3.13: `pyproject.toml` package-data entry for
    `biz.dfch.specmgr.gol` (`data/*.md`, `data/*.json`, alphabetical
    position between `adr` and `prb`); `.pre-commit-config.yaml` — all six
    existing schema-hook `files:` globs widened to include
    `gol/models/v1`, plus a new `specmgr-schema-gol-package` hook
    (mirrors the prb one); `ci.yml` — two new 3.13-pinned steps
    (`docs/gol_schema.json` all-types check + packaged-copy check) after
    the prb pair, before the coverage-badge step.
  - Tasks 3.14/3.15: `gol/data/gol_create_instructions.md` +
    `gol/prompts/create_gol.py` (`topic: str` only; narrates
    dedup-check-first via `list_gol` → `TodoWrite` list over `statement` +
    `Source` + each optional section → `question`-tool interview with
    explicit skip-allowed for optionals → `specmgr://gol/template|example|
    schema` references → `create_gol(content)` → `update_gol` for later
    revisions; also narrates the deliberate `Characteristics`/`Level`
    omissions) and `gol/data/gol_update_instructions.md` +
    `gol/prompts/update_gol.py` (`id: str` only — see Decisions Made;
    narrates `get_gol(id)` first → present-vs-empty section overview +
    `question` → per-section elicitation → `update_gol(id, content)`
    whole-body replace → `set_status_gol` as separate optional follow-up
    with `implemented`/`rejected`/`superseded` semantics). Both load
    packaged data via `read_packaged_text` + `string.Template` and let
    `FileNotFoundError` propagate uncaught.
  - Task 3.16: `gol/__init__.py` (docstring + `from . import prompts,
    resources, tools`); `server.py` bottom import line is now
    `from . import adr, general, gol, prb, qa, req, tsk, uc` and its
    module docstring lists the 10 gol tools, 3 gol resources, 2 gol
    prompts, the no-`/{id}`-no-`/list` paragraph, and the updated
    domain enumeration. Live registration verified: `list_tools` 64→74,
    `list_resources` 17→20, `list_prompts` 15→17.
  - Task 3.17: `tests/gol/tools/` (16 files: per-tool + `_paths`/`_io`/
    `_write`/`_lock` + `test_integration.py`), `tests/gol/resources/`
    (3 files), `tests/gol/prompts/` (2 files) — 104 new tests mirroring
    `tests/req/`/`tests/prb/` (temp-`SPECMGR_DOCS_DIR` isolation,
    `packaged_data_path` patching, `FileNotFoundError` propagation).
    `test_list_gol.py` covers the plan-mandated paging contract: default
    page size 25 with 26 docs (`total=26`/`max_results=25`/
    `truncated=True`), `max_results` clamped to the 100 cap, `offset`
    paging with no page overlap, the `truncated` boundary (offset
    exactly at/past the end → `False`), negative-offset flooring, and
    skip-malformed-file (`total` reflects parseable count only).
    `test_integration.py` walks the live sequence `list_gol` (empty) →
    `create_gol` → `get_gol` → `list_gol` (1) → `update_gol` →
    `set_status_gol` → `get_gol` (status reflected) → `list_gol` (status
    reflected) → `delete_gol` (stub raises, doc untouched) — the
    ACC-004/ACC-006 "verified live" evidence for this phase.
  - Task 3.18: quality gate green — see below.
- Next: Phase 4 (Cross-cutting registration) — `AGENTS.md` (heading to
  "eight domain/cross-cutting packages", `gol/` bullet after `prb/`,
  "Still genuinely missing" list, closing enumeration), then the
  `specmgr docs`/`mcp-docs`/`schema` zero-drift re-confirmation.
- Notes:
  - Quality gate: `ruff format --check` (all files formatted), `ruff
    check` (all passed), `vulture` (exit 0, no output — **no**
    `whitelist.py` change needed: every gol tool/resource/prompt function
    is import-referenced by its sub-package `__init__.py`, the same
    visibility REQ/PRB's own MCP entry points have; only
    `version_info` carries a whitelist entry in that section), full
    unittest suite (1609 tests, up from 1505, all OK, 54s), `specmgr
    coverage-badge` (98%, `docs/coverage.svg` byte-unchanged — all 22 new
    `gol` src modules at 100% coverage), `specmgr docs` (19 new
    `docs/api/biz.dfch.specmgr.gol*.md` pages + `docs/api/README.md` index
    + `docs/GENERATED.md` (test files 208→228, 22 new gol module lines) +
    `docs/api/biz.dfch.specmgr.server.md` (docstring) +
    `docs/api/biz.dfch.specmgr.general.models.paged_result.md` (new
    `PagedResult[GolSummary]` alias section) — second run a fixed point),
    `specmgr mcp-docs` (`docs/MCP.md`: +3 resources/+10 tools/+2 prompts
    in alphabetical positions, header count line 17/64/15 → 20/74/17,
    second run a fixed point), `specmgr schema` (exit 0, all six docs
    schemas unchanged) + `specmgr schema --type gol --output-dir
    src/biz/dfch/specmgr/gol/data` (exit 0, packaged copy unchanged),
    `specmgr adr-toc` (no change to `docs/adr/README.md`), smoke: `import
    biz.dfch.specmgr.server` OK and `uv build --wheel` wheel contains all
    five `gol/data/*` files plus every gol module (scratch-venv install
    is Phase 5's ACC-007 evidence), pre-commit: `specmgr-schema-gol-package
    --all-files` and the widened `specmgr-schema --all-files` both
    **Passed**.
  - `docs/api/` gained 19 gol pages, not ~20: `gol/models/` has no
    `__init__.py` (mirrors `req/models/`'s exact file shape per the
    Phase-1 decision), so `pkgutil.walk_packages` — which drives the
    per-module api pages — does not descend into it, exactly as it doesn't
    for `req/models/` (zero committed `req.models` api pages).
    `docs/GENERATED.md`'s static source-tree scan does list the
    `gol/models/v1/*` first lines regardless.
  - ACC-004/ACC-005/ACC-006 (this phase's acceptance criteria): covered by
    the per-tool/resource/prompt tests + the live integration test + the
    string-content/ordering prompt assertions. ACC-006's "manually walking
    the narrated flows end to end against a real document" transcript
    evidence is Phase 5's territory (Task 5.1); the concrete in-repo
    evidence landed here is `test_integration.py` plus the prompt tests.

#### Update 2026-08-25 (Phase 2)

- Completed: Phase 2 (Pydantic Models, Parser & Schema), Tasks 2.1–2.7.
  - Task 2.1: `GolDocument` (`gol/models/v1/document.py`) — `BaseModel`
    wrapper pairing `GolFrontmatter` + `Goal`; holds no file/id/path
    information itself (`frontmatter.id` carries it, same convention as
    `ReqDocument`).
  - Task 2.2: `parse_gol(text) -> GolDocument` (`gol/models/v1/parser.py`)
    — free function mirroring `parse_req`/`parse_prb`: `python-frontmatter`
    split, `_stringify_metadata` helper (PyYAML's unquoted dates parse as
    `datetime.date` → coerced back to `str`), then `Goal.from_text` on the
    `format_text`-normalized body. Two error channels (`AssertionError`
    structural / `pydantic.ValidationError` field-level). New
    `gol/models/v1/_util.py` with `SCHEMA_COMMENT_VERSION = "v1"`.
    `gol/models/v1/__init__.py` extended to the full REQ-shaped export set
    (`SCHEMA_COMMENT_VERSION` first, `parse_gol` last, class names
    alphabetical in between).
  - Task 2.3: `GolSummary` (`gol/models/v1/summary.py`) — `DocSummary`
    subclass (`id`/`title`/`status`/`ref`, base untouched), docstring notes
    `list_gol` is a paged **tool** (no `specmgr://gol/list` resource, ADR
    ec9f5262), `title` = body H1.
  - Task 2.4: `Field(description=...)` parity audit — every field of
    `Goal`/`RelatedArtifacts`/`Priority`/`Tags`/`Source` and the four
    sub-lists already carries a description (Phase 1).
    `GolDocument.frontmatter`/`body`, `GolFrontmatter.type`, and `GolSummary`
    (inherited `DocSummary` fields) are bare — which *is* parity, since
    `ReqDocument`/`ReqFrontmatter`/`ReqSummary` are bare too. Zero new
    descriptions added.
  - Task 2.5: `generate_gol_schema()` in `commands/schema.py` (mirrors
    `generate_req_schema`: `$schema` from `GenerateJsonSchema.schema_dialect`,
    `$comment` = `"v1"`, `indent=2, sort_keys=True` + trailing newline) and
    `"gol"` registered **first** in `_GENERATORS` (alphabetical). First
    `specmgr schema` run exited 1 (the new-file drift signal; file written
    regardless); re-run exits 0, all six schemas byte-identical. Sanity:
    `GolDocument` top-level (`required: [frontmatter, body]`), `Goal`
    requires only `[statement, source]`, no `Characteristics`/`Level`
    sections, fields, or RFC 2119 values in the schema structure (see
    Notes). `docs/api/biz.dfch.specmgr.commands.schema.md` regenerated for
    the new generator (expected churn from the mandated `specmgr docs` run).
  - Task 2.6: `tests/gol/models/v1/test_parser.py` — `TestParseGol`, 10
    tests mirroring `TestParseReq`: minimal zero-optional-sections doc (the
    end-to-end proof of the optional `default=None` fields), full reference-
    doc parse with byte-exact `str(doc.body)` round-trip of the on-disk
    `gol_reference.md`, frontmatter defaults when the block is absent,
    invalid `status`/`type` `ValidationError`, `Priority` 100/-1/007
    `ValidationError` (99 accepted), missing-`statement` and
    missing-`## Source` `AssertionError`, and an out-of-order-sections
    `AssertionError` (`## Source` before `## Tags` → the engine's "text
    left over after processing all fields").
  - Task 2.7: quality gate green — `ruff format --check` (938 files),
    `ruff check`, `vulture` (exit 0, no output, no `whitelist.py` change —
    see Notes), full unittest suite (1505 tests, up from 1495), `specmgr
    coverage-badge` (98%, `docs/coverage.svg` byte-unchanged), `specmgr
    docs` (only `docs/GENERATED.md` + the `schema.py` API page changed,
    `docs/gol_schema.json` new), `specmgr mcp-docs` (no `docs/MCP.md`
    drift — gol registers no MCP surface until Phase 3), `specmgr schema`
    (exit 0, zero drift), `specmgr adr-toc` (no change).
- Next: Phase 3 (MCP Surface) — `gol/tools/` (incl. the `list_gol` paged
  tool consuming `GolSummary`), `gol/resources/`, `gol/prompts/`, packaged
  `gol/data/`, `gol/__init__.py` + `server.py` registration.
- Notes:
  - Vulture: the new Phase-2 names needed **no** `whitelist.py` entry —
    `GolDocument`/`parse_gol`/`GolSummary` are import-visible via
    `gol/models/v1/__init__.py`, and `SCHEMA_COMMENT_VERSION` additionally
    via `commands/schema.py`. This mirrors REQ/PRB exactly (their
    `parse_req`/`ReqSummary`/`parse_prb`/`PrbSummary` are likewise absent
    from the whitelist). `whitelist.py` is unchanged this phase.
  - `docs/gol_schema.json` carries the words "Characteristics"/"Level"
    only inside the `$defs.Goal.description` prose (the `Goal` class
    docstring documents the deliberate omissions: "Mirrors `Requirement`
    (REQ) minus `Characteristics` and minus `Level`"). The schema *
    structure* itself contains no such sections, fields, or RFC 2119
    values — that is what the plan's sanity check targets. Rewording the
    Phase-1 `body.py` docstring would be an edit outside this phase's
    allowed file surface, so it was left as-is.
  - ACC-001/ACC-002/ACC-003 (this phase's acceptance criteria) are covered
    by the reference-doc round-trip + minimal-doc + invalid-field tests in
    `test_parser.py` (on top of Phase 1's `test_frontmatter.py`/
    `test_body.py`); `docs/gol_schema.json` is the ACC-001 schema artifact
    (the `specmgr://gol/schema` resource that serves it is Phase 3).

#### Update 2026-08-25 (Phase 1)

- Completed: Phase 1 (Specification), Tasks 1.1–1.5.
  - Task 1.1: `gol_reference.md` written — `GOL-0007: Competitive Engines in
    Consumer Vehicles` (the exact goal `req_example.md`'s `### Goals`
    sub-list cross-references), exercising every field: `statement`,
    `Source`, and all optional sections present (`Description`/`Priority`
    with comment/`Tags`/`Related Artifacts` with all four sub-lists/
    `More Information`/`Notes`). Verified `specmgr mdformat`-clean (exit 0,
    idempotent) and byte-exact round-trippable through the models.
  - Task 1.2: `GolFrontmatter` (`gol/models/v1/frontmatter.py`) —
    `MarkdownFrontmatter` subtype, `type=Literal["gol"]`, REQ's exact
    7-value status set with its own `_ALLOWED_STATUSES` frozenset and
    validator.
  - Task 1.3: `Goal` body (`gol/models/v1/body.py`) — REQ's body minus
    `Characteristics`/minus `Level`; mandatory `statement` + `source`,
    six optional sections; `Priority` re-declares REQ's
    `MarkdownSection2WithComment` + `field_validator` pattern (0–99, no
    leading zeros); `RelatedArtifacts` with four optional
    `SPACE_SEPARATED`-derived `MarkdownSection3` sub-lists; `Goal`'s H1 is
    free-form (`@alias ".+"` REGEX).
  - Task 1.4: `tests/gol/models/v1/test_frontmatter.py` (9 tests) +
    `test_body.py` (32 tests) — structural + validation coverage including
    each optional section individually absent/present, each of the four
    sub-lists individually absent/present, mandatory-field
    `ValidationError` (direct construction) and `AssertionError`
    (`from_text`) channels, `Priority` range/leading-zero validation, and
    the reference document's byte-exact round-trip.
  - Task 1.5: quality gate green — `ruff format --check` (933 files),
    `ruff check`, `vulture` (exit 0, no output, no new whitelist entries
    needed — every `gol` field name already exists in REQ's models), full
    unittest suite (1495 tests, baseline was 1454), `specmgr mdformat` on
    the reference doc (exit 0 twice).
- Next: Phase 2 (Pydantic Models, Parser & Schema) — `GolDocument`,
  `parse_gol`, `GolSummary`, `Field(description=...)` parity, `specmgr
  schema` wiring + `docs/gol_schema.json`, parser tests.
- Notes:
  - The body's `description` field (`Goal.description`) is declared with
    `default=None` — a deliberate deviation from REQ's own line, where
    `description: Description | None` carries no default and is therefore
    pydantic-*required* (REQ's `Requirement.from_text` fails on a document
    without a `## Description` section — verified). The plan makes
    `Description` optional for `gol`, so the default is mandatory here.
    REQ's quirk is out of scope for this feature (see Decisions Made).
  - Engine quirk documented for later phases: multi-item
    `list[MarkdownListItem]` fields round-trip tight → loose (each item's
    stored extent ends with `\n` and the `__str__` join adds another), so
    the reference doc's multi-item lists (`Tags`, the `### Goals`
    sub-list) are authored loose; single-item lists are unaffected. Loose
    lists remain byte-exact (the engine's documented exception).
  - Package-init state: `gol/models/v1/__init__.py` exists with the
    Phase-1 export set (frontmatter + body classes; `__all__` kept
    alphabetical) and must be extended in Phase 2 with `GolDocument`,
    `parse_gol`, `GolSummary`, `SCHEMA_COMMENT_VERSION` to match REQ's
    full `__init__`. `gol/__init__.py` is intentionally *not* created yet
    (Task 3.16 owns it, and its `from . import prompts, resources, tools`
    line would fail while those sub-packages don't exist); `gol/models/`
    has no `__init__.py`, mirroring REQ's exact file shape. `gol` is a
    namespace package until Task 3.16 — imports and setuptools'
    `namespaces = true` packaging both work.

#### Update 2026-08-25 (planning)

- Completed: GitHub issue #18 filed ("Add artifact type Goal (GOL)") with a
  short overview description. Full design/planning discussion — schema
  shape (REQ mirrored minus `Characteristics` and minus `Level`; mandatory
  `statement` + `Source` only), status set (REQ's 7-value set), related-
  artifact sub-lists (all four, identical to REQ), update mechanism
  (whole-body replace), prompt behavior, and MCP surface (10 tools / 3
  resources / 2 prompts) all decided; this README written from that
  discussion.
- Next: Phase 1 (Specification) — write `gol_reference.md`, define
  frontmatter/body models.
- Notes: Planning-only session per explicit user instruction (no
  implementation attempted). Issue numbering note: GitHub number 17 was
  already consumed by the merged feat-16 PR, so this feature's issue is
  #18 and the folder is `feat-18-goal` accordingly (the `feat-NNN-slug`
  convention ties the folder name to the issue number).

### Decisions Made

- **2026-08-25**: Type abbreviation `gol`, domain-first layout
  (`gol/models/v1/`, `gol/tools/`, `gol/resources/`, `gol/prompts/`,
  `gol/data/`) — matches REQ/PRB precedent (schema lives inside the domain
  package, not top-level `models/`), since GOL is a new domain built after
  the domain-first refactor.
- **2026-08-25**: Body mirrors REQ minus `## Characteristics` — ISO 25010
  quality characteristics are a requirement-level attribute; a business
  goal states *what* to achieve, not *which quality dimension* it loads
  (user decision).
- **2026-08-25**: No `## Level` section — a goal is implicitly always a
  MUST; RFC 2119 obligation strength is a requirement-level attribute
  (user decision). Consequently the only mandatory body fields are
  `statement` and `Source`, and `gol/models/v1/body.py` declares no
  `Level` class or RFC 2119 validator.
- **2026-08-25**: Status set = REQ's exact 7-value set
  `draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/
  `implemented` — goals are business-level requirements, so
  requirement-lifecycle semantics apply (user decision), with goal-specific
  meanings for `implemented` (= goal reached) and `superseded` (= replaced
  by another goal) as spelled out in Design Notes.
- **2026-08-25**: `Related Artifacts` carries all four sub-lists, identical
  to REQ (`Requirements`/`Decisions`/`Goals`/`Acceptance Criteria`), each
  optional and opaque free text — the `### Goals` sub-list cross-
  references peer/superseding goals (user decision).
- **2026-08-25**: `update_gol` is a single whole-body replace tool
  (REQ/PRB convention), not an ADR-style `update_section`/option-style
  granular tool — the latter is currently ADR-specific code (ADR
  71fd95d7), same decision as feat-16's for `prb`. Individual sections
  remain addressable by their fixed heading text within the whole-body
  markdown.
- **2026-08-25**: `list_gol` is a paged tool from day one per ADR
  ec9f5262 — no `specmgr://gol/list` resource, no resource-then-convert
  history.
- **2026-08-25**: `gol_example.md` is drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` — the exact goal `req_example.md`'s
  `### Goals` sub-list already cross-references — so the two packaged
  examples read coherently side by side; it reuses `gol_reference.md`'s
  content verbatim (feat-16's own `prb_example.md`/`prb_reference.md`
  precedent).
- **2026-08-25**: Folder name `feat-18-goal` (issue #18) — GitHub number
  17 was already consumed by the merged feat-16 PR, so the convention's
  `feat-NNN-slug` ↔ issue-number tie lands on 18.
- **2026-08-25**: Body `Description` is declared
  `description: Description | None = Field(default=None, ...)` — a
  deliberate deviation from a 1:1 copy of REQ's line, where `description`
  has *no* default and is therefore pydantic-required (REQ's
  `Requirement.from_text` demonstrably fails on a document without a
  `## Description` section; REQ's own docstring for that section says
  "Mandatory"). The plan makes `Description` optional for `gol` ("a
  freshly created `gol` document may have zero optional sections"), so the
  default is mandatory here. Fixing REQ's own quirk is out of scope for
  this feature.
- **2026-08-25**: `gol_reference.md` frontmatter values:
  `id: deaddead-goal-goal-goal-deaddeadgoal` (prb_reference's
  `deaddead-cafe-cafe-cafe-deaddeadcafe` dead-UUID pattern, `goal` in
  place of `cafe`), `status: accepted` (a non-default status, so the
  packaged example demonstrates the closed set in action; the goal is an
  agreed, pursued business goal), `created`/`updated: 2026-08-25`
  (prb_reference's plain-`YYYY-MM-DD` style, not req_example's
  full-timestamp style).
- **2026-08-25**: Multi-item bullet lists in `gol_reference.md` (`Tags`'s
  three items, the `### Goals` sub-list's two items) are authored *loose*
  (blank line between items). Engine behavior (documented in
  `MarkdownListItem`'s docstring): a `list[MarkdownListItem]` field
  round-trips tight → loose, while loose lists remain byte-exact. Since
  ACC-001/Task 1.4 require the reference doc to round-trip byte-exactly,
  it is authored in the engine's own canonical output form. Single-item
  lists (the other three sub-lists) are unaffected by tight/loose and are
  authored tight, matching `req_example.md`'s look.
- **2026-08-25**: Package-init split for Phase 1 — `gol/models/v1/__init__.py`
  is created now with the Phase-1 export set (frontmatter + body classes,
  `__all__` alphabetical, mirroring `req/models/v1/__init__.py`'s shape)
  and is extended in Phase 2 (`GolDocument`, `parse_gol`, `GolSummary`,
  `SCHEMA_COMMENT_VERSION`); `gol/models/__init__.py` is *not* created
  (mirrors REQ's exact file shape — REQ has none; PRB's docstring-only
  one is not the pattern the plan points at); `gol/__init__.py` is *not*
  created (Task 3.16 owns it, and its `from . import prompts, resources,
  tools` line would fail while those sub-packages don't exist). `gol` is
  therefore an implicit namespace package until Phase 3 — imports work
  today and setuptools' `namespaces = true` keeps wheel packaging
  correct.
- **2026-08-25**: No `whitelist.py` entry for the Phase-2 `gol` names —
  vulture sees `GolDocument`/`parse_gol`/`GolSummary` through their imports
  in `gol/models/v1/__init__.py` and `SCHEMA_COMMENT_VERSION` additionally
  through `commands/schema.py`; mirroring REQ/PRB, whose `parse_req`/
  `ReqSummary`/`parse_prb`/`PrbSummary` are also not whitelisted. The
  extended `__all__` order follows the REQ/PRB shape: `SCHEMA_COMMENT_VERSION`
  first, class names alphabetical, `parse_gol` last.
- **2026-08-25**: `docs/gol_schema.json`'s `$defs.Goal.description` prose
  contains the words "Characteristics"/"Level" (verbatim from the `Goal`
  class docstring, which documents the deliberate omissions); the schema
  structure itself has no such sections, fields, or RFC 2119 values. The
  Phase-1 `body.py` docstring was not reworded (outside this phase's file
  surface) — if a character-level absence is ever required, that is a
  one-line docstring edit to make together with its `specmgr docs`
  regeneration.
- **2026-08-26**: `gol`'s `update_gol` **prompt** takes `id: str` only —
  no `instructions: str | None = None` parameter, deliberately diverging
  from the `update_req`/`update_prb` prompt signatures. The plan settles
  this in two independent places (Design Notes' bullet
  "`update_gol(id: str) -> str`" and the Task 3.15 guidance repeating the
  same signature), and its narrated flow discovers the requested change
  *during* the interview (step 2 shows the user which sections are present
  vs. empty and asks via `question`), so a pre-filled "requested change"
  argument would be redundant. `gol/prompts/update_gol.py`'s own docstring
  calls out the divergence explicitly. The `update_gol` **tool** is
  unaffected (`(id, content)` exactly like `update_req`).
- **2026-08-26**: `gol_template.md`'s frontmatter uses the domain's
  dead-UUID `id: deaddead-goal-goal-goal-deaddeadgoal` (gol_reference's own
  pattern, like prb_template's `deaddead-b00b-...`) with plain
  `2026-08-26` dates (gol_reference's plain-date style), rather than
  req_template's generic `deaddead-dead-dead-dead-deaddeaddead` id and
  full-timestamp dates. Both styles parse identically (`_stringify_metadata`
  coerces either); the choice keeps the packaged gol data internally
  consistent.
- **2026-08-26**: Two `AGENTS.md` domain-set enumerations beyond the four
  the task explicitly lists were updated, per the task's item-5 rule
  ("update those too IF the enumeration is about the domain set"): (a)
  the "Still genuinely missing" bullet "`req`/`tsk`/`qa`/`prb` each
  register `tools`, `resources`, and `prompts`" gained `/`gol`` (GOL
  registers all three, verified in Phase 3 — without it the bullet
  understates the domain set); (b) the "MCP server (`server.py`)"
  section's parenthetical list of the domain packages imported by
  `server.py`'s bottom line gained `gol` (that line has included `gol`
  since Phase 3, so the list was factually stale). Both are minimal
  in-place insertions, no reflow.
- **2026-08-26**: The "Models location" paragraph's sentence "REQ, UC,
  and TSK were built *after* that refactor and each keep their schema
  inside their own domain package (`req/models/`, `uc/models/`,
  `tsk/models/`) instead" was deliberately **not** touched: it is
  already stale *before* this feature (it omits QA and PRB, both of
  which keep their schemas in-domain — the `prb/` bullet itself says
  "PRB is a new domain built after the domain-first refactor, same as
  REQ/UC/TSK/QA"), so making it complete would mean fixing pre-existing
  staleness for three domains at once, which is outside Task 4.1's
  scope ("do not rewrite or reflow anything else in the file"). The new
  `gol/` bullet carries GOL's own models-location statement, so nothing
  GOL-specific is left unrecorded. Flagged for the orchestrator to
  decide separately.
- **2026-08-26**: No `whitelist.py` entry for any Phase-3 `gol` name —
  every `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` function is
  import-referenced by its sub-package's `__init__.py`
  (`gol/tools/__init__.py` imports all ten tools by name;
  `gol/resources/__init__.py` and `gol/prompts/__init__.py` likewise),
  which vulture sees, exactly as REQ's/PRB's own MCP entry points are seen
  (the MCP section of `whitelist.py` holds only `version_info`). Vulture
  ran clean (exit 0, no output) with the new tree in place.

### Related PRs / Commits

- [Issue #18](https://github.com/dfch/biz.dfch.SpecMgr/issues/18): Add
  artifact type Goal (GOL) — the issue this feature implements.
