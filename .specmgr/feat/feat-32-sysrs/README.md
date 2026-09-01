---
created: 2026-08-30
id: feat-32-sysrs
status: in-progress
updated: 2026-09-01
version: 1.0.0
---

# Feature: Add artifact type "System Specification" (SYSRS)

## Plan

### Overview

New aggregator domain for a **System Specification** document: a
document-type that ties together already-existing specmgr artifacts
(`gol`, `prb`, `uc`, `req`, `rsk`, `dec`/`adr`, `qa`) into one coherent,
navigable specification, rather than duplicating their content. Follows
the domain-first hierarchy (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and
is expected to land on the "simple surface" used by GOL/RSK/QA/DEC/SOP
(generic `update`/`set_status` dispatch from day one, per ADR
36905d5b-8057-4294-8665-c7eed5534db0 — no per-domain mutation tools).

Domain key: `sysrs` (decided 2026-08-30 — see Decisions Made).

### Requirements

- REQ-001 (research, done): Survey existing external standards/templates
  for system-level specification documents to ground the new schema's
  section outline instead of inventing one from scratch. Sources
  reviewed: ISO/IEC/IEEE 29148:2018 (SyRS/StRS/SRS/BRS/OpsCon templates),
  INCOSE (SE Handbook v5, Needs and Requirements Manual, Guide to Writing
  Requirements — requirement categorization: Function/Performance,
  Fit/Operational, Form, Quality, Compliance; **primary-source-verified
  wording differs, see Design Notes item 2**), MIL-STD-961E (System/
  Subsystem Specification format — recalled from training, not freshly
  verified against a primary source), MITRE's system-specification
  writing guide (not accessible for verification over the web; a local
  copy of MITRE's Systems Engineering Guide was added to this folder and
  is being converted to markdown for direct reading — see Task 0.5),
  HERMES 2022 (Swiss PM method — confirmed to be process/role-oriented,
  not a content-outline source), NASA SE Handbook (specification-tree
  concept, no fixed template of its own).
- REQ-002 (decided 2026-08-31): The final section outline for the
  `sysrs` body is `example.v7.md` (REV 7, user-approved): 29148 §9.5
  clause structure with the BRS/StRS content borrowed up front,
  `## Requirements` grouped by the nine ISO/IEC 25010:2023
  characteristics (canonical names/order), `## Other Characteristics`
  for 29148's non-25010 requirement categories (§9.5.11–9.5.17), plus
  `## Appendix`/`## Definitions and Acronyms`; per-section mandatory/optional
  flags and content types are approved in that file (18 H2s, 22 H3s).
  See Decisions Made (2026-08-31, REV 6/7 entries).
- REQ-003 (decided): Cross-references to other domains carry **id,
  title, and a very short (one-line) agent-generated paraphrase**, not
  embedded full content — mirrors GOL/DEC/SOP's `RelatedArtifacts`
  bullet-list shape, with an added short-summary field per entry. The
  exact field shape is decided (2026-08-31/2026-09-01 — see Decisions
  Made): a `<TYPE> <uuid>: <title>` bullet plus a per-bullet optional
  indented notes-paragraph paraphrase (the `MarkdownListItemWithNotes`
  shape), with per-section type-tag regex enforcement — implemented as
  REQ-005/REQ-006.
- REQ-004 (not started): Everything else a from-scratch domain needs —
  the full `sysrs` implementation, broken down into REQ-005..REQ-014
  below and Phases 1–6 of the Task List; patterned on `sop`'s precedent
  (`.specmgr/feat/feat-30-sop/README.md`), with `vcr` (fully shipped on
  this branch since the 2026-08-31 dev merge) as the newest from-
  scratch reference for Phase 1's empirical-validation discipline.
- REQ-005: Define the `sysrs` markdown schema — frontmatter
  (`type="sysrs"`, the closed 5-value status set
  `draft`/`review`/`approved`/`active`/`retired`, default `draft` —
  Decisions Made 2026-09-01) and body = the approved `example.v7.md`
  outline (18 H2s / 22 H3s in binding order, every heading's
  MANDATORY/OPTIONAL flag + content type as annotated in that file; H1
  prefix `^System Requirements Specification: .+$`; cross-reference
  sections per REQ-006; DEC/VCR-style optional `## Updates` last).
- REQ-006: Pydantic models under `sysrs/models/v1/` (frontmatter, body,
  document, parser, summary), domain-first, mirroring `sop`/`vcr`'s
  exact file shapes — **no** `models/md` engine changes: if Phase 1's
  empirical validation finds a shape the engine does not support, stop
  and report rather than patching the engine. **Per-section cross-
  reference bullet regex enforcement** (Decisions Made 2026-09-01):
  each cross-reference list's item text must fullmatch
  `<ALLOWED-TYPE-TAG(S)> <lowercase-8-4-4-4-12-hex-uuid>: <title>`,
  mirroring the shipped `vcr` precedent (`_VERIFIES_PATTERN` in
  `vcr/models/v1/body.py`, exact uuid-fragment style), with allowed
  tags per section: `### Goals` → `GOL`; `### Problem Statement` →
  `PRB`; `## Stakeholder Needs and Elicitation` → `QA`; `##
  Operational Concept and Scenarios` → `UC`; `## Decisions` → `DEC` or
  `ADR`; `## Risks` → `RSK`; the nine `## Requirements` H3s and the six
  `## Other Characteristics` H3s → `REQ`; `## Verification` → `VCR`.
  The per-bullet notes paragraph stays free text; semantic live
  validation of the referenced uuid/title is out of v1.
- REQ-007: Parse/validate `sysrs` documents from markdown, mirroring
  `parse_dec`/`parse_sop`'s two-error-channel convention
  (`AssertionError` for structural problems,
  `pydantic.ValidationError` for field-level problems).
- REQ-008: 7 MCP tools — **no** `update_sysrs`/`set_status_sysrs`
  (dispatch-only from day one, ADR 36905d5b, `sop`'s precedent):
  `create_sysrs` (fresh `uuid4`, `status="draft"`, filename
  `sysrs-{id}-{slug}.md`), `parse_sysrs`, `list_sysrs` (paged tool from
  day one, ADR ec9f5262), `get_sysrs(id, raw=False)`,
  `get_sysrs_example`, `get_sysrs_template`,
  `validate_sysrs` — plus private `_paths`/`_io`/`_lock`/`_write`
  helpers. **No** per-domain `delete_sysrs` tool either — deletion
  goes through the generic `delete` tool in `general/tools/`
  (`type="sysrs"`, feat-36-delete convention, ADR 1af6787b; the
  `_delete_sysrs` adapter is REQ-011).
- REQ-009: MCP resources: `specmgr://sysrs/schema`, `/example`,
  `/template` (exactly three — no `/list`, listing is the `list_sysrs`
  tool, ADR ec9f5262; no `/{id}`, id-based reads are `get_sysrs`-only,
  ADR ddfb1109).
- REQ-010: MCP prompts `create_sysrs(topic)`/`update_sysrs(id,
  instructions=None)` — narrated instruction flows reading their own
  packaged instruction data files (`sysrs/data/sysrs_create_
  instructions.md`/`sysrs_update_instructions.md`), reusing the dedup-
  check-first pattern (`list_sysrs`); `create_sysrs` includes an
  explicit step to read the existing cross-cutting
  `specmgr://iso25010` resource for the nine canonical ISO/IEC
  25010:2023 characteristic names + the REQ placement rule (no new
  `general` resource is introduced); `update_sysrs` names the generic
  `update`/`set_status` tools with `type="sysrs"`.
- REQ-011: Add `"sysrs"` to the generic cross-domain mutation tools —
  `_update_sysrs`/`_set_status_sysrs`/`_delete_sysrs` private
  adapters, `"sysrs"` dispatch-table entries, and `"sysrs"` added to
  the `Literal[...]` parameter unions in `general/tools/update.py`,
  `general/tools/set_status.py`, and `general/tools/delete.py`
  (`_DELETE_TYPES` + `type` `Literal` + imports + the docstring
  count, eleven→twelve whole-body domains) (`set_status` rejects
  `superseded_by` for `sysrs` with the standard non-adr
  `ValueError`; `adr` stays excluded from `delete`).
- REQ-012: Packaged example/template/instructions/schema data
  (`sysrs/data/`) via the existing generic
  `general/tools/_packaged_data.py`, with the matching `pyproject.toml`
  package-data entry, pre-commit hook, and CI step.
- REQ-013: Doc generation/registration wiring — `specmgr docs`,
  `specmgr schema` (new `sysrs` entry in the doc-type registry,
  `commands/schema.py`), `specmgr mcp-docs`, all kept drift-free via
  pre-commit/CI; `server.py` (import line + module docstring),
  `AGENTS.md`, and root `README.md` updated.
- REQ-014: Full test coverage mirroring `tests/sop/`'s + `tests/vcr/`'s
  layout (models, tools, resources, prompts) and coverage depth, plus
  new test coverage in `tests/general/tools/test_update.py`/
  `test_set_status.py` for the `"sysrs"` dispatch entries (REQ-011).

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — this README's Design Notes section
  documents the outline of every reviewed source (29148, INCOSE, MIL-
  STD-961E, MITRE, HERMES, NASA) with an explicit confidence note on
  which were freshly verified vs. recalled from training.
- [x] ACC-002: Verifies REQ-002 — user has reviewed and approved a
  concrete `## H2` section list for `sysrs` (not just the tailored-SyRS
  direction): `example.v7.md` (REV 7), approved 2026-08-31 — all
  per-section mandatory/optional flags accepted, `## Appendix`/
  `## Definitions and Acronyms` added.
- [ ] ACC-003: Verifies REQ-003 — the exact `RelatedArtifacts`-with-
  summary field shape is written down in Design Notes and validated
  against the `models/md` engine (mirroring `sop`'s pre-implementation
  empirical-verification discipline) in Phase 1 before any Pydantic
  model code (Phase 2) is written.
- [ ] ACC-004: Verifies REQ-005/006/007 — packaged example **and**
  template parse via `parse_sysrs`; structural violations raise
  `AssertionError`: unknown H2; missing mandatory H2 (`System Purpose`/
  `System Scope`/`Business Context and Goals`/`System Overview`/
  `Requirements`); `## Requirements` present with zero H3s; a
  cross-reference list section present with zero items; `## References`
  present with zero items; H1 prefix mismatch (a `# ...` line not
  starting `System Requirements
  Specification: `); misordering of any top-level section; second H1;
  non-blank content before the H1; a mandatory free-text H2/H3
  present with zero body content (the engine's behavior for that case
  is pinned in Phase 1, Task 1.3(e), and the pinned behavior is
  asserted); a `## Updates` entry heading failing its timestamp-led
  alias (missing timestamp lead or an em-dash separator) and out-of-
  order `## Updates` entries (newest-first is parse-enforced — the
  locked sibling-feature shape, see Dependencies).
- [ ] ACC-005: Verifies REQ-005/006 — value violations raise
  `pydantic.ValidationError`: `status` outside the 5-value set; `type`
  != `"sysrs"`; a cross-reference bullet with the wrong type tag for
  its section, a malformed uuid (not 8-4-4-4-12 lowercase hex), or a
  missing `: <title>`; `DEC` and `ADR` both accepted under `##
  Decisions` (and `REQ` rejected there); a bare cross-reference bullet
  without a notes paragraph accepted (notes are per-bullet optional).
- [ ] ACC-006: Verifies REQ-008 — every listed tool is implemented,
  registered, and callable; `create_sysrs`→`get_sysrs`→`list_sysrs`→
  `update` (generic, `type="sysrs"`)→`set_status` (generic,
  `type="sysrs"`)→`validate_sysrs` round-trip against a temp
  `SPECMGR_DOCS_DIR`; `create_sysrs` fixes `status="draft"` and writes
  `sysrs-{id}-{slug}.md`; `get_sysrs(id, raw=True)` returns the
  frontmatter-stripped body text verbatim; `list_sysrs` paging
  (default 25 / cap 100 / `truncated` boundary) mirrors every other
  domain's `list_<d>` tool exactly.
- [ ] ACC-007: Verifies REQ-009 — every listed resource is implemented
  and registered (exactly three — no `/{id}`, no `/list`);
  `specmgr://sysrs/schema` equals fresh `generate_sysrs_schema()`
  output; example/template resources equal the packaged files
  byte-for-byte.
- [ ] ACC-008: Verifies REQ-010 — both prompts return instruction text
  with `$topic`/`$id`/`$instructions` substituted from packaged data;
  `create_sysrs`'s narration includes the `list_sysrs` dedup check
  first and the `specmgr://iso25010` read-first step; `update_sysrs`
  names the generic `update`/`set_status` tools with `type="sysrs"`.
- [ ] ACC-009: Verifies REQ-011 — the generic `update`/`set_status`/
  `delete` tools accept `type="sysrs"` and correctly dispatch to
  `_update_sysrs`/`_set_status_sysrs`/`_delete_sysrs`; both the whole-
  body and line-range (`begin`/`end`) branches of `update` work for
  `sysrs`; `set_status` rejects `superseded_by` for `type="sysrs"`
  with the same `ValueError` every non-adr type gets; `delete`
  resolves through the `sysrs` base dir and returns the deleted path;
  new test cases added to
  `tests/general/tools/test_update.py`/`test_set_status.py`/
  `test_delete.py` (not just `tests/sysrs/`) exercise this.
- [ ] ACC-010: Verifies REQ-012 — packaged data resolves correctly from
  a real, non-editable install (`uv build --wheel` + scratch-venv
  install), mirroring `sop`'s ACC-007 verification.
- [ ] ACC-011: Verifies REQ-013 — `specmgr docs`/`specmgr schema`/
  `specmgr mcp-docs` all report no drift after implementation;
  `AGENTS.md` and root `README.md` reflect the new `sysrs` domain,
  including the "dispatch-only, no per-domain update/set_status tools"
  note and the per-section cross-ref type-tag regex note.
- [ ] ACC-012: Verifies REQ-004/014 — full unittest suite green; ruff
  format/check and vulture clean; `specmgr unused-code` clean.

### Scope

Included:

- The full `sysrs` domain implementation (Phases 1–6):
  `sysrs/models/v1/` schema + parser, `sysrs/tools/` (7 tools,
  dispatch-only), `sysrs/resources/` (3), `sysrs/prompts/` (2),
  `sysrs/data/` packaged data.
- Per-section cross-reference bullet type-tag regex enforcement
  (Decisions Made 2026-09-01) — the confirmed
  `<TYPE> <uuid>: <title>` shape with the per-section allowed-tag
  mapping (REQ-006).
- The `"sysrs"` dispatch entries in the generic `update`/`set_status`
  tools (`general/tools/`) — dispatch-only from day one, per ADR
  36905d5b (REQ-011).
- Cross-cutting registration (`server.py`, `pyproject.toml`,
  `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`,
  root `README.md`) (REQ-013).
- Tests mirroring `tests/sop/`'s + `tests/vcr/`'s layout and coverage
  depth, plus new dispatch-entry test cases in `tests/general/tools/`
  (REQ-014).

Explicitly out of scope:

- Any changes to the `models/md` engine itself — if Phase 1's
  empirical validation finds a shape the engine does not support, stop
  and report rather than patching the engine.
- Per-domain `update_sysrs`/`set_status_sysrs` mutation tools —
  generic `update`/`set_status` dispatch only (ADR 36905d5b).
- A `render_sysrs` / deterministic re-render (raw-body persistence
  like GOL/RSK/QA/DEC/SOP/VCR).
- A `specmgr://sysrs/{id}` resource or a `specmgr://sysrs/list`
  resource (ADR ddfb1109 / ec9f5262).
- A per-domain `delete_sysrs` tool — deletion goes through the
  generic `delete` tool (feat-36-delete, ADR 1af6787b); the `sysrs`
  `_delete_sysrs` adapter is in Scope/REQ-011 (no whole-body domain
  has a per-domain `delete_*` tool).
- Semantic live validation of cross-referenced ids (that the
  `<uuid>`/title actually matches the referenced document) — text-only
  references in v1, same as every other domain's cross-references
  today.
- A new cross-cutting `general` resource — the `create_sysrs` prompt
  points at the existing `specmgr://iso25010` resource instead (unlike
  `sop`'s `specmgr://rasci` or `vcr`'s `specmgr://dtais`).
- Any changes to any other existing domain's schema, tools, or data.
- Task 0.11's ISO_24765 grounding question stays open and non-blocking
  — `## Definitions and Acronyms` is free-form text either way.

### Dependencies

- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR 36905d5b-8057-4294-8665-c7eed5534db0 (generic
  `update`/`set_status` dispatch — new domains use it from day one), ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614 (tool-only id-based reads), ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 (paged `list_<d>` tool, not a
  resource); `.specmgr/feat/feat-30-sop/README.md` as the most recent
  from-scratch-domain precedent to copy tooling/registration shape from;
  `.specmgr/feat/feat-33-vcr/README.md` (sibling feature, its own
  worktree/branch) — the `vcr` ("Verification Case Record") domain it
  builds fills the "Verification/Test and Evaluation" gap this feature's
  own research identified (Task 0.6/0.9), and is now fully shipped on
  this branch (2026-08-31 dev merge); `sysrs`'s `## Verification`
  section (see `example.v7.md`) is a cross-reference list to `vcr`, and
  `vcr`'s shipped `_VERIFIES_PATTERN` (`vcr/models/v1/body.py`) is the
  regex-shape precedent every `sysrs` cross-reference section mirrors
  (Decisions Made 2026-09-01). Also depends on: `sop`'s shipped
  frontmatter 5-value status set (`sop/models/v1/frontmatter.py`) as
  the `sysrs` status-vocabulary precedent (Decisions Made 2026-09-01),
  and the existing cross-cutting `specmgr://iso25010` resource
  (`general/resources/`) as the source of the nine canonical ISO/IEC
  25010:2023 characteristic names the `create_sysrs` prompt's REQ
  placement rule reads.
- Coordinates with (2026-09-01 decision): `.specmgr/feat/feat-38-39-
  41-43-44/README.md` (sibling branch `feat-38-39-31-43-44`, design
  complete 2026-09-01 with decisions D1–D10 locked, not yet
  implemented) changes the two surfaces `sysrs` mirrors — the `##
  Updates` entry shape (issues #38/#39: em-dash separators rejected,
  ` - ` or ` : ` separators, timestamp-led headings, parse-enforced
  newest-first ordering, `MarkdownSection2WithComment` containers with
  an ordering-hint comment in templates) and the frontmatter
  `created`/`updated` format (issue #44: date+time only, `yyyy-MM-dd
  HH:mm:ss.fff` + `Z`/`±HH:mm`, three-digit milliseconds, one shared
  `general/tools/_timestamps.py` generator helper). `sysrs` adopts
  the locked post-sibling shapes from day one (no rework after its
  merge); `sysrs-example.md` was migrated to them in the same planning
  pass (Task 0.12, done). Execution order relative to the sibling's
  development (2026-09-01): Phases 1–2 are fully parallel-safe —
  Phase 1 exercises only standard engine mechanics that already ship
  in other domains (REGEX-aliased H3 headings: `vcr`'s
  `AcceptanceCriterion`; the `assert`-based newest-first
  `model_validator`: `feat`'s `Updates` — the locked `## Updates`
  shape needs no sibling code), and Phase 2 writes only new
  `sysrs/`/`tests/sysrs/` files (the ordering check ships domain-
  local per the Design Notes fallback — use the shared
  `models/md/_ordering.py` helper directly if the sibling's Phase 2
  has landed by Task 2.3). Phase 3's Tasks 3.1/3.2 (new
  `sysrs/tools/` files) are parallel-safe too (the Task 3.1
  checkpoint picks the then-current mirror shape — `_timestamps.py`
  and `_path_safety` guards included). The only shared-file surfaces
  are Task 3.3 — which edits `general/tools/update.py`/
  `set_status.py`/`delete.py`, the same files the sibling's Phase 4
  rewrites (issue #43 path-safety guards) — and Phase 6's
  `server.py` docstring / `AGENTS.md` edits (the sibling's Phase 4
  Task 4.5 touches both). Run Task 3.3 after the sibling's Phase 4
  has merged to `dev` (preferred — the `sysrs` adapters then carry
  the `_path_safety` guards from day one), or do it now and rebase
  on the sibling's merge (a mechanical conflict in three files, not
  a semantic one); its tests/gate, Tasks 3.4/3.5, chain behind it,
  and with them Phases 4–6 under the phase-gate discipline (Phases
  4/5 themselves are new-file-only, no sibling overlap). Re-merge
  `dev` at the start of Phase 6 (Task 6.1) and rebase the
  enumeration edits on the post-sibling text. New `sysrs` files
  shadowing `id`/`type` carry the per-file pylint disable line (the
  sibling's Phase 5 convention) regardless of order.
- Blocks: nothing known.

### Design Notes

**External source outlines reviewed (REQ-001):**

1. **ISO/IEC/IEEE 29148:2018** (verified via a live example document) —
   defines 5 related templates (BRS/StRS/OpsCon/SyRS/SRS). SyRS/SRS
   outline:

   - 1 Introduction (Purpose, Scope, Product perspective incl. system/
     user/hardware/software/communications interfaces, memory
     constraints, operations, site adaptation; Product functions; User
     characteristics; Limitations; Assumptions/dependencies;
     Definitions; Acronyms)
   - 2 Requirements (External interfaces, Functions, Usability,
     Performance, Logical database, Design constraints, Standards
     compliance, System attributes)
   - 3 Verification
   - 4 Supporting information
   - 5 References

   **Correction (2026-08-31, Task 0.10, done)**: the outline above was
   recorded before the actual ISO/IEC/IEEE 29148:2018 standard text was
   available locally ("verified via a live example document" meant an
   example SyRS instance, not the standard itself) and **does not match**
   the standard's real normative SyRS content clause. The user has since
   added `ISO_29148.md` (full converted standard text) and
   `ISO_24765.md` (ISO/IEC/IEEE 24765:2017, *Systems and software
   engineering — Vocabulary*) to this folder. Reading `ISO_29148.md`
   directly (§8.4 "System requirements specification" — general
   description and example-outline pointer; §9.5 "System requirements
   specification (SyRS) content" — the actual normative clause) shows
   the true structure is **19 sub-clauses**, not 5: 9.5.1 SyRS overview,
   9.5.2 System purpose, 9.5.3 System scope, 9.5.4 System overview
   (9.5.4.1 System context, 9.5.4.2 System functions, 9.5.4.3 User
   characteristics), 9.5.5 Functional requirements, 9.5.6 Usability
   requirements, 9.5.7 Performance requirements, 9.5.8 System interface
   requirements, 9.5.9 System operations (9.5.9.1 Human system
   integration, 9.5.9.2 Maintainability, 9.5.9.3 Reliability, 9.5.9.4
   Other quality requirements), 9.5.10 System modes and states, 9.5.11
   Physical characteristics (9.5.11.1 Physical, 9.5.11.2 Adaptability),
   9.5.12 Environmental conditions, 9.5.13 System security requirements,
   9.5.14 Information management requirements, 9.5.15 Policy and
   regulation requirements, 9.5.16 System life cycle sustainment
   requirements, 9.5.17 Packaging/handling/shipping/transportation
   requirements, 9.5.18 Verification, 9.5.19 Assumptions and
   dependencies. §9.5.18 (Verification) itself says verification content
   should be given "in a parallel manner with the information elements in
   9.5.5 to 9.5.17" — i.e. interleaved per requirement category, not a
   separate document artifact — which is additional supporting evidence
   for modeling `sysrs`'s own `## Verification` as a cross-reference to
   `vcr` entries rather than a monolithic free-text section (see
   `example.v5.md`). §5.4 also confirms exactly **six** named information
   items overall — BRS, StRS, SyRS, SRS, ConOps, OpsCon — and that
   ConOps/OpsCon are themselves interdependent with StRS's own
   operational-concept sub-clauses (§9.4.16/9.4.17), i.e. the overlap
   `sysrs` has between `## Stakeholder Needs and Elicitation` (`qa`) and
   `## Operational Concept and Scenarios` (`uc`) is inherent to the
   standard, not introduced by specmgr's own tailoring. §6.4.3 confirms
   the standard **4** verification methods (inspection, analysis or
   simulation, demonstration, test) MITRE SEG/INCOSE also describe —
   direct primary-source support for `vcr`'s own "DTAIS adds a 5th method
   deliberately" framing. The still-open question is now Task 0.3.2's:
   whether/how the richer 19-subclause §9.5 categorization (vs. INCOSE's
   five-word scheme) should drive `## System Requirements`'s grouping —
   see `example.v5.md`'s updated inline `<!-- Q: ... -->` there. `ISO_24765.md` (the vocabulary standard) is not yet referenced by any
    design decision here — candidate use: grounding a future `## Definitions`/
    `## Acronyms` section (mirroring 29148 §9.2.3/9.2.5) if/when one is
    added; flagged, not yet actioned.

    **Resolution (2026-08-31, REV 6/7)**: the still-open grouping
    question above is settled by the user in `example.v6.md`/
    `example.v7.md`: `## Requirements` is grouped by the nine ISO/IEC
    25010:2023 product-quality characteristics (canonical names and
    model order, per the `specmgr://iso25010` resource) instead of
    29148's per-subclause categories or INCOSE's five-word scheme, and
    29148's remaining non-25010 requirement categories (§9.5.11–9.5.17)
    sit under `## Other Characteristics`. The full 29148 §9.5 → section
    mapping (incl. 9.5.8 → Compatibility/Interoperability and the
    9.5.9.4 absorption note) and the REQ placement rule (first `##
    Characteristics` item of the REQ document, no `req`-domain change)
    are recorded in `example.v7.md`'s header comment.

2. **INCOSE** (SEBoK, SE Handbook v5, Needs and Requirements Manual,
   Guide to Writing Requirements) — process-oriented, not a fixed
   template; contributes a requirement **categorization** scheme and two
   artifacts every system spec should carry: a requirement tree
   (parent/child allocation) and bidirectional traceability to needs,
   verification, and design.

   **Verified against the primary source (Task 0.9, done)**: the user
   supplied a local copy of *INCOSE Systems Engineering Handbook, 5th
   Edition (2023)* (`INCOSE Systems Engineering Handbook 5e 2023.pdf`,
   370 pages), converted to `incose-se-handbook-5e-2023.md` (Task 0.8,
   same `pdftotext`+`pandoc` pipeline as the MITRE guide — see
   "Conversion method" below), and read directly (via a delegated
   sub-agent research pass, since the converted file is ~5,900 lines/
   1.2MB). Findings:

   - **The categorization scheme's exact wording differs from what was
     recalled above.** The Handbook's actual, verbatim text (Section
     2.3.5.3 "System Requirements Definition", ~line 2232): *"The
     system requirements must address **function, fit, form, quality,
     and compliance** with stakeholder and business needs."* — five
     bare words, not the "Function/**Performance**, Fit/**Operational**"
     slash-compounds used above; those extra qualifiers are not
     supported by this primary source and are likely a conflation with
     the Guide to Writing Requirements/Needs and Requirements Manual
     (cited alongside but not present in this converted file) — treat
     as unverified until GtWR/NRM are checked directly. **The bullet
     above is being kept as originally recorded for history, but any
     future schema/prompt wording should use the Handbook's own five
     words, not the slash-compound version.**
   - **No document-outline/SyRS artifact exists in this Handbook at
     all**: `SyRS`/"System Requirements Specification" do not appear
     anywhere in the text (confirmed by full-text search). The
     Handbook's IPO ("Typical Outputs") lists for the Stakeholder
     Needs/Requirements Definition (2.3.5.2) and System Requirements
     Definition (2.3.5.3) processes are granular data items
     ("stakeholder needs and requirements", "traceability mapping", a
     "report") — never a single consolidated specification document.
     Appendices D (N2 diagram legend) and E (input/output glossary)
     looked like the most likely place for a document template but
     turned out to be a process-dependency map and a flat one-line
     glossary respectively — useful for precise term definitions, not
     a section outline.
   - **29148 is cited ~12 times**, always for term/method definitions
     (e.g. the four verification methods, the ConOps definition) —
     never for document structure; the Handbook does not defer to
     29148's document shape, it just borrows some of its vocabulary.
   - **Traceability (Section 3.2.3)** confirms the
     bidirectional/vertical/horizontal traceability concepts and the
     need→stakeholder-req→system-req→architecture/design→verification/
     validation chain, but gives no concrete matrix/table structure —
     conceptual only.
   - **Verification (2.3.5.9) and Systems Integration (2.3.5.8)** are
     both real, well-developed processes with their own IPO
     input/output lists, but neither yields a ready section-content
     checklist — same "confirmed gap, no template" conclusion already
     reached from the MITRE guide, not a new one.
   - **Overall**: this primary-source read corroborated rather than
     extended the secondhand INCOSE knowledge already captured above
     (aside from tightening the categorization wording) — it did not
     surface any new candidate structure for `sysrs`'s section outline.
     29148 (tailored) and the MITRE SEG's life-cycle view remain the
     primary structural sources; INCOSE stays a corroborating/
     terminology source, not an outline source.

3. **MIL-STD-961E** (recalled from training — DTIC/primary source was
   unreachable during this research pass, re-verify before relying on
   it structurally) — classic System/Subsystem Specification (SSS)
   shape: 1 Scope, 2 Applicable Documents, 3 Requirements, 4
   Verification (1:1 traceable to Section 3), 5 Packaging, 6 Notes, plus
   appendices.

4. **MITRE Systems Engineering Guide** (2014 ed., ~726 pages) — a local
   PDF (`se-guide-book-interactive.pdf`) supplied by the user in this
   folder (web fetches of MITRE's site returned 403 during the initial
   research pass) was converted to `se-guide-book-interactive.md` (Task
   0.5 — see Design Notes' "Conversion method" for the pipeline used)
   and read directly (Task 0.6). Confirmed content, directly relevant to
   the outline decision:

   - Organizes its "SE Life-Cycle Building Blocks" section as a V-model:
     **Concept Development** (Operational Needs Assessment → Concept of
     Operations → Operational Requirements → High-Level Conceptual
     Definition) → **Requirements Engineering** (Eliciting/Collecting/
     Developing Requirements → Analyzing and Defining Requirements →
     Prototyping/Experimentation for uncertainty) → **System
     Architecture** (Architectural Frameworks/Models/Views → Approaches
     to Architecture Development → Architectural Patterns) → **System
     Design and Development** (Develop System-Level Technical
     Requirements → Develop Top-Level System Design → Assess the
     Design's Ability to Meet the System Requirements) → **Systems
     Integration** → **Test and Evaluation** → **Implementation,
     Operations and Maintenance, and Transition**. This is a *process*
     view (mirrors INCOSE's), not a document-section outline, but it
     independently confirms our gol→uc→req→dec→rsk/verification chain
     mapping and flags **Test and Evaluation / verification** and
     **Systems Integration** as life-cycle stages with no current
     specmgr domain.
   - Its "Concept of Operations" article endorses **IEEE Std
     1362-1998** and lists CONOPS' critical components: the existing
     system being replaced, justification for a new/modified system, a
     description of the proposed system, and scenarios of system use in
     the user's environment — this maps directly onto `gol` (existing-
     system/justification) + `uc` (scenarios).
   - Its "Develop System-Level Technical Requirements" article
     explicitly names the deliverable a **"system specification
     document"** using formal "shall"/"should" statements, and gives a
     "System-Level Requirements Checklist" (traceable to user
     requirements; describes a function/performance/constraint/
     reference; appropriate level of detail; legal/regulatory
     constraints; enterprise-architecture constraints; environmental
     design requirements; all external interfaces; quantifiable/
     testable/verifiable performance; avoid "shall not" and vague words
     like "maximize"; use ranges not single-point values; distinguish
     threshold vs. objective requirements) — independently confirms
     INCOSE's Function/Performance, Fit/Operational, Form, Quality,
     Compliance categorization from a second source (**note**: the
     INCOSE Handbook's own primary-source wording, verified in Task
     0.9, is the plainer five words "function, fit, form, quality, and
     compliance" — see Design Notes item 2; this MITRE bullet has not
     itself been re-verified against MITRE's primary text for the
     slash-compound wording).
   - Its "Assess the Design's Ability to Meet the System Requirements"
     article confirms the traceability chain explicitly: mission/needs
     → operational requirements → functional/system requirements →
     design → performance verification — the same chain our candidate
     domain-to-source mapping table already reflects.

   > **Note — Task 0.7 replaced (2026-08-30):** a second, narrower
   > MITRE technical report, *Guide for Writing System Specifications*
   > (MITRE Product/Case No. PR 14-3372), was originally slated for
   > Task 0.7 as likely more directly relevant to `sysrs`'s document
   > structure than the broader SEG book above. It could never be
   > fetched over the web (`403 Forbidden` from both
   > `https://www.mitre.org/sites/default/files/publications/pr-14-3372-guide-for-writing-system-specifications.pdf`
   > and the MITRE SEG landing page tried as a fallback), and the user
   > has not supplied a local copy. **Per explicit user instruction,
   > Task 0.7 now targets a different, already-supplied document
   > instead**: INCOSE's own *Guide for Writing Requirements* (2019
   > revision, `INCOSE Guide for Writing Requirements 2019.pdf`, ~132
   > pages, owner-read-only permissions on disk). Converted to
   > `incose-guide-writing-requirements-2019.md` (1,437 lines/~319 KB)
   > via a delegated sub-agent, same `pdftotext` + `pandoc -f markdown-fancy_lists -t gfm --wrap=none` pipeline as the two
   > prior conversions — this PDF needed **no** control-character
   > stripping at all (unlike the MITRE SEG guide's `\f`/`\x07` or the
   > INCOSE Handbook's wider `\x08`/`\x1e`/`\x1f` set), and the
   > ordered-list-marker-corruption spot-check passed cleanly (several
   > mid-sentence `(NNN)`-style parentheticals like `(2014)`/`(1)`/`(2)`
   > all remained plain inline text, zero renumbering). **Not yet
   > read** — this document is very plausibly the "Guide to Writing
   > Requirements" (GtWR) the INCOSE Handbook cites alongside the Needs
   > and Requirements Manual for the "Function/Performance,
   > Fit/Operational, Form, Quality, Compliance" categorization wording
   > that Design Notes item 2 flagged as unverified against the
   > Handbook's own plainer "function, fit, form, quality, and
   > compliance" (Task 0.9) — reading it (mirroring Task 0.6/0.9's
   > treatment) is a natural, high-value next step, tracked as a new
   > Task 0.7b below, but has not been done yet as part of this
   > conversion.

5. **HERMES 2022** (Swiss federal PM method) — a project-management
   method (roles/scenarios/results), not a requirements-content
   standard; could not confirm current result/document names from the
   site during this pass. Weak fit for section-outline purposes; may be
   more relevant later for a process/role model.

6. **NASA SE Handbook** — discusses a "specification tree"
   (System/Segment/Subsystem specs derived from the ConOps) but defers
   to 29148/MIL-STD-961-style content rather than defining its own
   outline.

**Domain-to-source mapping (candidate, not yet final):**

| Concept (29148/INCOSE) | Existing specmgr domain |
|---|---|
| Business/mission rationale (BRS) | `gol` |
| Stakeholder needs (StRS) | `gol` / `qa` |
| Operational concept/scenarios (OpsCon) | `uc` |
| System requirements (SyRS), incl. categories | `req` |
| Risk identification | `rsk` |
| Design/architecture decisions | `dec` / `adr` |
| Problem framing | `prb` |
| Verification planning / Test & Evaluation | `vcr` (feat-33, Phase 1 complete — closes the gap below, updated 2026-08-31) |
| Systems Integration | no dedicated domain yet (confirmed gap by MITRE SEG too) |
| Traceability / requirement tree | `RelatedArtifacts`-style cross-refs; ISO/IEC/IEEE 29148 itself names this a "Requirements Traceability Matrix" (RTM, §6.4.3) — a real standard concept, not just an ad hoc shape (added 2026-08-31) |

**Decisions made so far (see Decisions Made log):**

- Aggregation model: reference by id + title, plus a very short (one
  line) agent-paraphrased summary per reference — not full-content
  embedding.
- Section outline: lean toward a **tailored** (not verbatim) ISO/IEC/
  IEEE 29148 SyRS shape; exact section list still open, to be refined
  after reading MITRE's Systems Engineering Guide directly.
- (from your review comments on `example.md`, applied in `example.v2.md`)
  H1 title: mandatory, constrained to
  `^System Specification: .+$` (regex fullmatch against the heading
  text, same convention as `uc`'s `Extension N.`/`Step N:` and `sop`'s
  `Step N:` `@alias` regexes).
- (from your review comments on `example.md`, applied in `example.v2.md`)
  `## Overview`: mandatory, any
  markdown content — not restricted to a single paragraph.
- (from your review comments on `example.md`, applied in `example.v2.md`)
  No bold pseudo-heading (e.g.
  `**RelatedArtifacts:**`) for cross-reference lists anywhere in
  `sysrs` — use a real `### <Name>` heading instead, named for what it
  holds (`### Goals`, `### Problems`, `### Scenarios`, ...). Unlike
  `gol`'s `## Related Artifacts` wrapper (needed there because a
  goal's own H1 isn't domain-specific), `sysrs` needs no such wrapper
  H2 since every `sysrs` H2 is already domain-specific — its
  `### <Name>` list sits directly under it.
- (decided 2026-08-30, applied in `example.v3.md`) When an H2 holds
  exactly one cross-reference list, drop the `### <Name>` sub-heading
  entirely — the list sits directly under the H2. Keep the `### <Name>`
  sub-heading rule only for H2s that genuinely hold more than one
  distinct list or a mix of free text and a list (today: only
  `## Business Context and Goals`, which keeps its three H3s). Applied
  to `## Stakeholder Needs and Elicitation`, `## Operational Concept and Scenarios`, `## System Requirements`, `## Architecture and Design Decisions`, and `## Risks`, which in `example.v2.md` each had a
  redundant single H3 that just repeated (or barely reworded) its own
  H2's name (`## Risks` → `### Risks`, `## Architecture and Design Decisions` → `### Decisions`).
- (decided 2026-08-30, applied in `example.v4.md`) Cross-reference
  bullets show the title inline (`GOL-<id> + title`), reversing
  `example.v2.md`'s "id-only, no inline title" draft shape — applied
  uniformly to every cross-reference list in the document (`gol`/`prb`/
  `qa`/`uc`/`req`/`dec`/`rsk`), not just some. Matches how `gol`/`dec`'s
  own existing `### Requirements`/`### Goals`/etc. lists already show
  `"GOL-0007: <title>"` inline today. Closes the "Not yet decided" item
  from `example.v2.md`'s changelog.
- (decided 2026-08-30) `## Architecture and Design Decisions`'s example
  entries in `example.v3.md`/`example.v4.md` are `dec`-only, as a
  discussion-draft illustration convention — **not** a decision to
  deprecate the `adr` domain itself. Real `sysrs` documents may still
  cross-reference either `dec` or `adr` ids; any future decision to
  phase out `adr` repo-wide would need its own README/ADR entry.
- (decided 2026-08-30, applied in `example.v4.md`; **superseded
  2026-08-31, see below**) `## Updates` — a new
  mandatory section tracking changes to the `sysrs` document itself
  over time, added alongside `## More Information` (mirrors `req`'s/
  `feat`'s `### More Information`, level-shifted to H2). `## Updates`
  reuses `feat.Updates`/`feat.UpdateEntry` (`feat/models/v1/body.py`)
  exactly — entry heading `{ISO8601 date+time+millis+offset} — {title}`
  (em dash included) and newest-first ordering — one nesting level
  shallower than `feat`'s own `## Progress` → `### Updates` →
  `#### {timestamp} — {title}` since `sysrs` has no Plan/Progress
  split.
- (decided 2026-08-31, applied in `example.v5.md`) `## Updates` corrected
  to mirror `dec`'s/`vcr`'s actual shipped shape instead of `feat`'s —
  literal reuse of `feat.Updates`/`UpdateEntry` was never possible
  (different heading-level base classes), and reading the code showed
  `dec` (already shipped, already at the right H2/H3 level) and
  `feat-33-vcr` (built concurrently at the same level, explicitly
  choosing to mirror `dec` rather than `feat`) both use a **free-form**
  H3 title (`@alias(value=".+")`, no timestamp regex, no ordering
  validator) and treat `## Updates` as **optional as a whole**, not
  mandatory. `sysrs` now follows that same precedent instead of being the
  only H2-level domain with a stricter, mandatory, `feat`-style
  variant.
- (decided 2026-08-31, applied in `example.v5.md`) Cross-reference
  bullets switched from the `gol`/`dec`-style illustrative, hyphenated,
  truncated pseudo-id (`GOL-4b1e2c9a-...`) to `feat-33-vcr`'s now-settled
  real-id shape: `<TYPE> <uuid>: <title>` (type tag, space, a real
  8-4-4-4-12 hex UUID, colon, title) — `vcr`'s own `## Verifies` field
  uses exactly this pattern (`_VERIFIES_PATTERN` in
  `vcr/models/v1/body.py`) after an explore-agent audit found the
  `GOL-0007`-style codes shipped in `gol`/`dec`'s own examples are
  illustrative-only, structurally unenforced text with no relation to
  real (bare-UUID) ids. Also fixed a latent bug found while making this
  change: every cross-reference bullet in `example.v4.md` literally
  spelled out the four characters `+ title` as placeholder text instead
  of an actual title, despite that revision's own changelog claiming
  every bullet "carries `+ title`" (i.e. an inline title) — REV 4 never
  actually demonstrated the shape it described. `example.v5.md` fills in
  a real (fictional) title on every bullet.
- (decided 2026-08-31, applied in `example.v5.md`) `## Verification and Test Planning` renamed to `## Verification` and reshaped from a
  three-way-undecided free-text placeholder into a cross-reference list
  to `vcr` ids — same shape as every other section — now that the
  sibling `vcr` domain (feat-33) exists specifically to fill this gap
  and has completed its Phase 1 (models + parser). `## Systems Integration` is unaffected (no domain covers it yet).
- (from your review comments on `example.md`, applied in `example.v2.md`
  as a draft — see "Not yet decided" below
  for the still-open confirmation) Cross-reference entry shape: a
  bullet holding *only* the id, followed by a blank line and an
  indented "notes" paragraph carrying the paraphrase (title is not
  shown inline; resolvable via the referenced domain's own `get_<d>`
  tool on demand). Empirically maps directly onto `models/md`'s
  existing `MarkdownListItemWithNotes` class (already used by `gol`'s
  `Tags` section) — no new parser mechanics needed, which materially
  de-risks ACC-003's "validated against the `models/md` engine"
  requirement.

**Not yet decided:**

- Exact `## H2` section list and which are mandatory vs. optional.
- Whether dropping the inline title from cross-reference bullets
  (relying on id-based lookup, per the draft shape above) is
  acceptable, or the title should still appear (e.g. as the notes
  paragraph's first line) — `gol`/`dec`'s own existing
  `### Requirements`/`### Goals`/etc. lists use an inline
  `"GOL-0007: <title>"` shape today, so this is a deliberate departure
  pending confirmation.
- Whether `## Business Context` (free markdown, no fixed template)
  should be agent-drafted from linked Goals or simply omitted when
  empty.
- Whether `rsk` entries' initial/residual probability-impact
  coordinates and strategy belong in the notes paragraph's prose (as
  currently drafted) or need a more structured field/table.
- Whether/how a `## Verification` section (no existing domain covers
  this today) should be modeled.
- Whether HERMES-style role/process framing is wanted at all, or fully
  dropped given its weak fit for a content outline.
- Whether "Systems Integration" becomes its own `## H2` section in
  `sysrs` (free text, since no domain models it yet) or is deferred
  entirely to a later feature/domain — independently confirmed as a gap
  by INCOSE and MITRE SEG. **Verification is no longer part of this open
  question** (resolved 2026-08-31): the sibling `vcr` domain (feat-33)
  fills that gap, so `sysrs`'s `## Verification` is now designed as a
  `vcr` cross-reference list (`example.v5.md`), the same shape as every
  other section — see the updated Domain-to-source mapping table and
  Dependencies.
- Whether ISO/IEC/IEEE 29148 §9.5's own 19-subclause requirement-category
  taxonomy (vs. INCOSE's five-word scheme) should inform `## System Requirements`'s grouping, and whether `ISO_24765.md` (the vocabulary
  standard, added alongside the full `ISO_29148.md` text) should ground a
  future `## Definitions`/`## Acronyms` section — both added 2026-08-31,
  see Design Notes item 1's correction and Task 0.10/0.11.

**Conversion method used for the MITRE guide (Task 0.5) and the INCOSE
SE Handbook (Task 0.8), for reproducibility:** `pandoc` cannot read PDF
directly (`pandoc --list-input-formats` has no `pdf` entry), so the
pipeline was
`pdftotext se-guide-book-interactive.pdf raw.txt` (poppler-utils; the
PDF only restricts editing, not copy/print, so no password was needed) →
strip non-printable control characters (`\f` page breaks, stray `\x07`
bytes) with `tr` → `pandoc -f markdown-fancy_lists -t gfm --wrap=none`
to normalize into clean GFM. The `-fancy_lists` extension is explicitly
disabled: pandoc's default `markdown` reader treats a line like `(781) 271-2000` as an ordered-list marker `(781)` and **silently renumbers
it** on the next such line (verified: a two-line repro turned `(703)`
into `782)`), which would corrupt numbers throughout the body text.
Quality spot-checked against the "Develop System-Level Technical
Requirements" and "Concept of Operations" articles — prose reads
cleanly and a real table of contents is preserved; page-number/header/
footer noise from the original layout remains interspersed (expected,
not worth cleaning further for a read-only research reference). An
`pdftohtml`-based alternative was tried first and rejected: it emits
almost no real `<hN>` heading tags (one `<h1>` in a 30-page test) and
wraps everything in absolutely-positioned `<div>`s that produce far
noisier markdown than the plain-text route.

**Task 0.8 (INCOSE SE Handbook) run notes:** same pipeline, applied to
`INCOSE Systems Engineering Handbook 5e 2023.pdf` (370 pages, not
password-protected) → `incose-se-handbook-5e-2023.md`. This PDF had a
wider set of stray control bytes than the MITRE guide's: besides `\f`/
`\x07`, found 154 `\x08` (backspace) artifacts — all inside the table
of contents, where a run of dot-leader characters collapsed to a single
backspace between a TOC entry title and its page number — plus one each
of `\x1e`/`\x1f` inside a single cost-effectiveness formula (`CE = SE / (IC × SC)`, Blanchard 1967), where `pdftotext` mis-decoded a
math/multiplication-symbol glyph from the PDF's embedded font as a
control byte; all four were stripped the same way (`tr -d`). No
ordered-list-marker corruption found on spot-check (verified the
"History of Changes" version table's `1.0`/`2.0`/`2.0A`/`3.0`/`3.1`
sequence round-tripped intact, and the "What Is Systems Engineering?"
body prose in Section 1.1 reads cleanly with citations intact). As with
the MITRE guide, no real `#`/`##` heading tags are produced (plain-text
input carries no font-size/bold signal for pandoc to infer headings
from) — this is expected and acceptable for a read-only research
reference, not a document meant to be parsed structurally.

**Implementation design (added 2026-09-01, Phases 1–6)**

Phase 0 is complete; this subsection is the implementation plan the
Task List's Phases 1–6 execute. Everything below that is marked
"preliminary" gets empirically validated against the live `models/md`
engine in Phase 1 (a throwaway /tmp scratch script, vcr's Phase 0
discipline) **before** any Pydantic model code is written in Phase 2 —
the outcomes (pass + exact mechanics) are recorded back into this
subsection and the preliminary sketch refined accordingly.

**Confirmed frontmatter shape** (Decisions Made 2026-09-01):
`SysrsFrontmatter(MarkdownFrontmatter)` — `type: Literal["sysrs"] =
"sysrs"`; the closed 5-value status set
`frozenset({"draft", "review", "approved", "active", "retired"})`,
default `"draft"`, mirroring `sop`'s shipped set
(`sop/models/v1/frontmatter.py`) including its GOL/DEC error-message
pattern. Semantics: `draft` = being written; `review` = under review
by the responsible authority; `approved` = signed off; `active` =
currently in force, the specification of record for the system;
`retired` = no longer in force, kept for reference.

**Confirmed cross-reference bullet shape + per-section type-tag
regex** (Decisions Made 2026-09-01): every cross-reference section's
bullet text must fullmatch the per-section pattern
`<ALLOWED-TYPE-TAG(S)> <lowercase-8-4-4-4-12-hex-uuid>: <title>` —
mirroring the shipped `vcr` precedent (`_VERIFIES_PATTERN` in
`vcr/models/v1/body.py`; copy its exact uuid-fragment style:
`[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`,
anchored `^...$`, `re.fullmatch`). Per-section allowed type tags:

| cross-reference section | allowed type tag(s) |
|---|---|
| `### Goals` (under `## Business Context and Goals`) | `GOL` |
| `### Problem Statement` (under `## Business Context and Goals`) | `PRB` |
| `## Stakeholder Needs and Elicitation` | `QA` |
| `## Operational Concept and Scenarios` | `UC` |
| `## Decisions` | `DEC` or `ADR` (real `sysrs` documents may cross-reference either `dec` or `adr` ids — 2026-08-30 decision) |
| `## Risks` | `RSK` |
| the nine `## Requirements` H3s | `REQ` |
| the six `## Other Characteristics` H3s | `REQ` |
| `## Verification` | `VCR` |

The indented notes paragraph (the `MarkdownListItemWithNotes` shape)
is free text, per-bullet optional; `rsk`'s initial/residual
probability-impact coordinates + strategy fold into the notes prose
(decided 2026-08-31). **Semantic live validation** (that the
uuid/title actually matches the referenced document) is **out of v1** —
same as every other domain's cross-references today.

**Section order** (binding — field declaration order = markdown order;
full M/O flags, content types, and the 29148 §9.5 mapping table live
in `example.v7.md`, and the worked content in `sysrs-example.md`):

| # | H2 (in order) | M/O | content |
|---|---|---|---|
| 1 | `System Purpose` | M | free-text leaf |
| 2 | `System Scope` | M | free-text leaf |
| 3 | `Business Context and Goals` | M | container: `### Business Context` (O, leaf), `### Goals` (M, GOL list), `### Problem Statement` (O, PRB list) |
| 4 | `Stakeholder Needs and Elicitation` | O | QA list directly under the H2 |
| 5 | `Operational Concept and Scenarios` | O | UC list directly under the H2 |
| 6 | `Decisions` | O | DEC/ADR list directly under the H2 |
| 7 | `Risks` | O | RSK list directly under the H2 |
| 8 | `Assumptions and Dependencies` | O | free-text leaf (mixed prose+bullets) |
| 9 | `System Overview` | M | container: `### System Context` (M, leaf), `### System Functions` (M, leaf), `### User Characteristics` (O, leaf), `### System Integration` (O, leaf) |
| 10 | `System Modes and States` | O | free-text leaf |
| 11 | `Requirements` | M | container, ≥1 of the nine H3s present (each O, ≥1 item when present, REQ list): `Functional Suitability`, `Performance Efficiency`, `Compatibility`, `Interaction Capability`, `Reliability`, `Security`, `Maintainability`, `Flexibility`, `Safety` (canonical 25010:2023 order) |
| 12 | `Other Characteristics` | O | umbrella: `Physical Characteristics`, `Environmental Conditions`, `Information Management`, `Policy and Regulation`, `System Life Cycle Sustainment`, `Packaging, Handling, Shipping and Transportation` (each O, ≥1 item when present, REQ list) |
| 13 | `Verification` | O | VCR list directly under the H2 |
| 14 | `References` | O | plain bullet list (no notes, no specmgr ids, no type-tag regex) |
| 15 | `More Information` | O | free-text leaf |
| 16 | `Appendix` | O | free-text leaf (may carry fenced code blocks) |
| 17 | `Definitions and Acronyms` | O | free-text leaf |
| 18 | `Updates` | O, last | dynamic timestamp-led H3 entries (post-sibling DEC/VCR shape) |

("list directly under the H2" = the list sits in the H2's own body, no
`###` sub-heading — the 2026-08-30 "drop the redundant single H3"
decision; those five sections are H2-level list classes
(`MarkdownSection2`), the `### Goals`/`### Problem Statement` and the
fifteen REQ-list sections are H3-level (`MarkdownSection3`).)

**Preliminary model-class sketch** (for `sysrs/models/v1/body.py`;
**Preliminary — to be empirically validated against the live
`models/md` engine in Phase 1 before Phase 2 writes Pydantic code
(vcr precedent)**; one section subclass per heading; implicit
SPACE_SEPARATED aliases unless LITERAL is noted — LITERAL is required
wherever the heading carries a lowercase "and" or a comma, the same
pinning `sop` uses for `Safety and Precautions`):

- `Sysrs(MarkdownSection1)` — `@alias(value=r"^System Requirements Specification: .+$", type=AliasType.REGEX)` (the mandated H1 prefix — unlike every other domain's free-form H1, this one constrains it); the 18 fields in the section-order table's binding markdown order: `system_purpose`, `system_scope`, `business_context_and_goals` (mandatory — plain non-`Optional` types), `stakeholder_needs_and_elicitation | None`, `operational_concept_and_scenarios | None`, `decisions | None`, `risks | None`, `assumptions_and_dependencies | None`, `system_overview` (mandatory), `system_modes_and_states | None`, `requirements` (mandatory), `other_characteristics | None`, `verification | None`, `references | None`, `more_information | None`, `appendix | None`, `definitions_and_acronyms | None`, `updates | None`.
- Opaque free-text leaves (DEC-`Context`/sop-`Purpose` shape: no declared nested fields; any body content — paragraphs, bullets, fenced code blocks): `SystemPurpose` (M), `SystemScope` (M), `BusinessContext` (O, H3), `AssumptionsAndDependencies` (O, LITERAL), `SystemContext` (M, H3), `SystemFunctions` (M, H3), `UserCharacteristics` (O, H3), `SystemIntegration` (O, H3), `SystemModesAndStates` (O, LITERAL), `MoreInformation` (O), `Appendix` (O), `DefinitionsAndAcronyms` (O, LITERAL).
- `BusinessContextAndGoals(MarkdownSection2)` — LITERAL; mandatory container; `business_context: BusinessContext | None`, `goals: Goals` (mandatory), `problem_statement: ProblemStatement | None`.
- `SystemOverview(MarkdownSection2)` — mandatory container; `system_context: SystemContext`, `system_functions: SystemFunctions`, `user_characteristics: UserCharacteristics | None`, `system_integration: SystemIntegration | None`.
- The cross-reference list classes — `Goals` (H3, `GOL`), `ProblemStatement` (H3, `PRB`), `StakeholderNeedsAndElicitation` (H2, LITERAL, `QA`), `OperationalConceptAndScenarios` (H2, LITERAL, `UC`), `Decisions` (H2, `DEC|ADR`), `Risks` (H2, `RSK`), plus the nine `## Requirements` H3s and six `## Other Characteristics` H3s (all `REQ`; LITERAL pins on `PolicyAndRegulation` and `PackagingHandlingShippingAndTransportation` — lowercase "and" and commas). Each: `items: list[MarkdownListItemWithNotes] = Field(min_length=1)` (≥1 item when present — absent is the section's own `| None`, present-with-zero-items must raise `AssertionError`) + a per-class `field_validator("items")` regex-checking each item's `.text` (the `MarkdownListItem` computed property holding the lead paragraph with the marker stripped — the exact item-text field name, confirmed from `models/md/markdown_list_item.py`; Phase 1 re-confirms that a list-level validator sees it) against the section's own module-level pattern, e.g. `_GOALS_PATTERN = r"^GOL [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}: .+$"` (vcr's `_VERIFIES_PATTERN` fragment style); `Decisions`'s pattern allows `(DEC|ADR)`. The item's `notes` field (`list[MarkdownParagraph] | None`, declared on `MarkdownListItemWithNotes`) holds the optional per-bullet indented notes paragraph (free text).
- `Requirements(MarkdownSection2)` — mandatory container; nine `| None` H3 fields in canonical 25010:2023 order + a `model_validator(mode="after")` asserting at least one of the nine is present — a present-but-empty `## Requirements` is a **structural** violation, so the validator asserts (raises `AssertionError`), unlike DEC's duplicate-option-number after-validator, which raises `ValueError` into the `ValidationError` channel (Phase 1 confirms the engine mechanics for "≥1 of N optional children").
- `OtherCharacteristics(MarkdownSection2)` — optional umbrella; six `| None` H3 fields; **no** ≥1-of-N validator (the whole umbrella is optional — "omit if none of the six apply").
- `References(MarkdownSection2)` — optional; `items: list[MarkdownListItem] = Field(min_length=1)` — the plain no-notes variant (external standards/documents, no specmgr ids, no per-item regex). Present ⇒ ≥1 item required (user-confirmed 2026-09-01 — a bare heading with zero bullets is a structural error; see the resolved question below).
- `Updates(MarkdownSection2WithComment)` + `UpdateEntry(MarkdownSection3)` — the locked post-sibling shape (feat-38-39-41-43-44 D2/D3, adopted from day one — see Dependencies), mirroring `dec`'s/`vcr`'s `## Updates` as it exists on `dev` after that feature's Phases 1–2: `UpdateEntry` with a timestamp-led REGEX alias `^\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2}\.\d{3}(Z|[+-]\d{2}:\d{2}))?(?: - | : ) .+$` (date-only or full date+time lead, then ` - ` or ` : `, then title — em-dash separators rejected), mandatory `content: MarkdownParagraph`, plus the computed `timestamp` field the sibling feature adds to DEC/VCR's entries; `Updates` with `updates: list[UpdateEntry] = Field(min_length=1)`, optional as a whole, last section, and a `model_validator(mode="after")` newest-first ordering check delegating to the shared `models/md/_ordering.py::validate_newest_first` helper once it exists on `dev` (the FEAT precedent `feat/models/v1/body.py::Updates._validate_newest_first` — `assert`-based, so the structural `AssertionError` channel). If the sibling feature's Phase 2 has not merged by the time Task 2.3 runs, implement the identical ordering check as a domain-local validator in `sysrs/models/v1/body.py` (no `models/md` change) and switch to the shared helper when it lands. The inherited `comment` field stays absent in `sysrs-example.md` and carries the "newest first, prepend" ordering hint only in the packaged template.
- `SysrsFrontmatter`/`SysrsDocument`/`parse_sysrs`/`SysrsSummary` — per the confirmed frontmatter shape above and sop's document/parser/summary shapes (`SysrsSummary(DocSummary)` plain: id/title/status/ref, no extras).
- **Error channels** (codebase convention, no new exception types): structural → engine `AssertionError` (missing/unknown/misordered sections, zero-item list sections, zero-H3 `## Requirements`, H1 prefix mismatch, a `## Updates` entry heading failing its timestamp-led alias, out-of-order `## Updates` entries, and — the engine's behavior to be pinned in Phase 1, Task 1.3(e) — a mandatory free-text section present with zero body content); value → `pydantic.ValidationError` (`status` outside the 5-set, `type` != `sysrs`, a cross-ref bullet failing its section's type-tag regex — the `field_validator` `ValueError` channel).

**Tools** (one module per tool, mirror `sop/tools/`/`vcr/tools/`;
**dispatch-only — no** `update_sysrs`/`set_status_sysrs`, ADR
36905d5b; **no** per-domain `delete_sysrs` either — deletion is the
generic `delete` tool with a `sysrs` adapter, feat-36-delete):
`create_sysrs` (fresh `uuid4`, `status="draft"` always,
`created`/`updated`=now via the shared `general/tools/_timestamps.py`
helper once it is on `dev` (feat-38-39-41-43-44 Phase 3), else the
current sop `datetime.now().isoformat(timespec="microseconds")`
pattern — tests assert system-owned/both-set, never the literal
format, `version=CURRENT_SCHEMA_VERSION`, filename
`sysrs-{id}-{slugify(body text)}.md`); `parse_sysrs(path)`;
`list_sysrs(max_results?, offset?)` (paged from day one, ADR ec9f5262,
inline `SysrsSummary`, skip-on-parse-failure); `get_sysrs(id, raw=False)`
(`raw=True` returns the frontmatter-stripped body text verbatim — the
text the generic `update`'s `begin`/`end` index into);
`get_sysrs_example()`/`get_sysrs_template()` (`read_packaged_text`);
`validate_sysrs(content, full=False)`.
Private helpers `_paths.py` (`SYSRS_TYPE_NAME = "sysrs"`,
`SysrsNotFoundError`), `_io.py`, `_lock.py`, `_write.py` — identical
shape to SOP/VCR's.

**Generic-tool dispatch** (REQ-011): `general/tools/update.py` gains
`_update_sysrs` (verbatim-shape port of `_update_sop`, using
`sysrs_lock`/`load_by_id`/`write_sysrs_file`/`SysrsNotFoundError`, plus
the range branch) + a `"sysrs"` entry in `_ADAPTERS` + `"sysrs"` in the
`type` `Literal[...]` + `SysrsDocument` in the return union (the
"eleven whole-body domains" becomes twelve); `general/tools/
set_status.py` gains `_set_status_sysrs` (same shape as
`_set_status_sop`; the public level rejects `superseded_by` for
`type="sysrs"` with the standard non-adr `ValueError`) + a `"sysrs"`
entry in `_ADAPTERS` + `"sysrs"` in `type`'s `Literal[...]` (twelve
domains becomes thirteen incl. `adr`); `general/tools/delete.py` gains
`_delete_sysrs` (mirror of `_delete_sop`: resolve via
`load_by_id`, take `sysrs_lock`, `Path.unlink` confined by
`assert_within`) + `"sysrs"` in `_DELETE_TYPES` and the `type`
`Literal[...]` (eleven becomes twelve; `adr` stays excluded) +
imports + the docstring count. All three modules' imports gain the
`sysrs.*` equivalents.

**Resources**: `specmgr://sysrs/schema` (JSON from packaged
`sysrs/data/sysrs_schema.json`), `specmgr://sysrs/example`,
`specmgr://sysrs/template` — exactly three; no `/{id}` (ADR
ddfb1109), no `/list` (ADR ec9f5262). Unlike `sop` (gained
`specmgr://rasci`) and `vcr` (gained `specmgr://dtais`), `sysrs`
introduces **no** new cross-cutting `general` resource: the
characteristic names its `create_sysrs` prompt needs come from the
existing `specmgr://iso25010` resource.

**Prompts**: `create_sysrs(topic)` and `update_sysrs(id,
instructions=None)` reading packaged `sysrs/data/sysrs_create_
instructions.md`/`sysrs_update_instructions.md` via `string.Template`
(standard "(not given — ask the user before making any change)"
fallback for `instructions`); mirror SOP/VCR. `create_sysrs`'s
narration: `list_sysrs` dedup-check first, then an explicit step to
read `specmgr://iso25010` for the nine canonical ISO/IEC 25010:2023
characteristic names + the REQ placement rule (a REQ bullet sits under
the H3 named by the FIRST item of the REQ's own `## Characteristics`),
then the `specmgr://sysrs/template`/`/example`/`/schema` starting-
point resources. `update_sysrs` must name the GENERIC `update`/
`set_status` tools with `type="sysrs"` (both whole-body and line-range
via `get_sysrs(id, raw=True)`).

**Packaged data**: `sysrs_example.md` — content = this folder's
(Task 0.12-migrated) `sysrs-example.md`, cleaned per the shipped-
example convention if the research differs (verify against
`sop/data/sop_example.md`'s comment-free body: no instructional
comments, only permanent structural anchors or realistic filled
annotations — note: `vcr/data/vcr_example.md` carries one stray HTML
comment, left untouched: other-domain data, out of scope); must
parse. `sysrs_template.md` — all-sections placeholder skeleton,
`status: draft`, conforming date+time frontmatter, every optional
cross-reference list populated (blind text + real-looking placeholder
UUIDs, per Task 4.2's explicit enumeration) so it round-trips through
`parse_sysrs` (SOP/VCR precedent), with the "newest first, prepend"
ordering-hint comment in its `## Updates` (the locked sibling-feature
template convention). `sysrs_create_instructions.md`/
`sysrs_update_instructions.md` — narrated `string.Template` flows.
`sysrs_schema.json` — generated copy (Task 4.4).

**Cross-cutting wiring**:

- `server.py`: add `sysrs` to the final import line (`from . import adr, dec, feat, general, gol, prb, qa, req, rsk, sop, sysrs, tsk, uc, vcr`)
  + module docstring (3 resources, 7 tools, 2 prompts, domain summary,
  explicit dispatch-only note) + every stale domain enumeration/count
  sentence (the `update`/`set_status`/`delete` domain counts, the "...
  and later `ac`" reservation sentence, the per-domain registration
  paragraphs).
- `pyproject.toml`: `"biz.dfch.specmgr.sysrs" = ["data/*.md", "data/*.json"]`
  under `[tool.setuptools.package-data]` (alphabetical slot: after
  `sop`, before `tsk`).
- `.pre-commit-config.yaml`: add `sysrs/models/v1` to the 12 existing
  `files:` globs (`specmgr-schema` + the 11 per-domain
  `specmgr-schema-*-package` hooks) + new `specmgr-schema-sysrs-
  package` hook (`--type sysrs --output-dir src/biz/dfch/specmgr/
  sysrs/data`).
- `.github/workflows/ci.yml`: one new step for
  `src/biz/dfch/specmgr/sysrs/data/sysrs_schema.json` mirroring the
  per-type packaged-copy steps (the all-types `docs/*_schema.json`
  step picks `sysrs` up automatically once registered in
  `_GENERATORS`).
- `AGENTS.md`: `sysrs/` bullet in the Status section; add `sysrs` to
  the "each register `tools`, `resources`, and `prompts`" enumeration,
  the `delete_*` stub list, and the validate-tool list; note that
  `sysrs` is dispatch-only with per-section type-tag regex
  enforcement.
- Root `README.md`: add `System Requirements Specification (SYSRS)` to
  the "At this time, we have these artifact:" list (after SOP, before
  TSK).
- Regenerate: `docs/MCP.md` (`specmgr mcp-docs`),
  `docs/GENERATED.md` + `docs/api/` (`specmgr docs`),
  `docs/sysrs_schema.json` (`specmgr schema`).

**Resolved question (recorded 2026-09-01, decided 2026-09-01):**

- `## References`'s cardinality when present — the question was open
  because `example.v7.md` flags it "OPTIONAL. Free-form bullet list"
  without the "at least 1 item when present" marker the cross-
  reference lists carry (the v7 list rule is scoped to cross-
  reference lists only). **DECIDED (user-confirmed 2026-09-01):
  present ⇒ ≥1 item required** — `items: list[MarkdownListItem] =
  Field(min_length=1)`, consistent with every other list section in
  the codebase (a bare heading with no bullets is useless); the may-
  be-present-with-zero-items shape exists only for `sop`'s RASCI
  `Support`/`Consulted`/`Informed`, a special case with its own
  explicit rationale that does not apply here; the "no references"
  case is already covered by the section being omittable
  (`OPTIONAL`).

**Commit discipline (binding for every phase)**: each phase ends with
one Conventional Commit, scope `sysrs` (e.g. `feat(sysrs): add models
and parser`). Include any hook-regenerated `docs/` files in the same
commit (the `specmgr docs`/`mcp-docs` pre-commit hooks trigger on
`src/` changes and regenerate `docs/GENERATED.md`+`docs/api/` by
filesystem scan — from Phase 2 on, `sysrs` modules will appear there
before `server.py` registers the domain in Phase 6; that is expected
and correct, same as every prior domain's build history). Record each
phase's commit hash in this README's "Related PRs / Commits" as it
lands (it stays "None yet." until the first phase commits).

### Related ADRs

- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: No `/{id}` resources for
  id-based reads (tool-only `get_<d>`)
- ec9f5262-9912-49d0-903f-fcfb54f28c13: Paged `list_<domain>` tool
  instead of a `/list` resource
- 36905d5b-8057-4294-8665-c7eed5534db0: Generic `update`/`set_status`
  dispatch tools — new domains use these from day one, no per-domain
  mutation tools
- 1af6787b-eaab-4e8f-888f-531c1e76c19d: Path-safety guards for the
  generic `delete` tool (feat-36-delete) — `sysrs` ships no per-domain
  `delete_sysrs` tool; it adds a `_delete_sysrs` adapter to the
  generic `delete` tool (REQ-011)

No new ADR is anticipated yet; revisit once the aggregation-model and
schema decisions above are finalized — if the "reference + AI-paraphrase"
pattern turns out to generalize beyond this one domain, it may warrant
its own ADR rather than living only in this feature's Design Notes.

### Task List

#### Phase 0: Research and outline definition

- [x] Task 0.1: Survey external standards/templates (29148, INCOSE,
  MIL-STD-961E, MITRE, HERMES, NASA SE Handbook) — depends on: none —
  status: done (2026-08-30)
- [x] Task 0.2: Capture research + open questions in this README —
  depends on: Task 0.1 — status: done (2026-08-30)
- [x] Task 0.5: Convert the locally-supplied
  `se-guide-book-interactive.pdf` (MITRE Systems Engineering Guide) to
  markdown via `pdftotext` + `pandoc` (see Design Notes' "Conversion
  method") for direct reading — output: `se-guide-book-interactive.md`
  in this folder — depends on: none — status: done (2026-08-30)
- [x] Task 0.6: Read the converted MITRE guide's system-specification-
  relevant sections and fold findings into this README's Design Notes —
  depends on: Task 0.5 — status: done (2026-08-30)
- [x] Task 0.3.1: Decide `sysrs`'s organizing principle for the section
  list — one `## H2` per source domain (as drafted in `example.v2.md`,
  the latest reviewed revision; see `example.md` for the first
  reviewed revision) vs.
  grouping by MITRE SE life-cycle stage (Concept Development →
  Requirements Engineering → Architecture → Design → Integration →
  Test) — this is a prerequisite for 0.3.2–0.3.5 below — depends on:
  Task 0.2, Task 0.6 — status: done (2026-08-31, REV 6/7: neither
  option — 29148 §9.5 clause structure with the BRS/StRS content
  borrowed up front, and `## Requirements` grouped by the nine
  ISO/IEC 25010:2023 product-quality characteristics; see
  `example.v7.md` and Decisions Made)
- [ ] Task 0.3.2: Decide the concrete `## H2` section list and which
  sections are mandatory vs. optional, walking through `example.v2.md`
  section by section (incl. whether Business Context and Problem
  Statement merge, whether a `qa` reference belongs at the sysrs level
  at all, whether requirements get grouped by INCOSE category, and
  whether a dedicated `## Traceability` section is needed or is
  redundant with per-section cross-reference lists) — depends on: Task
  0.3.1 — status: done (2026-08-31: the user approved the concrete
  H2/H3 list in `example.v7.md` (REV 7) — all PROPOSED
  mandatory/optional flags accepted (annotated "-- > OK"), plus
  `## Appendix` and `## Definitions and Acronyms` added as OPTIONAL free-form
  H2s; ACC-002 checked. Settled within it: Business Context + Problem
  Statement merge (H3s under one H2), `qa` belongs (Stakeholder Needs
  and Elicitation), requirements grouped by 25010:2023 characteristics
  (not INCOSE), no dedicated `## Traceability` (implicit via
  per-section cross-refs))
- [x] Task 0.3.3: Decide whether/how to model Verification and Test &
  Evaluation — free-text `## H2` now, omitted from `sysrs` v1 entirely,
  or stubbed as "not yet available" pending a future dedicated domain
  (see `example.v2.md`'s three options under that section) — depends on:
  Task 0.3.2 — status: done (2026-08-31, superseded by feat-33-vcr:
  `## Verification` is now a `vcr` cross-reference list, see
  `example.v5.md` and Decisions Made; formal sign-off still tracked via
  ACC-002)
- [x] Task 0.3.4: Decide whether Systems Integration gets its own
  `## H2` section or is deferred — same three options as Task 0.3.3,
  decided independently since Verification and Systems Integration may
  land on different answers — depends on: Task 0.3.2 — status: done
  (2026-08-31, REV 6: no own H2 — folded under `## System Overview` as
  `### System Integration`, free text, PROPOSED optional in
  `example.v7.md`)
- [x] Task 0.3.5: Decide whether HERMES-style role/process framing is
  wanted anywhere in `sysrs`, or dropped entirely given its weak fit as
  a content-outline source (per Design Notes item 5) — depends on: Task
  0.3.1 — status: done (2026-08-31: closed as dropped — no HERMES-style
  role/process framing in `sysrs`; the approved outline is
  29148/25010-based, and HERMES was already confirmed process/role-
  oriented rather than a content-outline source, Design Notes item 5)
- [x] Task 0.3.6: Decide the exact `RelatedArtifacts`-with-paraphrase
  cross-reference field shape — plain-text suffix on the existing
  bullet vs. a distinct structured sub-field — and whether any domain
  (e.g. `rsk`'s initial/residual probability-impact coordinates) may
  surface extra inline data without crossing into "full-content
  embedding" (REQ-003) — depends on: Task 0.2, Task 0.6 — status: done
  (2026-08-31 — already recorded in Decisions Made: bullets use
  `<TYPE> <uuid>: <title>` + a notes-paragraph paraphrase, `rsk`
  coordinates fold into the notes prose; this task line lagged behind
  those entries, corrected now)
- [x] Task 0.4: Re-verify MIL-STD-961E's structure against a primary
  source (currently unreachable) if it ends up informing the final
  outline — depends on: Task 0.3.2 — status: done (2026-08-31: closed
  as dropped — the approved outline (REV 7) does not draw on
  MIL-STD-961E, so there is nothing left to re-verify; the recalled
  notes stay flagged as such in Design Notes)
- [x] Task 0.7: ~~Fetch/convert/read MITRE's *Guide for Writing System
  Specifications* (PR 14-3372)~~ **replaced 2026-08-30, per explicit
  user instruction** — see Design Notes' note under item 4. MITRE
  PR 14-3372 remains unobtainable (403 over the web, no local copy
  supplied) and is no longer being pursued for this task slot. Instead:
  convert the user-supplied `INCOSE Guide for Writing Requirements 2019.pdf` to markdown via a delegated sub-agent, same `pdftotext` +
  `pandoc` pipeline as Tasks 0.5/0.8 — output:
  `incose-guide-writing-requirements-2019.md` in this folder — depends
  on: none — status: done (2026-08-30, conversion only; see Task 0.7b
  for reading it)
- [x] Task 0.7b: Read the converted INCOSE *Guide for Writing
  Requirements* (2019)'s relevant sections and fold findings into
  Design Notes item 2 (mirrors Task 0.6/0.9's treatment for the MITRE
  SEG guide/INCOSE Handbook) — in particular, check whether this is
  the "Guide to Writing Requirements" (GtWR) the Handbook cites for
  the "Function/Performance, Fit/Operational, Form, Quality,
  Compliance" categorization wording still flagged as unverified there
  — depends on: Task 0.7 — status: done (2026-08-31: skipped per user —
  "not needed at this time"; the approved outline (REV 7) groups
  requirements by 25010:2023 characteristics, so the INCOSE
  categorization question it was meant to settle is moot)
- [x] Task 0.8: Convert the user-supplied `INCOSE Systems Engineering Handbook 5e 2023.pdf` (370 pages) to markdown via `pdftotext` +
  `pandoc` (see Design Notes' "Conversion method" → "Task 0.8 run
  notes") for direct reading — output:
  `incose-se-handbook-5e-2023.md` in this folder — depends on: none —
  status: done (2026-08-30)
- [x] Task 0.9: Read the converted INCOSE SE Handbook's
  system-specification-relevant sections (mirrors Task 0.6 for the
  MITRE guide; delegated to a sub-agent given the file's size, ~5,900
  lines) and fold findings into Design Notes item 2 (INCOSE) —
  depends on: Task 0.8 — status: done (2026-08-30)
- [x] Task 0.10: Re-verify Design Notes item 1's ISO/IEC/IEEE 29148 SyRS
  outline directly against the now-locally-available full standard text
  (`ISO_29148.md`), correcting it if it doesn't match (mirrors Task 0.9's
  treatment for INCOSE) — depends on: none — status: done (2026-08-31;
  outline did not match — corrected, see Design Notes item 1's
  "Correction" note, §8.4/9.5/5.4/6.4.3 cited directly)
- [ ] Task 0.11: Decide whether/how `ISO_24765.md` (ISO/IEC/IEEE
  24765:2017, *Systems and software engineering — Vocabulary*, added to
  this folder alongside `ISO_29148.md`) grounds a future `## Definitions`/
  `## Acronyms` section (mirroring 29148 §9.2.3/9.2.5), or stays an
  unused reference — depends on: Task 0.3.2 — status: not-started
- [x] Task 0.12: Migrate `sysrs-example.md` to the locked sibling-
  feature conventions (feat-38-39-41-43-44, D2/D7) — both `## Updates`
  heading separators `—` → ` - ` (issue #38) and the frontmatter
  `created`/`updated` date-only → date+time midnight-UTC (`2026-08-30`
  → `2026-08-30 00:00:00.000Z`, `2026-09-14` → `2026-09-14
  00:00:00.000Z`, issue #44) — prerequisite of Task 1.4's full-
  document round-trip — depends on: none — status: done (2026-09-01,
  applied in the plan-review pass)

#### Phase 1: Empirical schema validation

- [ ] Task 1.1: Cross-reference list mechanics — read-only, in-memory
  validation of the approved shapes against the **live** `models/md`
  engine using a throwaway scratch script under /tmp (NOT committed,
  NOT a permanent test file — no `sysrs` model code exists yet): the
  `<TYPE> <uuid>: <title>` + indented-notes bullet shape via
  `MarkdownListItemWithNotes` (bullet with notes, bare bullet without
  notes, and the per-list regex enforcement approach — a
  `field_validator` over the `items` list checking each item's `.text`;
  confirm the exact item-text field name and that a list-level
  validator sees it); the three states of an optional list section
  (absent entirely vs. present-with-N-items via `Field(min_length=1)`
  vs. present-with-zero-items, which must raise `AssertionError` — how
  the "≥1 item when present" list rule is enforced); and `## References`
  as a plain `list[MarkdownListItem]` (no-notes variant — confirm the
  `MarkdownListItem` vs. `MarkdownListItemWithNotes` distinction works
  as intended) — depends on: none — status: not-started
- [ ] Task 1.2: Container mechanics — same discipline: (a) `##
  Requirements`, a mandatory section where at least ONE of the nine
  optional H3 children must be present (confirm the engine mechanics
  for "≥1 of N optional children", e.g. a `model_validator(mode="after")`
  on the container asserting ≥1; zero-H3 input must raise
  `AssertionError`); (b) `## Business Context and Goals` (mandatory
  container; optional free-text `### Business Context`; mandatory
  `### Goals` list; optional `### Problem Statement` list) and `##
  System Overview` (mandatory container; mandatory leaves `### System
  Context`/`### System Functions`; optional leaves `### User
  Characteristics`/`### System Integration`); (c) `## Other
  Characteristics` optional umbrella + six optional
  `Field(min_length=1)` H3 lists — depends on: Task 1.1 — status:
  not-started
- [ ] Task 1.3: Free-form and heading mechanics — same discipline: (a)
  the locked post-sibling `## Updates` shape (optional-as-a-whole,
  timestamp-led H3 titles with the alias `^\d{4}-\d{2}-\d{2}(?:
  \d{2}:\d{2}:\d{2}\.\d{3}(Z|[+-]\d{2}:\d{2}))?(?: - | : ) .+$`,
  newest-first `model_validator` ordering check) — confirm the
  alias+validator mechanics on `MarkdownSection3` entries and the
  `AssertionError` channel for both the alias failure (missing
  timestamp lead, em-dash separator) and an out-of-order pair; the
  FEAT precedent `feat/models/v1/body.py::Updates._validate_newest_
  first` is the reference — `example.v7.md`'s trailing answer comment
  is illustrative only (it predates the sibling feature and shows an
  em-dash); (b) fenced code blocks (```mermaid) inside
  opaque free-text leaves (they occur in `sysrs-example.md` under
  `### System Context` and `## Appendix`) — confirm the engine
  tolerates them in free-text sections; (c) a mixed prose+bullets
  free-text leaf (`## Assumptions and Dependencies` in
  `sysrs-example.md` has paragraphs AND bolded bullets) — confirm it
  parses as an opaque free-text leaf; (d) the H1 prefix regex
  `^System Requirements Specification: .+$` as the root class's REGEX
  alias; (e) a mandatory free-text leaf present with zero body content
  (e.g. a `## System Purpose` heading immediately followed by the next
  H2) — pin whether the engine raises `AssertionError` or accepts, and
  record the outcome (it feeds ACC-004/Task 2.5's matrix either way) —
  depends on: Task 1.2 — status: not-started
- [ ] Task 1.4: Full-document round-trip — validate the entire
  `sysrs-example.md` content (all 18 H2s in order, all 22 H3s, every
  cross-reference bullet against its section's allowed type tag)
  through a scratch in-memory model built on the live engine per the
  preliminary sketch in Design Notes — depends on: Task 1.3 — status:
  not-started
- [ ] Task 1.5: Record every outcome (pass + exact mechanics) in this
  README's Design Notes' "Implementation design" subsection and refine
  the preliminary model sketch accordingly — closes ACC-003; the
  scratch script stays under /tmp (uncommitted) — depends on: Task 1.4
  — status: not-started
- [ ] Task 1.6: Phase-end quality gate (ruff format/check, vulture,
  full unittest) + commit (the Design Notes outcome record only — no
  `sysrs` code exists yet, and the /tmp scratch script is never
  committed); update this README's Progress section — depends on:
  Task 1.5 — status: not-started

#### Phase 2: Models + parser (`sysrs/models/v1/`)

- [ ] Task 2.1: Package skeleton — `sysrs/__init__.py` (`from . import prompts, resources, tools`
  + registration docstring, per `sop`'s Task 0.1 shape), empty
  `sysrs/models/v1/`, `sysrs/tools/`, `sysrs/resources/`,
  `sysrs/prompts/`, `sysrs/data/` packages, and `tests/sysrs/`
  skeleton mirroring `tests/sop/` (`models/v1/`, `tools/`, `prompts/`,
  `resources/` + `__init__.py` files) — plus `sysrs/models/v1/_util.py`
  (`SCHEMA_COMMENT_VERSION = "v1"`) — depends on: Task 1.6 — status:
  not-started
- [ ] Task 2.2: `sysrs/models/v1/frontmatter.py` —
  `SysrsFrontmatter(MarkdownFrontmatter)`: `type: Literal["sysrs"] =
  "sysrs"`, the confirmed closed 5-value status set
  `draft`/`review`/`approved`/`active`/`retired` (default `draft`,
  GOL/DEC/SOP error-message pattern; Decisions Made 2026-09-01) —
  depends on: Task 2.1 — status: not-started
- [ ] Task 2.3: `sysrs/models/v1/body.py` — every section class per the
  (Phase 1-validated) Design Notes sketch: root `Sysrs` (H1 REGEX
  prefix alias, 18 fields in binding order), the opaque free-text
  leaves, the `BusinessContextAndGoals`/`SystemOverview`/
  `OtherCharacteristics` containers, all the cross-reference list
  classes
  (H2- and H3-level) with `items: list[MarkdownListItemWithNotes] =
  Field(min_length=1)` + per-class type-tag regex validator,
  `Requirements` with its nine optional H3 children + ≥1-of-9 after-
  validator,   `References` (plain `list[MarkdownListItem] =
  Field(min_length=1)` — present ⇒ ≥1 item, Decisions Made 2026-09-01),
  `Updates`/`UpdateEntry` per the locked post-sibling shape in Design
  Notes (timestamp-led alias, computed `timestamp`, newest-first
  ordering — the shared `models/md/_ordering.py` helper once it exists
  on `dev`, else the domain-local validator fallback) — **no**
  `models/md` engine changes; implement the mechanics Phase 1 recorded,
  not new ones — depends on: Task 2.2 — status: not-started
- [ ] Task 2.4: `sysrs/models/v1/document.py` (`SysrsDocument`),
  `parser.py` (`parse_sysrs` glue, two-error-channel convention),
  `summary.py` (`SysrsSummary` — plain id/title/status/ref),
  `models/v1/__init__.py` + `models/__init__.py` exports — depends on:
  Task 2.3 — status: not-started
- [ ] Task 2.5: Tests `tests/sysrs/models/v1/` mirroring
  `tests/sop/models/v1/` — `test_frontmatter.py` (status-set
  acceptance/rejection, `type` literal), `test_body.py` (alias
  acceptance/rejection incl. every LITERAL-vs-SPACE_SEPARATED pin; the
  full structural-violation matrix: unknown H2, missing mandatory H2,
  `## Requirements` with zero H3s, cross-ref list present with zero
  items, `## References` present with zero items, H1 prefix mismatch,
  misordering, second H1, content before H1; the per-section cross-ref
  regex matrix incl. wrong-type-tag
  rejection, `DEC`/`ADR` dual acceptance under `## Decisions` (and
  `REQ` rejection there), malformed-uuid/missing-title rejection, bare-
  bullet-without-notes acceptance; `## Updates` timestamp-led-H3
  acceptance (date-only and date+time leads, both ` - ` and ` : `
  separators) + em-dash-heading rejection + out-of-order rejection +
  zero-entry rejection + the empty-mandatory-leaf case pinned by Task
  1.3(e)), `test_parser.py` (ACC-004/ACC-
  005 matrix + full round-trip of `sysrs-example.md`'s content) —
  depends on: Task 2.4 — status: not-started
- [ ] Task 2.6: Phase-end quality gate (ruff format/check, vulture,
  full unittest) + commit; update this README's Progress section —
  depends on: Task 2.5 — status: not-started

#### Phase 3: Tools (`sysrs/tools/`) + generic-tool dispatch

- [ ] Task 3.1: **Sibling coordination checkpoint** — re-merge `dev`
  and check feat-38-39-41-43-44's merge status (Dependencies), re-
  verifying the mirror targets (`sop`/`vcr` helpers, the generic
  tools' current shape, whether `_timestamps.py`/`_ordering.py`/
  `_path_safety` guards are on `dev` yet) against the live tree —
  then: private helpers `sysrs/tools/_paths.py` (`SYSRS_TYPE_NAME =
  "sysrs"`, `SysrsNotFoundError`, wrappers over
  `general.tools._doc_paths`), `_io.py` (`read_sysrs`, `load_by_id`),
  `_lock.py` (`sysrs_lock`), `_write.py` (`write_sysrs_file`) —
  mirror SOP/VCR (plus the `_path_safety` guards in `get_sysrs` if
  the sibling's Phase 4 has landed) — depends on: Task 2.6 — status:
  not-started
- [ ] Task 3.2: The 7 tool modules + `tools/__init__.py` per Design
  Notes — `create_sysrs` (fresh `uuid4`, `status="draft"` always,
  `created`/`updated`=now via the shared `general/tools/_timestamps.py`
  helper if it is on `dev`, else the current sop microsecond pattern,
  filename `sysrs-{id}-{slug}.md`), `parse_sysrs(path)`,
  `list_sysrs(max_results?, offset?)` (paged from day one, ADR
  ec9f5262), `get_sysrs(id, raw=False)`, `get_sysrs_example`,
  `get_sysrs_template`, `validate_sysrs(content, full=False)` —
  **no** per-domain mutation tools (dispatch-only from day one, ADR
  36905d5b; deletion is the generic `delete` tool, REQ-011) — depends
  on: Task 3.1 — status: not-started
- [ ] Task 3.3: `"sysrs"` dispatch entries — **gated on the sibling's
  Phase 4 per the Dependencies execution order** (run it after that
  phase has merged to `dev`, or now + rebase on its merge — a
  mechanical conflict in the three files, not a semantic one) —
  `general/tools/update.py`:
  `_update_sysrs` adapter (verbatim-shape port of `_update_sop`) +
  `"sysrs"` in `_ADAPTERS` + in the `type` `Literal[...]` +
  `SysrsDocument` in the return union + import wiring; same for
  `general/tools/set_status.py` (`_set_status_sysrs`, rejects
  `superseded_by` with the standard non-adr `ValueError`) and
  `general/tools/delete.py` (`_delete_sysrs` mirroring `_delete_sop`,
  `"sysrs"` in `_DELETE_TYPES` and the `type` `Literal[...]`, imports,
  docstring count eleven→twelve) — depends on: Task 3.1 — status:
  not-started
- [ ] Task 3.4: Tests `tests/sysrs/tools/` — one module per tool +
  helper tests + `test_integration.py` (ACC-006 round-trip using the
  generic `update`/`set_status` tools with `type="sysrs"`, both whole-
  body and `begin`/`end` line-range branches); new test cases in
  `tests/general/tools/test_update.py`/`test_set_status.py`/
  `test_delete.py` covering `type="sysrs"` (ACC-009) —
  `get_sysrs_example`/`get_sysrs_template`
  mock-tested only this phase (the real packaged data files arrive in
  Phase 4) — depends on: Task 3.2, Task 3.3 — status: not-started
- [ ] Task 3.5: Phase-end quality gate (ruff format/check, vulture,
  full unittest) + commit; update this README's Progress section —
  depends on: Task 3.4 — status: not-started

#### Phase 4: Resources + packaged data + schema

- [ ] Task 4.1: `sysrs/data/sysrs_example.md` — content = this folder's
  (Task 0.12-migrated) `sysrs-example.md`, cleaned per the shipped-
  example convention if the research differs (verify against
  `sop/data/sop_example.md`'s comment-free body: no instructional
  comments, only permanent structural anchors or realistic filled
  annotations — note: `vcr/data/vcr_example.md` carries one stray HTML
  comment and is left untouched, other-domain data); must parse via
  `parse_sysrs` — depends on: Task 3.5 — status: not-started
- [ ] Task 4.2: `sysrs/data/sysrs_template.md` — all-sections
  placeholder skeleton, `status: draft`, conforming date+time
  frontmatter; populated exactly: one placeholder bullet each in
  `### Goals` (mandatory anyway), `### Problem Statement`, `##
  Stakeholder Needs and Elicitation`, `## Operational Concept and
  Scenarios`, `## Decisions`, `## Risks`, `## Verification`, and in
  every one of the nine `## Requirements` H3s and the six `## Other
  Characteristics` H3s (each a `REQ <uuid>: <title>` bullet reusing
  `sysrs-example.md`'s UUIDs, so template and example share the
  fictional story); one `## References` bullet; one-line blind text in
  every free-text leaf; `## Updates` with the "newest first, prepend"
  ordering-hint comment plus one placeholder entry — so it round-
  trips through `parse_sysrs` (SOP/VCR precedent) — depends on: Task
  3.5 — status: not-started
- [ ] Task 4.3: `sysrs/data/sysrs_create_instructions.md` + `sysrs_update_instructions.md`
  — narrated flows with `$topic`/`$id`/`$instructions` placeholders;
  `create` includes the `list_sysrs` dedup-check-first step and an
  explicit step to read `specmgr://iso25010` for the nine canonical
  ISO/IEC 25010:2023 characteristic names + the REQ placement rule
  before filling `## Requirements`; `update` names the GENERIC
  `update`/`set_status` tools with `type="sysrs"` (no per-domain tool
  shape anywhere) — depends on: Task 3.5 — status: not-started
- [ ] Task 4.4: `commands/schema.py` — `generate_sysrs_schema()`
  (mirror `generate_sop_schema`) + `_GENERATORS["sysrs"]`; run
  `specmgr schema --type sysrs` (writes `docs/sysrs_schema.json`) and
  `specmgr schema --type sysrs --output-dir src/biz/dfch/specmgr/
  sysrs/data` (packaged copy) — depends on: Task 3.5 — status:
  not-started
- [ ] Task 4.5: `sysrs/resources/` — `sysrs_schema.py`
  (`specmgr://sysrs/schema`, JSON from the packaged copy),
  `sysrs_example.py`, `sysrs_template.py`, `__init__.py` — exactly
  three `sysrs` resources, no `/{id}` (ADR ddfb1109), no `/list` (ADR
  ec9f5262) — depends on: Task 4.1, Task 4.2, Task 4.4 — status:
  not-started
- [ ] Task 4.6: Tests `tests/sysrs/resources/` (ACC-007: schema equals
  fresh `generate_sysrs_schema()`, example/template equal the packaged
  files byte-for-byte, example parses, template round-trips, exactly
  three registered) mirroring `tests/sop/resources/` +
  `tests/vcr/resources/`; plus the deferred real-packaged-data tool
  tests for `get_sysrs_example`/`get_sysrs_template` — depends on:
  Task 4.3, Task 4.5 — status: not-started
- [ ] Task 4.7: Phase-end quality gate (ruff format/check, vulture,
  full unittest) + commit; update this README's Progress section —
  depends on: Task 4.6 — status: not-started

#### Phase 5: Prompts

- [ ] Task 5.1: `sysrs/prompts/` — `create_sysrs.py`
  (`create_sysrs(topic)`), `update_sysrs.py` (`update_sysrs(id, instructions=None)`
  with the standard "(not given — ask the user before making any
  change)" fallback), `__init__.py` — both read their packaged
  instruction file via `string.Template` — depends on: Task 4.3 —
  status: not-started
- [ ] Task 5.2: Tests `tests/sysrs/prompts/` (ACC-008: substitution
  from packaged data, `list_sysrs` dedup-check-first, the
  `specmgr://iso25010` read-first step, generic-tool naming in
  `update_sysrs`, fresh-read-per-call + `FileNotFoundError` behavior)
  — depends on: Task 5.1 — status: not-started
- [ ] Task 5.3: Phase-end quality gate (ruff format/check, vulture,
  full unittest) + commit; update this README's Progress section —
  depends on: Task 5.2 — status: not-started

#### Phase 6: Cross-cutting registration

- [ ] Task 6.1: `server.py` — **re-merge `dev` first** (the sibling's
  Phase 4 Task 4.5 also edits the `server.py` docstring and
  `AGENTS.md`; rebase the enumeration edits below on the post-
  sibling text) — add `sysrs` to the final import line
  (`from . import adr, dec, feat, general, gol, prb, qa, req, rsk, sop, sysrs, tsk, uc, vcr`)
  + module docstring (3 resources, 7 tools, 2 prompts, domain summary,
  the dispatch-only/no-per-domain-mutation-tools note, the no-`/{id}`/
  no-`/list` paragraph) + every domain enumeration/count sentence that
  would otherwise go stale (the `update` "eleven whole-body domains"
  becomes twelve, the `set_status` "twelve domains" becomes thirteen,
  the `delete` eleven-domain count becomes twelve, the "... and later
  `ac`" reservation sentence, the per-domain
  registration paragraphs) — depends on: Task 5.3 — status:
  not-started
- [ ] Task 6.2: `pyproject.toml` — `"biz.dfch.specmgr.sysrs" = ["data/*.md", "data/*.json"]`
  package-data entry (alphabetical slot: after `sop`, before `tsk`) —
  depends on: Task 4.7 — status: not-started
- [ ] Task 6.3: `.pre-commit-config.yaml` — add `sysrs/models/v1` to
  the 12 existing `files:` globs (`specmgr-schema` + the 11 per-domain
  `specmgr-schema-*-package` hooks) + new `specmgr-schema-sysrs-
  package` hook (`--type sysrs --output-dir src/biz/dfch/specmgr/
  sysrs/data`) — depends on: Task 4.4 — status: not-started
- [ ] Task 6.4: `.github/workflows/ci.yml` — new packaged-copy drift
  step for `sysrs/data/sysrs_schema.json` mirroring the per-type
  steps (the all-types `docs/*_schema.json` step picks `sysrs` up
  automatically once registered in `_GENERATORS`) — depends on: Task
  4.4 — status: not-started
- [ ] Task 6.5: `AGENTS.md` — new `sysrs/` bullet in the Status section
  (domain-first layout, dispatch-only from day one, schema at
  `sysrs/models/v1/`, the per-section type-tag regex note, the cross-
  reference aggregation model, the `raw` param, deletions through the
  generic `delete` tool (`type="sysrs"`), 3 resources / 7 tools / 2
  prompts); update the "still missing" enumerations so `sysrs` joins
  the tools/resources/prompts registration list and the validate-
  tool list, and the `general/` bullet's `update`/`set_status`/
  `delete` "eleven whole-body domains" wordings become twelve —
  depends on: Task 6.1 — status: not-started
- [ ] Task 6.6: Root `README.md` — add `System Requirements Specification (SYSRS)`
  to the "At this time, we have these artifact:" list (alphabetical
  slot: after SOP, before TSK) — depends on: Task 6.1 — status:
  not-started
- [ ] Task 6.7: Regenerate `docs/MCP.md` (`specmgr mcp-docs`),
  `docs/GENERATED.md` + `docs/api/` (`specmgr docs`),
  `docs/sysrs_schema.json` (`specmgr schema`); verify all idempotent
  on a second run (ACC-011) — depends on: Task 6.1, Task 6.2 —
  status: not-started
- [ ] Task 6.8: Final quality gate (ruff format/check, vulture, full
  unittest, `specmgr unused-code`) + commit — depends on: Task 6.3,
  Task 6.4, Task 6.5, Task 6.6, Task 6.7 — status: not-started
- [ ] Task 6.9: Final verification pass — walk every ACC-004..ACC-012
  with concrete evidence (including a live `create_sysrs`→
  `get_sysrs`→`list_sysrs`→`update`(type="sysrs", whole-body AND line-
  range)→`set_status`(type="sysrs")→`validate_sysrs` run, not just
  unit tests, and the ACC-010 non-editable wheel check); update this
  README's Progress section; record the phase commit hashes in
  "Related PRs / Commits"; set this README's frontmatter `status` to
  `done` — depends on: Task 6.8 — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in
place; rely on git history (`git log -p` on this file) to recover what
was originally planned, rather than keeping a second copy of the task
around.

## Progress

### Current Status

**As of 2026-09-01 (plan-review fixes applied)**: A plan review
against the live codebase and the sibling feature
`.specmgr/feat/feat-38-39-41-43-44/README.md` (issues
#38/#39/#41/#43/#44 — design complete 2026-09-01, D1–D10 locked,
not yet implemented) found and fixed three things, recorded below
and in Decisions Made: (1) the delete story was stale — `sysrs` now ships
**7** MCP tools, not 8: the per-domain `delete_sysrs` stub is
dropped (no whole-body domain has a per-domain delete tool since
feat-36-delete) and `sysrs` instead adds a `_delete_sysrs` adapter
to the generic `delete` tool (REQ-008/REQ-011/ACC-006/ACC-009,
Tasks 3.2/3.3/3.4/6.1/6.5 updated, ADR 1af6787b added to Related
ADRs); (2) `sysrs` now adopts the sibling feature's locked
conventions from day one — the `## Updates` timestamp-led entry
shape (em-dash separators rejected, ` - `/`: ` separators, parse-
enforced newest-first ordering, `MarkdownSection2WithComment`
  container, ordering-hint comment in the template only) and the
  conforming frontmatter `created`/`updated` date+time form
  (`yyyy-MM-dd HH:mm:ss.fff` + `Z`/`±HH:mm`) — so no rework after its
  merge (Dependencies gained the coordination entry with the
  execution-order checkpoints — Phases 1–2 and Tasks 3.1/3.2
  parallel-safe now, Task 3.3 and Phase 6's `server.py`/`AGENTS.md`
  regions gated on its Phase 4; the Design Notes `Updates` sketch/
  error-channels/packaged-data/tools lines and Tasks 1.3/2.3/2.5/
  3.1/3.2/3.3/4.1/4.2/6.1 follow); Task 0.12 (done in this pass)
  migrated
`sysrs-example.md` to those conventions; (3) Phase 1 pins the
engine's behavior for a mandatory free-text section present with
zero body content (Task 1.3(e), ACC-004, Task 2.5), Task 4.2's
template content is now explicitly enumerated, and Task 4.1's
comment-free reference is `sop/data/sop_example.md` (`vcr/data/
vcr_example.md` carries one stray HTML comment, left untouched —
other-domain data). Every other technical claim in the plan was
re-verified against the code in this pass and held. Next action:
Phase 1.

**As of 2026-09-01**: Phase 0 complete; implementation broken down.
The approved section outline (`example.v7.md`, REV 7 — 18 H2s / 22
H3s, every heading annotated MANDATORY/OPTIONAL + content type, user-
approved 2026-08-31) and the filled-in reference document
(`sysrs-example.md`) are locked. Three 2026-09-01 user-confirmed
decisions closed the last open schema questions — the frontmatter
`status` vocabulary (the closed 5-set `draft`/`review`/`approved`/
`active`/`retired`, default `draft`, mirroring `sop`'s shipped set),
the per-section cross-reference bullet type-tag regex (`<TYPE>
<uuid>: <title>`, vcr's `_VERIFIES_PATTERN` uuid-fragment style;
allowed tags per section — `GOL`/`PRB`/`QA`/`UC`/`DEC|ADR`/`RSK`/
`REQ`×15/`VCR` — with semantic live validation out of v1), and
`## References`'s cardinality when present (≥1 item required). The Task
List's "Phase 1+" stub is replaced by the full breakdown: Phase 1
(empirical schema validation of the approved shapes against the live
`models/md` engine before any model code — vcr's Phase 0 discipline,
closes ACC-003), Phase 2 (models + parser), Phase 3 (tools + generic-
tool dispatch), Phase 4 (resources + packaged data + schema), Phase 5
(prompts), Phase 6 (cross-cutting registration). Requirements
extended (REQ-004 umbrella; REQ-005..REQ-014), acceptance criteria
extended (ACC-003 reworded, still unchecked; ACC-004..ACC-012 added),
Scope rewritten to the full-implementation split, and Design Notes
gained the "Implementation design (added 2026-09-01, Phases 1–6)"
subsection (confirmed shapes, the section-order table, the preliminary
model-class sketch flagged for Phase 1 validation, tools/resources/
prompts/packaged-data/cross-cutting wiring, commit discipline; the
one recorded open question on `## References` cardinality was resolved
the same day (present ⇒ ≥1 item required)). Next action: execute
Phase 1. Task 0.11 (ISO_24765 → `## Definitions and Acronyms`
grounding) is the only leftover from Phase 0 and stays open/non-
blocking — that section is free-form text either way.

**As of 2026-08-31**: Research done, outline defined, still Phase 0 —
no schema or code written yet. All six primary sources are surveyed
and, where primary text was available, directly read (29148/24765 via
`ISO_29148.md`/`ISO_24765.md`, MITRE SEG via
`se-guide-book-interactive.md`, INCOSE SE Handbook — findings in
Design Notes items 1–2 with confidence notes; the INCOSE source PDF
and its conversion were intentionally deleted afterward, the recorded
findings stand as-is). Local `dev` was merged into this branch on
2026-08-31: the sibling `feat-33-vcr` domain is now **fully shipped**
(models, parser, tools, resources, prompts — not just Phase 1), and
the `specmgr://iso25010`/`specmgr://dtais`/`specmgr://rasci`
resources plus staged release automation (v0.15.0) are on this branch
— `sysrs`'s `## Verification` cross-reference design now has its
dependency in place for real. Seven discussion-draft outline
revisions exist: `example.md` (REV 1) through `example.v7.md` (REV 7,
latest), plus one filled-in reference example with actual (fictional)
content for the same case, `sysrs-example.md` (added 2026-09-01) —
the document the future `get_sysrs_example` tool/resource is expected
to return. REV 1–4 were user-reviewed rounds; REV 5 a self-directed
cross-check pass; **REV 6 (user hand-edits) reorganized the outline
into its final shape** — 29148 §9.5 clause structure with the BRS/StRS
content borrowed up front, `## Requirements` grouped by the nine
ISO/IEC 25010:2023 characteristics, `### System Integration` folded
under `## System Overview`, `## References` restored, `## Overview`/
`## Traceability` dropped — settling Task 0.3.1 (organizing
principle) and Task 0.3.4 (Systems Integration). REV 7 applied the
2026-08-31 decisions (H1 prefix `^System Requirements Specification:
.+$`, no clause numbers in headings, canonical 25010 names/order,
title-case headings) and added a mandatory/optional flag + content-type
comment after every heading — **all approved by the user the same day**
(annotated "-- > OK"), with two further OPTIONAL free-form H2s added
(`## Appendix`, `## Definitions and Acronyms`) — closing Task 0.3.2 and ACC-002.
Tasks 0.3.5 (HERMES framing), 0.4 (MIL-STD-961E re-verification), and
0.7b (INCOSE GtWR read) were closed the same day as dropped/skipped, so
**Phase 0 is complete** (Task 0.11 — ISO_24765 → `## Definitions and Acronyms`
grounding — is the only non-blocking leftover). Four ISO 29148 outline
examples for the sibling document types (BRS/StRS/SyRS/SRS per
§9.3–9.6, committed in `bf0e703`) serve as reference material for the
borrowed-section content.

### Handoff to next session (read this first if you are a new session)

- **You are here for a reason**: this feature moved out of the shared
  main checkout into its own `git worktree` because another agent was
  concurrently working on `feat-30-sop` directly on `dev` in the main
  checkout (`/home/user/src/biz.dfch.SpecMgr`). Do **not** `cd` back into
  that main checkout and run git commands there on this feature's
  behalf — it's a different agent's live working directory. (This
  concern may be stale by now — re-check whether `feat-30-sop` has
  since merged — but don't assume the main checkout is free to use
  without checking first.)
- **Where you are**: worktree
  `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-32-sysrs`, branch
  `feat-32-sysrs`, originally branched from local `dev` (rebuilt clean
  at `4a4fc62`); local `dev` was merged in on 2026-08-31 (`0f2794d`,
  vcr fully shipped + v0.15.0 + release automation — 2,704 tests OK
  after the merge), so the branch now contains the full current dev
  tree plus this feature's docs. **Run `git status`/`git log
  --oneline` yourself before trusting any commit list** — as of this
  update (2026-09-01) the working tree is **clean** at `055fd2d`
  (`feat(feat-32): add design document` — all research artifacts,
  `example.md`…`example.v7.md`, `sysrs-example.md`, and the README
  state before this planning pass are committed). The plan-review
  pass's fixes (this README + the `sysrs-example.md` migration,
  Task 0.12) land in one further commit on top of it.
- **Folder history**: this feature folder was originally created as
  `feat-0-sysrs` (no GitHub issue yet) in the main checkout, then
  renamed to `feat-32-sysrs` and moved into this worktree/branch per
  explicit user instruction (branch name and folder name both use issue
  number 32). If you see any stray reference to `feat-0-sysrs` anywhere
  outside this README's own history, it's stale — the folder's live
  name is `feat-32-sysrs`.
- **INCOSE PDF/conversion — confirmed gone on purpose, not a bug**:
  `INCOSE Systems Engineering Handbook 5e 2023.pdf` and
  `incose-se-handbook-5e-2023.md` do **not** exist anywhere in this
  worktree or in git history (`git log --all` on both paths returns
  nothing) — this was discovered and confirmed with the user during
  this session's wrap-up: **intentional deletion**, not lost work. The
  findings already folded into Design Notes item 2 (INCOSE) stand as
  recorded and are not expected to be re-verified against the primary
  source again. Don't spend time searching for these files or asking
  the user to re-supply them unless something *new* about INCOSE needs
  checking.
- **Session transcripts**: re-verified 2026-09-01 — neither
  `session-ses_fac9-feat-32-00-design.md` (first session: initial
  research, MITRE SEG conversion, worktree-move discussion) nor
  `session-ses_fac6-feat-32-01-design.md` (second session: domain-key
  decision, Task 0.3 split, `example.md`/`example.v2.md` review
  rounds, INCOSE conversion/read) exists in this worktree or in its
  git history (`git log --all` on both paths returns nothing — the
  earlier "committed at `ad9e12f`"/"currently staged" claims in this
  bullet are stale). **This third session (H3 sub-heading decision,
  REV 3/REV 4 example review, the ADR/DEC and Updates/More Information
  decisions, this wrap-up) has no separate transcript export either** —
  this README's Recent Updates log is the only record of it, same as
  every other session gap so far. If the user exports one later, move
  it into this folder following the same
  `session-ses_*-feat-32-NN-*.md` naming/`git check-ignore`-at-nested-
  path pattern already used in other feature folders.
- **Immediate next action**: **execute Phase 1 (empirical schema
  validation)** per the new Task List (the Phases 1–6 breakdown added
  2026-09-01): read-only, in-memory validation of the approved shapes
  against the live `models/md` engine via a throwaway /tmp scratch
  script (NOT committed, NOT a permanent test file) — the cross-
  reference bullet mechanics, the container/optional-list mechanics,
  the `## Updates`/free-text/H1-prefix mechanics (including the
  locked post-sibling `## Updates` shape and the empty-mandatory-
  leaf pin, Task 1.3(a)/(e)), and a full `sysrs-example.md` round-
  trip (`sysrs-example.md` is already migrated to the locked
  conventions by the done Task 0.12) — recording every outcome in
  Design Notes' "Implementation design" subsection and closing ACC-
  003 **before Phase 2 writes any Pydantic model code** (mirrors
  `vcr`'s Phase 0 discipline). Reference artifacts: `example.v7.md`
  (the approved section list — its worked `## Updates` example is
  illustrative only, it predates the sibling feature) and
  `sysrs-example.md` (the filled-in content for the same case);
  Design Notes' preliminary model-class sketch is the starting point
  (flagged preliminary for exactly this phase). Non-blocking
  leftovers: Task 0.11 (ISO_24765 → `##
  Definitions and Acronyms` grounding).
- **Still open / unresolved**: Task 0.11 (whether/how `ISO_24765.md`
  grounds the new `## Definitions and Acronyms` section or stays an
  unused reference — non-blocking; the approved section is free-form
  text either way); optional cleanup of the `req` docstring's pre-2023
  example characteristic names (noted in `example.v7.md`'s header,
  out of scope); the sibling-feature execution-order checkpoints
  (Phases 1–2 and Tasks 3.1/3.2 parallel-safe now; Task 3.3 gated
  on the sibling's Phase 4 — or done now + rebased on its merge;
  Phase 6 re-merges `dev` at Task 6.1 for the `server.py`/`AGENTS.md`
  overlap — see Dependencies; the locked conventions are already
  adopted, so these are verification steps, not open design
  questions). **Settled and closed**: the Phase 1–6 implementation
  breakdown itself (2026-09-01 — the Task List's "Phase 1+" stub is
  replaced; the frontmatter `status` vocabulary and the per-section
  cross-ref type-tag regex decided the same day); `## References`'s
  cardinality when present (2026-09-01 — present ⇒ ≥1 item required,
  user-confirmed); Task 0.3.2 + ACC-002 (approved list in `example.v7.md` —
  all M/O flags accepted, Appendix/Definitions and Acronyms added),
  Task 0.3.5 (HERMES framing dropped), Task 0.4 (MIL-STD-961E
  re-verification dropped — the outline doesn't use it), Task 0.7b
  (INCOSE GtWR read skipped — not needed at this time). Also settled
  earlier (2026-08-31): organizing principle (Task 0.3.1 — 29148
  clause structure + 25010 categories), Systems Integration placement
  (Task 0.3.4 — `### System Integration` under `## System Overview`),
  `## Traceability`/`## Overview` (dropped), cross-reference field
  shape (Task 0.3.6, `<TYPE> <uuid>: <title>` + notes paraphrase).

### Blockers

None currently open. (Former Task 0.7 blocker — MITRE's *Guide for
Writing System Specifications*, PR 14-3372, unreachable over the web —
was resolved 2026-08-30 by replacing that task's source document
entirely, per explicit user instruction, rather than continuing to
wait on it; see Task List Task 0.7/Design Notes item 4's note.)

### Recent Updates

#### Update 2026-09-01 (plan-review fixes — 7 tools + generic delete adapter; locked sibling #38/#39/#44 conventions adopted from day one; Phase 1 pins extended)

- Completed: A plan review against the live codebase (vcr/sop
  models, the `models/md` engine, the generic `update`/`set_status`/
  `delete` tools, the pre-commit/CI/pyproject wiring, the shipped
  data files) and the sibling feature `feat-38-39-41-43-44`'s
  locked design found and fixed: (1) the stale delete story —
  REQ-008 now lists 7 tools (the `delete_sysrs` stub dropped; no
  whole-body domain has a per-domain delete tool since feat-
  36-delete), REQ-011/Task 3.3 gain the `_delete_sysrs` adapter in
  `general/tools/delete.py` (`_DELETE_TYPES`/`Literal`/imports/
  docstring count), ACC-006 drops the stub assertion, ACC-009 and
  Task 3.4 cover `tests/general/tools/test_delete.py`, and the
  Scope/Design Notes/Related ADRs/Task 6.1/6.5 wording follows suit
  (ADR 1af6787b added); (2) adoption of the sibling feature's
  locked conventions from day one (D1–D10 locked there 2026-09-01):
  the `## Updates` timestamp-led shape (em-dash rejected, ` - `/`: `
  separators, parse-enforced newest-first, `MarkdownSection2With
  Comment` container, ordering-hint comment in the template only)
  and the conforming frontmatter date+time format (`yyyy-MM-dd
   HH:mm:ss.fff` + `Z`/`±HH:mm`) — Dependencies gained the
   coordination entry with the execution-order checkpoints (Phases
   1–2 and Tasks 3.1/3.2 parallel-safe; Task 3.3 and Phase 6's
   `server.py`/`AGENTS.md` regions gated on its Phase 4, with
   Tasks 3.3/6.1 carrying the gate notes), the Design Notes
   `Updates` sketch/error-channels/packaged-data/tools lines were
   reworded, Tasks 1.3/2.3/2.5/3.1/3.2/4.1/4.2 updated,
  and new Task 0.12 (done in this pass) migrated `sysrs-example.md`
  (both Updates headings `—` → ` - `, frontmatter date-only →
  midnight-UTC date+time per D7); (3) Phase 1 pins the empty-
  mandatory-leaf engine behavior (Task 1.3(e), ACC-004, Task 2.5),
  Task 4.2's template content is explicitly enumerated (all nine +
  six H3s with one placeholder `REQ` bullet each, reusing the
  example's UUIDs), and Task 4.1's comment-free reference is
  `sop/data/sop_example.md` (the vcr example's one stray HTML
  comment is left untouched — other-domain data, out of scope).
  Every other technical claim in the plan was re-verified against
  the code in this pass and held.
- Next: Phase 1 (Tasks 1.1–1.6) — with the sibling-feature
  checkpoint recorded for before Phase 3.

#### Update 2026-09-01 (## References cardinality resolved — present ⇒ ≥1 item)

- Completed: The user confirmed the decision — `## References`'s
  cardinality when present is ≥1 item required, i.e. a bare
  `## References` heading with zero bullets is a structural error
  (`AssertionError`). The Design Notes open question was resolved in
  place (heading flipped to "Resolved question", the `References`
  sketch line updated); ACC-004 and Tasks 2.3/2.5 now name the
  `## References` zero-items rejection explicitly; Current Status and
  the Handoff's next-action/still-open bullets updated; a Decisions
  Made entry added. Implementation remains on hold per the user's
  2026-09-01 instruction — next action is still to execute Phase 1
  when the user says to continue.
- Next: unchanged — execute Phase 1 (empirical schema validation) per
  the Task List, once the user lifts the hold.

#### Update 2026-09-01 (implementation broken down — Phases 1–6; status set + per-section cross-ref regex decided)

- Completed: Two user-confirmed schema decisions recorded in Decisions
  Made: (1) the frontmatter `status` closed 5-value set
  `draft`/`review`/`approved`/`active`/`retired` (default `draft`),
  mirroring `sop`'s shipped set; (2) per-section cross-reference
  bullet type-tag regex enforcement (`<TYPE> <uuid>: <title>`, vcr's
  `_VERIFIES_PATTERN` uuid-fragment style; the allowed-tag mapping
  `GOL`/`PRB`/`QA`/`UC`/`DEC|ADR`/`RSK`/`REQ`×15/`VCR`; semantic live
  validation out of v1). The Task List's "Phase 1+" stub is replaced
  by the full implementation breakdown — Phase 1 (empirical schema
  validation of the approved shapes against the live `models/md`
  engine, vcr's Phase 0 discipline, closing ACC-003), Phase 2 (models
  + parser), Phase 3 (tools + generic-tool dispatch), Phase 4
  (resources + packaged data + schema), Phase 5 (prompts), Phase 6
  (cross-cutting registration) — each with per-task dependencies and a
  phase-end gate task. Requirements extended (REQ-003/REQ-004
  reworded; REQ-005..REQ-014 added), acceptance criteria extended
  (ACC-003 reworded to the new numbering, still unchecked;
  ACC-004..ACC-012 added), Scope rewritten from the planning-pass
  split to the full-implementation split, Dependencies gained the
  `vcr`-regex/`sop`-status/`specmgr://iso25010` precedents, and Design
  Notes gained the "Implementation design (added 2026-09-01, Phases
  1–6)" subsection (confirmed frontmatter shape, the cross-ref regex
  decision + allowed-tag mapping table, the 18-H2/22-H3 section-order
  table, the preliminary model-class sketch flagged for Phase 1
  validation, the tools/resources/prompts/packaged-data/cross-cutting-
  wiring bullets, commit discipline, one open question on
  `## References` cardinality). Frontmatter `status` is now
  `in-progress`; Handoff's git-status/next-action/still-open bullets
  re-verified against the current tree (clean at `055fd2d`).
- Next: execute Phase 1 (Tasks 1.1–1.6) per the new Task List —
  nothing before it is open except the non-blocking Task 0.11 and the
  one recorded `## References` open question.

#### Update 2026-09-01 (sysrs-example.md added — filled-in reference example with actual content)

- Completed: At the user's request, wrote `sysrs-example.md` — the
  first filled-in `sysrs` document: the approved REV 7 section list
  (`example.v7.md`) instantiated with actual (fictional) content for
  the same "Example Widget Platform" case used by `example.md` …
  `example.v5.md` and the `iso-29148-*` companion examples. No
  discussion-draft comments, no MANDATORY/OPTIONAL flags: real
  frontmatter (`created`/`updated` consistent with its own `## Updates`
  entries) + body — H1, all 18 H2s in approved order, all 22 H3s
  present and filled,
  cross-reference bullets in the settled `<TYPE> <uuid>: <title>` +
  one-line notes-paragraph shape (REV 5's already-established UUIDs
  reused verbatim where the same artifact is referenced; the rest
  newly invented, all fictional), and DEC/VCR-style `## Updates`
  carrying the two entries from REV 7's own worked example. Serves as
  the reference artifact for Phase 1 — the document the future
  `get_sysrs_example` tool/resource is expected to return, and the
  concrete worked input for the `models/md` empirical verification.
  Scope, Current Status, and Handoff updated to point at it.
- Next: unchanged — break down Phase 1 and empirically verify the
  approved section shapes against the `models/md` engine, using
  `sysrs-example.md` as the worked input.

#### Update 2026-08-31 (example.v7.md approved — section list final, ACC-002; Tasks 0.3.5/0.4/0.7b closed)

- Completed: The user reviewed `example.v7.md`, approved all 38
  PROPOSED mandatory/optional flags (annotated "-- > OK" on each —
  normalized to bare MANDATORY/OPTIONAL comments in the file), and
  added two new OPTIONAL free-form H2s (`## Appendix`,
  `## Definitions and Acronyms`, with purpose comments) — closing Task 0.3.2 and
  ACC-002 (REQ-002 decided; the approved 18-H2/22-H3 list in
  `example.v7.md` is the schema's basis for Phase 1). Answered the
  file's two inline TODOs: the exact REQ cross-reference format
  (`- REQ <uuid>: <title>` bullet + optional indented notes-paragraph
  paraphrase, with worked examples) under `## Requirements`, and the
  `## Updates` shape (H3 entries with free-form date-led titles +
  prose, with a two-entry worked example) at the end of the file.
  Closed per user direction: Task 0.3.5 (HERMES framing dropped),
  Task 0.4 (MIL-STD-961E re-verification dropped — the outline doesn't
  use it), Task 0.7b (INCOSE GtWR read skipped — not needed at this
  time). **Phase 0 is now complete** (only non-blocking leftover:
  Task 0.11, ISO_24765 → Abbreviations grounding). Current Status,
  Handoff (immediate next action = break down Phase 1), Task List,
  Decisions Made, and the v7 header all updated to record the
  approval.
- Next: break down Phase 1 (models/parser, then tools/resources/
  prompts/registration) mirroring `feat-30-sop`'s phase structure with
  `vcr` (now on this branch) as the newest precedent; empirically
  verify the section shapes against the `models/md` engine before
  writing Pydantic models.

#### Update 2026-08-31 (example.v7.md added — REV 6 reviewed, organizing principle settled, concrete section list with proposed mandatory/optional comments)

- Completed: Reviewed the user's hand-edited `example.v6.md` (REV 6)
  against REV 5, the recorded decisions, 29148 §9.5, and the
  `specmgr://iso25010` resource, and wrote `example.v7.md` (REV 7, new
  file per the never-edit-in-place convention) applying the decisions
  agreed in review: H1 prefix now `^System Requirements
  Specification: .+$` (supersedes REV 2's `^System Specification:
  .+$`); the `(9.5.x)` clause numbers removed from the headings
  (traceability annotations only, mapping table in v7's header); the
  nine Requirements H3s ordered per the canonical ISO/IEC 25010:2023
  model (resolves REV 6's TODO); heading casing normalized to title
  case. REV 6's structural changes carried over as-is: `### System
  Integration` folded under `## System Overview`, `## Other Quality
  Requirements` renamed to `## Other Characteristics`, `## References`
  restored, `## Overview`/`## Traceability` dropped. Every heading in
  v7 now carries a PROPOSED: MANDATORY/OPTIONAL + content-type comment
  for the user to pick from, plus the agreed rules: optional
  cross-reference sections (GOL/PRB/QA/UC/DEC/ADR/RSK/REQ/VCR) must
  have ≥ 1 item when present, and a REQ's placement under a 25010/
  Other-Characteristics H3 is determined by the FIRST item of that
  REQ's own `## Characteristics` section (free text in the shipped
  `req` schema — no `req` change, near-names resolved by the agent).
  Settled as a result: Task 0.3.1 (organizing principle — 29148 clause
  structure + 25010 categories), Task 0.3.4 (Systems Integration →
  `### System Integration` under System Overview), Task 0.3.6
  (task line synced with the already-recorded decision); Task 0.3.2
  now in-progress with the user's M/O pick as the only remaining step.
  Design Notes item 1 gained a Resolution note; Current Status and
  Handoff rewritten to the new state.
- Next: the user's pick on `example.v7.md`'s PROPOSED comments (see
  Handoff → Immediate next action), then ACC-002 sign-off and Phase 1
  planning.

#### Update 2026-08-31 (dev merged — vcr fully shipped, v0.15.0, release automation)

- Completed: Merged local `dev` (= `origin/dev` @ `9eb7e8a`) into
  `feat-32-sysrs` (merge commit `0f2794d`; the uncommitted README edits
  were stashed across the merge and restored). 14 commits landed:
  `feat(33)` — the VCR domain **complete** (models, parser, all 8
  tools, resources, prompts, tests; not just Phase 1), `feat(30)` SOP
  domain, the `specmgr://iso25010`/`specmgr://dtais`/`specmgr://rasci`
  general resources, staged release automation (`scripts/release.sh`,
  `/release` command, release SOP), v0.15.0 version bump, CI/
  pre-commit updates. Post-merge: `uv sync --all-extras --frozen`
  (env now 0.15.0) and the full test suite — 2,704 tests OK.
- Next: `sysrs`'s `## Verification` cross-reference design now has its
  `vcr` dependency fully in place on this branch; Phase 1 can model
  against `vcr`'s shipped `<TYPE> <uuid>: <title>` id shape for real.

#### Update 2026-08-31 (ISO 29148 outline examples added — BRS/StRS/SyRS/SRS per §9.3–9.6)

- Completed: Added four new discussion-draft examples, one per
  specification document type the ISO/IEC/IEEE 29148:2018 norm gives a
  normative content outline for: `iso-29148-brs-example.md` (§9.3, 18
  sections), `iso-29148-strs-example.md` (§9.4, 18),
  `iso-29148-syrs-example.md` (§9.5, 18 + 9 nested under System
  overview / System operations / Physical characteristics), and
  `iso-29148-srs-example.md` (§9.6, 19 + 9 nested under Product
  perspective). Convention in all four: section names are verbatim
  from the standard (the norm's mandatory outline, clause number in
  each heading); the standard's descriptive text is paraphrased into
  HTML guidance comments, never quoted verbatim (the full standard
  text stays gitignored); and the section bodies carry concrete
  fictional example content — all four form one consistent BRS → StRS
  → SyRS → SRS chain for the same "Example Widget Platform" case used
  by `example.md`…`example.v5.md`, with the SRS zooming onto the Key
  Issuance Service product. The §x.x.1 "overview" subclauses are
  omitted (meta-text about the clause, not document content).
- Next: use these as filled-in reference examples when finalizing the
  tailored `sysrs` outline (Tasks 0.3.1/0.3.2) — §9.5's actual 18+
  subclause content is now available as a worked example, not just as
  the summarized taxonomy in `example.v5.md`'s changelog.

#### Update 2026-08-31 (example-example-inc.md added — data-grounded companion example from an external project)

- Completed: At the user's request, examined `~/src/example-acme` (an
  external, already-populated specmgr-style project: example-inc, the
  planned replacement for the legacy production-control system
  "example-inc" used by the Example Inc) to judge
  whether a "fully fledged" `sysrs` example could be built from real
  data, then wrote `example-example-inc.md` doing exactly that. Judgment:
  partially — `example-acme` has real, specmgr-authored `qa` (1 large
  document), `uc` (54 documents, mostly still stubs), and `req` (80
  short documents) artifacts, but **no `gol`/`prb`/`dec`/`rsk`/`vcr`
  artifacts at all**. Populated the corresponding H2 sections
  (Goals/Problem Statement/Architecture and Design Decisions/Risks/
  Verification) from real narrative source material in that project
  (`Ausschreibungsgegenstand.md`'s Ziel/Nutzen/Ausgangslage,
  `Bewertungregeln.md`'s real TS/ZK acceptance methodology,
  `summary-example-acme.md`'s make-or-buy/risk analysis,
  `img/jwt-flow-1.plantuml`'s OIDC flow) but cross-referenced with
  illustrative, obviously-fake ids for those five domains, clearly
  flagged as such throughout. Discovered mid-task that `example.v5.md`
  had landed concurrently in this same folder (a different session's
  work) — rebased `example-example-inc.md` from `example.v4.md`
  conventions onto REV 5's (real `<TYPE> <uuid>: <title>`
  cross-reference shape, `vcr`-backed `## Verification`, DEC/VCR-style
  `## Updates`) before finalizing, to avoid shipping an already-stale
  illustration.
- Next: get the user's reaction to `example-example-inc.md`, in
  particular whether the "real ids for qa/uc/req, illustrative-flagged
  ids for gol/prb/dec/rsk/vcr" approach is an acceptable way to handle
  a source project with partial domain coverage, and whether this kind
  of external-data cross-check should become a standard step before
  Task 0.3.1/0.3.2 are finalized. Does not itself resolve Task 0.3.1
  (still the actual next priority, unchanged).

#### Update 2026-08-31 (example.v5.md added — cross-checked against ISO_29148.md/ISO_24765.md and feat-33-vcr's shipped code)

- Completed: At the user's request, examined `example.v4.md` for gaps,
  inconsistencies, and improvements, considering both the now-locally-
  available full ISO/IEC/IEEE 29148:2018 standard text (`ISO_29148.md`,
  plus `ISO_24765.md`, the vocabulary standard — both added to this
  folder since the last research pass) and the sibling `feat-33-vcr`
  ("Verification Case Record") feature, which is being built concurrently
  in its own worktree/branch and has already shipped its Phase 1
  (`vcr/models/v1/`, schema + parser + tests). Read `feat-33-vcr`'s
  README and actual model source (not just its plan text) directly.
  Findings, all folded into Design Notes/Decisions Made/Task List/Not
  yet decided above and applied to a new `example.v5.md`:
  - Design Notes item 1's recorded ISO/IEC/IEEE 29148 SyRS outline (a
    5-part "Introduction/Requirements/Verification/Supporting
    information/References" shape) does **not** match the standard's
    actual normative SyRS content clause (§9.5, 19 sub-clauses) — it was
    recorded before the full standard text was available locally.
    Corrected with exact clause citations (new Task 0.10, done).
  - `feat-33-vcr` exists specifically to fill the "Verification/Test and
    Evaluation" gap this feature's own research identified, and its
    Phase 1 is complete — `## Verification and Test Planning` renamed to
    `## Verification` and reshaped into a `vcr` cross-reference list
    (closes Task 0.3.3; `## Systems Integration`/Task 0.3.4 is
    unaffected, still open).
  - `example.v4.md`'s cross-reference bullets used the same
    illustrative, unenforced, hyphenated pseudo-id style already shipped
    in `gol`/`dec`'s own examples (`GOL-0007`-ish codes); `feat-33-vcr`
    independently audited this exact question for its own `## Verifies`
    field and settled on a real, regex-enforced `<TYPE> <uuid>: <title>`
    shape — adopted here too, closing REQ-003. Also discovered and fixed
    a REV 4 bug in the process: every cross-reference bullet's "inline
    title" was literally the placeholder text `+ title`, never an actual
    title, despite REV 4's own changelog claiming otherwise.
  - `## Updates`'s plan ("reuses `feat.Updates`/`UpdateEntry` exactly")
    was never actually achievable (different heading-level base classes)
    and, more importantly, both `dec` (shipped) and `feat-33-vcr`
    (in-flight, same H2/H3 level as `sysrs`) independently use a
    free-form-title, optional-as-a-whole shape instead of `feat`'s
    stricter one — `sysrs` now follows that precedent instead.
  - Minor: `## More Information`'s precedent citation corrected from "a
    level-shift from `req`/`feat`'s H3" to "`dec`/`vcr`'s own H2 shape
    directly" (the closer, already-correct-level precedent).
  - New open questions added: whether/how 29148 §9.5's own richer
    requirement-category taxonomy should inform `## System Requirements`'s grouping (alongside INCOSE's five-word scheme); how
    `ISO_24765.md` might ground a future Definitions/Acronyms section
    (new Task 0.11); `## Traceability`'s options, now with 29148's named
    "Requirements Traceability Matrix" (RTM) concept as concrete
    grounding for a matrix-view option.
- **`example.v5.md` has not yet been reviewed by the user** — unlike REV
  2/REV 4 (which applied specific user review comments), REV 5 is a
  self-directed cross-check pass done at the user's request to "find
  gaps, inconsistencies and improvements," not a response to inline
  annotations on a prior revision. Flagged prominently in Handoff.
- Next: get the user's reaction to `example.v5.md`, in particular
  whether the `## Verification`-as-`vcr`-cross-reference approach and
  the `<TYPE> <uuid>: <title>` id-format switch are acceptable, then
  continue with Task 0.3.1 (still the actual next priority, unchanged).

#### Update 2026-08-30 (Task 0.7 replaced — INCOSE Guide for Writing Requirements converted)

- Completed: Per explicit user instruction, replaced Task 0.7's source
  document. The old target, MITRE's *Guide for Writing System
  Specifications* (PR 14-3372), stays unobtainable (403 over the web,
  no local copy ever supplied) and is no longer being pursued for this
  task slot. The user supplied a local copy of INCOSE's own *Guide for
  Writing Requirements* (2019 revision) in this folder instead
  (`INCOSE Guide for Writing Requirements 2019.pdf`, owner-read-only
  permissions). Converted it to `incose-guide-writing-requirements-2019.md`
  (1,437 lines/~319 KB) via a delegated sub-agent, using the same
  `pdftotext` + `pandoc -f markdown-fancy_lists -t gfm --wrap=none`
  pipeline as the two prior conversions in this folder. This PDF
  needed **no** control-character stripping at all (a first — the
  MITRE SEG guide needed `\f`/`\x07` stripped, the INCOSE Handbook
  needed a wider `\x08`/`\x1e`/`\x1f` set); the ordered-list-marker-
  corruption spot-check passed cleanly. Marked Task 0.7 done
  (conversion only) and split off a new Task 0.7b (not started) to
  actually read it and fold findings into Design Notes item 2 —
  flagged that this document is plausibly the "Guide to Writing
  Requirements" (GtWR) the INCOSE Handbook cites for the still-
  unverified "Function/Performance, Fit/Operational, Form, Quality,
  Compliance" categorization wording (vs. the Handbook's own plainer
  "function, fit, form, quality, and compliance", confirmed in Task
  0.9). Cleared the former Task 0.7 entry from Blockers.
- Next: Task 0.7b (read the new conversion, fold findings in) is
  available whenever wanted, but is not itself blocking Task 0.3.1,
  which remains the actual next priority (see Handoff).

#### Update 2026-08-30 (session wrap-up — context limit reached)

- Completed (this session, full arc): explained the H3-sub-heading
  pattern in `example.v2.md`, then applied the user's "drop it when
  there's exactly one list" decision as `example.v3.md`; explained the
  ISO/IEC/IEEE 29148 "Verification" section and the four verification
  methods (Inspection/Analysis/Demonstration/Test — flagged as recalled
  from training, no single standardized acronym, not re-verified this
  session); reviewed the user's own edits to `example.v3.md` (inline
  titles, ADR→DEC rename, `## References`/`## More Information`/
  `## Updates` additions), resolved the open points interactively, and
  snapshotted the result as `example.v4.md` (restoring the "never edit
  in place" convention `example.v3.md` had broken for one round). All
  decisions recorded in Decisions Made/Design Notes. During wrap-up,
  discovered and confirmed with the user that the INCOSE PDF/`.md`
  conversion were intentionally deleted (not lost work) — Current
  Status and Handoff updated accordingly.
- **This session is being wrapped up here due to context-window
  limits, not because the work is done** — Task 0.3.1 is still the
  immediate next action (unchanged from before this session started;
  this session was all groundwork/example-review, not the organizing-
  principle decision itself). See "Handoff to next session" above for
  the full current git-status picture (staged vs. further-modified vs.
  untracked) before doing anything else — don't assume the summary
  there is still accurate without running `git status` yourself first,
  the same caveat every prior wrap-up has carried.
- Next: a new session should (1) run `git status` to confirm the
  handoff summary above, (2) decide with the user how to split the
  accumulated uncommitted changes across commits (nothing has been
  committed since `ad9e12f`, across two full sessions now), then
  (3) proceed with Task 0.3.1 interactively using `example.v4.md`.
  Optional hygiene suggestion, carried over from the previous wrap-up
  and still not acted on: "Recent Updates" has accumulated many entries
  all dated the same day — consider running the `compact_history`
  prompt (`general/prompts/`) to rotate older ones into a sibling
  `history.md`.

#### Update 2026-08-30 (example.v4.md added — inline titles, dec-only illustration, Updates/More Information sections)

- Completed: `example.v3.md` was edited in place (breaking the "new
  file per reviewed round" convention) to add `+ title` to some
  cross-reference bullets, rename an `ADR-...` example entry to
  `DEC-...`, and sketch new `## References`/`## More Information`/
  `## Updates` sections. Reviewed the edit with the user and resolved
  the open points: (1) inline titles apply to **every** cross-reference
  bullet, not just some — reverses `example.v2.md`'s "id-only" draft
  shape; (2) the ADR→DEC rename is a `sysrs`-example-illustration
  convention only, **not** a decision to deprecate the `adr` domain
  repo-wide; (3) `## Updates`'s entry heading reuses
  `feat.Updates`/`feat.UpdateEntry` (`feat/models/v1/body.py`) exactly
  — `{timestamp} — {title}` with em dash and newest-first ordering,
  one nesting level shallower than `feat`'s own `## Progress` →
  `### Updates` → `#### {timestamp} — {title}`; (4) restored the
  "never edit in place" convention by snapshotting the resolved state
  into a fresh `example.v4.md`, leaving `example.v3.md` untouched for
  history. Also clarified `## References`'s "loose bullet list" intent:
  a plain unstructured bullet list (no per-item id model), mirroring
  `feat`'s `#### Depends On`/`#### Blocks` (`MarkdownSection4`, free
  markdown text, no `items: list[X]`), since references point outside
  specmgr and have no `id` to extract. Recorded all four decisions in
  Decisions Made/Design Notes.
- Next: continue Task 0.3.1/0.3.2 with the user using `example.v4.md`
  (the flagged-for-confirmation `## Related Artifacts` wrapper-drop
  question from `example.v2.md`'s changelog is still open).

#### Update 2026-08-30 (example.v3.md added — H3 sub-heading redundancy resolved)

- Completed: Walked through `example.v2.md` with the user, who flagged
  that several sections had a `### <Name>` sub-heading that just
  repeated (or barely reworded) their own H2's name (`## Risks` →
  `### Risks`, `## Architecture and Design Decisions` →
  `### Decisions`), since REV 2 had applied "every cross-reference list
  gets a named H3" uniformly without checking whether the name added
  information. Decided: drop the `### <Name>` sub-heading whenever an
  H2 holds exactly one list; keep it only where an H2 genuinely holds
  more than one distinct list or a mix of free text and a list (today,
  only `## Business Context and Goals`, which keeps its three H3s).
  Wrote `example.v3.md` applying this to `## Stakeholder Needs and Elicitation`, `## Operational Concept and Scenarios`,
  `## System Requirements`, `## Architecture and Design Decisions`, and
  `## Risks` — no other content changes from REV 2. Recorded the
  decision in Decisions Made and Design Notes.
- Next: continue Task 0.3.1/0.3.2 with the user using `example.v3.md`
  (the flagged-for-confirmation items from REV 2's changelog — the
  `## Related Artifacts` wrapper drop and the inline-title omission —
  are still open).

#### Update 2026-08-30 (session wrap-up — context limit reached)

- Completed (this session, full arc): domain key decided (`sysrs`);
  MITRE SEG and INCOSE SE Handbook both converted to markdown and read
  directly (Tasks 0.5/0.6, 0.8/0.9); Task 0.3 split into Tasks
  0.3.1–0.3.6; two discussion-draft outline revisions written and
  reviewed (`example.md` REV 1 with the user's inline comments,
  `example.v2.md` applying them — each new revision gets its own file,
  never edited in place, after an earlier in-session mistake overwrote
  `example.md` and had to be recovered from conversation history, see
  the "example.v2.md added" entry below). Design Notes, Decisions Made,
  and "Not yet decided" are all current as of this update.
- **This session is being wrapped up here due to context-window limits
  in the conversation, not because the work is done** — Task 0.3.1 is
  still the immediate next action (see "Handoff to next session"
  above), and there are real uncommitted changes on disk (this README
  plus the four new files listed in "Where you are" above) that a new
  session must not lose track of.
- Next: a new session should (1) confirm the uncommitted-files
  situation above is still accurate (`git status`), deciding whether to
  commit before or after further work, (2) read this README's Design
  Notes/Decisions Made/Not-yet-decided in full for context (no separate
  session-transcript export exists for this stretch of work, unlike the
  earlier worktree-move session — this README plus the on-disk files
  are the only record), then (3) proceed with Task 0.3.1 interactively
  with the user, using `example.v2.md`. Optional hygiene suggestion,
  not required: "Recent Updates" below has accumulated ~10 entries all
  dated the same day — consider running the `compact_history` prompt
  (`general/prompts/`) to rotate the older ones into a sibling
  `history.md` if this file's length becomes a problem for a future
  session's own context budget.

#### Update 2026-08-30 (INCOSE SE Handbook read — Task 0.9 done)

- Completed: Delegated a read of `incose-se-handbook-5e-2023.md`
  (~5,900 lines/1.2MB, no real markdown headings) to a research
  sub-agent, targeting six specific questions: whether Sections 2.3.5.2/
  2.3.5.3 name a concrete "System Requirements Specification"/SyRS
  output artifact; whether Appendices D/E (N2 diagram legend,
  input/output glossary) give document-content guidance; whether/how
  INCOSE cross-references 29148 for document structure; whether
  Section 3.2.3 gives a concrete traceability-matrix structure;
  whether Verification (2.3.5.9)/Integration (2.3.5.8) yield a
  document-content checklist for the two MITRE-identified gaps; and
  verifying the exact wording of the requirement categorization scheme.
  Findings folded into Design Notes item 2 (INCOSE) and into REQ-001's
  source list and the MITRE-guide bullet that had cited the same
  categorization: **no** SyRS/document-outline artifact exists anywhere
  in the Handbook (confirmed by full-text search); Appendices D/E are a
  process-dependency legend and a flat glossary, not a template;
  29148 is cited ~12 times but only for term/method definitions, never
  document structure; traceability guidance (bidirectional/vertical/
  horizontal, Section 3.2.3) is conceptual only, no matrix template;
  Verification/Integration processes have IPO output lists but no
  section-content checklist (same "confirmed gap" as MITRE, not new);
  and the categorization scheme's *verbatim* wording (Section 2.3.5.3,
  ~line 2232) is the plainer "function, fit, form, quality, and
  compliance" — the "Function/**Performance**, Fit/**Operational**"
  slash-compounds used elsewhere in this README are not supported by
  this primary source and are flagged as unverified (possibly
  conflated with the Guide to Writing Requirements/Needs and
  Requirements Manual, neither of which is in this converted file).
  Net effect: this primary-source read corroborated rather than
  extended prior secondhand INCOSE knowledge — it does not change the
  structural direction (29148-tailored + MITRE SEG life-cycle view
  remain the outline sources), but it does correct one piece of
  previously-unverified wording.
- Next: proceed with Tasks 0.3.1–0.3.6 using `example.v2.md`; no
  further action needed on INCOSE unless the GtWR/NRM sources
  mentioned above are later supplied for direct verification of the
  slash-compound categorization wording.

#### Update 2026-08-30 (INCOSE SE Handbook 5e 2023 converted)

- Completed: User supplied a local copy of the *INCOSE Systems
  Engineering Handbook, 5th Edition (2023)* (`INCOSE Systems Engineering Handbook 5e 2023.pdf`, 370 pages) in this feature folder
  — the actual primary source behind Design Notes item 2's INCOSE
  bullet points, which until now reflected recalled/secondary knowledge
  only. Converted it to `incose-se-handbook-5e-2023.md` (Task 0.8) via
  the same `pdftotext` + `pandoc -f markdown-fancy_lists -t gfm --wrap=none` pipeline used for the MITRE guide (see Design Notes'
  "Conversion method"). This PDF needed a wider control-character strip
  than the MITRE guide (`\x08`/`\x1e`/`\x1f` in addition to `\f`/
  `\x07` — see "Task 0.8 run notes" for what each artifact was).
  Quality spot-checked: no ordered-list-marker corruption (verified via
  the "History of Changes" version table and Section 1.1's opening
  prose), full 370-page range converted through to the closing Index.
  Not yet read section-by-section.
- Next: Task 0.9 — read the converted handbook's
  system-specification-relevant sections and fold findings into Design
  Notes item 2, same treatment as Task 0.6 did for the MITRE guide;
  then continue with Tasks 0.3.1–0.3.6.

#### Update 2026-08-30 (example.v2.md added — first user review of example.md)

- Completed: User reviewed `example.md` and left inline comments
  resolving several open points: H1 title is mandatory with prefix
  regex `^System Specification: .+$`; `## Overview` is mandatory but
  unrestricted markdown (not one paragraph); no bold pseudo-heading for
  cross-reference lists anywhere (`**RelatedArtifacts:**` banned, real
  `### <Name>` headings used instead, no `## Related Artifacts` wrapper
  needed since sysrs's H2s are already domain-specific); and a concrete
  cross-reference bullet shape (id-only bullet + loose "notes"
  paragraph carrying the paraphrase, title omitted). Wrote a **new**
  file, `example.v2.md`, applying all of the above, generalized
  consistently to every section (not just the one the user annotated) —
  `example.md` itself (REV 1, with the user's original inline comments)
  is left untouched on disk precisely so every reviewed revision stays
  independently comparable; this is now the standing convention for
  this artifact (new numbered file per round, never edit-in-place).
  Note: an earlier pass in this same session had mistakenly overwritten
  `example.md` in place with the REV 2 content, losing the user's
  original comments from disk (the file was never committed, so git
  history didn't help either) — recovered only because this
  conversation's own tool-call history still held the exact REV 1 text,
  which was rewritten back to `example.md` verbatim before `example.v2.md`
  was created. Also discovered that the new cross-reference shape maps
  directly onto `models/md`'s existing `MarkdownListItemWithNotes` class
  (already used by `gol`'s `Tags` section) — no new parser mechanics
  needed. Folded the resolved items into this README's Decisions
  Made/Design Notes, and added new "Not yet decided" items for the
  parts `example.v2.md` explicitly flags for confirmation
  (title-omission generalization, `## Business Context` sourcing,
  `rsk` coordinate placement, the `## Related Artifacts` wrapper drop).
- Next: get the user's reaction to `example.v2.md`, in particular the
  flagged-for-confirmation items in its changelog comment (points 3
  and 4), then continue resolving the remaining open questions (Tasks
  0.3.1–0.3.6).

#### Update 2026-08-30 (Task 0.3 split into Tasks 0.3.1–0.3.6)

- Completed: Split the remaining Task 0.3 work into six sequenced
  sub-tasks in the Task List: 0.3.1 (organizing principle — per-domain
  vs. MITRE life-cycle-stage grouping, prerequisite for the rest), 0.3.2
  (concrete `## H2` section list and mandatory/optional flags), 0.3.3
  (Verification/Test & Evaluation modeling), 0.3.4 (Systems Integration
  modeling), 0.3.5 (HERMES role/process framing), 0.3.6
  (`RelatedArtifacts`-with-paraphrase field shape). Task 0.4 now depends
  on Task 0.3.2 instead of the old singular Task 0.3. Updated all
  current-state references to the old Task 0.3 elsewhere in this README
  (Current Status, Handoff, Blockers) to point at the relevant
  sub-task(s); left dated historical Recent Updates entries from before
  the split untouched.
- Next: work through the sub-tasks in order with the user, starting
  with Task 0.3.1, using `example.md` as the discussion artifact for
  0.3.1/0.3.2.

#### Update 2026-08-30 (domain key decided; discussion-draft outline added)

- Completed: Decided the domain key is `sysrs` (dropping `sys`/`spec`/
  `sss` candidates) — recorded in Decisions Made. Wrote a discussion-draft
  document outline to `example.md` in this folder (not a schema, not
  wired into any tool/resource) to give the user a concrete artifact to
  react to for Task 0.3's section-list decision — sketches H2 sections
  tailored from the 29148/INCOSE/MITRE-SEG mapping table already in
  Design Notes, including `RelatedArtifacts`-style cross-references to
  `gol`/`prb`/`qa`/`uc`/`req`/`dec`/`adr`/`rsk`, and free-text stand-ins
  for the confirmed Verification and Systems Integration gaps.
- Next: walk through `example.md` with the user, section by section;
  fold agreed changes back into Design Notes/this README and, once
  approved, close ACC-002 and move to the cross-reference field shape
  (ACC-003).

#### Update 2026-08-30 (moved to dedicated worktree/branch; session wrap-up)

- Completed: Discovered another agent was concurrently working on
  `feat-30-sop` directly on `dev` in the shared main checkout
  (`/home/user/src/biz.dfch.SpecMgr`) — modified
  `general/tools/set_status.py`/`update.py`/`sop/tools/__init__.py`
  plus ~20 new untracked files under `sop/tools/`/`tests/sop/tools/`.
  No file overlap was found with this feature's own untracked additions
  (`.specmgr/feat/feat-0-sysrs/` at the time), but working directly in
  the shared checkout risked future collisions and made branch-level
  git operations unsafe (any `checkout`/`stash`/`reset` there would have
  disrupted the other agent's live work). Per explicit user instruction:
  created a new `git worktree` at
  `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-32-sysrs` on a new
  branch `feat-32-sysrs` (`git worktree add ... -b feat-32-sysrs dev`,
  based on local `dev` at `d2fa3e4`) — this command alone never touches
  the main checkout's HEAD/index/files. Moved (not copied) the
  then-`feat-0-sysrs` folder's contents into the new worktree, renamed
  it to `feat-32-sysrs` per the user's chosen branch/folder name
  (matching this repo's `feat-NNN-slug` convention, issue 32), updated
  the README frontmatter `id` to match, and committed
  (`87f53c3`) inside the new worktree only. Verified afterward that the
  main checkout was completely unaffected: still on `dev` at `d2fa3e4`,
  same pending file count as before the move, zero remaining `sysrs`
  references there.
- Next: this session is being wrapped up here; a new session will
  continue from this README's "Handoff to next session" section above,
  in this worktree, on this branch. Outstanding handoff item: move the
  user's session-transcript export (created on `dev`, not yet present as
  of this update) into this folder once it exists.

#### Update 2026-08-30 (session transcript moved in; session wrap-up complete)

- Completed: The user exported this session's transcript to the main
  checkout's repo root as `session-ses_fac9-feat-32-00-design.md`
  (gitignored there by design, per `.gitignore`'s root-anchored
  `/session-ses_*.md` pattern — the repo's normal export location).
  Moved it (not copied) into this worktree at
  `.specmgr/feat/feat-32-sysrs/session-ses_fac9-feat-32-00-design.md`
  (confirmed not ignored at this nested path), matching the naming
  convention already used by other feature folders, and committed it on
  `feat-32-sysrs`. Updated the "Handoff to next session" section above
  to mark this item resolved. This closes out the outstanding item from
  the previous update — the session wrap-up is now complete.
- Next: a new session should read this README's "Handoff to next
  session" section, then the session transcript for full narrative
  context, then proceed with Task 0.3.

#### Update 2026-08-30 (MITRE guide converted and read)

- Completed: Converted the user-supplied
  `se-guide-book-interactive.pdf` (MITRE Systems Engineering Guide, 726
  pages) to `se-guide-book-interactive.md` via `pdftotext` +
  `pandoc -f markdown-fancy_lists -t gfm` (pandoc has no native PDF
  reader; `-fancy_lists` disabled to prevent silent number corruption —
  see Design Notes for the full reproducible pipeline and why an
  `pdftohtml`-based alternative was rejected). Read the "Concept
  Development", "Requirements Engineering", "System Design and
  Development" sections directly and folded findings into Design Notes:
  MITRE's SE life-cycle building blocks (Concept Development →
  Requirements Engineering → System Architecture → System Design and
  Development → Systems Integration → Test and Evaluation →
  Implementation/O&M/Transition), IEEE 1362-1998 CONOPS critical
  components, the "System-Level Requirements Checklist", and the
  mission→operational→functional/system-requirements→design→
  verification traceability chain.
- Next: Task 0.3 — finalize domain key, concrete section list, and the
  cross-reference-with-paraphrase field shape with the user.

#### Update 2026-08-30 (MITRE guide added)

- Completed: User supplied a local copy of MITRE's Systems Engineering
  Guide (`se-guide-book-interactive.pdf`) in this feature folder, to be
  converted to markdown via `pandoc` so it can be read directly instead
  of relying on training recall or blocked web fetches.
- Next: Task 0.5 (pandoc conversion), then Task 0.6 (read + fold findings
  in), then Task 0.3 (finalize outline/domain key with the user).

#### Update 2026-08-30 (initial research)

- Completed: Surveyed ISO/IEC/IEEE 29148, INCOSE (SEBoK/NRM/GtWR),
  MIL-STD-961E (recalled, not freshly verified), MITRE (inaccessible over
  the web), HERMES (inaccessible/weak fit), NASA SE Handbook. Mapped
  concepts to existing specmgr domains. Captured two user decisions on
  aggregation model and outline direction.
- Next: Task 0.5/0.6 — read MITRE's guide directly; then Task 0.3 — nail
  down the concrete section list and domain key with the user.

### Decisions Made

- **2026-09-01**: `sysrs` adopts the sibling feature `feat-38-39-
  41-43-44`'s locked conventions (issues #38/#39/#44, D1–D10 locked
  there 2026-09-01) from day one — the `## Updates` timestamp-led
  entry shape (em-dash separators rejected, ` - ` or ` : `
  separators, parse-enforced newest-first ordering,
  `MarkdownSection2WithComment` container with the ordering-hint
  comment in the template only) and the conforming frontmatter
  `created`/`updated` date+time form (`yyyy-MM-dd HH:mm:ss.fff` +
  `Z`/`±HH:mm`, three-digit milliseconds) — rationale: `sysrs`
  mirrors exactly the `dec`/`vcr`/shared-frontmatter surfaces that
  feature changes, so waiting for its merge would only defer the
  same shape and risk rework; `sysrs-example.md` was migrated to the
  conventions in the same pass (Task 0.12, done); checkpoint before
  Phase 3 (re-merge `dev`, re-verify mirror targets — the sibling's
  Phases 1–4 touch the same `general/tools` files).
- **2026-09-01**: `sysrs` ships **7** MCP tools, not 8 — the per-
  domain `delete_sysrs` stub is dropped and deletion goes through
  the generic `delete` tool (feat-36-delete, ADR 1af6787b), to
  which `sysrs` adds its own `_delete_sysrs` adapter (REQ-011) —
  rationale: the plan's 8-tool list predated feat-36's convention
  change; no whole-body domain (sop/vcr included) has a per-domain
  `delete_*` tool anymore, and ADR 36905d5b's new-domain
  convention explicitly says "one `delete` adapter in the generic
  `delete` tool ... not new ... `delete_<d>` tools".
- **2026-09-01**: `## References`'s cardinality when present — ≥1
  item required (`items: list[MarkdownListItem] =
  Field(min_length=1)`); a bare `## References` heading with zero
  bullets is a structural error (`AssertionError`). User-confirmed;
  rationale: consistent with every other list section in the
  codebase (a bare heading with no bullets is useless); the may-be-
  present-with-zero-items shape exists only for `sop`'s RASCI
  `Support`/`Consulted`/`Informed`, a special case with its own
  explicit rationale that does not apply here; the "no references"
  case is already covered by the section being omittable
  (`OPTIONAL`).
- **2026-09-01**: `sysrs` frontmatter `status` uses the closed 5-value
  set `draft`/`review`/`approved`/`active`/`retired` (default `draft`)
  — user-confirmed; rationale: mirrors `sop`'s shipped set
  (`sop/models/v1/frontmatter.py`) rather than inventing a new
  lifecycle vocabulary. Semantics: `draft` = being written; `review` =
  under review by the responsible authority; `approved` = signed off;
  `active` = currently in force, the specification of record for the
  system; `retired` = no longer in force, kept for reference.
- **2026-09-01**: Cross-reference bullet syntax is regex-enforced per
  list — user-confirmed; rationale: each cross-reference section's
  bullet text must fullmatch
  `<ALLOWED-TYPE-TAG(S)> <lowercase-8-4-4-4-12-hex-uuid>: <title>`,
  mirroring the shipped `vcr` precedent (`_VERIFIES_PATTERN` in
  `vcr/models/v1/body.py` — exact uuid-fragment style copied). Allowed
  tags per section: `### Goals` → `GOL`; `### Problem Statement` →
  `PRB`; `## Stakeholder Needs and Elicitation` → `QA`; `##
  Operational Concept and Scenarios` → `UC`; `## Decisions` → `DEC`
  or `ADR` (real `sysrs` documents may cross-reference either `dec` or
  `adr` ids, per the 2026-08-30 decision); `## Risks` → `RSK`; the
  nine `## Requirements` H3s and the six `## Other Characteristics`
  H3s → `REQ`; `## Verification` → `VCR`. The per-bullet indented
  notes paragraph stays free text (`rsk`'s probability/impact
  coordinates + strategy fold into the notes prose, decided 2026-08-
  31). Semantic live validation (that the uuid/title matches the
  referenced document) is out of v1 — same as every other domain's
  cross-references today.
- **2026-08-31**: The concrete `sysrs` section list is FINAL — the
  user approved `example.v7.md` (REV 7): all 38 per-heading
  MANDATORY/OPTIONAL flags accepted as written (user-annotated "-- >
  OK"; normalized to bare flags in the file), plus two new OPTIONAL
  free-form H2s added by the user (`## Appendix`, `## Definitions and Acronyms`);
  the file's two inline TODOs were answered in place (REQ
  cross-reference format + worked example under `## Requirements`;
  `## Updates` shape + worked example at the end). Closes Task 0.3.2
  and ACC-002, decides REQ-002; the approved 18-H2/22-H3 shape is the
  schema's basis for Phase 1.
- **2026-08-31**: Closed three Phase 0 tasks without doing their work,
  per user direction — Task 0.3.5 (HERMES-style framing dropped
  entirely from `sysrs`), Task 0.4 (MIL-STD-961E re-verification
  dropped — the approved outline does not draw on it), Task 0.7b
  (INCOSE *Guide for Writing Requirements* read skipped — "not needed
  at this time"; moot anyway, since the 25010:2023 grouping replaces
  the INCOSE categorization question). Phase 0 is now complete (Task
  0.11 is the only leftover, non-blocking).
- **2026-08-31** (REV 6/7 review): Section shape decisions for the
  `sysrs` outline — (a) mandated H1 prefix is `^System Requirements
  Specification: .+$`, superseding the REV 2 decision (`^System
  Specification: .+$`); the "(SyRS)" abbreviation stays out of the
  title; (b) the `(9.5.x)` clause numbers are traceability
  annotations only — schema section names are bare (real documents
  don't carry standard-internal numbering); (c) `## Requirements` is
  grouped by the nine ISO/IEC 25010:2023 product-quality
  characteristics in canonical model order (Functional Suitability,
  Performance Efficiency, Compatibility, Interaction Capability,
  Reliability, Security, Maintainability, Flexibility, Safety),
  replacing both 29148's per-subclause categories (§9.5.5–9.5.9) and
  INCOSE's five-word scheme; 29148's non-25010 requirement categories
  (§9.5.11–9.5.17) sit under the `## Other Characteristics` umbrella
  (user's REV 6 rename of "Other Quality Requirements"); §9.5.8
  (interfaces) lands in Compatibility/Interoperability, §9.5.9.4's
  content is absorbed into Compatibility/Flexibility; (d) dropped
  `## Traceability` (traceability lives implicitly in the per-section
  cross-reference lists — REV 1's option (a)) and `## Overview`
  (absorbed by `## System Purpose` up front + `## System Overview`
  later); `## References` restored; Systems Integration has no own H2
  — `### System Integration` under `## System Overview` (free text);
  (e) every OPTIONAL section whose content is a cross-reference list
  (GOL/PRB/QA/UC/DEC/ADR/RSK/REQ/VCR) must carry ≥ 1 item when
  present; (f) a REQ bullet's placement under a 25010/
  Other-Characteristics H3 is determined by the FIRST item of that
  REQ's own `## Characteristics` section — no change to the shipped
  `req` domain (its Characteristics list is free text); placement
  vocabulary = the nine canonical 25010:2023 names + the six
  Other-Characteristics clause names, case-insensitive exact match,
  near-names resolved by the agent (e.g. "Performance" → Performance
  Efficiency, "Portability" → Flexibility); rationale for (f): the
  user's words — "we live with that and hope the agent will handle
  that". All recorded in `example.v7.md`'s header comment; the
  PROPOSED mandatory/optional flags per heading in that file await
  the user's pick (Task 0.3.2).
- **2026-08-31**: `## Verification and Test Planning` renamed to
  `## Verification`, reshaped into a `vcr` cross-reference list —
  rationale: the sibling `feat-33-vcr` domain now exists specifically to
  model verification/test-and-evaluation content (a confirmed gap this
  feature's own research identified), and its Phase 1 (schema + parser)
  is complete, so there is no longer a reason for `sysrs` to carry a
  free-text stand-in for this section.
- **2026-08-31**: Cross-reference bullets use `<TYPE> <uuid>: <title>`
  (feat-33-vcr's settled real-id shape), not the `gol`/`dec`-style
  illustrative hyphenated pseudo-id — rationale: the old style was
  audited and found to be unenforced, meaningless illustrative text; the
  new shape matches the one real id format an explore-agent search
  actually found precedent for, and closes REQ-003's exact-field-shape
  question.
- **2026-08-31**: `## Updates` reshaped to mirror `dec`'s/`vcr`'s
  free-form-title, optional-as-a-whole shape instead of `feat`'s
  mandatory, timestamp-regex-enforced one — rationale: literal reuse of
  `feat.Updates`/`UpdateEntry` was never possible (different heading
  levels), and both the existing (`dec`) and in-flight (`vcr`) sibling
  domains at `sysrs`'s own H2/H3 nesting level independently chose the
  free-form/optional shape, not `feat`'s.
- **2026-08-30**: Cross-references to other domains will carry id +
  title + a very short agent-generated paraphrase, not embedded full
  content — rationale: avoids content drift between the System
  Specification and its source documents while still giving readers a
  quick sense of what's referenced without opening each document.
- **2026-08-30**: Section outline will be based on ISO/IEC/IEEE 29148's
  SyRS shape but tailored to specmgr's existing domains, not copied
  verbatim — rationale: 29148 is the actively maintained standard (vs.
  superseded IEEE 830/1233), and a verbatim import would include
  sections (e.g., "Logical database requirements", "Memory constraints")
  that don't map cleanly onto anything specmgr already models.
- **2026-08-30**: Domain key is `sysrs` (not `sys`/`spec`/`sss`) —
  rationale: keeps the "System Requirements Specification"/SyRS lineage
  visible in the key itself, consistent with how other domains'
  short keys map back to their source concept (e.g. `adr`, `rsk`), and
  avoids the genericness of `sys`/`spec` colliding in meaning with
  unrelated future domains.
- **2026-08-30**: Drop the `### <Name>` cross-reference sub-heading
  when an H2 holds exactly one list; keep it only where an H2 holds
  more than one distinct list (or a mix of free text and a list) —
  rationale: `example.v2.md` applied "every list gets a named H3"
  uniformly to every section, which produced sub-headings that just
  repeated their own H2's name with no added information (e.g. `## Risks` → `### Risks`); the rule now only earns its keep where it
  actually disambiguates multiple things under one H2 (currently just
  `## Business Context and Goals`).
- **2026-08-30**: Cross-reference bullets keep an inline title
  (`GOL-<id> + title`) after all, reversing `example.v2.md`'s draft
  "id-only" shape — rationale: consistent with `gol`/`dec`'s own
  existing `### Requirements`/`### Goals`/etc. lists, which already
  show the title inline today; dropping it would have been a
  regression in readability for no offsetting benefit once the
  `MarkdownListItemWithNotes` shape already accommodates a title
  in the lead line.
- **2026-08-30**: `## Architecture and Design Decisions`'s example
  entries reference `dec` only, not `adr` — scoped to this
  discussion-draft document's own illustrations, not a decision to
  deprecate the `adr` domain repo-wide (see Design Notes for the
  distinction).
- **2026-08-30**: Add `## Updates` (mandatory, newest-first,
  timestamped) and `## More Information` (optional, free text) as new
  `sysrs` sections, reusing `feat.Updates`/`feat.UpdateEntry`'s exact
  heading format and ordering validator rather than inventing a new
  shape — rationale: no reason to duplicate an already-built,
  already-tested class when `sysrs` needs the same "track changes to
  this document over time" capability `feat` already has.

### Related PRs / Commits

None yet.
