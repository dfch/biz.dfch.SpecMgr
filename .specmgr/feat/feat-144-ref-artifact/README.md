---
classification: null
created: '2026-09-21 21:31:30.254+02:00'
id: feat-144-ref-artifact
status: planning
type: feat
updated: '2026-09-21 21:31:30.254+02:00'
version: 1.0.0
---

# Feature: List Referenced Artifacts

## Plan

### Overview

specmgr documents cross-reference each other via type-tagged lines (VCR's `## Verifies`, SYSRS per-section bullet lists, DEC's `## Related Artifacts`), but no tool extracts and resolves those references. This feature adds a new dispatch-only MCP tool in `general/tools/` (per ADR 36905d5b) that takes an artifact's `type` + `id` (uuid), regex-scans its body for `<TYPE> <uuid>: <title>` references, and returns a (possibly empty) list of rows with each referenced artifact's `type`, `id`, `title`, and resolved on-disk `path`. Per the planning-time decision, the feature also ships the issue's secondary request: an opencode `/refs` slash command and a read-only `ref-finder` subagent wrapping the tool.

### Requirements

- REQ-001: A new MCP tool (working name `list_references`) in `general/tools/` takes `type` (one of the whole-body domains req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs plus adr) and `id` (uuid-shaped) and reads that artifact's document.
- REQ-002: The tool extracts every cross-reference matching `<TYPE> <uuid>: <title>` from the document body, with TYPE drawn from a shared type vocabulary (at minimum the types SYSRS/VCR already validate: GOL/PRB/QA/UC/REQ/RSK/DEC/ADR/VCR/SYSRS).
- REQ-003: For each extracted reference the tool resolves the referenced artifact within its domain's base directory and returns a row with `type`, `id`, `title` (from the referenced document's frontmatter/H1), and `path` (resolved absolute path).
- REQ-004: A reference whose uuid cannot be resolved on disk still produces a row (with `title`/`path` null); unresolvable references never raise -- the result is a possibly-empty list.
- REQ-005: Repeated occurrences of the same `(type, id)` reference are deduplicated to a single row.
- REQ-006: The tool validates `type`/`id` with the same `_path_safety` guards as the other generic tools (ValueError before any filesystem access) and uses the domain's doc-cache read path.
- REQ-007: `server.py`'s module docstring, `AGENTS.md`, `README.md` (for the `/refs` command, per the `/release` command precedent), and the auto-generated `docs/MCP.md` (via `specmgr mcp-docs`) register the new tool and command.
- REQ-008: The feature ships an opencode slash command `.opencode/command/refs.md` (`/refs <type> <id>`) that delegates to a new read-only subagent defined in `.opencode/agent/ref-finder.md`, both following the `review-feature`/`feat-reviewer` conventions (the command's frontmatter declares `agent: ref-finder`; the subagent declares read-only permissions with `edit`/`write` denied).
- REQ-009: Unit tests cover the extraction regex (per type), the resolution and deduplication logic, the unresolved-reference behavior, the result shape, and the path-safety guards.

### Acceptance Criteria

- [ ] ACC-001: `list_references(type, id)` on a fixture SYSRS document referencing REQ/GOL/RSK artifacts returns one row per reference with correct `type`, `id`, `title`, `path`.
- [ ] ACC-002: A document with no cross-references returns an empty list, not an error.
- [ ] ACC-003: A reference to a uuid that does not exist on disk appears as a row with null `title`/`path` and does not raise.
- [ ] ACC-004: Duplicate references to the same `(type, id)` yield exactly one row.
- [ ] ACC-005: Invalid `type` or `id` raises ValueError before any filesystem access.
- [ ] ACC-006: `specmgr mcp-docs`/`specmgr docs` output regenerated, `server.py` docstring + `AGENTS.md` + `README.md` list the tool and command, and the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`) is green.
- [ ] ACC-007: The `/refs <type> <id>` command resolves through the `ref-finder` subagent and reports the `list_references` rows (flagging any unresolved references); `ref-finder.md` declares read-only permissions (`edit`/`write` denied), consistent with `feat-reviewer.md`.

### Scope

#### Included

- The `list_references` tool (dispatch-only, in `general/tools/`) plus its shared reference-extraction regex and type vocabulary
- Resolution of referenced artifacts via the existing per-domain base-directory/path/doc-cache infrastructure
- The `.opencode/command/refs.md` slash command and the `.opencode/agent/ref-finder.md` read-only subagent (decided at planning time; issue #144 secondary request)
- Tool and command registration: `server.py` docstring, `AGENTS.md`, `README.md`, `docs/MCP.md` (auto-generated)
- Unit tests for extraction, resolution, deduplication, and path safety
- Conformance checks for the command/subagent files against the existing `.opencode/agent`/`.opencode/command` conventions

#### Explicitly Out Of Scope

- Reverse references (finding documents that reference a given artifact)
- Changes to any domain's schema to store references structurally
- Semantic validation of references beyond existence (free-form DEC `## Related Artifacts` items that are not uuid-shaped)
- A `specmgr` Python CLI subcommand -- the wrapper is an opencode slash command only, not a Typer CLI entry

### Dependencies

#### Depends On

- feat-125-domain-lists (soft -- the shared domain-list source of truth the type vocabulary could be derived from, once it lands; otherwise decoupled)

#### Blocks

- None known.

### Design Notes

The following points sketch the working design; Phase 1 locks the open choices:

- Extraction is regex-based over the frontmatter-stripped body text, not schema-driven: a shared module (e.g. `general/tools/_references.py`) holds the type vocabulary and a `find_references(text)` returning `(type, uuid, title)` tuples in document order.
- Type vocabulary starts from the patterns SYSRS/VCR already validate (GOL/PRB/QA/UC/REQ/RSK/DEC/ADR/VCR/SYSRS); SOP/TSK/FEAT are candidates for a later vocabulary extension.
- Resolution: type maps to the domain package; the domain's base dir + `find_doc_path_by_id`-style scan (with `read_fn` wired to the domain's doc cache per feat-107) locates the file; `title` comes from the referenced document's frontmatter/H1; `path` is the resolved absolute path. Unresolvable uuids yield a row with `title=None`/`path=None`, never an exception.
- Result model: a Pydantic `ReferenceRow(type, id, title, path)`; the tool returns a possibly-empty `list[ReferenceRow]`, deduplicated on `(type, id)`, first-occurrence order preserved.
- ADR documents resolve through `SPECMGR_ADR_DIR` (default `docs/adr`) with the same dispatch.
- Per the planning-time decision (see `### Decisions Made`), the issue's secondary request ships: an opencode slash command `.opencode/command/refs.md` (`/refs <type> <id>`) delegating to a new read-only subagent `.opencode/agent/ref-finder.md`, following the `review-feature`/`feat-reviewer` conventions; command/agent files live under `.opencode/` (config, not `src/`), so no packaging/CI impact.
- Caveat: DEC `## Related Artifacts` items are free-form and not necessarily uuid-shaped, so only uuid-shaped references are extracted/resolved.

### Related Decisions

- ADR 36905d5b-8057-4294-8665-c7eed5534db0: dispatch-only convention (the tool is a generic `general/tools/` tool, not a per-domain tool)
- ADR 1af6787b-eaab-4e8f-888f-531c1e76c19d: path-safety guards for id-based tools
- ADR bfd76370-b59b-4d65-b550-a969f6c93c9d: doc cache (resolved reads route through it)
- ADR ece4554b-725c-4f76-bc04-5d2b760363d2: domain-first hierarchy (where the shared module lives)

### Task List

#### Phase 1: Design

- [ ] Task 1.1: Pin the tool name, the result-row Pydantic schema, and the type vocabulary (the `/refs` command + `ref-finder` subagent decision is already recorded in `### Decisions Made` at planning time)
- [ ] Task 1.2: Run the full quality gate with tests (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`) and commit the phase as a single commit (no push)

#### Phase 2: Implementation

- [ ] Task 2.1: Add the shared reference-extraction regex and type vocabulary module in `general/`
- [ ] Task 2.2: Implement the resolution logic (base dir, path lookup, doc-cache read, title extraction)
- [ ] Task 2.3: Implement the `list_references` tool with `_path_safety` guards, registered in `server.py`
- [ ] Task 2.4: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 3: Tests

- [ ] Task 3.1: Unit tests for extraction per type, deduplication, unresolved references, and the empty-list case
- [ ] Task 3.2: Path-safety tests (invalid `id`/`type` raise before any filesystem access)
- [ ] Task 3.3: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 4: Command + Subagent

- [ ] Task 4.1: Create `.opencode/agent/ref-finder.md` -- a read-only subagent (frontmatter: `mode: subagent`, read-only permission block with `edit`/`write` denied, `feat-reviewer`-style) whose workflow parses `<type> <id>`, calls `list_references`, and reports the rows with unresolved references flagged
- [ ] Task 4.2: Create `.opencode/command/refs.md` -- the `/refs <type> <id>` slash command with frontmatter `description` + `agent: ref-finder`, `review-feature`-style body
- [ ] Task 4.3: Verify both files follow the conventions of the existing `.opencode/agent`/`.opencode/command` files and smoke-test `/refs` against a real document
- [ ] Task 4.4: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 5: Documentation

- [ ] Task 5.1: Update `server.py`'s module docstring, `AGENTS.md`, and `README.md` (new tool + `/refs` command, per the `/release` command precedent)
- [ ] Task 5.2: Regenerate `docs/MCP.md` (`specmgr mcp-docs`) and `docs/api/` + `docs/GENERATED.md` (`specmgr docs`)
- [ ] Task 5.3: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 6: Verification & Closeout

- [ ] Task 6.1: Run the full quality gate with tests as the final verification pass
- [ ] Task 6.2: Update `### Current Status` and `### Updates`, and set the feature status via the generic `set_status` tool (`type="feat"`)
- [ ] Task 6.3: Commit the phase as a single commit (no push)

## Progress

### Current Status

Planning: feature drafted from GitHub issue #144 (opened 2026-09-21). The `/command` + subagent decision is resolved at planning time (ship both; see `### Decisions Made`). No code written, no phase started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-21 19:30:35.557Z - Decision: ship the /refs command and the ref-finder subagent

Resolved the issue's secondary request at planning time: ship both an opencode `/refs <type> <id>` slash command (`.opencode/command/refs.md`) and a new read-only `ref-finder` subagent (`.opencode/agent/ref-finder.md`), following the `review-feature`/`feat-reviewer` conventions. The full rationale is in `### Decisions Made`.

#### 2026-09-21 19:10:10.879Z - Created

Drafted the feature plan from GitHub issue #144 'list referenced artifacts': a new dispatch-only `general/tools/` MCP tool that regex-extracts `<TYPE> <uuid>: <title>` cross-references from an artifact's body and resolves each to `type`/`id`/`title`/`path`, plus the issue's `/command` + subagent request (decided: ship both; see `### Decisions Made`).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-21 19:30:35.557Z - Ship the /refs command and the ref-finder subagent (issue #144 secondary request)

Issue #144 asks to also consider adding a `/command` and a subagent for the reference-listing tool. Decision (made at planning time, 2026-09-21): ship both. Rationale: the repo already keeps opencode commands under `.opencode/command/` and subagents under `.opencode/agent/`, and the commands that do real work delegate to a read-only subagent (`/review-feature` -> `feat-reviewer`); the wrapper is thin (one `list_references` call plus a narrated result), so the cost is two markdown config files with no packaging/CI impact; the subagent additionally provides a permission-isolated, reusable read-only agent that is callable via the task tool without a slash command. The task list carries a dedicated Phase 4 (Command + Subagent) for it.

### More Information

GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/144 (opened by dfch on 2026-09-21).
