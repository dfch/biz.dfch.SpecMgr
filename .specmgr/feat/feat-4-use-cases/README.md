---
created: 2026-08-05
id: feat-4-use-cases
status: planning
updated: 2026-08-16
version: 1.7.0
---

# Feature: Create Use Cases with tool support

## Plan

### Overview

Create a Markdown schema for use cases based on Alistair Cockburn's template, with tools to validate the schema and generate PlantUML diagrams (UC and Sequence diagrams). This enables specification of system behavior in a structured, machine-readable format that can be visualized and validated.

### Requirements

- REQ-001: Define a Markdown schema for use cases based on Cockburn's template (Characteristic Information, Main Success Scenario, Extensions, Sub-Variations, Related Information)
- REQ-002: Validate Markdown use cases against the schema (structure, required fields, format)
- REQ-003: Generate PlantUML Use Case diagrams from validated use cases (showing actors and use case relationships)
- REQ-004: Generate PlantUML Sequence diagrams from use case scenarios (separate diagrams for main success path and each extension)
- REQ-005: Create MCP tools to support the workflow (parse, validate, generate diagrams)

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — Markdown schema defined with all Cockburn attributes; documented with examples
- [ ] ACC-002: Verifies REQ-002 — Validation tool checks required fields, format, and structure; rejects invalid use cases with clear error messages
- [ ] ACC-003: Verifies REQ-003 — UC diagram generator creates PlantUML code showing all actors and use cases with correct associations
- [ ] ACC-004: Verifies REQ-004 — Sequence diagram generator creates separate diagrams for main success path and each extension, showing actor-system interactions
- [ ] ACC-005: Verifies REQ-005 — MCP tools available for parse, validate, and generate operations; integrated into specmgr CLI/server

### Scope

**Included in this feature:**

- Markdown schema definition for use cases (based on Cockburn's template from https://www.cs.otago.ac.nz/coursework/cosc461/uctempla.htm)
- Pydantic models for use case structure (Characteristic Information, Main Success Scenario, Extensions, Sub-Variations, Related Information)
- Validation tool to check Markdown use cases against schema
- PlantUML UC diagram generator (actors and use case associations)
- PlantUML Sequence diagram generator (separate diagrams per scenario: main success + each extension)
- MCP tools for parse, validate, and generate operations
- CLI integration (specmgr uc-\* commands)

**Explicitly out of scope:**

- Rendering PlantUML to PNG/SVG (PlantUML server/CLI is external dependency)
- Activity diagrams (Sequence diagrams chosen as primary flow visualization)
- Use case editing UI (Markdown is the source format)
- Automatic diagram layout optimization (PlantUML handles this)

### Dependencies

- Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr` structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy), feat-5-md-model-parser (done, 2026-08-11) — Task 1.5 rebuilds the uc schema/models on its `models/md` engine
- Blocks: None identified yet
- External: PlantUML (for diagram rendering, not included in this feature)

### Design Notes

**Formal Schema Specification:**
Canonical (v2, current): `v2/uc_schema.json` for the complete JSON Schema definition, built on `uc/models/v2`'s `models/md`-engine-backed Pydantic models; `v2/uc-schema.md` for the narrative walkthrough; `v2/uc_reference_mdformat_class.puml` for the class diagram; `v2/uc_reference.md`/`v2/uc_reference_mdformat.md` for detailed example use cases. `v2/uc_reference_mdformat_schema.json` is a sibling artifact scoped to one specific worked example, not the general schema.

**Superseded (v1, historical only — do not use for current schema shape):** `v1/uc_schema.json`, `v1/uc-schema.md`, `v1/uc_class.puml`, `v1/uc_example-v1.md`. These describe the hand-written `uc/models/v1` parser and Cockburn's compound extension-action numbering (`3a1.`, `3a2.`, ...), both replaced by Task 1.5/DEC-010's rebuild onto `uc/models/v2`. Kept only for historical reference (e.g. git-blame context on why v2 looks the way it does), never as a current schema description.

**Markdown Schema Design:**

- Use Cockburn's template attributes: Use Case name, Goal in Context, Scope, Level, Preconditions, Success End Condition, Failed End Condition, Primary Actor, Trigger, Main Success Scenario, Extensions, Sub-Variations, Related Information (Priority, Performance Target, Frequency, Channels, Secondary Actors, Open Issues, Schedule)
- Markdown structure: H2 for use case name, H3 for sections (Characteristic Information, Main Success Scenario, Extensions, Sub-Variations, Related Information)
- Steps in scenarios numbered (1, 2, 3...) with optional sub-steps (1a, 1b, 2a, etc.)
- Extensions and Sub-Variations reference step numbers for clarity

**Diagram Generation Strategy:**

- UC diagrams: Parse all use cases, extract actors and use case names, generate PlantUML with actor-to-usecase associations
- Sequence diagrams: For each scenario (main success + each extension), generate separate diagram showing actor-system interactions as message exchanges
- Each diagram is a separate .puml file for modularity

**Validation:**

- Pydantic models enforce required fields and structure
- Custom validators check for valid step numbering, actor references, etc.
- Clear error messages guide users to fix schema violations

**MCP Surface (Tools, Prompts, Resources):**

- To be defined in Task 1.5 (specification phase)
- Expected tools: parse_uc, validate_uc, generate_uc_diagram, generate_sequence_diagram
- Expected resources: uc_list (list all use cases), uc_get (read specific use case)
- Expected prompts: create_uc (guided use case creation), update_uc (revise existing use case)
- Follows existing specmgr patterns (ADR tools/prompts/resources as reference)

### Related ADRs

- e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in `.specmgr` with feature-driven work units
- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by document-type domain (domain-first hierarchy)

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

#### Phase 1: Schema Definition & Validation

- [x] Task 1.1: Define Markdown schema for use cases (Cockburn attributes) — depends on: none — status: completed

- [x] Task 1.2: Create Pydantic models for use case structure — depends on: Task 1.1 — status: completed

- [x] Task 1.3A: Implement Markdown parser (parse_uc) + fix Extension model for compound action numbering — depends on: Task 1.2 — status: completed

- [x] Task 1.3B: Implement validation tool (step-numbering, cross-reference model_validators) — depends on: Task 1.3A — status: completed

- [x] Task 1.4: Write schema documentation with examples — depends on: Task 1.1 — status: completed

- [x] Task 1.5: Rebuild the uc schema/models on feat-5-md-model-parser's generic `models/md` engine (`MarkdownStr`, `MarkdownSection1`..`6`, `MarkdownParagraph`, `MarkdownListItem`, `MarkdownFrontmatter`), replacing the hand-written `uc/models/v1` Pydantic models and the custom `parse_uc` parser/renderer with a class tree built on that engine's recursive `from_text`/`__str__` — depends on: Task 1.4, feat-5-md-model-parser (done) — status: **completed (2026-08-12)**, now that Task 1.7 (its last remaining gate) is done too (see 2026-08-12 Recent Updates entries for the full session log). Reopened, then re-closed, Phase 1 (previously marked complete on 2026-08-05); see feat-5's own Follow-up #3, which explicitly flagged this as worth revisiting once feat-4 evaluates adoption. **Unblocks Task 2.2 onward** — see Phase 2 note below.

  **Superseded finding (the 2026-08-11 finding below no longer holds; see DEC-010):** the original 2026-08-11 finding claimed a literal "full rebuild" was not achievable — Cockburn's compound action numbering (`3a1.`, `3a2.`, ...) is not valid CommonMark list syntax, and `Extensions`/`SubVariations`'s dynamically-named per-item h3 headings supposedly could not be decomposed by the generic engine at all, requiring a hybrid two-pass (generic engine + a second dedicated regex parser reusing `uc/models/v1/parser.py`'s patterns, with a `parsed_items()` escape hatch). **This is now known to be wrong on the second half of that claim**: the generic engine's regex `@alias` (`AliasType.REGEX`) natively supports a dynamically-named repeated h3 sub-heading under a fixed h2 parent (e.g. `Extension` matching `^Extension \d+[a-z]?\. .+$`, collected as `Extensions.extensions: list[Extension]`) — proven empirically in `tests/uc/models/v2/test_extensions_parsing.py`/`test_sub_variations_parsing.py`, including byte-exact round-trips. The compound-numbering half of the original blocker was resolved differently: **not** by parsing `3a1.`/`3a2.` at all, but by changing the on-disk schema itself (DEC-010, option 2 from the draft sketch's own "Open decisions" block) so extension actions are now a real, plain CommonMark ordered list (`1.`, `2.`, `3.`) under an `### Extension {ref}. {condition}` heading, with cross-references expressed as prose ("Return to step 4.") rather than encoded in a compound list marker. **No hybrid/second parsing pass/`parsed_items()` is needed** — the entire document tree, including `Extensions`/`SubVariations`, is now handled by the generic engine alone.

  **What is actually done (`src/biz/dfch/specmgr/uc/models/v2/`, `tests/uc/models/v2/`, 39 tests):**

  - `use_case.py`: `CharacteristicInformation` and all ~15 h3 fields, `MainSuccessScenario` (`steps: list[MarkdownListItem]`), `Extensions`/`Extension`/`ExtensionItem` (regex `@alias`, `notes: list[MarkdownParagraph] | None` for optional continuation paragraphs — see below), `SubVariations`/`SubVariation` (regex `@alias`), `OpenIssues`, `RelatedInformation`/`Notes`/`Assumptions`, root `UseCase`.
  - `frontmatter.py`: `UcFrontmatter` (narrows `MarkdownFrontmatter`; `type: Literal["uc"]`, `status` narrowed to v1's closed 5-value set; `id`'s `uc-NNN` pattern deliberately dropped in favor of `AdrFrontmatter.id`'s specmgr-assigned-identifier convention).
  - `document.py`: `UcDocument` (`frontmatter: UcFrontmatter` + `body: UseCase`), mirroring `models.adr.v1.Adr`. No parser/`from_text` yet — frontmatter stripping stays a caller concern (feat-5's REQ-003 convention).
  - **Cross-cutting framework bug found and fixed while integrating** (not scoped to this feature, but discovered by it): `MarkdownSection.get_extent` never checked `@alias`, only heading level — see `.specmgr/feat/feat-5-md-model-parser/README.md`'s 2026-08-12 Recent Updates entry for the full writeup. Fixed in `models/md/markdown_section.py`; that closed feature's own test suite updated in place (no design change, a bugfix with documented, deliberate test fallout).

  **What is still open** — see Task 1.6 below (validation porting) and the "Related Use Cases" free-text field (`related_use_cases: RelatedUseCases | None`, currently just `items: list[MarkdownListItem]` — v1's typed `superordinate: str | None`/`subordinate: list[str]` split, parsed on demand, was not ported; low priority, not blocking).

- [x] Task 1.6: Port the three Task 1.3B cross-field `model_validator`s onto the v2 (`uc/models/v2`) model tree — depends on: Task 1.5 — status: completed (2026-08-12). **Not all three still apply** — the move to the generic engine's real CommonMark lists structurally eliminates one of them:

  1. **`MainSuccessScenario.steps` numbered contiguously (1, 2, 3, ... no gaps/duplicates)** — **now structurally unnecessary**, not just "ported forward": `steps: list[MarkdownListItem]` is backed by a genuine CommonMark ordered list (via `feat-5`'s `process_list_field`), which has no representable gap/duplicate/out-of-order state to validate against in the first place. No action needed here; only note this finding on this task when picked up.
  2. **`Extension` actions numbered sequentially** — v1's shape was `{step_reference}1`, `{step_reference}2`, ... (compound numbering, e.g. `3a1`, `3a2`). Since v2's schema change (DEC-010) replaced compound numbering with a plain ordered list (`ExtensionItem` under `Extension.items: list[ExtensionItem]`), this validator's *original* form no longer applies either (same "real ordered list" argument as #1) — but confirm this explicitly with a test before crossing it off, since `ExtensionItem` uniquely also has an optional `notes: list[MarkdownParagraph]` field (continuation paragraphs) that v1 never had; make sure nothing about *that* addition needs its own invariant.
  3. **`UseCase`-level step-reference resolution**: every `Extension` heading's `{ref}` (e.g. `"3a"` in `"Extension 3a. ..."`) and every `SubVariation` heading's `{N}` (e.g. `"1"` in `"Step 1: ..."`) must resolve to an existing 1-based position in `main_success_scenario.steps`, with no duplicate `Extension`/`SubVariation` references within either collection. **This one still genuinely applies** and needs porting: extracting `{ref}`/`{N}` from the heading text requires a small regex (the same shape as the existing `@alias` patterns on `Extension`/`SubVariation`, e.g. `re.match(r"^Extension (\d+)([a-z]?)\. ", heading_text)`), then cross-checking against `len(main_success_scenario.steps)` (a plain step number) — `Extension`'s letter suffix (`3a` vs `3b` vs `3c`) is itself never checked against `main_success_scenario.steps`, only the leading digit portion, mirroring v1's own `_validate_unique_and_resolvable` behavior in `uc/models/v1/use_case.py`. Write this as a `model_validator(mode="after")` on the v2 `UseCase` class, with dedicated tests (both success and each failure mode: unresolvable reference, duplicate reference) mirroring `tests/uc/models/v1/test_use_case.py`'s existing coverage for the same invariant.

  **Done (2026-08-12):** items #1/#2 confirmed structurally unnecessary (with a
  dedicated documentation-only test for #2's `ExtensionItem.notes` question);
  item #3 written as `UseCase.validate_step_references_resolve_and_are_unique`
  (`uc/models/v2/use_case.py`) plus 7 new tests in
  `tests/uc/models/v2/test_use_case.py` (success case, unresolvable/duplicate
  reference for both `Extension` and `SubVariation`, letter-suffix-not-checked
  case, and the `ExtensionItem.notes` documentation case). 545 tests total.

- [x] Task 1.7: Update `uc_schema.json`/`uc-schema.md` for DEC-010's schema change — depends on: Task 1.6 — status: completed (2026-08-12). Resolved the "promote or duplicate" open decision by **duplicating**: `v2/uc_reference_mdformat_schema.json` (scoped to one specific worked example) stays untouched, and a new `v2/uc_schema.json` was created as its generalized duplicate — same field shape, but with example-specific commentary (reference-document literal values, "derived from `uc_reference_mdformat.md`/`.ast`" framing) stripped in favor of document-agnostic wording — this is now *the* canonical v2 schema. Wrote a fresh `v2/uc-schema.md` narrative walkthrough (not a port of `v1/uc-schema.md`), including a brief callout on why 2 of the 3 original Task 1.3B cross-field validators are now structurally unnecessary (§6/§7) versus the one that still applies (§9). `v1/uc_schema.json`/`v1/uc-schema.md` are explicitly marked superseded in this file's own Design Notes section (not edited themselves) rather than deleted, per repo-owner decision to keep them as historical-only artifacts. Feature README's Design Notes section repointed at the v2 artifacts as current/canonical.

- [x] Task 1.8: Add a `from_text`/parser entry point for `UcDocument` — depends on: Task 1.6 — status: completed (2026-08-12). Added `uc/models/v2/parser.py::parse_uc(text: str) -> UcDocument` as a free function, mirroring `models.adr.v1.parser.parse_adr`'s own split (not a classmethod/`@model_validator` on `UcDocument`) — `frontmatter.loads(text)` + `UcFrontmatter.model_validate(...)` (with the same `_stringify_metadata` YAML-date-coercion fix `parse_adr` needed) for the frontmatter half, `UseCase.from_text(format_text(post.content))` for the body half. Unlike `parse_adr`, there is no dedicated `UcParseError`: a malformed heading/list structure surfaces as the generic `models/md` engine's own `AssertionError`, and field/cross-field validation failures as `pydantic.ValidationError` — both left uncaught, same as `parse_adr`'s two-channel split. Re-exported from `uc/models/v2/__init__.py`. 6 new tests in `tests/uc/models/v2/test_parser.py` (minimal doc, the feature's own `v2/uc_reference.md` full round-trip, absent-frontmatter defaulting, invalid-status/unresolvable-reference/malformed-structure failure modes).

Task 1.5 is now fully done (see Current Status below).

#### Phase 2: PlantUML Diagram Generation

- [x] Task 2.1: Implement UC diagram generator (actors + use case associations) — depends on: Task 1.3B — status: completed. **Note (2026-08-11):** built against the current custom `UseCase` model (`uc/models/v1/usecase.py`); may need rework now that Task 1.5 has landed and the model shape changed (v1 → v2).
- [ ] Task 2.2: Implement Sequence diagram generator (main success path) — depends on: Task 1.3B, Task 1.5 — status: not-started (Task 1.5 dependency now satisfied — no longer blocked, build against `uc/models/v2`)
- [ ] Task 2.3: Implement Sequence diagram generator (extensions) — depends on: Task 2.2 — status: not-started
- [ ] Task 2.4: Test diagram generation with sample use cases — depends on: Task 2.3 — status: not-started

#### Phase 3: MCP Tools & CLI Integration

**Note (2026-08-12):** a single `parse_uc` `@mcp.tool()` was added out of
sequence, ahead of Task 3.1's specification, at the repo owner's explicit
request (`uc/tools/parse_uc.py`, registered via `uc/__init__.py` +
`server.py`; 3 tests in `tests/uc/tools/test_parse_uc.py`). It takes raw
markdown text directly (there is no id-based file storage layer for use
cases yet, unlike `adr/tools/`'s `_paths.py`/`_io.py`), and is a thin
wrapper over Task 1.8's `parse_uc` free function. This is **not** Task 3.1
(no specification was written first) nor a claim that Task 3.2 is done
(only this one tool exists) — both tasks below remain open for the rest of
the tool/prompt/resource surface.

- [ ] Task 3.1: Define MCP tools, prompts, and resources (specification) — depends on: Task 2.4 — status: not-started (no separate written spec — same precedent as `parse_uc`'s own note above: 3.1.1-3.1.6 below were implemented directly, without a standalone specification document)
- [x] Task 3.1.1: add resource: uc_schema (same behaviour as req_schema, but do NOT reference this in all the doc strings - DRY) — status: completed (2026-08-16). `uc/resources/uc_schema.py` (`specmgr://uc/schema`), code-generated from `UcDocument.model_json_schema()` via a new `generate_uc_schema()` in `commands/schema.py`, packaged at `uc/data/uc_schema.json`, kept in sync by a pre-commit hook/CI step mirroring req's.
- [x] Task 3.1.2: add resource: uc_example, and tool: get_uc_example (same behaviour as req_example/get_req_example, but do NOT reference this in all the doc strings - DRY) — status: completed (2026-08-16). `uc/resources/uc_example.py` + `uc/tools/get_uc_example.py`, both reading packaged `uc/data/uc_example.md` — a verbatim copy of this feature's own `v2/uc_reference.md` worked example.
- [x] Task 3.1.3: add resource: uc_template, and tool: get_uc_template (same behaviour as req_template/get_req_template, but do NOT reference this in all the doc strings - DRY) — status: completed (2026-08-16). `uc/resources/uc_template.py` + `uc/tools/get_uc_template.py`, both reading a newly authored packaged `uc/data/uc_template.md` (every section present, placeholder content, structurally parses via `UseCase.from_text`/`parse_uc`).
- [x] Task 3.1.4: add resource: uc_list (same behaviour as req_list, but do NOT reference this in all the doc strings - DRY) — status: completed (2026-08-16). `uc/resources/uc_list.py` (`specmgr://uc/list`), using the new `UcSummary` model (`uc/models/v2/summary.py`).
- [x] Task 3.1.5: add CRUD tools: create_uc, get_uc, update_uc, delete_uc (stub), set_status_uc, validate_uc (same behaviour as req's equivalents, but do NOT reference this in all the doc strings - DRY) — status: completed (2026-08-16). New `uc/tools/_paths.py`/`_io.py`/`_lock.py`/`_write.py` (id-based storage layer, mirroring `req/tools/`'s own, on top of the already-generic `general.tools._doc_paths`), plus `create_uc.py`/`get_uc.py`/`update_uc.py`/`delete_uc.py` (stub)/`set_status_uc.py`/`validate_uc.py`.
- [x] Task 3.1.6: confirm parse_uc stays path-based (`path: str`) — status: completed (2026-08-16). Checked against the actual req code: `parse_req` itself is path-based too (it's the separate `get_req` tool, Task 3.1.5, that is id-based), so `parse_uc` already matched this shape and needed no signature change; `get_uc` (Task 3.1.5) covers the id-lookup use case instead.
- [ ] Task 3.2: Implement MCP tools per specification (Task 3.1) — depends on: Task 3.1 — status: not-started as its own tracked task, but its actual scope (the full uc tool surface) is now done via Task 3.1.2/3.1.3/3.1.5 above
- [ ] Task 3.3: Implement MCP prompts per specification (Task 3.1) — depends on: Task 3.2 — status: not-started (genuinely open — no `uc/prompts/` package exists yet)
- [ ] Task 3.4: Implement MCP resources per specification (Task 3.1) — depends on: Task 3.2 — status: not-started as its own tracked task, but its actual scope (the full uc resource surface) is now done via Task 3.1.1/3.1.2/3.1.3/3.1.4 above
- [ ] Task 3.5: Add CLI commands (specmgr uc-validate, specmgr uc-generate) — depends on: Task 3.2 — status: not-started
- [ ] Task 3.6: Integration tests for full workflow — depends on: Task 3.5 — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-12**: Task 1.5 (rebuild `uc` on `models/md`) is **fully
complete** — see the Task List entry itself and the 2026-08-12 Recent Updates
entries below for the full session log. The entire document tree
(`CharacteristicInformation`, `MainSuccessScenario`, `Extensions`/`Extension`,
`SubVariations`/`SubVariation`, `OpenIssues`, `RelatedInformation`,
`UcFrontmatter`, `UcDocument`) is implemented in `uc/models/v2/` and covered
by 46 passing tests, with the original 2026-08-11 "full rebuild isn't
achievable" finding now superseded (DEC-010): the generic engine's regex
`@alias` handles `Extensions`/`SubVariations`' dynamic h3 headings natively,
once the on-disk schema itself dropped Cockburn's compound action numbering
in favor of a plain ordered list. **A genuine framework bug was found and
fixed while integrating** (`MarkdownSection.get_extent` never checked
`@alias`) — see `.specmgr/feat/feat-5-md-model-parser/README.md`'s own
2026-08-12 entry. **Task 1.6 (cross-field validator porting) is done** — see
the Task List entry and its own 2026-08-12 Recent Updates entry.
**Task 1.8 (`parse_uc`/`UcDocument.from_text` entry point) is done**
(`uc/models/v2/parser.py`) — see its Task List entry. **Task 1.7
(`uc_schema.json`/`uc-schema.md` updates for DEC-010's schema change) is now
done too** — `v2/uc_schema.json` (a generalized duplicate of
`v2/uc_reference_mdformat_schema.json`) and a fresh `v2/uc-schema.md` were
added; `v1/uc_schema.json`/`v1/uc-schema.md` are marked superseded in this
file's own Design Notes section. This closes out Task 1.5's last remaining
gate.

A `parse_uc` `@mcp.tool()` (`uc/tools/parse_uc.py`) was also added this
session, ahead of Task 3.1's specification, wrapping Task 1.8's parser
function — see the Phase 3 Task List note for scope (single tool only, not
the full Task 3.1/3.2 surface).

**Blocker:** None — Task 1.5 is done, so Task 2.2 onward is unblocked (still
not-started, but no longer waiting on a model-shape decision; see Task List,
Phase 2).

### Recent Updates

If this section grows too long, move older entries to `history.md` in this
same folder and leave a pointer here, e.g.:
`See history.md for updates before YYYY-MM-DD.`

#### 2026-08-16 Tasks 3.1.1-3.1.6 completed: full uc MCP tool/resource surface

- **Tasks 3.1.1-3.1.6 COMPLETED**, mirroring `req/`'s existing MCP surface
  file-by-file (see Task List entries for the per-task breakdown):
  - **Resources** (`uc/resources/`, new package): `uc_schema`
    (`specmgr://uc/schema`, code-generated via a new `generate_uc_schema()` in
    `commands/schema.py` from `UcDocument.model_json_schema()`, packaged at
    `uc/data/uc_schema.json`), `uc_example` (`specmgr://uc/example`, packaged
    `uc/data/uc_example.md` — a verbatim copy of this feature's own
    `v2/uc_reference.md`), `uc_template` (`specmgr://uc/template`, a newly
    authored `uc/data/uc_template.md`), `uc_list` (`specmgr://uc/list`, backed
    by a new `UcSummary` model, `uc/models/v2/summary.py`).
  - **Tools** (`uc/tools/`): `get_uc_example`, `get_uc_template`, `get_uc`,
    `create_uc`, `update_uc`, `delete_uc` (stub), `set_status_uc`,
    `validate_uc` — all built on a new id-based storage layer
    (`uc/tools/_paths.py`/`_io.py`/`_lock.py`/`_write.py`), reusing the
    already-generic `general.tools._doc_paths` the same way `req/tools/_paths.py`
    does. `parse_uc` stays path-based, unchanged (Task 3.1.6 — confirmed this
    matches `parse_req`'s own shape; `get_req`/`get_uc` are the id-based ones,
    not `parse_req`/`parse_uc`).
  - **Infra**: `pyproject.toml` package-data entry for `biz.dfch.specmgr.uc`;
    `.pre-commit-config.yaml`/CI updated with a `specmgr-schema-uc-package`
    hook/step mirroring req's, and the shared `specmgr-schema` hook's file
    glob widened to include `uc/models/v2`.
  - Deliberately **not** done: no `uc/prompts/` package (Task 3.3 stays
    genuinely open), no `uc/models/v3` (stayed entirely within `uc/models/v2`
    — only additive `summary.py`/`_util.py`), `parse_uc`'s signature untouched.
- 856 tests total (up from prior count), `ruff format`/`ruff check`/`vulture`
  clean, `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` all regenerated
  and clean.

#### 2026-08-13 `parse_uc` MCP tool signature changed: text → path parameter

- **`parse_uc` MCP tool signature changed** (`uc/tools/parse_uc.py`): the
  `@mcp.tool()` wrapper now accepts a file path (`path: str`) instead of raw
  markdown text (`text: str`), and reads the file from disk before parsing.
  Breaking change — not a storage-layer addition (no id-based UC file storage
  exists yet), just a convenience shift from "parse text you pass directly" to
  "parse text read from a file you reference". File-access errors propagate
  naturally as `FileNotFoundError`/`PermissionError`/`OSError`, mirroring the
  existing "let parse/validation failures propagate uncaught" convention from
  `adr/tools/` — no wrapping or custom error types introduced.
- **Model-layer `parse_uc` unchanged** (`uc/models/v2/parser.py`): the free
  function `parse_uc(text: str) -> UcDocument` stays as-is — it's still the
  file-existence-agnostic entry point used by model tests and non-MCP code.
  Only the thin `@mcp.tool()` wrapper in `uc/tools/parse_uc.py` changed.
- **Tests fully rewritten** (`tests/uc/tools/test_parse_uc.py`): each test now
  writes its test document to a `tempfile.TemporaryDirectory`, passes the path
  string to `parse_uc`, and verifies the result. Added a new case:
  nonexistent path → `FileNotFoundError`. Same three validation scenarios
  (valid document, invalid frontmatter, malformed structure) covered, now
  through file-based input. 4 tests → 4 tests (no net addition), all passing.
- **Module and tool docstrings updated** to reflect path-based operation, with
  explicit callout on file-access error propagation.
- 555 tests total (554 prior + 1 new FileNotFoundError case), all passing.
  `ruff format`/`ruff check`/`vulture` clean, `specmgr docs` regenerated.

#### 2026-08-12 Task 1.7 completed; Task 1.5 fully closed

- **Task 1.7 COMPLETED**: Resolved the two open decisions its own task text
  had flagged (promote-vs-duplicate the JSON Schema; what to do about
  `v1/uc-schema.md`):
  - **Duplicated, not promoted**: `v2/uc_reference_mdformat_schema.json`
    (scoped to, and named after, one specific worked example) is left
    untouched. A new `v2/uc_schema.json` is a generalized duplicate of it —
    identical field shape/nesting, but with every reference-document-specific
    comment (literal `id`/`created`/`updated` values, "derived directly from
    `uc_reference_mdformat.md`/`.ast`" framing) rewritten to be
    document-agnostic. `v2/uc_schema.json` is now *the* canonical v2 schema;
    validated via `jsonschema.Draft7Validator.check_schema()`.
  - **Wrote `v2/uc-schema.md` from scratch** (not a port of `v1/uc-schema.md`)
    — a narrative walkthrough of the current `uc/models/v2` shape: heading
    structure (now with `Extensions`/`Sub-Variations`/`Open Issues`/
    `Related Information` genuinely optional, not v1's always-present
    DEC-005 convention), frontmatter, each H2 section, and a brief callout
    (§6/§7) on why 2 of the original 3 Task 1.3B cross-field validators are
    now structurally unnecessary versus the one (§9) that still applies and
    how it's implemented (`UseCase.validate_step_references_resolve_and_are_unique`).
  - **`v1/uc_schema.json`/`v1/uc-schema.md` marked superseded**: not edited
    themselves (kept as an unmodified historical record), but the feature
    README's own Design Notes section now explicitly calls out all `v1/`
    schema artifacts as superseded/historical-only, and repoints the
    "canonical schema" pointer at the `v2/` artifacts.
  - No re-diff of the schema against `uc/models/v2` code was needed — Task
    1.8 (added after the original `uc_reference_mdformat_schema.json` was
    written) only added a parser function, no model/field changes.
- **Task 1.5 marked COMPLETED**: its last remaining gate (Task 1.7) is now
  closed, so the whole "rebuild `uc` on `models/md`" task is done. Phase 2's
  Task 2.2 (blocked on Task 1.5) is now unblocked (still not-started, but
  no longer waiting on a model-shape decision) — see the Phase 2 Task List
  note.
- No test/code changes this session (documentation/schema-artifact task
  only); `ruff format`/`ruff check`/`vulture` untouched, no new tests added
  (554 tests remains current).

#### 2026-08-12 Task 1.8 completed (`parse_uc`); `parse_uc` MCP tool added ahead of Phase 3

- **Task 1.8 COMPLETED**: `uc/models/v2/parser.py::parse_uc(text: str) -> UcDocument`,
  a free function mirroring `models.adr.v1.parser.parse_adr`'s split (frontmatter via
  `frontmatter.loads`/`UcFrontmatter.model_validate` with the same YAML-date
  `_stringify_metadata` coercion `parse_adr` needed; body via
  `UseCase.from_text(format_text(post.content))`). No dedicated `UcParseError`
  introduced — structural failures surface as the generic engine's own
  `AssertionError`, field/cross-field failures as `pydantic.ValidationError`,
  both left uncaught like `parse_adr`. Re-exported from `uc/models/v2/__init__.py`.
  6 new tests in `tests/uc/models/v2/test_parser.py`, including a full round-trip
  of the feature's own `v2/uc_reference.md` reference document.
- **`parse_uc` MCP tool ADDED** (`uc/tools/parse_uc.py`, `uc/tools/__init__.py`),
  per repo-owner request, ahead of Task 3.1's specification/Task 3.2's full
  implementation: a thin `@mcp.tool()` wrapper over the parser function above,
  taking raw markdown text directly since no id-based use-case file storage
  layer exists yet (unlike `adr/tools/`'s `_paths.py`/`_io.py`). Registered by
  `uc/__init__.py` (new, previously empty) and wired into `server.py`'s
  domain-package import list, mirroring `adr`'s own self-registration
  pattern. 3 new tests in `tests/uc/tools/test_parse_uc.py`. Explicitly scoped
  as a single tool, not a claim that Phase 3 is done — see the Task List's
  Phase 3 note.
- 554 tests total (545 prior + 6 + 3 new), `ruff format`/`ruff check`/`vulture`
  clean, `specmgr docs` regenerated.

#### 2026-08-12 New `v2/uc_reference*` artifacts; `uc_reference_mdformat_schema.json` written; 3 model/document discrepancies resolved

- Repo owner renamed `v2/uc_example.md` to `v2/uc_reference.md`, and added
  `v2/uc_reference.ast` (its raw CommonMark AST dump), plus an mdformat-
  normalized pair (`v2/uc_reference_mdformat.md`/`.ast`) and two `.puml`
  diagrams. Old top-level exploration docs (`eval-uc.md`, `uc-schema.md`,
  `uc_schema.json`, `uc_example.md`/`.ast`, etc.) were moved into a new
  `v1/` subfolder for the same reason `v2/` exists — separating the
  original hand-written-parser-era artifacts from the `models/md`-engine-era
  ones. `tests/uc/models/v1/test_parser.py`/`test_uc_diagram.py`'s hardcoded
  `_EXAMPLE_PATH` was updated to the new `v1/uc_example-v1.md` location (a
  path-only fix, no behavior change) — this had silently broken 2 tests
  until caught by this session's full-suite run.
- **Wrote `v2/uc_reference_mdformat_schema.json`**: a JSON Schema (draft-07)
  for `uc_reference_mdformat.md`, built by cross-referencing its AST against
  `uc/models/v2/use_case.py`/`frontmatter.py`/`document.py`, mirroring those
  Pydantic classes' property names/nesting (including the
  `extensions.extensions`/`sub_variations.sub_variations` double-naming and
  the extra `related_information.notes.items`/`.assumptions.items` nesting
  level vs. v1's flatter shape). Validated via
  `jsonschema.Draft7Validator.check_schema()` plus a hand-built instance
  from the reference document's actual content.
- **Found, then fixed, 3 discrepancies** between the reference document and
  the then-current `uc/models/v2` code (surfaced while writing the schema
  above — `UseCase.from_text()` would have failed on this exact reference
  document before this fix):
  1. `### Preconditions` (doc, plural) vs. `Precondition`'s auto-derived
     singular heading — **resolved by renaming the class/field**
     `Precondition`/`precondition` to `Preconditions`/`preconditions`
     (matches the doc without needing an explicit `@alias`, same as every
     other plain-name h3 field).
  2. `### Channels to Primary/Secondary Actors` (doc, lowercase "to") vs.
     `ChannelsToPrimaryActor`/`ChannelsToSecondaryActors`'s
     `space_separated_name`-derived title-cased heading ("Channels **To**
     ...") — **resolved by adding an explicit `@alias(..., AliasType.LITERAL)`**
     to both classes, matching the document's exact casing.
  3. Frontmatter `type: doc-uc` (doc) vs. `UcFrontmatter.type: Literal["uc"]`
     (code) — **resolved in the document's favor of the code**: updated
     `v2/uc_reference.md`'s frontmatter to `type: uc`. `uc_reference_mdformat.md`
     itself carries no `type` field in its (AST-mangled, unstripped)
     frontmatter heading, so nothing needed changing there.
     `uc_reference_mdformat_schema.json` updated to drop its `x-discrepancy`
     notes now that all three are resolved (`type` is `const: "uc"`, no
     remaining code/document mismatch). `uc/models/v2/__init__.py`'s exports
     updated for the `Preconditions` rename. 4 existing tests updated for the
     heading-text rename (`test_use_case.py`, `test_document.py`) plus the
     `_EXAMPLE_PATH` fixes above; 545 tests still passing, `ruff format`/
     `ruff check`/`vulture` clean, `specmgr docs` regenerated.

#### 2026-08-12 Task 1.6 completed; Task 1.7/1.8 added to close out Task 1.5

- **Task 1.6 COMPLETED**: Ported the one still-applicable Task 1.3B cross-field
  `model_validator` onto `uc/models/v2/use_case.py`:
  `UseCase.validate_step_references_resolve_and_are_unique`, checking that every
  `Extension`/`SubVariation` heading's `{ref}`/`{N}` resolves to an existing
  1-based position in `main_success_scenario.steps`, with no duplicate
  references within either collection — same invariant as v1's
  `_validate_unique_and_resolvable`, adapted to extract the reference from the
  heading's `.text` (via `_EXTENSION_HEADING_PATTERN`/`_SUB_VARIATION_HEADING_PATTERN`)
  instead of a dedicated `step_reference` field, since v2 has no such field.
  The other two original Task 1.3B validators were confirmed (not re-written)
  as structurally unnecessary now that `steps`/`Extension.items` are real
  CommonMark ordered lists — including a dedicated test proving
  `ExtensionItem.notes` (new vs. v1) introduces no numbering invariant of its
  own. `ruff format`/`ruff check` clean.
- **Task 1.7/1.8 ADDED**: splitting the "remaining work before Task 1.5 can be
  marked done" prose (previously only in Current Status, not the Task List)
  into two tracked tasks — Task 1.7 (`uc_schema.json`/`uc-schema.md` updates
  for DEC-010's schema change) and Task 1.8 (a `from_text`/parser entry point
  for `UcDocument`) — per repo-owner request, so Task 1.5's remaining scope is
  enumerated the same way every other task is, rather than living only as
  Current-Status narrative.
- 545 tests total (538 prior + 7 new: `tests/uc/models/v2/test_use_case.py`).

#### 2026-08-12 Task 1.5 substantially implemented; full-rebuild finding superseded (DEC-010); framework bug found+fixed in feat-5

- **Task 1.5 (rebuild on `models/md`) substantially implemented**, correcting the
  2026-08-11 finding that a "full rebuild" wasn't achievable. Built out, in
  `src/biz/dfch/specmgr/uc/models/v2/`: `use_case.py` (`CharacteristicInformation`
  and its ~15 h3 fields, `MainSuccessScenario.steps: list[MarkdownListItem]`,
  `Extensions`/`Extension`/`ExtensionItem`, `SubVariations`/`SubVariation`,
  `OpenIssues`, `RelatedInformation`/`Notes`/`Assumptions`, root `UseCase`),
  `frontmatter.py` (`UcFrontmatter`, narrowing `MarkdownFrontmatter`'s `type`/
  `status`, dropping v1's `uc-NNN` `id` pattern in favor of `AdrFrontmatter.id`'s
  specmgr-assigned-identifier convention), and `document.py` (`UcDocument`,
  pairing `UcFrontmatter`+`UseCase`, mirroring `models.adr.v1.Adr`). 39 new
  tests in `tests/uc/models/v2/` (full repo suite: 538 passing).
- **Finding superseded (DEC-010)**: proved empirically
  (`tests/uc/models/v2/test_extensions_parsing.py`/`test_sub_variations_parsing.py`)
  that the generic engine's regex `@alias` *does* support a dynamically-named,
  repeated h3 sub-heading under a fixed h2 parent — the exact capability the
  2026-08-11 finding claimed didn't exist. The other half of that finding
  (Cockburn's compound action numbering, e.g. `"3a1."`, is not valid CommonMark
  list syntax) still holds, but was resolved by changing the on-disk schema
  instead of building a hybrid parser (DEC-010): `Extension` actions are now a
  plain ordered list (`ExtensionItem` under `Extension.items`), with
  cross-references expressed as prose ("Return to step 4."), matching how
  `MainSuccessScenario.steps` already worked. `ExtensionItem` additionally
  supports an optional `notes: list[MarkdownParagraph]` field for a loose-list
  continuation paragraph (a v1 gap this happens to close, not something v1 had).
  No hybrid two-pass parser / `parsed_items()` escape hatch from the original
  draft sketch was needed in the end.
- **Framework bug found and fixed in the (closed) feat-5-md-model-parser
  feature**, discovered while integrating: `MarkdownSection.get_extent` only
  ever checked heading *level*, never the declared `@alias`, unlike
  `from_text`. This broke `process_field`'s optional-field "absence" detection
  whenever an absent optional heading-section field was immediately followed
  by a *different*, same-level sibling heading (reproduced independently
  against this feature's own `RelatedInformation.notes`/`assumptions` and the
  pre-existing `CharacteristicInformation.failed_end_condition`/
  `secondary_actors`). Fixed in `models/md/markdown_section.py`
  (`get_extent` now also calls `match_alias`); feat-5's own
  `test_markdown_section.py` updated in place (7 tests switched from the bare,
  unaliased `MarkdownSection3` to its own pre-existing `_AnyHeadingLeafSection`
  fixture, plus 1 new regression test) — see
  `.specmgr/feat/feat-5-md-model-parser/README.md`'s matching 2026-08-12 entry
  for the full writeup and rationale for why this was treated as a bugfix on a
  closed feature, not a reopening of its design.
- **Task 1.6 ADDED**: port/re-verify the three Task 1.3B cross-field
  `model_validator`s onto the v2 model tree -- see the Task List entry for the
  per-validator breakdown (one now structurally obsolete thanks to real
  CommonMark lists, one needs re-confirming now `ExtensionItem` has a new
  `notes` field v1 never had, one -- `UseCase`-level step-reference resolution
  -- still genuinely needs writing). Not started this session; left for a
  fresh session per repo-owner request (context budget).

#### 2026-08-11 Task 1.5 draft sketch — full-rebuild feasibility finding

- **Task 1.5 draft**: Wrote `.specmgr/feat/feat-4-use-cases/uc_model_v2_draft.py`, a design-review-only sketch (not wired into `src/`, not tested) of the rebuilt model tree. Found, and verified empirically via `MarkdownIt().parse(...)`, that a literal full rebuild is not achievable as scoped: Cockburn's compound extension-action numbering (`"3a1. ..."`) is not valid CommonMark ordered-list syntax (letters after the leading digits disqualify it) — it tokenizes as one plain paragraph, not a list — unlike Main Success Scenario's steps (`"1. ..."`, `"2. ..."`), which *are* a real `ordered_list_open`/`list_item_open` list. Worse, `Extensions`/`SubVariations`'s own per-item h3 headings (`"### 3a. ..."`, `"### Step 1: ..."`) are dynamically named per document, which `MarkdownStr.from_text`'s statically-declared-field model cannot decompose at all yet — feat-5's own REQ-007 note already flagged this same gap for its fixture. The draft sketch adopts a hybrid instead: the generic engine owns frontmatter, top-level sections, Characteristic Information's ~15 h3 fields (via a new `BulletListSection`/`ProseSection` convenience pair, an improvement over the fixture's opaque-leaf shape), and Main Success Scenario's real ordered list (`Step(MarkdownListItem)`, `MainSuccessScenario.steps: list[Step]` — as a bonus, Task 1.3B's step-numbering-contiguity validator becomes structurally unnecessary under this shape, not just ported forward); `Extensions`/`SubVariations` stay leaf `MarkdownSection2`s with a second, dedicated regex-based parse pass (reusing `uc/models/v1/parser.py`'s existing patterns and the existing `Extension`/`ExtensionAction`/`SubVariation` models unchanged) recovering typed structure from the leaf's raw text. Left `parsed_items()`/the cross-reference re-validation as `NotImplementedError` in the sketch (routine porting, not a design question). Three open decisions block finalizing Task 1.5 (see the sketch's trailing comment block): accept the hybrid as final; change the on-disk document format so extension actions become real ordered lists (schema/format-level, likely its own ADR); or raise a "repeated section" primitive as new follow-up work against the now-closed feat-5.

#### 2026-08-11 Task 1.5 added (Phase 1 reopened)

- **Task 1.5 ADDED**: Rebuild the uc schema/models on feat-5-md-model-parser's now-closed generic `models/md` Markdown-to-Pydantic engine (`MarkdownStr`, `MarkdownSection1`..`6`, `MarkdownParagraph`, `MarkdownListItem`, `MarkdownFrontmatter`), replacing the hand-written `uc/models/v1` Pydantic models and the custom `parse_uc` parser/renderer. Directly actions feat-5's own Follow-up #3 ("worth revisiting if/when `feat-4-use-cases` evaluates adopting this engine for its own `uc` schema"). Scoped as a full rebuild (DEC-009), not an evaluation-only spike. Reopens Phase 1 (previously marked complete on 2026-08-05); the three cross-field `model_validator`s from Task 1.3B must be preserved on the rebuilt model tree, since the generic engine has no equivalent built-in check. Task 2.1 (UC diagram generator, done) is flagged as possibly needing rework once Task 1.5 lands; Task 2.2 (Sequence diagram generator, main success path) is now explicitly blocked on Task 1.5 rather than started against a model shape that may be replaced. Dependencies section updated to record feat-5-md-model-parser as a completed dependency for this task.

#### 2026-08-05 (continued)

- **Task 1.1 COMPLETED**: Markdown schema definition and formal specification
  - Created `uc_schema.json` — Complete JSON Schema with validation rules, constraints, and field types (312 lines)
  - Created `uc_reference_mdformat.md` — Detailed "Buy Goods" use case example with all sections
  - Created `uc_class.puml` — Class diagram showing schema structure
  - Frontmatter: `id`, `version`, `status`, `created`, `updated` (no title field; H1 is source of truth)
  - H1: Use case name
  - H2: Main sections (Characteristic Information, Main Success Scenario, Extensions, Sub-Variations, Open Issues, Related Information)
  - H3: Subsections (Goal in Context, Scope, Level, Preconditions, Success End Condition, Failed End Condition, Primary Actor, Secondary Actors, Trigger, Frequency, Priority, Performance Target, Channels, Related Use Cases, step variations)
  - Max heading depth: H1-H3
  - Required sections: Characteristic Information, Goal in Context, Scope, Level, Preconditions, Success End Condition, Primary Actor, Trigger, Main Success Scenario
  - Optional sections: Failed End Condition, Secondary Actors, Frequency, Priority, Performance Target, Channels, Related Use Cases, Extensions, Sub-Variations, Open Issues, Related Information (Notes, Assumptions)
  - Generated PlantUML diagrams (activity and sequence diagrams for main success path and extensions)
- **Task 1.2 COMPLETED**: Create Pydantic models from JSON Schema
  - Created 5 model files in `src/biz/dfch/specmgr/uc/models/v1/`:
    - `frontmatter.py` — `UseCaseFrontmatter`
    - `characteristic_information.py` — `CharacteristicInformation`, `RelatedUseCases`
    - `scenario.py` — `Step`, `MainSuccessScenario`, `Extension`, `Extensions`, `SubVariation`, `SubVariations`
    - `related_information.py` — `OpenIssues`, `RelatedInformation`
    - `usecase.py` — `UseCase` (root model)
  - 12 Pydantic model classes total, matching class diagram exactly
  - Full validation with pattern matching, enum validation, min/max constraints, required/optional field enforcement
  - Created comprehensive test suite: 55 tests across 5 test files covering all models and validation rules (tests/uc/models/v1/)
  - All tests passing (257 total tests in project: 186 ADR + 55 UC + 16 other)
  - Package structure follows DEC-004: models inside domain package (`uc/models/` not shared `models/uc/`)
  - One class per file policy enforced (with logical grouping for tightly coupled classes)
  - Class names aligned with class diagram: `UseCaseFrontmatter` (not `UcFrontmatter`), `Step` (not `MainSuccessScenarioStep`)
- **Housekeeping**: Moved Java reference implementation files to `playground/` subdirectory (not part of Python implementation)
- Notes: User confirmed preference for UC + Sequence diagrams (not Activity diagrams). Sequence diagrams will have separate diagrams for main success path and each extension. Reference: https://www.cs.otago.ac.nz/coursework/cosc461/uctempla.htm

#### 2026-08-05 Task 1.3 split into 1.3A/1.3B

- **Task 1.3 split**: Originally a single task ("Implement validation tool"), split into Task 1.3A (Markdown parser) and Task 1.3B (cross-field validators) since a `parse_uc` parser didn't yet exist — a prerequisite for any file-based validation, unlike ADR where `parse_adr` predates its `validate_adr` tool. Kept the dotted sub-numbering so the overall task numbering (Task 2.x, 3.x) didn't need renumbering. See DEC-006/DEC-007.
- **Task 1.3A COMPLETED**: Fixed `Extension.actions` (previously `list[str]`) to `list[ExtensionAction]`, modeling the compound sub-numbering (`3a1`, `3a2`, ...) already present in `uc_reference_mdformat.md` but not yet in the Pydantic schema. Updated `uc_schema.json` to match. Implemented `parse_uc` (`uc/models/v1/parser.py`), mirroring ADR's `parse_adr` heading-outline-tree approach (`models/adr/v1/parser.py`) but extended with numbered/bulleted Markdown list parsing (Main Success Scenario steps, Extension actions, most `list[str]` fields) and compound-heading parsing (`### {stepRef}. {condition}` for Extensions, `### Step N: {label}` for Sub-Variations). Raises a dedicated `UcParseError` for structural problems, distinct from `pydantic.ValidationError` for field-content/invariant problems — same two-channel split as ADR's parser. Round-trips the full `uc_reference_mdformat.md` file correctly. 14 new parser tests (structural-error cases + full-document + minimal-document round trips), plus 1 new `ExtensionAction` test file and updated `Extension`/`Extensions`/`UseCase` model tests for the new `actions` shape.
- **Task 1.3B COMPLETED**: Added three `model_validator`s not expressible in JSON Schema draft-07 (cross-item/cross-field invariants): (1) `MainSuccessScenario.steps` must be numbered contiguously 1, 2, 3, ... ascending, no gaps/duplicates/out-of-order; (2) `Extension.actions` must be numbered `{step_reference}1`, `{step_reference}2`, ... sequentially; (3) `UseCase`-level check that every `Extension`/`SubVariation` `step_reference` resolves to an existing `main_success_scenario` step number, with no duplicate references within either collection. Unlike ADR's analogous Considered-Options/Option-section gap (deliberately left unenforced per `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §7), this cross-reference check is explicitly enforced here since Task 1.3's original title named "step numbering" as in-scope. 12 new tests across `test_main_success_scenario.py`, `test_extension.py`, `test_use_case.py`.
- All 292 tests passing (186 ADR + 90 UC + 16 other), `ruff format`/`ruff check` clean, `specmgr docs` regenerated.

#### 2026-08-05 Task 1.4 completed

- **Task 1.4 COMPLETED**: Wrote `uc-schema.md` — a narrative walkthrough of the Cockburn-based use case schema (heading structure, frontmatter, each H2 section, the three cross-field `model_validator` invariants and where each constraint lives across `uc_schema.json`/Pydantic field declarations/`model_validator`s, and how `parse_uc` maps Markdown onto it). References rather than duplicates `uc_schema.json` (exact field constraints) and `uc_reference_mdformat.md` (full worked example), mirroring how `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` explains MADR sections without restating the whole template. Placed at `.specmgr/feat/feat-4-use-cases/uc-schema.md` (feature-local, not top-level `doc/`) since the feature is still mid-flight. Phase 1 now fully complete.

#### 2026-08-05 Task 2.1 completed

- **Task 2.1 COMPLETED**: Implemented `render_uc_diagram(use_case: UseCase) -> str` (`uc/models/v1/uc_diagram.py`), a pure function (no file I/O, no multi-document resolution — parses/renders exactly one `UseCase` at a time, mirroring `models/adr/v1/renderer.py`'s style) that generates a PlantUML Use Case diagram: one `usecase` node for the document itself, one `actor` node per distinct label derived from `primary_actor`/`secondary_actors`, and one association edge per actor. Sub-use-case mentions in actor/extension text (e.g. "(UC-044)") are left as plain text, never resolved into separate nodes, since no id→document listing/resolution layer exists yet (Phase 3). Actor label extraction rule: use the contents of the first double-quoted substring if present (taking priority over any parenthetical), otherwise strip everything from the first `" ("` onward, otherwise use the text as-is. A label that is already a bare PlantUML identifier (e.g. `"Buyer"`, `"Bank"`) is reused as its own alias unquoted; otherwise a generated `actorN` alias is used with the label quoted. 12 new tests in `tests/uc/models/v1/test_uc_diagram.py` (label-extraction cases, diagram structure, full `uc_reference_mdformat.md` round-trip). 304 tests total (292 prior + 12 new), `ruff format`/`ruff check` clean, `specmgr docs` regenerated.

### Decisions Made

- **DEC-001** \[2026-08-05\]: Use UC + Sequence diagrams (not Activity diagrams) — Sequence diagrams better show interactions between actors and system; UC diagrams show the big picture. Together they provide overview + detail.
- **DEC-002** \[2026-08-05\]: Separate Sequence diagrams per scenario (main success + each extension) — Clearer visualization of different flows; easier to understand each scenario independently.
- **DEC-003** \[2026-08-05\]: Markdown as source format (not a UI) — Keeps use cases in version control, reviewable in PRs, and compatible with existing specmgr workflow.
- **DEC-004** \[2026-08-05\]: Create a new domain "uc" (use cases) — Following the domain-first hierarchy established in ADR ece4554b-725c-4f76-bc04-5d2b760363d2, create `uc/` as a top-level package alongside `adr/`, with sub-packages for `uc/models/`, `uc/tools/`, `uc/prompts/`, `uc/resources/`. This differs from current `adr/` structure (which has models in shared `models/adr/`) — see tech debt note below.
- **DEC-005** \[2026-08-05\]: Always include all optional section headings in use case documents — Even when empty, include Extensions, Sub-Variations, Open Issues, and Related Information sections. This ensures structural consistency across all use cases, makes it clear that these aspects were considered (even if empty), simplifies parsing/validation, and makes git diffs cleaner when content is added later. Empty sections can contain "(None identified)" or similar placeholder text.
- **DEC-006** \[2026-08-05\]: Split Task 1.3 into Task 1.3A (Markdown parser) and Task 1.3B (cross-field validators) — No `parse_uc` existed yet, and file-based "validation" is meaningless without first parsing a `.md` file into a `UseCase`. Splitting mirrors ADR's own parse/validate separation (`models/adr/v1/parser.py` vs. `adr/tools/validate_adr.py`) while keeping the overall task numbering stable via dotted sub-numbers.
- **DEC-007** \[2026-08-05\]: Model `Extension.actions` as `list[ExtensionAction]` (compound number + description), not `list[str]` — `uc_reference_mdformat.md` already showed compound sub-numbering (`3a1`, `3a2`, ...) that the original `list[str]` model couldn't represent or validate. Fixed before writing the parser so the parser has a real target field to populate, and so action-numbering sequencing (Task 1.3B) has something to validate against.
- **DEC-008** \[2026-08-05\]: Enforce Extension/SubVariation step-reference cross-resolution against `main_success_scenario.steps` via a `UseCase`-level `model_validator` — Unlike ADR's deliberate choice not to enforce Considered-Options/Option-section consistency (`.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §7), Task 1.3's original title explicitly named "step numbering" as in-scope, so this cross-check (plus step/action numbering contiguity) is enforced rather than left as a known gap.
- **DEC-009** \[2026-08-11\]: Rebuild the uc schema/models on feat-5-md-model-parser's `models/md` engine (Task 1.5), fully replacing the hand-written `uc/models/v1` Pydantic models and custom `parse_uc` parser/renderer, rather than keeping the two in parallel or leaving adoption as an unscheduled follow-up — feat-5 closed 2026-08-11 with a generic, proven (498 tests) heading-recursion engine (`MarkdownStr`/`MarkdownSection1`..`6`/`MarkdownParagraph`/`MarkdownListItem`) and explicitly flagged this exact adoption as its own Follow-up #3. Doing a full rebuild now (rather than a spike/evaluation-only task) avoids maintaining two parsing mechanisms for the same document type. Consequence: Task 2.1 (UC diagram generator) may need rework, and Task 2.2 onward (Sequence diagram generator) is blocked until Task 1.5 lands, since building further diagram/MCP tooling against a model shape that is about to be replaced would be wasted work.
- **DEC-010** \[2026-08-12\]: Change the on-disk schema so `Extension` actions are a plain CommonMark ordered list (`1.`, `2.`, `3.` under `### Extension {ref}. {condition}`), abandoning Cockburn's compound sub-numbering (`3a1.`, `3a2.`, ...) entirely, rather than adopting the draft sketch's hybrid two-pass parser (option 1) or raising a "repeated section" primitive against feat-5 (option 3) — the two other options the draft sketch's "Open decisions" block left open. Chosen because it needed no new parsing machinery at all: the generic engine already handles a dynamically-named, regex-`@alias`ed, repeated h3 sub-heading (`Extension`) under a fixed h2 parent (`Extensions`) natively, once the *action list inside it* is a real ordered list rather than compound-numbered prose. Cross-references that compound numbering used to encode structurally (e.g. `"3a1."` implying "extension 3a's first action") are now expressed the same way Main Success Scenario's own steps already do it: prose text ("Return to step 4.", "Continue to step 6.") inside a plain list item, not the list marker itself. This also means `Extension`'s own heading `{ref}` (e.g. `"3a"`) is the *only* remaining structural cross-reference into `main_success_scenario.steps` that needs validating (Task 1.6, item 3) — nothing below that heading needs its own numbering invariant anymore. Consequence: `uc_reference_mdformat.md`'s literal Markdown shape changed (every `### {ref}1.`/`### {ref}2.`-style compound heading was rewritten to a heading + plain list), and `uc_schema.json`/`uc-schema.md` (Task 1.1/1.4 outputs) are now stale with respect to this new shape — updating them is follow-up work, not yet done as of this entry.

### Related PRs / Commits

- [Issue #4](https://github.com/dfch/biz.dfch.SpecMgr/issues/4): Feature: Create Use Cases with tool support
- [PR #NNN](link): [description]
- [Commit hash](link): [description]

## Technical Debt

### ADR models location refactoring (unrelated to this feature)

Currently, `adr/` domain has its schema models in the shared `models/adr/` folder (outside the domain package). This feature establishes a new pattern: `uc/models/` (models inside the domain package). For consistency, `adr/models/` should be moved into `adr/models/` to match the new pattern. This is a separate refactoring task, not part of this feature's scope, but should be tracked and prioritized.

**Tracking**: [GitHub Issue #1](https://github.com/dfch/biz.dfch.SpecMgr/issues/1)

**Impact**: Once completed, both `adr/` and `uc/` will have consistent internal structure with models co-located in their respective domain packages.

### Update `.specmgr/_template/v1/README.md` to include Tech Debt section

The feature template at `.specmgr/_template/v1/README.md` does not include a "Technical Debt" section. This section is useful for recording known issues, refactoring needs, and architectural inconsistencies discovered during feature work. The template should be updated to include an optional "## Technical Debt" section with guidance on when to use it.

**Tracking**: [GitHub Issue #2](https://github.com/dfch/biz.dfch.SpecMgr/issues/2)

**Impact**: Future features will have a consistent place to record tech debt, making it discoverable and prioritizable.
