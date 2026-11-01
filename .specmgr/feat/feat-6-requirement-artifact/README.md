---
created: '2026-08-13 00:00:00.000Z'
id: feat-6-requirement-artifact
status: done
updated: '2026-10-07T06:21:40.946Z'
version: 1.0.0
---

# Feature: Requirement (REQ) artifact template with characteristic assignment

## Plan

### Overview

Provide a markdown-based REQ artifact type for storing requirements with assignable characteristics. The REQ artifact follows the domain-first hierarchy (ADR ece4554b) and provides a structured template for capturing, organizing, and tracking requirements alongside existing document types (ADR, UC). A defining capability is the ability to assign arbitrary characteristics (metadata tags) to each requirement.

### Requirements

- REQ-001: Define the REQ markdown schema structure
- REQ-002: Support assigning characteristics (key-value pairs or tags) to requirements
- REQ-003: Pydantic models for REQ documents (`req/models/v1/` — domain-first path, see Design Notes)
- REQ-004: Parse and validate REQ documents from markdown
- REQ-005: MCP tools, prompts, and resources for REQ management (specified in Task 3.1, detailed further in Tasks 3.9-3.20) — completed: 8 tools (`parse_req`, `get_req_example`, `get_req_template`, `create_req`, `update_req`, `set_status_req`, `delete_req` (stub), `validate_req`), 5 resources (`specmgr://req/schema`, `/example`, `/template`, `/{id}`, `/list`), 2 prompts (`create_req`, `update_req`)

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — Requirements to be defined during specification phase
- [x] ACC-002: Verifies REQ-002 — Characteristics model supports assignment and retrieval — assignment/retrieval implemented (flat list); filtering formally moved to out of scope (see Scope), not a pending gap
- [x] ACC-003: Verifies REQ-003 — Pydantic models validate required/optional fields correctly
- [x] ACC-004: Verifies REQ-004 — Parser produces valid object tree; validation detects malformed input
- [x] ACC-005: Verifies REQ-005 — MCP surface follows ADR/UC domain-first pattern — REQ-005 is now complete (see above); the lifecycle surface intentionally diverges from ADR's granular section-mutation tools (Task 3.9's design decision), but still follows the same domain-first `req/tools`/`req/resources`/`req/prompts` layout

### Scope

#### Included

in this feature:

- Specification of the REQ markdown schema (to be defined)
- Pydantic models with characteristic assignment support
- Parser and validator for REQ documents
- MCP tools, prompts, and resources (after spec is defined)

#### Explicitly Out Of Scope

- Rendering/exporting requirements to non-markdown formats (to be determined in spec phase)
- Cross-referencing between requirements and other document types (future enhancement)
- Characteristics/tags filtering (e.g. querying/listing requirements by characteristic or tag value) — deferred during Task 3.9's design discussion; `specmgr://req/list` returns every requirement unfiltered (Task 3.18). Assignment and retrieval (the actual REQ-002 requirement) are fully supported; only filtering is out of scope. Revisit as a future enhancement if a real need arises.

### Dependencies

#### Depends On

- ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr` structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic `MarkdownFrontmatter` base)

#### Blocks

- None identified yet

### Design Notes

The REQ domain will follow the same patterns established by existing domains:

- Models live under `req/models/v1/` (decided and implemented — domain-first path, not shared `models/req/v1/`; see Task 2.1)
- Schema versioning follows the ADR vN strategy (ADR d54abe50's variant of this decision)
- `type: Literal["req"]` discriminator in frontmatter via `MarkdownFrontmatter` subclass (ADR bc5e18ad)

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

**Note on scope:** unlike Phases 1-3, this phase is cross-cutting infrastructure — it covers every registered domain (ADR, REQ, UC, `general`), not REQ specifically. Tracked here rather than in its own `feat-N-slug` folder because it was prompted directly by this feature's own Phase 3 REQ tools/resources being absent from `README.md`'s stale, hand-maintained table, and was carried out in the same working session as Phase 3's tail end — see Decisions Made.

**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

### Related Decisions

- e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in `.specmgr` with feature-driven work units
- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by document-type domain (domain-first hierarchy)
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for markdown document types

### Task List

#### Phase 100: Specification

- [x] Task 100.100: Define the REQ markdown schema — document required/optional fields, heading depth, list vs prose format, and the characteristics assignment model — depends on: none — status: **completed (2026-08-13)**
- [x] Task 100.105: Define REQ frontmatter (`req/models/v1/frontmatter.py` — `ReqFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["req"]`, 7-value status set: draft/proposed/accepted/superseded/deprecated/rejected/implemented) — depends on: none — status: **completed (2026-08-13)**
- [x] Task 100.107: Define REQ body structure (H1 title, required/optional H2/H3 headings, list vs prose format) and characteristics assignment model in the markdown body — depends on: Task 1.1.1 — status: **completed (2026-08-13)** — `req/models/v1/body.py`: `Requirement` (H1) with `statement` (requirement-statement paragraph), `description`/`characteristics`/`level`/`source` (mandatory H2), `priority`/`tags`/`related_artifacts`/`more_information`/`notes` (optional H2). `characteristics`/`tags` are modeled as simple bullet/numbered lists (`list[MarkdownListItem]`), not key-value pairs — see Decisions Made. `related_artifacts` nests four optional H3 subsections (`requirements`/`decisions`/`goals`/`acceptance_criteria`), each a bullet list of `{ID}: {description}` references.
- [x] Task 100.110: Draft `req_schema.json` from the specification — depends on: Task 1.1.2 — status: **completed (2026-08-14)** — produced via **generation**, not hand-authoring, and in **JSON Schema 2020-12**, not the draft-07 originally specified — see Tasks 2.7-2.9 and Decisions Made.
- [x] Task 100.120: Create a reference REQ document (`req_reference.md`) showing all fields with sample data — depends on: Task 1.2 — status: **completed (2026-08-13)** — `.specmgr/feat/feat-6-requirement-artifact/req_reference.md` (+ `req_reference.ast` markdown-it token dump), done ahead of Task 1.2 rather than after it; used directly as the parser's own round-trip test fixture.

#### Phase 110: Pydantic Models & Parser

- [x] Task 110.100: Write Pydantic model tree under `req/models/v1/` mirroring the schema — depends on: Task 1.3 — status: **completed (2026-08-13)** — `body.py` (all section classes, built on the generic `models/md` `MarkdownStr`/`MarkdownSectionN` engine from `feat-5-md-model-parser`, not a hand-written token parser), `document.py` (`ReqDocument(frontmatter, body)`, mirrors `UcDocument`).
- [x] Task 110.110: Implement `parse_req(text: str) -> ReqDocument` (free function, following `parse_adr`/`parse_uc` pattern) — depends on: Task 2.1 — status: **completed (2026-08-13)** — `req/models/v1/parser.py`; mirrors `uc.models.v2.parser.parse_uc` exactly: `frontmatter.loads()` → `ReqFrontmatter.model_validate()` (via `_stringify_metadata`) → `Requirement.from_text(format_text(...))`. Same two uncaught error channels as `parse_uc` (`AssertionError` for structural failures, `pydantic.ValidationError` for field/cross-field failures) — no dedicated `ReqParseError`.
- [x] Task 110.120: Cross-field model validators (if any invariants arise from the specification) — depends on: Task 2.1 — status: **closed, not applicable (2026-08-14)** — no cross-field/model-level invariant exists anywhere in the current spec (unlike UC's extension/sub-variation step-reference resolution); the one candidate, validating `related_artifacts`' cross-reference IDs against other documents, is explicitly out of scope for this feature (see Scope) and wouldn't be a `@model_validator` in any case, since it needs data outside the document being validated. Re-open only if a genuine same-document cross-field rule is identified later.
- [x] Task 110.130: Add field-level `Field(description=...)` (with constraints, e.g. "list must contain at least one item") to `Requirement`'s scalar/optional fields and section `items`/`value` fields — bare attribute docstrings are not picked up by `model_json_schema()`, only explicit `Field(description=...)` is — depends on: Task 2.1 — status: **completed (2026-08-14)** — also extended to `RelatedArtifacts`'s four optional sub-section fields (not literally "items"/"value", but the same optional-field-needs-a-description gap) and `min_length=1` added to every `items: list[MarkdownListItem]` field (`Characteristics`/`Tags`/`Requirements`/`Decisions`/`AcceptanceCriteria`/`Goals`).
- [x] Task 110.140: Rewrite `req/models/v1/body.py` class docstrings to be self-contained — remove references to `models/adr/v1` and `req_reference.md`, dev-only artifacts an agent reading the emitted JSON schema at tool-discovery time cannot necessarily fetch or read — depends on: Task 2.1 — status: **completed (2026-08-14)** — the **class** docstrings (the only ones `model_json_schema()` surfaces) already had no such references from the 2026-08-14 audit above; only the **module**-level docstring did, cleaned up for consistency even though it never reaches the emitted schema.
- [x] Task 110.150: Shorten verbose docstrings on shared `models/md` "base" classes referenced by REQ's schema (e.g. `MarkdownListItem` ~2.7k chars, `MarkdownParagraph` ~1.3k chars) — they get inlined into every schema `$defs` entry that uses them, inflating the tool-discovery payload every client fetches — depends on: none — status: **completed (2026-08-14)** — `MarkdownListItem` class docstring ~2.7k → ~1.1k chars, `MarkdownParagraph` ~1.3k → ~0.7k chars (method docstrings, never surfaced in a schema, left untouched); done as a post-closure change to `feat-5-md-model-parser` (which owns the module), logged in that feature's own Recent Updates per the established cross-feature precedent.
- [x] Task 110.160: Implement `generate_req_schema()` — pure function producing REQ's JSON Schema (2020-12 dialect, see Decisions Made) via `ReqDocument.model_json_schema()`, serialized deterministically (`indent=2, sort_keys=True` + trailing newline) — depends on: Task 2.4, Task 2.5, Task 2.6 — status: **completed (2026-08-14)** — `commands/schema.py`; also explicitly injects `$schema` (Pydantic v2's `model_json_schema()` omits it by default) so the file self-describes its own dialect.
- [x] Task 110.170: Implement `specmgr schema` CLI command (`commands/schema.py`, mirroring `commands/adr_toc.py`'s generate-function + Typer-wrapper shape) — named generically (not `req-schema`) since more doc-type schemas are expected later. Built on a doc-type generator registry (`{"req": generate_req_schema}` today); a `--type` option selects one registered type by name (only `req` valid for now); omitting it generates **all** registered types (today: just `req`), each written to its own `docs/{type}_schema.json`. Exits with code 1 if any regenerated file's content differs from what was already on disk (including the file not existing yet), so CI can rely on the exit code directly instead of a separate `git diff --exit-code` step — depends on: Task 2.7 — status: **completed (2026-08-14)** — registered in `cli.py`/`commands/__init__.py`; `docs/req_schema.json` generated and committed.
- [x] Task 110.180: Wire `specmgr schema` into `.github/workflows/ci.yml`'s Python-3.13-only job (alongside the existing `specmgr docs`/`specmgr adr-toc` steps) — run it and fail the build directly on its own exit code (no separate `git diff --exit-code` step needed for this artifact) — depends on: Task 2.8 — status: **completed (2026-08-14)**
- [x] Task 110.190: Add a local pre-commit hook scoped to `src/biz/dfch/specmgr/req/models/v1/**/*.py` (and `src/biz/dfch/specmgr/models/md/**/*.py`, since the shared engine feeds this schema) that runs `specmgr schema` with **no** `--type` — always regenerates all registered types, even though `req` is the only one today — depends on: Task 2.8 — status: **completed (2026-08-14)** — `specmgr-schema` hook in `.pre-commit-config.yaml`, verified with `pre-commit run specmgr-schema`.
- [x] Task 110.200: Tests for the generator and CLI (`tests/commands/test_schema.py`, mirroring `test_docs.py`/`test_adr_toc.py`) — deterministic output, `$schema` is the 2020-12 URI, structural assertions on `frontmatter`/`body`/`required`, `--type req` vs. no-option ("all") behavior, exit code 0 when unchanged vs. 1 when the on-disk file differs or is missing — depends on: Task 2.7, Task 2.8 — status: **completed (2026-08-14)** — 14 new tests, 618 project-wide (no regressions).
- [x] Task 110.210: Update Task 1.2's status/wording (2020-12, not draft-07; command is `specmgr schema`, not REQ-specific) and this feature's Recent Updates once Tasks 2.7-2.11 land — depends on: Task 2.7, Task 2.8, Task 2.9, Task 2.10, Task 2.11 — status: **completed (2026-08-14)**

#### Phase 120: MCP Surface & CLI

- [x] Task 120.100: Define MCP tools, prompts, and resources for REQ management — depends on: Phase 2 complete — status: **partially completed (2026-08-13)** — only the `parse_req` tool defined/implemented so far (mirrors `uc/tools/`'s current scope, which also only has `parse_uc`); prompts/resources and id-based file storage (`_paths.py`/`_io.py` equivalent) not yet specified.
- [x] Task 120.110: Implement MCP per specification (Task 3.1) — depends on: Task 3.1 — status: **partially completed (2026-08-13)** — `req/tools/parse_req.py` (`@mcp.tool()` wrapper, reads path from disk, delegates to `parser.parse_req`), `req/tools/__init__.py`, `req/__init__.py`; registered in `server.py` (`from . import adr, general, req, resources, uc`). Remaining Task 3.1 scope (prompts, resources, further tools) still not-started.
- [x] Task 120.120: Implement CLI commands (`req-parse`, etc.) — depends on: Task 3.2 — status: **completed (2026-08-14)** — `commands/req_parse.py` (`req-parse <path> [--format json|markdown]`), registered in `cli.py`/`commands/__init__.py`. Scope narrowed to path-based `req-parse` only (mirroring `req.tools.parse_req`'s own path-based signature); no `req-get` (id-based) command, since REQ still has no id → file-path lookup layer (`_paths.py`/`_io.py` equivalent) — see Decisions Made.
- [x] Task 120.130: Add a `"$comment"` schema-version marker (e.g. `"v1"`, matching `req/models/v1`'s package version — not `"req v1"`, since the doc type is already clear from the file/resource identity) to `generate_req_schema()`'s emitted JSON, so a caller can detect a REQ schema layout change without diffing the whole file — depends on: Task 2.7 — status: **completed (2026-08-14)** — `SCHEMA_COMMENT_VERSION = "v1"` constant added to a new `req/models/v1/_util.py` (mirroring `models/adr/v1/_util.py`'s precedent), re-exported from `req/models/v1/__init__.py`, and injected as `generate_req_schema()`'s `$comment` key. `docs/req_schema.json` regenerated.
- [x] Task 120.140: Add `specmgr://req/schema` MCP resource — reads the persisted `docs/req_schema.json` directly from disk (trusts the `specmgr-schema` pre-commit hook to keep it current, same trust model as `adr-toc`'s `docs/adr/README.md`; no `commands/schema.py`/`typer` import, no on-the-fly regeneration). URI is deliberately unversioned (see Decisions Made) — depends on: Task 3.4 — status: **completed (2026-08-14)** — `req/resources/req_schema.py` (new `req/resources/` sub-package, registered from `req/__init__.py`); reads and `json.loads()`s a fixed path (no env var — this is a build artifact of the package's own source tree, not user-authored content), returning a parsed `dict`; missing/corrupted file raises `FileNotFoundError`/`json.JSONDecodeError` uncaught. Path resolution factored into a new, dependency-free `biz/dfch/specmgr/_paths.py` (`REPO_ROOT`/`DOCS_DIR`), shared with (and replacing the previously-duplicated computation in) `commands/schema.py`, so neither the `cli` extra (`typer`) nor the `mcp` extra leaks into the other's import graph.
- [x] Task 120.150: Add `specmgr://req/...` resources and tools: get_example - return an example file. The example file will be served by reading a file from disk (as we already do with the schema). We will search the example as markdown (maybe we have to encode this?) - opinions on this? The file must exist on disk (build time guarantee). Hard exception if not true. — depends on: Task 3.2 — status: **completed (2026-08-14)** — implemented as the `get_req_example` tool (domain-qualified, not the task's literal "get_example" wording) plus the `specmgr://req/example` resource (unversioned URI, matching the task's own wording and `specmgr://req/schema`'s precedent) — see Recent Updates and Decisions Made for the packaged-data storage choice, the raw-markdown/no-encoding return shape, and the naming rationale.
- [x] Task 120.160: Add `specmgr://req/...` resources and tools: get_template - return a template with all optional field and example text - very similar to the task 3.6. But this is not a full example, but a file with all fields and "blind text" (short lorem ipsum or similar) - same mechanism as in task 3.6. I already created a template file: `src/biz/dfch/specmgr/req/resources/data/req_template.md`. — depends on: Task 3.2 — status: **completed (2026-08-14)** — implemented as the `get_req_template` tool plus the `specmgr://req/template` resource, mirroring Task 3.6's `get_req_example`/`specmgr://req/example` shape exactly (same `req/_data.py` packaged-data pattern, same naming rationale) — see Recent Updates and Decisions Made for the template's own parse-validity caveat (independently being addressed, see the template file's own in-progress edits).
- [x] Task 120.170: Make sure, that `docs/req_schema.json` is accessible by MCP server when the mcp is installed and not in DEV mode. If current location is not accessible by MCP then make a COPY of it (via pre-commit hook) to `src/biz/dfch/specmgr/req/resources/data/` and load from there as we already with `req_example.md`. — depends on: Task 3.5 — status: **completed (2026-08-14)** — see Recent Updates and Decisions Made.
- [x] Task 120.180: Discuss `specmgr://req/...` resources and tools and prompts: discuss what is useful for this artifact type — depends on: none — status: **completed (design discussion, 2026-08-14)** — conclusion: granular, ADR-style section-level mutation tools (`update_section`/`option_*`) are **not** worth building for REQ — REQ documents are short (the reference doc is 64 lines), the schema/example/template/LLM combination is already good enough for reliable whole-document authoring, and REQ has no ADR-style derived section (`## Pros and Cons of the Options`) that only tool-mediation could keep in sync. Instead, settled on a small, generic, id-based lifecycle surface, factored so it generalizes to future doc types (UC next) rather than being a one-off REQ design. Full design captured in Tasks 3.10-3.20 below; see Recent Updates for the full discussion trail and rationale.

- [x] Task 120.190: Generalize id → file-path lookup plumbing into the `general/` domain (shared by REQ now, UC later) — `general/tools/_doc_paths.py` (name TBD at implementation time): `doc_base_dir(type_name: str) -> Path` (single root env var `SPECMGR_DOCS_DIR`, default `docs`, per-type subdirectory `{root}/{type_name}/`, e.g. `docs/req/`), `ensure_doc_base_dir(type_name)`, `iter_doc_paths(base_dir)`, `find_doc_path_by_id(base_dir, id_, parse_fn, get_id_fn)`, `slugify(title)` (ported from `adr/tools/_paths.py`). **ADR is explicitly left untouched** (`SPECMGR_ADR_DIR`/`docs/adr` unchanged) — migrating it to this shared module is optional future cleanup, not bundled here — depends on: none — status: **completed (2026-08-14)** — `general/tools/_doc_paths.py` (name kept, no rename needed); `DocNotFoundError(LookupError)` added (not explicitly named in the task text, needed by `find_doc_path_by_id`); `find_doc_path_by_id` catches `(AssertionError, ValueError)` around `parse_fn`, generic enough to cover both `AdrParseError`/`pydantic.ValidationError` (ADR) and the `AssertionError`/`pydantic.ValidationError` pair `parse_req` raises, without depending on either. Not re-exported from `general/tools/__init__.py`, matching `adr/tools/_paths.py`'s own private (underscore-prefixed, not `@mcp.tool()`) module convention.
- [x] Task 120.200: `req/tools/_paths.py` + `_io.py`, thin wrappers over Task 3.10's generic module — `req_base_dir()`, `iter_req_paths()`, `find_req_path(base_dir, id_)` (using `parse_req` + `frontmatter.id`, skip-on-parse-failure, mirroring `adr/tools/_paths.py::find_adr_path`), `ReqNotFoundError`, `read_req(path)`, `load_by_id(base_dir, id_)` — depends on: Task 3.10 — status: **completed (2026-08-14)** — implemented exactly the listed surface, split as specified: `_paths.py` (`REQ_TYPE_NAME`, `ReqNotFoundError`, `req_base_dir()`, `ensure_req_base_dir()` (not explicitly listed, added for the future `create_req`/Task 3.12, mirroring `adr.tools._paths.ensure_adr_base_dir`), `iter_req_paths()` (zero-arg, unlike the generic/ADR `iter_*_paths(base_dir)` shape — resolves `req_base_dir()` internally, per the task's own literal signature), `find_req_path(base_dir, id_)`) and `_io.py` (`read_req(path)`, `load_by_id(base_dir, id_)`). No `write_req`/`render_req` — Task 3.9's design never renders a body from the parsed model, so none is needed. Neither module is re-exported from `req/tools/__init__.py`, matching `adr/tools/_paths.py`/`_io.py`'s own unexported-private-module precedent.
- [x] Task 120.210: `create_req(content: str) -> ReqDocument` tool — `content` is **body markdown only** (the `Requirement` H1 + sections), no frontmatter block. MCP builds the entire frontmatter itself: `id=uuid4()`, `type="req"`, `status="draft"` (always, never caller-supplied on create), `created=updated=now`, `version=CURRENT_SCHEMA_VERSION`. Validates `content` via `Requirement.from_text(format_text(content))` — failure raises uncaught (`AssertionError`/`pydantic.ValidationError`), nothing is written. Writes `{req_base_dir}/req-{id}-{slug}.md` (`slug` from the body's H1 title, mirroring ADR's filename scheme). No body rendering is ever needed — the caller's own already-validated text is persisted byte-for-byte; only the small frontmatter YAML block is code-generated — depends on: Task 3.11 — status: **completed (2026-08-14)** — see Recent Updates.
- [x] Task 120.220: `update_req(id: str, content: str) -> ReqDocument` tool — `content` is body markdown only, same shape as `create_req`. Reads the *existing* file first to preserve `id`/`type`/`status`/`created`/`version` unchanged; only `updated=now` changes. Validates the new body the same way as `create_req`; failure raises uncaught, nothing written. `status` is never settable here — see Task 3.14 — depends on: Task 3.11 — status: **completed (2026-08-14)** — see Recent Updates.
- [x] Task 120.230: `set_status_req(id: str, status: str) -> ReqDocument` tool — the only path that changes `status` (mirrors ADR's `  `, minus the `superseded_by`-composition special case, since `ReqFrontmatter.status` has no `"superseded by ..."` pattern — just the closed seven-value set). Also bumps `updated=now` — depends on: Task 3.11 — status: **completed (2026-08-15)** — see Recent Updates.
- [x] Task 120.240: `delete_req(id: str) -> NoReturn` tool — registered stub, always `raise NotImplementedError("delete_req is not yet implemented")`. Reserves the name/slot for a future real implementation (soft-delete via `status`, archival, or similar — undecided) without blocking the rest of this surface — depends on: Task 3.11 — status: **completed (2026-08-15)** — see Recent Updates.
- [x] Task 120.250: `validate_req(content: str, full: bool = False) -> bool` tool — a disk-free, id-free dry run, always returns `True` on success (mirrors `validate_adr`'s "successfully constructing the model *is* the validation" contract), raises uncaught on failure. Uses `frontmatter.loads(content)` to detect whether `content` carries a frontmatter block (`post.metadata` non-empty). `full=False` (default): `content` must be body-only — raises `ValueError` with a clear corrective message if a frontmatter block is detected instead. `full=True`: `content` must be a complete document (frontmatter + body, same shape `parse_req` expects for a file) — raises the symmetric `ValueError` if *no* frontmatter block is found. Body-only validation (`full=False`) is literally the same check `create_req`/`update_req` run internally, exposed standalone — depends on: none (parallel to Task 3.12/3.13, not blocking them) — status: **completed (2026-08-15)** — see Recent Updates.
- [x] Task 120.260: `specmgr://req/{id}` resource — single-document read by id (mirrors `specmgr://adr/{id}`). Supersedes the earlier considered `get_req` tool — id-based single-document read is a resource only, everything else in this surface is a tool — depends on: Task 3.11 — status: **completed (2026-08-15)** — see Recent Updates. **Revisited/superseded (2026-08-15) by `feat-7-various-improvements` Task 0.9 and ADR `ddfb1109-422d-4507-8dbc-dc5e4bec9614`**: in practice, LLMs/agents failed to reliably invoke this resource, so the `get_req` tool this task explicitly superseded was added after all, and `specmgr://req/{id}` was removed — REQ is now tool-only for id-based reads. This line is left otherwise unedited as a historical record; see the ADR for the full rationale, including why `specmgr://adr/{id}` was deliberately left untouched.
- [x] Task 120.270: `specmgr://req/list` resource — every document in the base directory, `ReqSummary` (id/title/status/filename, mirroring `AdrSummary`), unfiltered (characteristics/tags filtering was explicitly deferred earlier in the Task 3.9 discussion, see Recent Updates) — depends on: Task 3.11 — status: **completed (2026-08-15)** — see Recent Updates.
- [x] Task 120.280: `req/prompts/create_req.py` + `update_req.py` — narrate the tool sequence above (mirroring ADR's `create_adr`/`update_adr` prompts): *create* — check `specmgr://req/list` for an existing duplicate, fetch `specmgr://req/template` or `/example` as a starting point, draft the body against `specmgr://req/schema`, call `create_req(content)`; *update* — read `specmgr://req/{id}`, edit the body, call `update_req(id, content)`, and route any status change through `set_status_req` instead of `update_req` — depends on: Tasks 3.12, 3.13, 3.14, 3.17, 3.18 — status: **completed (2026-08-15)** — see Recent Updates. Task 3.20 (unrelated: `models/md` inline-HTML-comment allowance) remains **not-started**, out of scope for this change.
- [x] Task 120.290: Coordinate with `feat-5-md-model-parser`: extend `models/md/_markdown.py`'s `_assert_no_raw_html` to also permit `html_inline` tokens whose content starts with `<!--` (block-level HTML comments are already permitted; inline ones are not). Unblocks Task 3.7's known, currently-blocked template-annotation attempt (an inline comment on the same line as a value, e.g. `MUST <!-- one of: MUST/SHOULD/MUST NOT/SHOULD NOT/MAY -->`, rather than a second standalone paragraph, which is what actually broke `Level`/`Priority`'s single-paragraph structural check) — depends on: none — status: **completed (2026-08-15)** — see Recent Updates. Implemented differently than originally sketched: rather than editing `req_template.md` to the same-line inline form, added a new, reusable `models.md.MarkdownComment` leaf class (an `"html_block"` comment) and declared an optional `comment: MarkdownComment | None` field ahead of `value` on `Level`/`Priority`, which fixes the *actual* structural break in the already-committed `req_template.md` (its two-block leading-comment-then-value form) without touching the template file or its `_LEVEL_PATTERN`/`_PRIORITY_PATTERN` regexes at all. The literal `_assert_no_raw_html` `html_inline` permission was implemented too (still independently useful/matches the task's own wording), but is not what unblocks the template — see Decisions Made.
- [x] Task 120.300: Discuss the placement of MarkdownComment | None in `Level` and `Priority` of "Requirement". Why not put an optional "comment" on each MarkdownSectionN or even MarkdownStr? Let's discuss pros and cons. — depends on: none — status: **completed (discussion only, 2026-08-15)** — conclusion: neither per-field duplication (status quo) nor a `comment` field on the shared `MarkdownSection`/`MarkdownStr` ABC (would touch every ADR/UC section too, for zero current benefit, and silently break any currently-leaf section that adopted it without also gaining a content-absorbing field — see Decisions Made for the `_get_field_names()`/leaf-path trace that found this). Settled on an opt-in `MarkdownSection{1..6}WithComment` mixin per level instead, implemented in Task 3.22. See Recent Updates for the full discussion trail.
- [x] Task 120.310: Implement `MarkdownSection{1..6}WithComment` opt-in mixins (`models/md/`) and refactor `Level`/`Priority` to inherit from `MarkdownSection2WithComment` instead of declaring their own `comment` field — depends on: Task 3.21 — status: **completed (2026-08-15)** — see Recent Updates.

#### Phase 130: MCP server reference documentation (`docs/MCP.md`, cross-cutting — all domains, not REQ-specific)

- [x] Task 130.100: Implement `commands/mcp_docs.py` (`generate_mcp_docs()` + `mcp_docs()` Typer entry point) — introspects the live `biz.dfch.specmgr.server:mcp` instance at runtime via its public `list_tools()`/`list_resources()`/`list_resource_templates()`/`list_prompts()` methods (not static `ast` parsing, contrast `commands/docs.py`) and writes a single `docs/MCP.md`: a summary/table-of-contents header plus one indexed table + one `### <Kind>: <name>` detail subsection per kind (Resources, Resource Templates, Tools, Prompts); tool parameter tables are derived from each tool's top-level JSON Schema `properties`/`required`, resolving `$ref`s to short type names rather than inlining the full nested schema — depends on: none — status: **completed (2026-08-15)**
- [x] Task 130.110: Register the `mcp-docs` command (`app.command()(mcp_docs)` in `cli.py`, `from .mcp_docs import mcp_docs` in `commands/__init__.py`) — Typer's automatic underscore-to-hyphen conversion gives `specmgr mcp-docs`, matching `adr-toc`/`coverage-badge`'s existing precedent (no explicit `name=` needed) — depends on: Task 4.1 — status: **completed (2026-08-15)**
- [x] Task 130.120: Add the `specmgr-mcp-docs` local pre-commit hook (`.pre-commit-config.yaml`), regenerating and `git diff --exit-code`-checking `docs/MCP.md` — trigger scope is `^src/.*\.py$` (the same broad pattern as `specmgr-docs`, not a narrower domain-only pattern), since a tool's generated parameter schema also depends on the shared `models/` package — depends on: Task 4.1, Task 4.2 — status: **completed (2026-08-15)**
- [x] Task 130.130: Replace `README.md`'s stale, hand-maintained MCP resource/tool table (ADR-only, missing REQ/UC/`general` entirely) with a short prose summary plus a pointer to `docs/MCP.md` as the single, always-current source — depends on: Task 4.1 — status: **completed (2026-08-15)**
- [x] Task 130.140: Tests (`tests/commands/test_mcp_docs.py`, 16 tests) mirroring `test_docs.py`'s "exercise the actual Typer entry point, not just private helpers" approach — covers both `--output` and default-path branches, output determinism across calls, unique anchors across kinds sharing a bare name (`create_adr` tool vs. prompt), and all three helper functions (`_schema_type_str`, `_tool_parameters`, `_slugify`); includes a regression guard for an off-by-one `_DEFAULT_OUTPUT` path bug caught during manual verification — depends on: Task 4.1 — status: **completed (2026-08-15)**
- [x] Task 130.150: Wire `specmgr mcp-docs` into `.github/workflows/ci.yml`'s Python-3.13-only job as a drift-check backstop, alongside the existing `specmgr docs`/`specmgr adr-toc` steps — currently only the pre-commit hook (Task 4.3) enforces this, unlike its two siblings which also have a CI-level check — depends on: Task 4.1 — status: **completed (2026-08-15)** — new "Make sure `docs/MCP.md` is correct" step added right after the `docs/adr/README.md` check (same regenerate + `git diff --exit-code` shape, since `mcp_docs()` doesn't self-exit on drift the way `specmgr schema` does), gated to `matrix.python-version == '3.13'` like its siblings. Verified locally: `specmgr mcp-docs` reports no drift.

#### Phase 140: Cleanup

- [x] Task 140.100: Move REQ's packaged data directory out of `req/resources/` — `resources` is explicitly the sub-package for **MCP resources** (`@mcp.resource()` registrations), not a place for arbitrary packaged data files; the `data/` directory (currently `req/resources/data/`, holding `req_example.md`, `req_template.md`, `req_schema.json`) does not belong there. Move it to `req/data/`, a sibling of `req/models/`, `req/prompts/`, `req/resources/`, and `req/tools/` — depends on: none — status: **completed (2026-08-15)** — all items below done exactly as planned; see Recent Updates. Todo list of concrete changes once this is picked up:

  Move the 3 files: `src/biz/dfch/specmgr/req/resources/data/{req_example.md,req_template.md,req_schema.json}` -> `src/biz/dfch/specmgr/req/data/{req_example.md,req_template.md,req_schema.json}` (new directory, no `__init__.py` needed — it holds data, not Python modules, same as today).
  `src/biz/dfch/specmgr/req/_data.py`: change `_DATA_PACKAGE` from `"biz.dfch.specmgr.req.resources"` to `"biz.dfch.specmgr.req"` (the `resources.files(_DATA_PACKAGE) / "data" / "..."` shape itself is unchanged, only the anchor package moves up one level); update the module's own docstring and each of `_EXAMPLE_PATH`/`_TEMPLATE_PATH`/`_SCHEMA_PATH`'s comments and `read_req_*_text()` docstrings that mention `req/resources/data/`.
  `pyproject.toml`'s `[tool.setuptools.package-data]`: rename the `"biz.dfch.specmgr.req.resources" = ["data/*.md", "data/*.json"]` entry's key to `"biz.dfch.specmgr.req"` (patterns unchanged).
  `src/biz/dfch/specmgr/req/resources/__init__.py`: drop the sentence "This sub-package also holds the `data/` directory of packaged, build-guaranteed example/template markdown files" from the module docstring — no longer true once `data/` moves out.
  `src/biz/dfch/specmgr/req/resources/req_schema.py`: update its module and function docstrings' mentions of `req/resources/data/req_schema.json` and the `--output-dir src/biz/dfch/specmgr/req/resources/data` command line to the new `req/data` path.
  `.pre-commit-config.yaml`'s `specmgr-schema-req-package` hook: update its `--output-dir` argument and description text from `src/biz/dfch/specmgr/req/resources/data` to `src/biz/dfch/specmgr/req/data`.
  `.github/workflows/ci.yml`'s "Make sure `src/biz/dfch/specmgr/req/resources/data/req_schema.json` is correct" step: rename the step title and update its `--output-dir` argument and `::error::` message to the new `req/data` path.
  Tests: `tests/req/test_data.py`, `tests/req/resources/test_req_example.py`/`test_req_template.py`/`test_req_schema.py`, `tests/req/tools/test_get_req_example.py`/`test_get_req_template.py` all patch `_data`'s module-level path constants (`_EXAMPLE_PATH`/`_TEMPLATE_PATH`/`_SCHEMA_PATH`) via `mock.patch.object`, not hardcoded path strings, so none of them are expected to need changes — confirm the full suite still passes rather than assuming so.
  Regenerate and commit: `specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data` (new location, replacing the old `--output-dir`), `specmgr docs` (picks up the moved/edited docstrings; also drops `docs/api/biz.dfch.specmgr.req.resources.md`'s `data/` mention and updates `biz.dfch.specmgr.req._data.md`/`biz.dfch.specmgr.req.resources.req_schema.md`), `specmgr mcp-docs` (confirm no drift — this move never touches tool/resource/prompt registration itself, only where the packaged files physically live).
  Delete the now-empty `src/biz/dfch/specmgr/req/resources/data/` directory once the files are moved.
  Verify with a real, non-editable install (e.g. `pip install .` into a scratch venv, or `python -m build` + install the wheel) that `specmgr://req/schema`/`/example`/`/template` still resolve correctly post-move — the whole point of packaged data (Task 3.8) is that it survives a non-editable install, so this needs an actual check, not just passing unit tests (which run against the editable source tree either way).
- [x] Task 140.110: Discuss generalizing packaged example/template/schema data access — `req/_data.py` (Task 5.1's post-move shape) is still REQ-specific (`_DATA_PACKAGE`, `_EXAMPLE_PATH`/`_TEMPLATE_PATH`/`_SCHEMA_PATH` constants, `read_req_*_text()` functions); a future artifact domain (UC, goal, acc, ...) would otherwise need its own byte-for-byte copy of this module — depends on: Task 5.1 — status: **completed (discussion only, 2026-08-15)** — prompted directly by a user question proposing the on-disk convention `{artifact-prefix}/data/{artifact-prefix}_{kind}.{ext}` (e.g. `req/data/req_example.md`), matching Task 5.1's own file layout exactly. Discussion trail: only REQ has packaged example/template/schema data today (neither ADR nor UC does), so this is a genuine premature-abstraction risk if built now with a single real consumer to validate against — flagged explicitly before proceeding. User's decision: build it now anyway (more artifact types are expected soon; the convention is already proven by Task 5.1's REQ move, so the risk is judged acceptable). Two things are being generalized, with different constraints: (1) the on-disk **file layout convention** — cheap to generalize, confirmed as proposed; (2) `pyproject.toml`'s `[tool.setuptools.package-data]` declaration — **not** generalizable (setuptools needs one explicit key per package), so every new artifact type still needs its own entry there, plus its own pre-commit hook/CI step for a packaged schema copy, mirroring `specmgr-schema-req-package`. Test-patchability trade-off resolved per the user's own suggestion: replace today's per-domain path *constants* (`_EXAMPLE_PATH` etc., patched via `mock.patch.object` per test) with a single generic *function* taking a `type_name` parameter, so exactly one seam (that function) is ever patched regardless of how many artifact domains exist. Placement: `general/tools/_packaged_data.py` (not a top-level `general/` module), mirroring `general/tools/_doc_paths.py`'s own placement from Task 3.10 — neither is an `@mcp.tool()` itself, both are private, unexported plumbing that domain `tools`/`resources` sub-packages import directly. `req/_data.py` is retired entirely (not kept as a thin per-domain wrapper) — see Task 5.3.
- [x] Task 140.120: Implement `general/tools/_packaged_data.py` (`packaged_data_path(type_name, kind, ext="md") -> Traversable`, `read_packaged_text(type_name, kind, ext="md") -> str`, per Task 5.2's design); retire `req/_data.py` entirely; update its 5 call sites (`req/resources/req_example.py`/`req_template.py`/`req_schema.py`, `req/tools/get_req_example.py`/`get_req_template.py`) to call `read_packaged_text("req", ...)` directly (literal `"req"` type name at each call site, not a shared `REQ_TYPE_NAME` import from `req/tools/_paths.py` — that would create a new `resources` → `tools` cross-dependency that `_data.py`'s own retired docstring had explicitly avoided); update tests accordingly — depends on: Task 5.2 — status: **completed (2026-08-15)** — see Recent Updates.

## Progress

### Current Status

**As of 2026-08-15**: Phase 1 (Specification) and Phase 2 (Pydantic Models & Parser) are both **fully complete**, including `req_schema.json` (Task 1.2), now generated (not hand-authored) via a new generic `specmgr schema` CLI command (JSON Schema 2020-12), with CI wiring and a pre-commit hook keeping it in sync. Phase 3 (MCP Surface) now has three tools (`parse_req`, `get_req_example`, `get_req_template`) and three resources (`specmgr://req/schema`, `specmgr://req/example`, `specmgr://req/template`); the generated schema carries a `"$comment": "v1"` layout-version marker (Task 3.4). `specmgr req-parse` (Task 3.3) is the first REQ CLI command. `specmgr://req/schema` now reads a packaged-data copy (`req/data/req_schema.json`) instead of `docs/req_schema.json` directly, so it also works from a real, non-editable install (Task 3.8). Task 3.9's design discussion is **complete** (see Recent Updates for the full trail): granular ADR-style section-mutation tooling was rejected as not worth the effort for REQ; a lean, generic, id-based lifecycle (`create_req`/`update_req`/`set_status_req`/`delete_req`-stub/`validate_req` tools plus `specmgr://req/{id}`/`specmgr://req/list` resources plus `create_req`/`update_req` prompts) was designed instead, detailed in Tasks 3.10-3.20. Task 3.10 (generic `general/tools/_doc_paths.py` id → path lookup plumbing, shared by REQ now and UC later), Task 3.11 (`req/tools/_paths.py`/`_io.py`, REQ's own thin wrappers over it), Task 3.12 (`create_req` tool), Task 3.13 (`update_req` tool), Task 3.14 (`set_status_req` tool), Task 3.15 (`delete_req` stub), Task 3.16 (`validate_req` tool), Task 3.17 (`specmgr://req/{id}` resource), Task 3.18 (`specmgr://req/list` resource), and Task 3.19 (`req/prompts/create_req.py`/`update_req.py`) are now **completed**; Task 3.20 (`models/md`'s new `MarkdownComment` class plus the `_assert_no_raw_html` inline-comment permission, fixing `req_template.md`'s Level/Priority parse-validity) is now also **completed**. **Phase 4** (cross-cutting MCP server reference documentation, prompted directly by observing this feature's own Phase 3 tools/resources missing from `README.md`'s stale hand-maintained table) is now also underway: Tasks 4.1-4.6 (`commands/mcp_docs.py`, the `specmgr mcp-docs` CLI command, the `specmgr-mcp-docs` pre-commit hook, the `README.md` rewrite, tests, and the CI drift-check backstop) are all **completed** — Phase 4 is now fully complete.

### Blockers

None.

### Updates

#### 2026-08-15 00:00:00.000Z - (continued) Tasks 5.2/5.3: packaged example/template/schema data access generalized into `general/tools/_packaged_data.py`

Prompted by a direct user question: with REQ's packaged `data/` just moved
to `req/data/` (Task 5.1), the user asked whether the access code
(`req/_data.py`) should also generalize into a shared, doc-type-agnostic
module ahead of future artifact types (UC, goal, acc, ...), using the
convention `{artifact-prefix}/data/{artifact-prefix}_{kind}.{ext}`.
**Task 5.2 (discussion)**: flagged the premature-abstraction risk first
(only REQ has packaged example/template/schema data today; neither ADR
nor UC does) before proceeding — the user explicitly accepted that risk
since more artifact types are expected soon and Task 5.1 already proved
out the convention. Two things were distinguished: the on-disk **file
layout convention** (cheap to generalize, confirmed as proposed) vs.
`pyproject.toml`'s `[tool.setuptools.package-data]` **declaration** (not
generalizable — setuptools needs one explicit key per package; every new
artifact type still needs its own entry there, plus its own pre-commit
hook/CI step for a packaged schema copy). Test-patchability was resolved
per the user's own suggestion: replace the old per-domain path
*constants* (`_EXAMPLE_PATH`/`_TEMPLATE_PATH`/`_SCHEMA_PATH`, each
individually patched via `mock.patch.object`) with a single generic
*function* taking a `type_name` parameter, so exactly one seam is ever
patched regardless of how many artifact domains exist later.
**Task 5.3 (implementation)**:
New `general/tools/_packaged_data.py` (mirrors `general/tools/_doc_paths.py`'s
own placement/precedent from Task 3.10 -- private, unexported plumbing,
not an `@mcp.tool()` itself): `packaged_data_path(type_name, kind, ext="md") -> Traversable` (the one function tests now patch) and
`read_packaged_text(type_name, kind, ext="md") -> str`.
`req/_data.py` retired entirely (`git rm`), not kept as a thin
per-domain wrapper — its 5 call sites now call
`read_packaged_text("req", ...)` directly:
`req/resources/req_example.py`/`req_template.py`/`req_schema.py`
(the latter with `ext="json"`), `req/tools/get_req_example.py`/
`get_req_template.py`. Used the literal `"req"` string at each call
site rather than importing `REQ_TYPE_NAME` from `req/tools/_paths.py`,
to avoid creating a new `resources` → `tools` cross-dependency that
the retired `_data.py`'s own docstring had explicitly avoided.
Tests: deleted `tests/req/test_data.py`; added
`tests/general/tools/test__packaged_data.py` (generic, exercised
against REQ's real packaged files since REQ is still the only real
domain to test against); updated the 5 consumer test files
(`tests/req/resources/test_req_example.py`/`test_req_template.py`/
`test_req_schema.py`, `tests/req/tools/test_get_req_example.py`/
`test_get_req_template.py`) to patch
`general.tools._packaged_data.packaged_data_path` instead of
`req._data`'s retired path constants. 771 tests project-wide (net -2
vs. 773: -12 deleted, +10 added), all passing.
`docs/api/biz.dfch.specmgr.req._data.md` manually deleted -- confirmed
`specmgr docs` never removes stale per-module doc pages for a module
that no longer exists (it only regenerates pages for currently-
importable modules), so this is a real gap in that command worth
remembering for any future file/module deletion, not just this one.
`specmgr docs` regenerated cleanly afterwards (new
`biz.dfch.specmgr.general.tools._packaged_data.md` page, updated
`docs/api/README.md` index, no further drift); `specmgr mcp-docs`/
`specmgr adr-toc` confirmed no drift (this change never touches
tool/resource/prompt registration, only how packaged files are read).
`ruff format --check`/`ruff check`/`vulture` all clean.

### Decisions Made

#### 2026-08-15 00:00:00.000Z : `comment` generalized into an opt-in `MarkdownSection{1..6}WithComment` mixin, not a field on the shared `MarkdownSection`/`MarkdownStr` ABC (Tasks 3.21/3.22)

putting `comment` directly on the cross-domain ABC was rejected on two grounds — (1) it would add a permanently-unused property to every ADR/UC section too (neither domain has any current use for it, and neither even has a template/example resource yet), and (2) a base-class field is always first in `model_fields` declaration order for every subclass forever, foreclosing any future section wanting a different shape. Tracing the proposal through `MarkdownSection.from_text`/`MarkdownStr.from_text`/`_get_field_names()` also surfaced a genuine correctness bug it would have introduced: any inherited `MarkdownStr`-typed field disqualifies a class from the "leaf" verbatim-`_value`-storage path, so a currently-bare/leaf section (`Description`/`MoreInformation`/`Notes`) that merely inherited `comment` would raise (`assert remaining_text == ""`) on any real content, since nothing would absorb the body. The chosen design instead is a per-level opt-in mixin (`MarkdownSection{1..6}WithComment`, `models/md/`), explicitly documented as "must be paired with >=1 other declared field", with a hard runtime guard (`assert len(cls._get_field_names()) > 1` in `get_extent`/`from_text`) enforcing that constraint — matching `MarkdownComment`'s own existing leaf-only guard idiom rather than introducing a novel `__pydantic_init_subclass__` class-definition-time hook (verified working in pydantic 2.13, but not used anywhere else in this codebase). Zero impact on ADR/UC unless/until they opt in themselves. `Level`/`Priority` refactored to inherit from `MarkdownSection2WithComment`, keeping their own field-specific `comment` description overrides. See Recent Updates for the full trail.

#### 2026-08-15 00:00:00.000Z : `req_template.md`'s Level/Priority parse-validity fixed via a new `models.md.MarkdownComment` field, not by editing the template to an inline same-line comment form (Task 3.20)

the task as written pointed at extending `_assert_no_raw_html` to permit `html_inline` comments so the template could switch to a `MUST <!-- ... -->` same-line form, then making `_LEVEL_PATTERN`/`_PRIORITY_PATTERN` tolerate the trailing comment text. Rejected that path once the actual on-disk break was root-caused: `req_template.md` already uses the *block* form (a standalone `<!-- ... -->` line before the value), which fails not because of raw-HTML rejection (already permitted) but because `Level`/`Priority`'s single-`MarkdownParagraph` `value` field never expected the extra sibling block. Fixed that directly by declaring an optional `comment: MarkdownComment | None` field ahead of `value` on both classes — the generic `MarkdownStr.from_text` field-distribution loop already supports an optional field anywhere in declaration order, so this needed no engine change, no template edit, and no regex change; regex validators keep matching `value.text` alone, comment-free. `_assert_no_raw_html`'s `html_inline` permission was still implemented (the task's own literal ask, and independently useful), but is a parallel change, not what fixes the template. `MarkdownComment` is a general-purpose class, not REQ-specific — any future `models/md`-based section can declare the same optional field wherever an explanatory comment is meaningful. See Recent Updates for the full trail.

#### 2026-08-15 00:00:00.000Z : Phase 4 (MCP reference documentation) tracked in this REQ feature's plan despite being cross-cutting

`commands/mcp_docs.py`/`docs/MCP.md` cover every registered domain (ADR, REQ, UC, `general`), not just REQ, and by rights could warrant its own `feat-N-slug` folder. Logged here instead because (a) it was prompted directly by observing this feature's own Phase 3 REQ tools/resources missing from `README.md`'s hand-maintained table, and (b) it was implemented in the same working session as Phase 3's tail end. Revisit and split into its own feature folder if it grows further (e.g. the still-open CI-wiring task, or a second doc-type-specific enhancement).

#### 2026-08-15 00:00:00.000Z : `specmgr-mcp-docs` pre-commit hook trigger scope matches `specmgr-docs`'s own broad `^src/.*\.py$`, not a narrower domain-only pattern (Task 4.3)

tool parameter schemas are derived from Pydantic models under the shared `models/` package too (not just `adr/`/`req/`/`uc/`/`general/`'s own tool files), so a narrower trigger could miss a schema-affecting change. Same trade-off `specmgr-docs` already accepted (cheap generation, broad trigger) for correctness.

#### 2026-08-15 00:00:00.000Z : MCP reference heading anchors are kind-prefixed (`### Tool: X` / `### Prompt: X`), not bare `### X` (Task 4.1)

avoids relying on GitHub's undocumented `-1`/`-2`/... duplicate-heading-anchor disambiguation, which would otherwise have to be guessed and kept in lock-step by hand whenever a name is reused across kinds (e.g. `create_adr` is both a tool and a prompt name).

#### 2026-08-15 00:00:00.000Z : `specmgr://req/schema` reads a packaged-data copy, not `docs/req_schema.json` directly (Task 3.8)

Task 3.5's implementation notes had accepted `DOCS_DIR`-based reads as an out-of-scope limitation ("no `mcp.run()` caller exists yet regardless"). Task 3.8 closes that gap specifically for this resource: `commands/schema.py` stays unmodified and doc-type-generic -- its existing `--type`/`--output-dir` options are simply invoked a second time, writing an additional, committed copy to `src/biz/dfch/specmgr/req/resources/data/req_schema.json` (real package data, per `pyproject.toml`), which `req._data.read_req_schema_text()` loads via `importlib.resources`, the same mechanism `req_example.md`/`req_template.md` already use. `docs/req_schema.json` is kept as-is -- it remains the human/GitHub-browsable, CI-checked artifact; the packaged copy is purely what the MCP resource itself reads. Two independent pre-commit hooks/CI steps (not one chained command) keep both copies in sync, matching this repo's existing one-hook-per-artifact convention. `commands/schema.py`'s own `DOCS_DIR` default remains fine as-is, since it is a dev/CI-only CLI command, not something that needs to survive a non-editable install.

#### 2026-08-15 00:00:00.000Z : Characteristics/Tags modeled as flat lists, not key-value pairs

REQ-002 originally described "characteristics (key-value pairs or tags)". The implemented `Characteristics`/`Tags` sections are both simple bullet/numbered lists (`list[MarkdownListItem]`, e.g. "Safety"/"Reliability" or "Combustion Engines"/"Vehicles") rather than a key-value map. This is scoped entirely to this feature's own implementation details (not architecture-level), so it is logged here rather than as a full ADR. Revisit if a future requirement needs structured key-value metadata rather than a flat tag/category list.

#### 2026-08-15 00:00:00.000Z : Body model built on the generic `models/md` engine (v2-style), not a hand-written parser

Unlike `uc/models/v1`/`models/adr/v1`'s custom `markdown_it`-token-based parsers, REQ's body (`body.py`) and parser (`parser.py`) are built directly on `feat-5-md-model-parser`'s `MarkdownStr`/`MarkdownSectionN` engine from day one — the same approach `uc/models/v2` migrated to. No REQ v1-style hand-written parser was ever written or needs to be superseded.

#### 2026-08-15 00:00:00.000Z : `req_schema.json` (Task 1.2) deferred, not blocking

the reference document (`req_reference.md`) plus the Pydantic model tree (`body.py`, `document.py`, `frontmatter.py`) already fully define and enforce the schema in practice; a standalone JSON Schema draft-07 file adds a second, hand-synced source of truth with no consumer yet. Revisit if/when an external tool needs a JSON Schema artifact specifically.

#### 2026-08-15 00:00:00.000Z : JSON Schema dialect: 2020-12 (native Pydantic v2 output), not draft-07

Task 1.2 originally specified "JSON Schema draft-07", matching the existing hand-authored `uc_schema.json`'s dialect (`.specmgr/feat/feat-4-use-cases/v2/uc_schema.json`). REQ's schema is instead **generated** directly from `ReqDocument.model_json_schema()` — Pydantic v2's native output (JSON Schema draft 2020-12: `$defs` not `definitions`, `prefixItems` where applicable). Converting to draft-07 would require lossy post-processing (`$defs`→`definitions`, `$ref` rewriting; some 2020-12-only keywords have no exact draft-07 equivalent) purely to match a dialect with no known external consumer yet (see the entry above). This deliberately diverges from `uc_schema.json`'s hand-authored draft-07 precedent — revisit if a future consumer specifically requires draft-07. Scoped to this feature's own generated-artifact choice, not a repo-wide architectural decision, so logged here rather than as a full ADR.

#### 2026-08-15 00:00:00.000Z : `specmgr://req/schema` resource URI is unversioned (Task 3.5)

considered addressing it as `specmgr://req/schema/v1` (mirroring `req/models/v1`'s package path) but rejected it — no existing resource or tool URI in this codebase ever exposes the internal `vN` model-package version: `specmgr://version`/`specmgr://adr/list`/`specmgr://adr/{id}` are all unversioned, and `parse_req`/`parse_uc` silently import from `models.v1`/`models.v2` respectively without either fact reaching the tool name, description, or signature. `vN` is purely an internal package-layout detail (ADR d54abe50's schema-versioning strategy), never part of the public MCP surface. Keeping `specmgr://req/schema` unversioned means it always means "the current REQ schema" — exactly like the tools already do — so a future `req/models/v2` (if REQ ever follows UC's v1→v2 migration) only changes what the resource reads internally, not its address, and callers never have to choose between two live, drifting endpoints. Scoped to this feature's own resource design, not a repo-wide architectural decision, so logged here rather than as a full ADR.

#### 2026-08-15 00:00:00.000Z : Schema `"$comment"` version marker omits the doc-type name (Task 3.4)

the marker added to `generate_req_schema()`'s output is a bare version token (e.g. `"v1"`), not `"req v1"` — the doc type is already unambiguous from context (the file is `docs/req_schema.json`, the resource is `specmgr://req/schema`), so repeating it inside the value would be redundant. Purpose is narrowly to let a caller that cached an earlier fetch notice the schema's layout changed, without diffing the whole document.

#### 2026-08-15 00:00:00.000Z : `req-parse` scoped down to path-based only, no `req-get` (Task 3.3)

Task 3.3 originally named `req-get`/`req-parse` as examples. Only `req-parse` (raw filesystem path, mirroring `parse_req`'s own signature) was implemented — `req-get` (by id) would need a REQ equivalent of `adr/tools/_paths.py`/`_io.py` (base-dir scan + id → path resolution) that does not exist yet and is out of this task's scope. Revisit once REQ gets its own id-based file-storage layer.

#### 2026-08-15 00:00:00.000Z : `req-parse --format markdown` reformats in-memory only, reusing `format_text()` rather than a new `render_req()`

no `render_req()` (analogous to `render_adr()`) exists for REQ, and building one purely for CLI display purposes was rejected as unnecessary scope — the CLI instead re-reads the original file, splits frontmatter, and normalizes the body via the same `format_text()` helper `general.tools.mdformat` already uses, without ever writing back to disk. `--format json` (default) and `--format markdown` both render through `rich` (`Console.print_json`/`Syntax`/`Markdown`) — the first actual use of the `rich` dependency in `src/`, previously declared but unused. Both choices are scoped entirely to this command's own implementation, not architecture-level, so logged here rather than as a full ADR.

#### 2026-08-15 00:00:00.000Z : REQ example file shipped as package data, not read from `docs/` (Task 3.6)

`req_schema.json`'s `DOCS_DIR`-based read (Task 3.5) only resolves correctly from an editable/source checkout -- `_paths.py`'s own docstring already documents this as an accepted, CI/dev-only-tool-scoped limitation. `get_req_example`/`specmgr://req/example` are general-purpose MCP capabilities any downstream consumer of the published package might call, not just dev/CI tooling, so the example markdown file is instead declared as real package data (`pyproject.toml`'s `[tool.setuptools.package-data]`, `src/biz/dfch/specmgr/req/resources/data/req_example.md`) and loaded via `importlib.resources` -- the first use of that mechanism in this codebase. Verified against an actual built wheel installed into a throwaway (non-editable) venv, not just the dev checkout. Revisit only if a future doc-type example needs the exact same treatment, at which point the pattern established here (a `_data.py` module + a `resources/data/` directory + a `package-data` entry) should be repeated, not re-designed.

#### 2026-08-15 00:00:00.000Z : `get_req_example`/`req_example`'s content returned as raw markdown text, not a parsed `ReqDocument` (Task 3.6)

unlike `adr.resources.adr_get`'s parsed-object return, the point of an example is to show the literal document shape (including its YAML frontmatter block) for a human or LLM to read/learn from -- parsing it into a structured object first would lose that and add a pointless round-trip of a file that's always valid anyway. Returned as a plain `str` with `mime_type="text/markdown"`; no base64 or other encoding is used or needed, since that's only relevant for binary resource content.

#### 2026-08-15 00:00:00.000Z : Tool named `get_req_example`, not the task's literal `get_example` (Task 3.6)

tool names are global across the whole MCP server's `tools/list`, unlike resource URIs which are already domain-scoped by their `specmgr://req/...` prefix. Every existing tool name in this codebase that isn't already domain-unambiguous is itself domain-qualified (`parse_req`, `parse_uc`; `get_adr`/`create_adr` are the one exception, but ADR is the only domain that has ever needed those verbs). A bare `get_example` would collide the day ADR or UC grows its own equivalent, so it was qualified up front. The resource URI (`specmgr://req/example`) keeps the task's literal wording since URIs are already domain-namespaced by construction.

#### 2026-08-15 00:00:00.000Z : `.specmgr/feat-6.../req_reference.md` and the new packaged `req_example.md` are intentionally kept as two separate, duplicated copies (Task 3.6)

the former is a dev-only test fixture (`tests/req/models/v1/test_parser.py`) living outside `src/`; the latter must live inside `src/` to be packaged. Unifying them (e.g. having the parser test load the packaged copy instead) was considered and explicitly rejected in favor of the simpler, duplicated-content approach -- accepted trade-off: a future edit to one is not automatically reflected in the other, so both must be kept in sync by hand if either's sample data ever changes.

### Related PRs / Commits

None yet.
