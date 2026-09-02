---
created: '2026-08-05 00:00:00.000Z'
id: feat-4-use-cases
status: planning
updated: '2026-08-19 00:00:00.000Z'
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

- [x] Task 3.1: Define MCP tools, prompts, and resources (specification) — depends on: none — status: completed (2026-08-16). **Dependency corrected**: originally listed as depending on Task 2.4 (Phase 2 diagram generation), but the MCP tool/resource/prompt surface (parse/validate/CRUD/schema/example/template/list) has no actual dependency on diagram generation being done first — that was a planning-time error, not a real blocker. No separate written specification document was produced (same precedent as `parse_uc`'s own note above); instead, the tool/resource surface was defined and built directly via Task 3.1.1-3.1.7, which now cover the full scope this task called for (schema/example/template/list resources, the full CRUD+validate tool set, `parse_uc`'s path-based shape confirmed, and class-hierarchy docstrings). Phase 3's remaining tasks (3.2-3.6) are unaffected by this dependency fix.
- [x] Task 3.1.1: add resource: uc_schema (same behaviour as req_schema, but do NOT reference this in all the doc strings - DRY) — status: completed (2026-08-16). `uc/resources/uc_schema.py` (`specmgr://uc/schema`), code-generated from `UcDocument.model_json_schema()` via a new `generate_uc_schema()` in `commands/schema.py`, packaged at `uc/data/uc_schema.json`, kept in sync by a pre-commit hook/CI step mirroring req's.
- [x] Task 3.1.2: add resource: uc_example, and tool: get_uc_example (same behaviour as req_example/get_req_example, but do NOT reference this in all the doc strings - DRY) — status: completed (2026-08-16). `uc/resources/uc_example.py` + `uc/tools/get_uc_example.py`, both reading packaged `uc/data/uc_example.md` — a verbatim copy of this feature's own `v2/uc_reference.md` worked example.
- [x] Task 3.1.3: add resource: uc_template, and tool: get_uc_template (same behaviour as req_template/get_req_template, but do NOT reference this in all the doc strings - DRY) — status: completed (2026-08-16). `uc/resources/uc_template.py` + `uc/tools/get_uc_template.py`, both reading a newly authored packaged `uc/data/uc_template.md` (every section present, placeholder content, structurally parses via `UseCase.from_text`/`parse_uc`).
- [x] Task 3.1.4: add resource: uc_list (same behaviour as req_list, but do NOT reference this in all the doc strings - DRY) — status: completed (2026-08-16). `uc/resources/uc_list.py` (`specmgr://uc/list`), using the new `UcSummary` model (`uc/models/v2/summary.py`).
- [x] Task 3.1.5: add CRUD tools: create_uc, get_uc, update_uc, delete_uc (stub), set_status_uc, validate_uc (same behaviour as req's equivalents, but do NOT reference this in all the doc strings - DRY) — status: completed (2026-08-16). New `uc/tools/_paths.py`/`_io.py`/`_lock.py`/`_write.py` (id-based storage layer, mirroring `req/tools/`'s own, on top of the already-generic `general.tools._doc_paths`), plus `create_uc.py`/`get_uc.py`/`update_uc.py`/`delete_uc.py` (stub)/`set_status_uc.py`/`validate_uc.py`.
- [x] Task 3.1.6: confirm parse_uc stays path-based (`path: str`) — status: completed (2026-08-16). Checked against the actual req code: `parse_req` itself is path-based too (it's the separate `get_req` tool, Task 3.1.5, that is id-based), so `parse_uc` already matched this shape and needed no signature change; `get_uc` (Task 3.1.5) covers the id-lookup use case instead.
- [x] Task 3.1.7: add brief docstrings to the classes that make up the UseCase class hierarchy. These docstrings must be helpful to an Agent to understand how the uc is structured and what it is for. Do not write docstrings like: "this is a section that derives from xyz as discussed in Task a.b.c." Write the intended purpose of the content of a structural element. — status: completed (2026-08-16). Added a purpose-focused docstring to every one of the ~25 classes in `uc/models/v2/use_case.py` (the file that previously had none): a one-sentence statement of what the section means for a use case, followed by a one-sentence note on its shape (free-form prose vs. bullet list vs. ordered list vs. composed-of-sub-sections) — no task/implementation-history references. `document.py`/`frontmatter.py`/`summary.py` already carried purpose-focused docstrings and needed no changes. `ruff format`/`ruff check`/`vulture` clean, all 856 tests still passing (no behavior change).
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

See `history.md` for updates — all entries have been moved to history.

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
