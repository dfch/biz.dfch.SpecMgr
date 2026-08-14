---
created: 2026-08-13
id: feat-6-requirement-artifact
status: in-progress
updated: 2026-08-14
version: 1.5.0
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
- [x] Task 2.3: Cross-field model validators (if any invariants arise from the specification) — depends on: Task 2.1 — status: **closed, not applicable (2026-08-14)** — no cross-field/model-level invariant exists anywhere in the current spec (unlike UC's extension/sub-variation step-reference resolution); the one candidate, validating `related_artifacts`' cross-reference IDs against other documents, is explicitly out of scope for this feature (see Scope) and wouldn't be a `@model_validator` in any case, since it needs data outside the document being validated. Re-open only if a genuine same-document cross-field rule is identified later.
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
- [x] Task 3.3: Implement CLI commands (`req-parse`, etc.) — depends on: Task 3.2 — status: **completed (2026-08-14)** — `commands/req_parse.py` (`req-parse <path> [--format json|markdown]`), registered in `cli.py`/`commands/__init__.py`. Scope narrowed to path-based `req-parse` only (mirroring `req.tools.parse_req`'s own path-based signature); no `req-get` (id-based) command, since REQ still has no id → file-path lookup layer (`_paths.py`/`_io.py` equivalent) — see Decisions Made.
- [x] Task 3.4: Add a `"$comment"` schema-version marker (e.g. `"v1"`, matching `req/models/v1`'s package version — not `"req v1"`, since the doc type is already clear from the file/resource identity) to `generate_req_schema()`'s emitted JSON, so a caller can detect a REQ schema layout change without diffing the whole file — depends on: Task 2.7 — status: **completed (2026-08-14)** — `SCHEMA_COMMENT_VERSION = "v1"` constant added to a new `req/models/v1/_util.py` (mirroring `models/adr/v1/_util.py`'s precedent), re-exported from `req/models/v1/__init__.py`, and injected as `generate_req_schema()`'s `$comment` key. `docs/req_schema.json` regenerated.
- [x] Task 3.5: Add `specmgr://req/schema` MCP resource — reads the persisted `docs/req_schema.json` directly from disk (trusts the `specmgr-schema` pre-commit hook to keep it current, same trust model as `adr-toc`'s `docs/adr/README.md`; no `commands/schema.py`/`typer` import, no on-the-fly regeneration). URI is deliberately unversioned (see Decisions Made) — depends on: Task 3.4 — status: **completed (2026-08-14)** — `req/resources/req_schema.py` (new `req/resources/` sub-package, registered from `req/__init__.py`); reads and `json.loads()`s a fixed path (no env var — this is a build artifact of the package's own source tree, not user-authored content), returning a parsed `dict`; missing/corrupted file raises `FileNotFoundError`/`json.JSONDecodeError` uncaught. Path resolution factored into a new, dependency-free `biz/dfch/specmgr/_paths.py` (`REPO_ROOT`/`DOCS_DIR`), shared with (and replacing the previously-duplicated computation in) `commands/schema.py`, so neither the `cli` extra (`typer`) nor the `mcp` extra leaks into the other's import graph.
- [x] Task 3.6: Add `specmgr://req/...` resources and tools: get_example - return an example file. The example file will be served by reading a file from disk (as we already do with the schema). We will search the example as markdown (maybe we have to encode this?) - opinions on this? The file must exist on disk (build time guarantee). Hard exception if not true. — depends on: Task 3.2 — status: **completed (2026-08-14)** — implemented as the `get_req_example` tool (domain-qualified, not the task's literal "get_example" wording) plus the `specmgr://req/example` resource (unversioned URI, matching the task's own wording and `specmgr://req/schema`'s precedent) — see Recent Updates and Decisions Made for the packaged-data storage choice, the raw-markdown/no-encoding return shape, and the naming rationale.
- [ ] Task 3.7: Add `specmgr://req/...` resources and tools: get_template - return a template with all optional field and example text - very similar to the task 3.6. But this is not a full example, but a file with all fields and "blind text" (short lorem ipsum or similar) - same mechanism as in task 3.6. I already created a template file: src/biz/dfch/specmgr/req/resources/data/req_template.md.
- [ ] Task 3.8: Discuss `specmgr://req/...` resources and tools and prompts: discuss what is useful for this artifact type

**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-14**: Phase 1 (Specification) and Phase 2 (Pydantic Models & Parser) are both **fully complete**, including `req_schema.json` (Task 1.2), now generated (not hand-authored) via a new generic `specmgr schema` CLI command (JSON Schema 2020-12), with CI wiring and a pre-commit hook keeping it in sync. Phase 3 (MCP Surface) now has two tools (`parse_req`, `get_req_example`) and two resources (`specmgr://req/schema`, `specmgr://req/example`); the generated schema carries a `"$comment": "v1"` layout-version marker (Task 3.4). `specmgr req-parse` (Task 3.3) is the first REQ CLI command. Prompts and Tasks 3.7 (`get_template`)/3.8 (design discussion) remain not-started.

### Blockers

None.

### Recent Updates

#### 2026-08-14 (continued) — Task 3.6 implemented: `get_req_example` tool + `specmgr://req/example` resource

- New packaged data file `src/biz/dfch/specmgr/req/resources/data/req_example.md`
  (a byte-for-byte copy of `.specmgr/feat-6.../req_reference.md`'s content) is
  declared as real **package data** in `pyproject.toml`'s
  `[tool.setuptools.package-data]` (`"biz.dfch.specmgr.req.resources" = ["data/*.md"]`) and read via `importlib.resources` -- the first use of that
  module anywhere in this codebase. Verified end-to-end: built the wheel
  (`python -m build --wheel`), confirmed `req_example.md` is actually inside
  it, installed it into a throwaway venv (no editable/source checkout) with
  the `mcp` extra, and confirmed `get_req_example()`/`req_example()` both read
  it successfully. This is a strictly stronger guarantee than
  `docs/req_schema.json`'s `DOCS_DIR`-based read (`_paths.py`'s own docstring
  already documents that approach only resolves from an editable/source
  checkout) -- see Decisions Made.
- New `req/_data.py` -- a small, stdlib-only, framework-free module (no
  `mcp`/`typer` import) exposing a patchable module-level `_EXAMPLE_PATH`
  (an `importlib.resources` `Traversable`) and `read_req_example_text() -> str`. Lives directly under `req/`, not `req/tools/` or `req/resources/`,
  so neither of those two sub-packages needs to import from the other just
  to share this one file read -- both import `req._data` directly.
- New `req/tools/get_req_example.py` (`@mcp.tool()`) and
  `req/resources/req_example.py` (`@mcp.resource("specmgr://req/example", mime_type="text/markdown")`), both thin wrappers around
  `_data.read_req_example_text()`. Registered in `req/tools/__init__.py`,
  `req/resources/__init__.py`, `req/__init__.py`'s docstring, and
  `server.py`'s resource/tool docstring lists.
- Return shape: plain `str` (the example's full markdown, frontmatter
  included), `mime_type="text/markdown"` -- no base64/encoding needed, that's
  only relevant for binary resources. No in-memory cache (read fresh every
  call, consistent with every other tool/resource here); a missing/corrupted
  packaged file is an uncaught, hard `FileNotFoundError`, matching the task's
  own "build time guarantee, hard exception if not true" requirement.
- Tests: `tests/req/test_data.py` (4 tests: real packaged file, patched
  round-trip, fresh-read-per-call, missing-file `FileNotFoundError`),
  `tests/req/tools/test_get_req_example.py` (3 tests), and
  `tests/req/resources/test_req_example.py` (4 tests, including one asserting
  the tool and the resource return identical content) -- 649 tests
  project-wide (up from 638), no regressions. `ruff format --check`/
  `ruff check`/`vulture` clean; `specmgr docs` regenerated (3 new module
  pages: `req._data`, `req.tools.get_req_example`,
  `req.resources.req_example`); `specmgr schema`/`specmgr adr-toc` both
  confirmed to have no drift (this task never touches either artifact).
- `.specmgr/feat-6.../req_reference.md` (Task 1.3's parser test fixture) was
  deliberately **not** unified with the new packaged file -- both now hold
  the same content independently, with no shared source and no enforced
  sync. See Decisions Made for the trade-off this accepts.

#### 2026-08-14 (continued) — Task 3.3 implemented: `specmgr req-parse` CLI command

- New `src/biz/dfch/specmgr/commands/req_parse.py` — the first REQ-specific CLI
  command, registered as flat top-level `specmgr req-parse <path>`
  (Typer auto-derives the hyphenated name from the `req_parse` function, same
  as `adr_toc` → `adr-toc`), consistent with this repo's existing flat command
  list (no sub-app/command-group pattern introduced).
- Path-based only, mirroring `req.tools.parse_req`'s own `Path(path).read_text(...)`
  → `parse_req(text)` flow — **no `req-get`** (id-based lookup): REQ has no
  `_paths.py`/`_io.py` equivalent to ADR's yet (Task 3.1/3.2 note this gap
  explicitly), so an id → file-path resolver would need to be built first;
  deferred to a future task rather than bundled into this one. Narrows Task
  3.3's original "`req-get`, `req-parse`, etc." wording down to just
  `req-parse` — see Decisions Made.
- Two output formats: `--format json` (default) prints the full parsed
  `ReqDocument` as `rich`-syntax-highlighted JSON (`Console.print_json`);
  `--format markdown` re-reads the original file, splits it into its raw
  YAML frontmatter block and markdown body, reformats the body via the
  existing `format_text()` helper (`models/md/_markdown.py`, the same one
  `general.tools.mdformat` uses) **without writing anything back to disk**,
  and renders both through `rich` (`Syntax` for the frontmatter, `Markdown`
  for the body). This is the first use of the `rich` dependency anywhere in
  `src/` — previously declared in the `cli` extra (`pyproject.toml`) but
  never actually imported.
- Parse errors (missing file → `OSError`, malformed structure →
  `AssertionError`, invalid field values → `pydantic.ValidationError`) are
  caught here and reported via `typer.echo(f"Error parsing '{path}': {ex}")`
  (the original exception's message included) followed by `typer.Exit(1)` —
  deliberately diverging from the parser/MCP tool's own "let it raise"
  philosophy, since a CLI should not surface a raw Python traceback for an
  expected failure mode. An unknown `--format` value is rejected the same
  way `schema.py`'s unknown `--type` is (plain `typer.echo` + `typer.Exit(1)`,
  no `err=True`, matching this repo's existing convention across all other
  commands).
- Tests: `tests/commands/test_req_parse.py` (10 tests, mirroring
  `test_schema.py`'s split between a pure-helper test class and a
  CLI-wrapper test class) — 638 tests project-wide (up from 628), no
  regressions. `ruff format --check`/`ruff check`/`vulture` clean;
  `specmgr docs` regenerated (new `commands.req_parse` module page).

#### 2026-08-14 (continued) — Task 3.5 implemented: `specmgr://req/schema` MCP resource

- New `req/resources/` sub-package (`req/resources/req_schema.py` + `__init__.py`),
  registered from `req/__init__.py` (`from . import resources, tools`) — the first
  `resources` sub-package under `req/`, mirroring `adr/`'s
  `tools`/`prompts`/`resources` shape.
- `req_schema()` reads `docs/req_schema.json` fresh on every call (no
  in-memory cache) and returns `json.loads()`'d content as a `dict[str, Any]` — chosen over a raw-`str` return after weighing fidelity
  (byte-identical to the committed file) against consistency with every
  other resource in this codebase (`version_info`/`adr_list`/`adr_get` all
  return a structured type that FastMCP serializes) and against turning a
  corrupted on-disk file into a hard failure at read time. Schema
  *presence* is a build-time guarantee (the `specmgr-schema` pre-commit
  hook/CI step), so a missing file raises `FileNotFoundError` and a
  corrupted one raises `json.JSONDecodeError`, both uncaught — no
  defensive handling, matching this codebase's existing let-it-raise
  convention.
- Path is a **fixed** location, not configurable via an env var (unlike
  `adr.tools._paths.adr_base_dir`'s `SPECMGR_ADR_DIR`) — `docs/req_schema.json`
  is a build artifact of this package's own source tree, not user-authored
  content living elsewhere, so there's no meaningful "different location" to
  override to.
- New `biz/dfch/specmgr/_paths.py` — a top-level, dependency-free module
  (only `pathlib`) exposing `REPO_ROOT`/`DOCS_DIR`, computed by climbing
  from `__file__`. Both `commands/schema.py` (the `cli` extra) and
  `req/resources/req_schema.py` (the `mcp` extra) import it, so neither
  extra's optional dependency (`typer`/`mcp`) leaks into the other's import
  graph — the Decisions Made entry below already ruled out importing
  `commands.schema` directly from the resource for exactly this reason;
  this factors out the *path* computation (previously duplicated inline in
  `commands/schema.py`) into a shared home instead of a second duplicate.
  Only resolves correctly from an editable/source checkout — a built,
  non-editable install doesn't ship `docs/` as package data, so this would
  hard-fail for a real `pip install` consumer; accepted as out of scope
  (no `mcp.run()` caller exists yet regardless, per AGENTS.md).
- Tests: `tests/req/resources/test_req_schema.py` (5 tests: real
  committed-schema smoke test, patched-file round-trip, no-cache/fresh-read
  regression, missing-file `FileNotFoundError`, corrupted-file
  `json.JSONDecodeError`) and `tests/test_paths.py` (2 tests: `REPO_ROOT`
  sanity-checked against `pyproject.toml`'s presence, `DOCS_DIR == REPO_ROOT / "docs"`) — 628 tests project-wide (up from 621), no
  regressions. `ruff format --check`/`ruff check`/`vulture` clean;
  `specmgr schema`/`specmgr docs`/`specmgr adr-toc` all regenerated with no
  further drift (`docs/req_schema.json` itself is byte-identical --
  `commands/schema.py`'s only change was importing the shared path
  constant instead of computing its own).

#### 2026-08-14 (continued) — Task 3.4 implemented: `"$comment": "v1"` schema-layout version marker

Implements the design queued in the "Tasks 3.4/3.5 queued" entry below.

- Added `SCHEMA_COMMENT_VERSION = "v1"` to a new, private
  `req/models/v1/_util.py` — mirroring `models/adr/v1/_util.py`'s existing
  `SCHEMA_MAJOR_VERSION`/`CURRENT_SCHEMA_VERSION` precedent, so the value
  can't silently drift from the package's own `v1` folder name the way a
  hardcoded literal in `commands/schema.py` could. Re-exported from
  `req/models/v1/__init__.py`.
- `generate_req_schema()` now injects `schema_dict["$comment"] = SCHEMA_COMMENT_VERSION` alongside its existing `$schema` injection.
  `docs/req_schema.json` regenerated (one new top-level key).
- Deliberately **not** wired into `ReqFrontmatter.version`/any
  document-instance validation — this constant is scoped purely to the
  generated schema *artifact's* own layout version, a different concept
  from the frontmatter's semver (see Decisions Made, "Schema `"$comment"`
  version marker omits the doc-type name").
- Added `test_comment_is_schema_layout_version` to
  `tests/commands/test_schema.py` — 621 tests project-wide (up from 620),
  no regressions. `ruff format --check`/`ruff check`/`vulture` clean;
  `specmgr schema`/`specmgr docs`/`specmgr adr-toc` all regenerated with no
  further drift.

#### 2026-08-14 (continued) — Bug fix: `## Priority` accepted any digit string, not just 0-99

Found during the Task 2.3 review above: `Priority.value`'s `Field(description=...)`
documents the range as "0 to 99", but `_PRIORITY_PATTERN` was `r"^\d+$"` —
digits-only, no upper bound, so e.g. `"12345"` passed validation despite the
stated contract. Fixed by narrowing the pattern to `r"^(0|[1-9][0-9]?)$"`
(0-99, no leading zeros other than "0" itself); the `field_validator` logic
around it (checking `value.text`, since `value` is a `MarkdownParagraph`
model, not a plain string) is unchanged.

Not a Task 2.4/2.3 scope change (both are already closed/completed) — fixed
directly as a bug rather than reopening either task, since it's a pure
correctness fix with no design decision attached. Added two regression
tests to `tests/req/models/v1/test_parser.py`
(`test_priority_out_of_range_raises_validation_error`,
`test_priority_upper_bound_is_accepted`) — 620 tests project-wide (up from
618), all passing. `ruff format --check`/`ruff check`/`vulture` clean;
`specmgr schema` exits 0 (unchanged) since this validator was never
reflected in the emitted JSON Schema's `pattern` keyword either before or
after (same pydantic model-vs-string-field limitation noted in the
2026-08-14 `Level`/`Priority` regression entry below).

#### 2026-08-14 (continued) — Task 2.3 closed as not applicable

Reviewed against `req/models/v1/body.py`'s final state (post Tasks 2.4–2.12):
no cross-field/model-level invariant exists in the current spec. The only
candidate — validating `related_artifacts`' cross-reference IDs against
other documents on disk — is explicitly out of scope for this feature (see
Scope) and, even if in scope, would need data outside the document being
validated, so wouldn't be a `@model_validator` regardless. Closed Task 2.3
rather than leave it open indefinitely, resolving the inconsistency between
its `not-started` status and "Current Status"'s claim that Phase 2 is fully
complete.

#### 2026-08-14 (continued) — Tasks 3.4/3.5 queued: `specmgr://req/schema` resource design settled (unversioned URI, disk-read only, `$comment` version marker)

Design-only entry (no code yet) resolving an agent-discoverability question raised in review: how should an agent learn the REQ schema's structure via MCP tools/resources, beyond `parse_req`'s own `outputSchema` (already fully populated via `model_json_schema()`, per the 2026-08-14 docstring-audit entry below).

- Decided a new `specmgr://req/schema` resource is the right complement to `parse_req`'s tool-discovery `outputSchema` — the latter is free but host-dependent (not every MCP client surfaces it as agent-usable context); the former is an explicit, addressable fetch, mirroring the existing `specmgr://version`/`specmgr://adr/list`/`specmgr://adr/{id}` pattern.
- Decided it must only read the already-persisted `docs/req_schema.json` from disk — trusting the `specmgr-schema` pre-commit hook to keep it current — rather than importing `commands/schema.py`'s `generate_req_schema()` directly, which would leak the `cli` extra's `typer` dependency into the `mcp` extra's import graph.
- Decided the resource's URI stays unversioned (`specmgr://req/schema`, no `/v1`) — see Decisions Made.
- Decided to add a bare `"$comment"` version marker (e.g. `"v1"`, no doc-type prefix) to `generate_req_schema()`'s output so a caller can detect a schema-layout change without diffing the whole document — see Decisions Made.
- Queued as Task 3.4 (the `"$comment"` marker, in `generate_req_schema()`) and Task 3.5 (the resource itself, depends on 3.4).

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

- **`specmgr://req/schema` resource URI is unversioned (Task 3.5)**: considered addressing it as `specmgr://req/schema/v1` (mirroring `req/models/v1`'s package path) but rejected it — no existing resource or tool URI in this codebase ever exposes the internal `vN` model-package version: `specmgr://version`/`specmgr://adr/list`/`specmgr://adr/{id}` are all unversioned, and `parse_req`/`parse_uc` silently import from `models.v1`/`models.v2` respectively without either fact reaching the tool name, description, or signature. `vN` is purely an internal package-layout detail (ADR d54abe50's schema-versioning strategy), never part of the public MCP surface. Keeping `specmgr://req/schema` unversioned means it always means "the current REQ schema" — exactly like the tools already do — so a future `req/models/v2` (if REQ ever follows UC's v1→v2 migration) only changes what the resource reads internally, not its address, and callers never have to choose between two live, drifting endpoints. Scoped to this feature's own resource design, not a repo-wide architectural decision, so logged here rather than as a full ADR.

- **Schema `"$comment"` version marker omits the doc-type name (Task 3.4)**: the marker added to `generate_req_schema()`'s output is a bare version token (e.g. `"v1"`), not `"req v1"` — the doc type is already unambiguous from context (the file is `docs/req_schema.json`, the resource is `specmgr://req/schema`), so repeating it inside the value would be redundant. Purpose is narrowly to let a caller that cached an earlier fetch notice the schema's layout changed, without diffing the whole document.

- **`req-parse` scoped down to path-based only, no `req-get` (Task 3.3)**: Task 3.3 originally named `req-get`/`req-parse` as examples. Only `req-parse` (raw filesystem path, mirroring `parse_req`'s own signature) was implemented — `req-get` (by id) would need a REQ equivalent of `adr/tools/_paths.py`/`_io.py` (base-dir scan + id → path resolution) that does not exist yet and is out of this task's scope. Revisit once REQ gets its own id-based file-storage layer.

- **`req-parse --format markdown` reformats in-memory only, reusing `format_text()` rather than a new `render_req()`**: no `render_req()` (analogous to `render_adr()`) exists for REQ, and building one purely for CLI display purposes was rejected as unnecessary scope — the CLI instead re-reads the original file, splits frontmatter, and normalizes the body via the same `format_text()` helper `general.tools.mdformat` already uses, without ever writing back to disk. `--format json` (default) and `--format markdown` both render through `rich` (`Console.print_json`/`Syntax`/`Markdown`) — the first actual use of the `rich` dependency in `src/`, previously declared but unused. Both choices are scoped entirely to this command's own implementation, not architecture-level, so logged here rather than as a full ADR.

- **REQ example file shipped as package data, not read from `docs/` (Task 3.6)**: `req_schema.json`'s `DOCS_DIR`-based read (Task 3.5) only resolves correctly from an editable/source checkout -- `_paths.py`'s own docstring already documents this as an accepted, CI/dev-only-tool-scoped limitation. `get_req_example`/`specmgr://req/example` are general-purpose MCP capabilities any downstream consumer of the published package might call, not just dev/CI tooling, so the example markdown file is instead declared as real package data (`pyproject.toml`'s `[tool.setuptools.package-data]`, `src/biz/dfch/specmgr/req/resources/data/req_example.md`) and loaded via `importlib.resources` -- the first use of that mechanism in this codebase. Verified against an actual built wheel installed into a throwaway (non-editable) venv, not just the dev checkout. Revisit only if a future doc-type example needs the exact same treatment, at which point the pattern established here (a `_data.py` module + a `resources/data/` directory + a `package-data` entry) should be repeated, not re-designed.

- **`get_req_example`/`req_example`'s content returned as raw markdown text, not a parsed `ReqDocument` (Task 3.6)**: unlike `adr.resources.adr_get`'s parsed-object return, the point of an example is to show the literal document shape (including its YAML frontmatter block) for a human or LLM to read/learn from -- parsing it into a structured object first would lose that and add a pointless round-trip of a file that's always valid anyway. Returned as a plain `str` with `mime_type="text/markdown"`; no base64 or other encoding is used or needed, since that's only relevant for binary resource content.

- **Tool named `get_req_example`, not the task's literal `get_example` (Task 3.6)**: tool names are global across the whole MCP server's `tools/list`, unlike resource URIs which are already domain-scoped by their `specmgr://req/...` prefix. Every existing tool name in this codebase that isn't already domain-unambiguous is itself domain-qualified (`parse_req`, `parse_uc`; `get_adr`/`create_adr` are the one exception, but ADR is the only domain that has ever needed those verbs). A bare `get_example` would collide the day ADR or UC grows its own equivalent, so it was qualified up front. The resource URI (`specmgr://req/example`) keeps the task's literal wording since URIs are already domain-namespaced by construction.

- **`.specmgr/feat-6.../req_reference.md` and the new packaged `req_example.md` are intentionally kept as two separate, duplicated copies (Task 3.6)**: the former is a dev-only test fixture (`tests/req/models/v1/test_parser.py`) living outside `src/`; the latter must live inside `src/` to be packaged. Unifying them (e.g. having the parser test load the packaged copy instead) was considered and explicitly rejected in favor of the simpler, duplicated-content approach -- accepted trade-off: a future edit to one is not automatically reflected in the other, so both must be kept in sync by hand if either's sample data ever changes.

### Related PRs / Commits

None yet.
