---
created: 2026-08-13
id: feat-6-requirement-artifact
status: in-progress
updated: 2026-08-14
version: 1.4.1
---

# Feature: Requirement (REQ) artifact template with characteristic assignment

## Plan

### Overview

Provide a markdown-based REQ artifact type for storing requirements with assignable characteristics. The REQ artifact follows the domain-first hierarchy (ADR ece4554b) and provides a structured template for capturing, organizing, and tracking requirements alongside existing document types (ADR, UC). A defining capability is the ability to assign arbitrary characteristics (metadata tags) to each requirement.

### Requirements

- [x] REQ-001: Define the REQ markdown schema structure
- [x] REQ-002: Support assigning characteristics (key-value pairs or tags) to requirements
- [x] REQ-003: Pydantic models for REQ documents (`req/models/v1/` — domain-first path, see Design Notes)
- [x] REQ-004: Parse and validate REQ documents from markdown
- [ ] REQ-005: MCP tools, prompts, and resources for REQ management (specified in Task 3.1) — only `parse_req` tool done so far; prompts/resources not-started

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — Requirements to be defined during specification phase
- [ ] ACC-002: Verifies REQ-002 — Characteristics model supports assignment, retrieval, and filtering — assignment/retrieval implemented (flat list); filtering not implemented/verified
- [x] ACC-003: Verifies REQ-003 — Pydantic models validate required/optional fields correctly
- [x] ACC-004: Verifies REQ-004 — Parser produces valid object tree; validation detects malformed input
- [ ] ACC-005: Verifies REQ-005 — MCP surface follows ADR/UC domain-first pattern — pending REQ-005 completion (prompts/resources)

### Scope

**Included in this feature:**

- Specification of the REQ markdown schema (to be defined)
- Pydantic models with characteristic assignment support
- Parser and validator for REQ documents
- MCP tools, prompts, and resources (after spec is defined)

**Explicitly out of scope:**

- Rendering/exporting requirements to non-markdown formats (to be determined in spec phase)
- Cross-referencing between requirements and other document types (future enhancement)

### Dependencies

- Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr` structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic `MarkdownFrontmatter` base)
- Blocks: None identified yet

### Design Notes

The REQ domain will follow the same patterns established by existing domains:

- Models live under `req/models/v1/` (decided and implemented — domain-first path, not shared `models/req/v1/`; see Task 2.1)
- Schema versioning follows the ADR vN strategy (ADR d54abe50's variant of this decision)
- `type: Literal["req"]` discriminator in frontmatter via `MarkdownFrontmatter` subclass (ADR bc5e18ad)

### Related ADRs

- e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in `.specmgr` with feature-driven work units
- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by document-type domain (domain-first hierarchy)
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for markdown document types

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

#### Phase 1: Specification

- [x] Task 1.1: Define the REQ markdown schema — document required/optional fields, heading depth, list vs prose format, and the characteristics assignment model — depends on: none — status: **completed (2026-08-13)**
- [x] Task 1.1.1 Define REQ frontmatter (`req/models/v1/frontmatter.py` — `ReqFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["req"]`, 7-value status set: draft/proposed/accepted/superseded/deprecated/rejected/implemented) — depends on: none — status: **completed (2026-08-13)**
- [x] Task 1.1.2 Define REQ body structure (H1 title, required/optional H2/H3 headings, list vs prose format) and characteristics assignment model in the markdown body — depends on: Task 1.1.1 — status: **completed (2026-08-13)** — `req/models/v1/body.py`: `Requirement` (H1) with `statement` (requirement-statement paragraph), `description`/`characteristics`/`level`/`source` (mandatory H2), `priority`/`tags`/`related_artifacts`/`more_information`/`notes` (optional H2). `characteristics`/`tags` are modeled as simple bullet/numbered lists (`list[MarkdownListItem]`), not key-value pairs — see Decisions Made. `related_artifacts` nests four optional H3 subsections (`requirements`/`decisions`/`goals`/`acceptance_criteria`), each a bullet list of `{ID}: {description}` references.
- [x] Task 1.2: Draft `req_schema.json` from the specification — depends on: Task 1.1.2 — status: **completed (2026-08-14)** — produced via **generation**, not hand-authoring, and in **JSON Schema 2020-12**, not the draft-07 originally specified — see Tasks 2.7-2.9 and Decisions Made.
- [x] Task 1.3: Create a reference REQ document (`req_reference.md`) showing all fields with sample data — depends on: Task 1.2 — status: **completed (2026-08-13)** — `.specmgr/feat/feat-6-requirement-artifact/req_reference.md` (+ `req_reference.ast` markdown-it token dump), done ahead of Task 1.2 rather than after it; used directly as the parser's own round-trip test fixture.

#### Phase 2: Pydantic Models & Parser

- [x] Task 2.1: Write Pydantic model tree under `req/models/v1/` mirroring the schema — depends on: Task 1.3 — status: **completed (2026-08-13)** — `body.py` (all section classes, built on the generic `models/md` `MarkdownStr`/`MarkdownSectionN` engine from `feat-5-md-model-parser`, not a hand-written token parser), `document.py` (`ReqDocument(frontmatter, body)`, mirrors `UcDocument`).
- [x] Task 2.2: Implement `parse_req(text: str) -> ReqDocument` (free function, following `parse_adr`/`parse_uc` pattern) — depends on: Task 2.1 — status: **completed (2026-08-13)** — `req/models/v1/parser.py`; mirrors `uc.models.v2.parser.parse_uc` exactly: `frontmatter.loads()` → `ReqFrontmatter.model_validate()` (via `_stringify_metadata`) → `Requirement.from_text(format_text(...))`. Same two uncaught error channels as `parse_uc` (`AssertionError` for structural failures, `pydantic.ValidationError` for field/cross-field failures) — no dedicated `ReqParseError`.
- [ ] Task 2.3: Cross-field model validators (if any invariants arise from the specification) — depends on: Task 2.1 — status: not-started — no cross-field invariants identified yet (unlike UC's extension/sub-variation step-reference resolution).
- [x] Task 2.4: Add field-level `Field(description=...)` (with constraints, e.g. "list must contain at least one item") to `Requirement`'s scalar/optional fields and section `items`/`value` fields — bare attribute docstrings are not picked up by `model_json_schema()`, only explicit `Field(description=...)` is — depends on: Task 2.1 — status: **completed (2026-08-14)** — also extended to `RelatedArtifacts`'s four optional sub-section fields (not literally "items"/"value", but the same optional-field-needs-a-description gap) and `min_length=1` added to every `items: list[MarkdownListItem]` field (`Characteristics`/`Tags`/`Requirements`/`Decisions`/`AcceptanceCriteria`/`Goals`).
- [x] Task 2.5: Rewrite `req/models/v1/body.py` class docstrings to be self-contained — remove references to `models/adr/v1` and `req_reference.md`, dev-only artifacts an agent reading the emitted JSON schema at tool-discovery time cannot necessarily fetch or read — depends on: Task 2.1 — status: **completed (2026-08-14)** — the **class** docstrings (the only ones `model_json_schema()` surfaces) already had no such references from the 2026-08-14 audit above; only the **module**-level docstring did, cleaned up for consistency even though it never reaches the emitted schema.
- [x] Task 2.6: Shorten verbose docstrings on shared `models/md` "base" classes referenced by REQ's schema (e.g. `MarkdownListItem` ~2.7k chars, `MarkdownParagraph` ~1.3k chars) — they get inlined into every schema `$defs` entry that uses them, inflating the tool-discovery payload every client fetches — depends on: none — status: **completed (2026-08-14)** — `MarkdownListItem` class docstring ~2.7k → ~1.1k chars, `MarkdownParagraph` ~1.3k → ~0.7k chars (method docstrings, never surfaced in a schema, left untouched); done as a post-closure change to `feat-5-md-model-parser` (which owns the module), logged in that feature's own Recent Updates per the established cross-feature precedent.
- [x] Task 2.7: Implement `generate_req_schema()` — pure function producing REQ's JSON Schema (2020-12 dialect, see Decisions Made) via `ReqDocument.model_json_schema()`, serialized deterministically (`indent=2, sort_keys=True` + trailing newline) — depends on: Task 2.4, Task 2.5, Task 2.6 — status: **completed (2026-08-14)** — `commands/schema.py`; also explicitly injects `$schema` (Pydantic v2's `model_json_schema()` omits it by default) so the file self-describes its own dialect.
- [x] Task 2.8: Implement `specmgr schema` CLI command (`commands/schema.py`, mirroring `commands/adr_toc.py`'s generate-function + Typer-wrapper shape) — named generically (not `req-schema`) since more doc-type schemas are expected later. Built on a doc-type generator registry (`{"req": generate_req_schema}` today); a `--type` option selects one registered type by name (only `req` valid for now); omitting it generates **all** registered types (today: just `req`), each written to its own `docs/{type}_schema.json`. Exits with code 1 if any regenerated file's content differs from what was already on disk (including the file not existing yet), so CI can rely on the exit code directly instead of a separate `git diff --exit-code` step — depends on: Task 2.7 — status: **completed (2026-08-14)** — registered in `cli.py`/`commands/__init__.py`; `docs/req_schema.json` generated and committed.
- [x] Task 2.9: Wire `specmgr schema` into `.github/workflows/ci.yml`'s Python-3.13-only job (alongside the existing `specmgr docs`/`specmgr adr-toc` steps) — run it and fail the build directly on its own exit code (no separate `git diff --exit-code` step needed for this artifact) — depends on: Task 2.8 — status: **completed (2026-08-14)**
- [x] Task 2.10: Add a local pre-commit hook scoped to `src/biz/dfch/specmgr/req/models/v1/**/*.py` (and `src/biz/dfch/specmgr/models/md/**/*.py`, since the shared engine feeds this schema) that runs `specmgr schema` with **no** `--type` — always regenerates all registered types, even though `req` is the only one today — depends on: Task 2.8 — status: **completed (2026-08-14)** — `specmgr-schema` hook in `.pre-commit-config.yaml`, verified with `pre-commit run specmgr-schema`.
- [x] Task 2.11: Tests for the generator and CLI (`tests/commands/test_schema.py`, mirroring `test_docs.py`/`test_adr_toc.py`) — deterministic output, `$schema` is the 2020-12 URI, structural assertions on `frontmatter`/`body`/`required`, `--type req` vs. no-option ("all") behavior, exit code 0 when unchanged vs. 1 when the on-disk file differs or is missing — depends on: Task 2.7, Task 2.8 — status: **completed (2026-08-14)** — 14 new tests, 618 project-wide (no regressions).
- [x] Task 2.12: Update Task 1.2's status/wording (2020-12, not draft-07; command is `specmgr schema`, not REQ-specific) and this feature's Recent Updates once Tasks 2.7-2.11 land — depends on: Task 2.7, Task 2.8, Task 2.9, Task 2.10, Task 2.11 — status: **completed (2026-08-14)**

#### Phase 3: MCP Surface & CLI

- [x] Task 3.1: Define MCP tools, prompts, and resources for REQ management — depends on: Phase 2 complete — status: **partially completed (2026-08-13)** — only the `parse_req` tool defined/implemented so far (mirrors `uc/tools/`'s current scope, which also only has `parse_uc`); prompts/resources and id-based file storage (`_paths.py`/`_io.py` equivalent) not yet specified.
- [x] Task 3.2: Implement MCP per specification (Task 3.1) — depends on: Task 3.1 — status: **partially completed (2026-08-13)** — `req/tools/parse_req.py` (`@mcp.tool()` wrapper, reads path from disk, delegates to `parser.parse_req`), `req/tools/__init__.py`, `req/__init__.py`; registered in `server.py` (`from . import adr, general, req, resources, uc`). Remaining Task 3.1 scope (prompts, resources, further tools) still not-started.
- [ ] Task 3.3: Implement CLI commands (`req-get`, `req-parse`, etc.) — depends on: Task 3.2 — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-14**: Phase 1 (Specification) and Phase 2 (Pydantic Models & Parser) are both **fully complete**, including `req_schema.json` (Task 1.2), now generated (not hand-authored) via a new generic `specmgr schema` CLI command (JSON Schema 2020-12), with CI wiring and a pre-commit hook keeping it in sync. Phase 3 (MCP Surface) has its first tool, `parse_req`, implemented and registered; prompts, resources, and further tools remain unspecified. No CLI commands yet (Task 3.3).

### Blockers

None.

### Recent Updates

#### 2026-08-14 (continued) — Task 2.4 regression fixed: invalid `Field(pattern=...)` on model-typed `Level.value`/`Priority.value`

- The Task 2.4 entry below added `Field(..., pattern=r"...")` to
  `Level.value`/`Priority.value` in `req/models/v1/body.py`. Both fields are
  typed `MarkdownParagraph` — a Pydantic **model** (built on `MarkdownStr`),
  not a `str` — and pydantic v2 cannot apply a string `pattern` constraint to
  a model-typed field: every call to `Requirement.from_text(...)` (i.e.
  `parse_req` and `parse_req()`/the MCP tool) raised
  `TypeError: Unable to apply constraint 'pattern' ... for schema of type 'model'`
  at instantiation. This was never caught at the time because Tasks 2.7/2.8's
  `model_json_schema()`-based schema generation and its own tests don't
  instantiate the model, only introspect its schema — the break only
  surfaced in the pre-existing parser/tool tests
  (`tests/req/models/v1/test_parser.py`,
  `tests/req/tools/test_parse_req.py`, 6 tests).
- Fixed by replacing each `pattern=...` `Field` argument with a
  `@field_validator("value")` that checks `value.text` (the paragraph's own
  inline text) against the same regex and raises `ValueError` otherwise —
  the same "constrain the rendered text, not the model" approach forced by
  `value`'s model type. `docs/req_schema.json` regenerated as a result (the
  two `value` fields' schema entries lose their `title` key, a
  pydantic/JSON-Schema side effect of moving the constraint out of `Field`;
  no `pattern` keyword was ever emitted for these two fields either before
  or after, since pydantic silently dropped the invalid keyword at schema-
  generation time rather than raising there too).
- Added `_._validate_value` to `whitelist.py`'s existing
  `@field_validator`/`@model_validator` false-positive section (same pattern
  as `_._validate_status`/`_._validate_version` etc.) since vulture flags
  the two new `_validate_value` methods as unused.
- 618 tests project-wide, all passing (no count change — this fixes
  previously-failing tests, doesn't add new ones). `ruff format --check`/
  `ruff check`/`vulture` clean; `specmgr schema` exits 0 (unchanged) on a
  second run; `specmgr docs` regenerated (picks up the `body.py`/
  `whitelist.py` changes).

#### 2026-08-14 (continued) — Tasks 2.4-2.12 implemented: `req_schema.json` now generated (JSON Schema 2020-12) via `specmgr schema`

Implements the plan queued in the entry directly below. Phase 1 and Phase 2
are now both fully complete.

- **Task 2.4**: `req/models/v1/body.py`'s `Requirement` fields and every
  section's `items`/`value` field now carry `Field(description=...)`;
  `RelatedArtifacts`'s four optional sub-fields got the same treatment for
  consistency; every `items: list[MarkdownListItem]` field gained
  `min_length=1` plus a "must contain at least one item" description.
- **Task 2.5**: verified the **class** docstrings (the only ones
  `model_json_schema()` surfaces) were already self-contained from the
  2026-08-14 audit entry below; only `body.py`'s **module**-level docstring
  still referenced `models.adr.v1`/`req_reference.md`, cleaned up for
  consistency even though it never reaches the emitted schema.
- **Task 2.6**: shortened `MarkdownListItem`'s (~2.7k → ~1.1k chars) and
  `MarkdownParagraph`'s (~1.3k → ~0.7k chars) **class** docstrings in
  `models/md/` — method docstrings (`get_extent`/`from_text`/`__str__`,
  never surfaced in a schema) untouched. This is `feat-5-md-model-parser`
  owned code; done as a post-closure change and logged in that feature's
  own Recent Updates (2026-08-14 entry), same "downstream feature triggers
  a fix in the closed engine" precedent as its 2026-08-12/13 entries. Net
  effect on `req_schema.json`'s total size was roughly a wash against
  Task 2.4's own additions — the benefit is capping what these two shared
  base classes contribute per `$ref`, not shrinking this particular
  schema's overall byte count.
- **Task 2.7/2.8**: new `commands/schema.py` — `generate_req_schema()`
  (pure function, `ReqDocument.model_json_schema()` + explicit `$schema`
  injection, since Pydantic v2 omits it by default) and the `specmgr schema` Typer command, registered in `cli.py`/`commands/__init__.py`.
  Built on a `_GENERATORS: dict[str, Callable[[], str]]` registry
  (`{"req": generate_req_schema}` today); `--type` restricts to one
  registered name, omitting it generates all; each type's output goes to
  `{output_dir}/{type}_schema.json` (default `docs/`). The command compares
  old vs. new content per file and exits 1 if anything changed (or didn't
  exist yet), while still writing the file either way — verified manually:
  first run exits 1 (file didn't exist), second run exits 0 (unchanged), an
  unknown `--type` exits 1 without writing anything.
- **Task 2.9**: added a "Make sure `docs/req_schema.json` is correct" step
  to `.github/workflows/ci.yml`'s Python-3.13-only job, right after the
  `docs/adr/README.md` step — just runs `specmgr schema` and relies on its
  own exit code (no `git diff --exit-code`, unlike the `docs`/`adr-toc`
  steps).
- **Task 2.10**: added a `specmgr-schema` local hook to
  `.pre-commit-config.yaml`, scoped to
  `src/biz/dfch/specmgr/(req/models/v1|models/md)/**/*.py`, entry `uv run --frozen specmgr schema` (no `--type` — always "all", future-proofed for
  when more doc types register). Verified with `uv run --frozen pre-commit run specmgr-schema --files src/biz/dfch/specmgr/req/models/v1/body.py`
  (passed).
- **Task 2.11**: `tests/commands/test_schema.py` — 14 new tests: valid
  JSON/deterministic output, `$schema` is the 2020-12 URI,
  `frontmatter`/`body` structural assertions, `--type req` vs. no-option
  ("all") file selection, unknown `--type` exits 1 without writing, exit 0
  when unchanged vs. 1 when missing/stale, `--output-dir` auto-creation.
  618 tests project-wide (up from 604), no regressions.
- Regenerated `docs/api/` and `docs/GENERATED.md` (`specmgr docs`, picks up
  the new `commands/schema.py` module and the shortened
  `MarkdownListItem`/`MarkdownParagraph` docstrings) and confirmed
  `docs/adr/README.md` (`specmgr adr-toc`) has no drift. `ruff format --check`/`ruff check`/`vulture` all clean throughout.

#### 2026-08-14 (continued) — `req_schema.json` generation planned: 2020-12 dialect, generic `specmgr schema` command, Tasks 2.7-2.12 queued

- Decided (Decisions Made) that `req_schema.json` (Task 1.2) will be
  **generated** from `ReqDocument.model_json_schema()` rather than
  hand-authored like `uc_schema.json`, and will use Pydantic v2's native
  **JSON Schema 2020-12** dialect rather than the draft-07 Task 1.2
  originally specified — avoids lossy `$defs`→`definitions` conversion for
  a dialect with no known consumer yet.
- Queued Tasks 2.7-2.12 to implement this: `generate_req_schema()` (2.7,
  depends on the docstring cleanup in 2.4-2.6 landing first so the emitted
  schema is clean on first generation); a new **generic** `specmgr schema`
  CLI command (2.8, `commands/schema.py`) — named `schema`, not
  `req-schema`, since more doc-type schemas are expected later — built on
  a doc-type generator registry (`{"req": generate_req_schema}` today), a
  `--type` option to restrict to one registered type, and "generate all
  registered types" as the no-option default; the command exits 1 if any
  regenerated file differs from what was already on disk, so CI can rely
  on the exit code directly instead of a separate `git diff --exit-code`
  step; CI wiring (2.9); a pre-commit hook that always runs `specmgr schema` with no `--type` (2.10, future-proofed for when more types are
  registered); tests (2.11); and a final README status sync-up (2.12).

#### 2026-08-14 (continued) — Requirements/Acceptance Criteria checklists synced with actual progress

- The top-level Requirements (REQ-001..005) and Acceptance Criteria
  (ACC-001..005) checklists had drifted out of sync with the canonical Task
  List and Recent Updates — all ten checkboxes were still unchecked despite
  Phase 1/2 being complete and Phase 3 partially so. Checked off
  REQ-001..004 and ACC-001/003/004, which the completed Task List entries
  and passing tests already substantiate; left REQ-005/ACC-002/ACC-005
  unchecked since MCP prompts/resources and characteristics "filtering"
  remain unimplemented.
- Fixed REQ-005's parenthetical, which pointed at "Task 2.1" (the Pydantic
  model task) instead of Task 3.1 ("Define MCP tools, prompts, and
  resources for REQ management").
- Fixed REQ-003's stated path (`models/req/v1/`) to match what was actually
  implemented (`req/models/v1/`), and updated Design Notes' "decision
  deferred until spec phase" wording for the same model-location question,
  which had never been revisited after Task 2.1 actually settled it.

#### 2026-08-14 Docstrings audited against actual MCP schema exposure; follow-up tasks queued

- Added concise class docstrings to every `req/models/v1/body.py` section
  class and to `Requirement` itself (agent-annotation request).
- Verified against the installed `mcp>=2.0.0` SDK (`mcp.server.mcpserver`)
  exactly how these surface to a calling agent: `model_json_schema()` builds
  the tool's `outputSchema` at `tools/list` time, and every class docstring
  lands verbatim as that type's `$defs[...].description` — confirmed via a
  live `Requirement.model_json_schema()` dump. Field/attribute docstrings are
  **not** picked up automatically (only explicit `Field(description=...)`
  is); `required`/`anyOf ... null` already communicates mandatory/optional
  structurally. Per-call tool results (`_convert_to_content`) only ever
  serialize field values (`model_dump`/`pydantic_core.to_json`) — no
  docstring text is ever resent per call, only once at discovery.
- Follow-up: Tasks 2.4-2.6 queued to (1) add field-level descriptions with
  constraints, (2) make class docstrings self-contained (no references to
  `models/adr/v1` or `req_reference.md`, which an agent can't necessarily
  read at runtime), and (3) shorten the shared `models/md` base classes'
  docstrings that get inlined into every schema referencing them.

#### 2026-08-13 (continued) — upstream `MarkdownSection.text` leaf-serialization bug found and fixed

While reviewing `parse_req`'s output, noticed `Description`/`MoreInformation`/
`Notes` (the three bare leaf `MarkdownSection2`s in `body.py` — no `value`/
`items` field of their own) serialized via `model_dump()` to just their
heading text (e.g. `{"text": "Notes"}`), with the entire prose body silently
missing. Root cause was upstream in `feat-5-md-model-parser`'s shared engine,
not this feature's own model code: `MarkdownSection.text`'s computed_field
always extracted only the heading, regardless of leaf vs. composite, even
though a leaf's `_value` already held the complete heading+body extent
verbatim. Fixed at the source (`models/md/markdown_section.py`) rather than
worked around here by adding `value: MarkdownParagraph` fields to
`Description`/`MoreInformation`/`Notes` — the fix makes `.text` return the
complete extent for *any* leaf `MarkdownSection`, so REQ's own body model
needed no change at all. Full details, root cause, and fix recorded in
`feat-5-md-model-parser`'s own Recent Updates (2026-08-13 entry) since it
owns that module; noted here only because it was discovered through this
feature's own `parse_req` tool.

- Extended `tests/req/tools/test_parse_req.py`'s `_VALID_DOC` fixture with
  `## More Information`/`## Notes` sections and added
  `test_model_dump_surfaces_leaf_section_body_content`, a dedicated
  regression test asserting `model_dump()` now surfaces the full body text
  (heading included) for `description`/`more_information`/`notes` — REQ
  test count now 21 (up from 19), 604 tests project-wide.

#### 2026-08-13 Body model, reference document, parser, and `parse_req` MCP tool completed

- **Task 1.1.2 COMPLETED**: `req/models/v1/body.py` defines the full REQ body hierarchy on top of `feat-5-md-model-parser`'s generic `models/md` engine (`MarkdownStr`/`MarkdownSectionN`/`MarkdownParagraph`/`MarkdownListItem`), the same approach `uc/models/v2` uses — not a hand-written token parser like `uc/models/v1`/`models/adr/v1`. `Requirement` (H1, `@alias(".+", REGEX)` to accept any title) has: `statement` (the requirement-statement paragraph directly under the H1, before any H2); mandatory `description`/`characteristics`/`level`/`source`; optional `priority`/`tags`/`related_artifacts`/`more_information`/`notes`. `related_artifacts` nests four optional H3 subsections (`requirements`/`decisions`/`goals`/`acceptance_criteria`), each a bullet list of `{ID}: {description}` references (e.g. `REQ-9687: ...`, `DEC-2703: ...`). All section classes rely on the engine's default `SPACE_SEPARATED` alias (PascalCase class name → heading text), no explicit `@alias` needed beyond `Requirement`'s own.
- **Task 1.3 COMPLETED** (ahead of Task 1.2): `.specmgr/feat/feat-6-requirement-artifact/req_reference.md` — a full sample requirement ("Maximum Engine Temperature") exercising every section — plus `req_reference.ast` (its markdown-it token dump). Used directly as the parser's own test fixture rather than a separate, hand-maintained example.
- **Task 2.1 COMPLETED**: `req/models/v1/document.py` — `ReqDocument(frontmatter: ReqFrontmatter, body: Requirement)`, mirroring `uc.models.v2.document.UcDocument`.
- **Task 2.2 COMPLETED**: `req/models/v1/parser.py` — `parse_req(text) -> ReqDocument`, mirroring `uc.models.v2.parser.parse_uc` line-for-line (`frontmatter.loads()` → `_stringify_metadata()` → `ReqFrontmatter.model_validate()` → `Requirement.from_text(format_text(post.content))` → `ReqDocument(...)`). Same two uncaught error channels: `AssertionError` for structural failures (unrecognized/missing heading), `pydantic.ValidationError` for field/frontmatter validation failures — no dedicated `ReqParseError`.
- **Task 3.1/3.2 PARTIALLY COMPLETED**: `req/tools/parse_req.py` — `@mcp.tool()` wrapper (`parse_req(path: str) -> ReqDocument`), reading the file from disk and delegating to the parser, mirroring `uc.tools.parse_uc` exactly (including its docstring's error-propagation contract). `req/tools/__init__.py` and `req/__init__.py` added for registration; `server.py` now imports `req` alongside `adr`/`general`/`uc`, and `parse_req` appears in `mcp.list_tools()`. No `_paths.py`/`_io.py`/id-based file resolution yet (same as `uc/tools/`'s current scope) — the tool takes a raw filesystem path, not an id.
- **Tests**: `tests/req/models/v1/test_parser.py` (5 tests: minimal doc, full reference-document round-trip, frontmatter-absent defaults, invalid status → `ValidationError`, malformed structure → `AssertionError`) and `tests/req/tools/test_parse_req.py` (5 tests: happy path, `model_dump()` surfaces `MarkdownParagraph`-backed field content via its `text` computed field, invalid frontmatter, malformed structure, nonexistent file) — 19 REQ tests total, 600 project-wide (no regressions). `ruff format`/`ruff check` clean, `vulture` clean (9 new whitelist entries added for body.py's Pydantic fields, same false-positive pattern as UC's existing entries: `statement`, `characteristics`, `tags`, `source`, `related_artifacts`, `requirements`, `decisions`, `goals`, `acceptance_criteria`).

#### 2026-08-13 Task 1.1.1 completed — REQ frontmatter

- **Task 1.1.1 COMPLETED**: Created `src/biz/dfch/specmgr/req/models/v1/frontmatter.py` with `ReqFrontmatter(MarkdownFrontmatter)` subclass, narrowing:
  - `type: Literal["req"] = "req"` (fixed discriminator)
  - `status`: 7-value closed set (`draft`, `proposed`, `accepted`, `superseded`, `deprecated`, `rejected`, `implemented`) — ADR's 6 values plus `"implemented"` since requirements track implementation beyond acceptance
  - Inherits `id`, `created`, `updated`, `version` unchanged from base
  - Blank/None normalization correct (blank status → "draft", blank optional → None)
- Created `tests/req/models/v1/test_frontmatter.py` — 8 test cases mirroring existing patterns, all passing. 590 tests total (no regressions), ruff format/check clean, vulture clean.

### Decisions Made

- **Characteristics/Tags modeled as flat lists, not key-value pairs**: REQ-002 originally described "characteristics (key-value pairs or tags)". The implemented `Characteristics`/`Tags` sections are both simple bullet/numbered lists (`list[MarkdownListItem]`, e.g. "Safety"/"Reliability" or "Combustion Engines"/"Vehicles") rather than a key-value map. This is scoped entirely to this feature's own implementation details (not architecture-level), so it is logged here rather than as a full ADR. Revisit if a future requirement needs structured key-value metadata rather than a flat tag/category list.
- **Body model built on the generic `models/md` engine (v2-style), not a hand-written parser**: Unlike `uc/models/v1`/`models/adr/v1`'s custom `markdown_it`-token-based parsers, REQ's body (`body.py`) and parser (`parser.py`) are built directly on `feat-5-md-model-parser`'s `MarkdownStr`/`MarkdownSectionN` engine from day one — the same approach `uc/models/v2` migrated to. No REQ v1-style hand-written parser was ever written or needs to be superseded.
- **`req_schema.json` (Task 1.2) deferred, not blocking**: the reference document (`req_reference.md`) plus the Pydantic model tree (`body.py`, `document.py`, `frontmatter.py`) already fully define and enforce the schema in practice; a standalone JSON Schema draft-07 file adds a second, hand-synced source of truth with no consumer yet. Revisit if/when an external tool needs a JSON Schema artifact specifically.
- **JSON Schema dialect: 2020-12 (native Pydantic v2 output), not draft-07**: Task 1.2 originally specified "JSON Schema draft-07", matching the existing hand-authored `uc_schema.json`'s dialect (`.specmgr/feat/feat-4-use-cases/v2/uc_schema.json`). REQ's schema is instead **generated** directly from `ReqDocument.model_json_schema()` — Pydantic v2's native output (JSON Schema draft 2020-12: `$defs` not `definitions`, `prefixItems` where applicable). Converting to draft-07 would require lossy post-processing (`$defs`→`definitions`, `$ref` rewriting; some 2020-12-only keywords have no exact draft-07 equivalent) purely to match a dialect with no known external consumer yet (see the entry above). This deliberately diverges from `uc_schema.json`'s hand-authored draft-07 precedent — revisit if a future consumer specifically requires draft-07. Scoped to this feature's own generated-artifact choice, not a repo-wide architectural decision, so logged here rather than as a full ADR.

### Related PRs / Commits

None yet.
