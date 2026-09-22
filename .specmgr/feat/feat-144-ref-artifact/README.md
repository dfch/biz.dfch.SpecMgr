---
classification: null
created: '2026-09-21 21:31:30.254+02:00'
id: feat-144-ref-artifact
status: planning
type: feat
updated: '2026-09-22 07:56:23.155+02:00'
version: 1.0.0
---

# Feature: List Referenced Artifacts

## Plan

### Overview

specmgr documents cross-reference each other via type-tagged lines (VCR's `## Verifies`, SYSRS per-section bullet lists, DEC's `## Related Artifacts`), but no tool extracts and resolves those references. This feature adds a new dispatch-only MCP tool in `general/tools/` (per ADR 36905d5b) that takes an artifact's `type` + `id`, regex-scans its frontmatter-stripped body for `<TYPE> <uuid>: <title>` references, resolves each, and returns a **paged** `PagedResult[ReferenceRow]` — one row per unique reference carrying `type`, `id`, `title`, the resolved on-disk `path`, and an `error` for references that could not be resolved. It uses the same paging mechanism as every `list_*` tool (ADR ec9f5262), because a SYSRS can link hundreds of artifacts, so the result is always windowed, never a single unbounded list. Per the planning-time decision, the feature also ships the issue's secondary request: an opencode `/refs` slash command and a read-only `ref-finder` subagent wrapping the tool. Resolution is naive per-reference in v1; the per-domain batched optimization for large reference lists is tracked separately in #145.

### Requirements

- REQ-001: A new MCP tool `list_references` in `general/tools/` takes `type` (one of the whole-body domains req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs plus adr — the **source** document, whose id is validated per-domain), `id`, and read-style paging `max_results`/`offset`, and returns a paged `PagedResult[ReferenceRow]`.
- REQ-002: The tool extracts every cross-reference matching `<TYPE> <uuid>` from the source's frontmatter-stripped body, with TYPE drawn from a shared 10-tag reference vocabulary: the nine tags the SYSRS/VCR structured patterns validate as reference *targets* (GOL/PRB/QA/UC/REQ/RSK/DEC/ADR/VCR) plus SYSRS (the aggregator documents may reference in free-form prose). Matching is case-insensitive on the tag, tolerates a space or dash between tag and uuid, and finds matches anywhere in the body (not only at line start); the reference's own inline title is not captured (it is re-derived from the resolved document). The vocabulary is decoupled from feat-125 (a distinct set, not derivable from feat-125's source-domain lists).
- REQ-003: For each extracted reference the tool resolves the referenced artifact within its target domain's base directory (via that domain's cache-backed `load_by_id`) and returns a row with `type`, `id`, `title` (the resolved document's H1 — `doc.body.text` for the flat domains, `doc.body.title` for ADR), and `path` (the resolved absolute path, `str(path.resolve())`).
- REQ-004: A reference whose uuid cannot be resolved on disk still produces a row — `title`/`path` null and `error` carrying the domain not-found message (`list_*`-style inline failure) — and never raises; the row list is returned in full and paged.
- REQ-005: Repeated occurrences of the same `(type, id)` reference are deduplicated to a single row, first-occurrence order preserved.
- REQ-006: The tool validates the source `type`/`id` with the same `_path_safety` guards as the other generic tools (`validate_id` → ValueError before any filesystem access; `assert_within` after resolution). The **source** is read as raw frontmatter-stripped body text (`general.tools._splice.body_text`) — the doc-cache does not apply to it, since extraction needs the literal markdown (bullet prefixes, indentation); the **targets** are read through the domain doc-cache.
- REQ-007: `server.py`'s module docstring, `AGENTS.md`, `README.md` (for the `/refs` command), `CHANGELOG.md`, and the auto-generated `docs/MCP.md` (via `specmgr mcp-docs`) + `docs/api/` + `docs/GENERATED.md` (via `specmgr docs`) register the new tool and command.
- REQ-008: The feature ships an opencode slash command `.opencode/command/refs.md` (`/refs <type> <id>`) that delegates to a new read-only subagent defined in `.opencode/agent/ref-finder.md`, both following the `review-feature`/`feat-reviewer` conventions (the command's frontmatter declares `agent: ref-finder`; the subagent declares read-only permissions with `edit`/`write` denied). These two config artifacts are staged ahead of the tool (they are inert until `list_references` exists).
- REQ-009: Unit tests cover the extraction regex (per tag, plus case/dash/anywhere-in-line variants), deduplication, the resolved-vs-not-found row shape, the paging contract (`total`/`truncated`/`error_count`/clamp), the empty-list case, the source-missing raise, and the path-safety guards.
- REQ-010: The result is paged with the same mechanism as every `list_*` tool (`general.tools._paging.normalize_paging` + `paginate`, wrapping the rows in `general.models.paged_result.PagedResult`): `total` = number of unique references (known before resolution), `error_count` = number of not-found references, `truncated` set when further references exist beyond the page; `max_results` defaults to 25 and clamps to [1,100], `offset` floors to 0 (out-of-range values clamp, never error).

### Acceptance Criteria

- [ ] ACC-001: `list_references(type, id)` on a fixture SYSRS document referencing REQ/GOL/RSK artifacts returns a `PagedResult` with one row per unique reference, each carrying the correct `type`, `id`, `title` (from the resolved document), and `path` (resolved absolute).
- [ ] ACC-002: A document with no cross-references returns an empty `results` list (`total` 0, `truncated` false), not an error.
- [ ] ACC-003: A reference to a uuid that does not exist on disk appears as a row with null `title`/`path` and an `error` carrying the domain not-found message, and does not raise.
- [ ] ACC-004: Duplicate references to the same `(type, id)` yield exactly one row.
- [ ] ACC-005: An invalid source `type` or `id` raises ValueError before any filesystem access.
- [ ] ACC-006: A source document that does not exist on disk (valid shape, no file) raises the domain's not-found error, identical to `get_<d>`.
- [ ] ACC-007: `specmgr mcp-docs`/`specmgr docs` output regenerated; `server.py` docstring, `AGENTS.md`, `README.md`, and `CHANGELOG.md` list the tool and command; and the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`) is green.
- [ ] ACC-008: The `/refs <type> <id>` command resolves through the `ref-finder` subagent and reports the `list_references` rows (flagging any not-found references); `ref-finder.md` declares read-only permissions (`edit`/`write` denied), consistent with `feat-reviewer.md`.
- [ ] ACC-009: Paging mirrors the `list_*` tools: a source with more than 25 unique references returns `truncated=true` and a page of at most `max_results` rows with correct `total`; `offset` advances the window; `max_results` clamps to [1,100] and `offset` floors to 0 (out-of-range values clamp, never error).

### Scope

#### Included

- The `list_references` tool (dispatch-only, in `general/tools/`) plus its shared reference-extraction regex, 10-tag type vocabulary, and per-domain resolution dispatch
- `ReferenceRow` (a new model in `general/models/`) and the `PagedResult[ReferenceRow]` paging wrapper (the shared `list_*` mechanism)
- Resolution of referenced artifacts via the existing per-domain base-directory / `load_by_id` / doc-cache infrastructure (ADR special-cased: no cache, `body.title`)
- The `.opencode/command/refs.md` slash command and the `.opencode/agent/ref-finder.md` read-only subagent (decided at planning time; issue #144 secondary request) — staged ahead of the tool
- Tool and command registration: `server.py` docstring, `AGENTS.md`, `README.md`, `CHANGELOG.md`, `docs/MCP.md` + `docs/api/` + `docs/GENERATED.md` (auto-generated)
- Unit tests for extraction, deduplication, resolved/not-found rows, paging, the empty-list case, and path safety
- Conformance checks for the command/subagent files against the existing `.opencode/agent`/`.opencode/command` conventions
- The follow-up GitHub issue #145 (per-domain batched resolution for large reference lists)

#### Explicitly Out Of Scope

- Reverse references (finding documents that reference a given artifact)
- The per-domain batched resolution optimization (tracked in #145; naive per-ref `load_by_id` ships in v1)
- Changes to any domain's schema to store references structurally
- Semantic validation of references beyond existence (free-form DEC `## Related Artifacts` `TYPE-NNNN:` items that are not uuid-shaped are ignored)
- A `specmgr` Python CLI subcommand -- the wrapper is an opencode slash command only, not a Typer CLI entry

### Dependencies

#### Depends On

- feat-125-domain-lists (soft, **decoupled** — feat-125's shared source is the *source-domain* lists (the 12 whole-body domains + adr); feat-144's *reference-tag* vocabulary (10 types) is a distinct set and is not derivable from it. feat-144 owns its own vocabulary; if feat-125 lands first an optional cross-link test may be added, but nothing blocks on it)

#### Blocks

- #145 (per-domain batched resolution for large reference lists) — a perf follow-up that replaces this feature's naive per-ref resolution; it can only be built once `list_references` exists

### Design Notes

All open choices are now locked (Phase 1 complete). The design:

- **Extraction** is regex-based over the source's frontmatter-stripped body (not schema-driven), so it works for any source domain and catches free-form references anywhere. A private module `general/tools/_references.py` holds the tag vocabulary and a compiled pattern applied via `re.finditer`:
  `\b(GOL|PRB|QA|UC|REQ|RSK|DEC|ADR|VCR|SYSRS)[ \t-]+([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?![0-9a-f])` with `re.IGNORECASE`. The tag is case-insensitive; the separator is one-or-more space/tab/dash (so both `REQ 4f2a…` and `GOL-0e15…` match); the match may sit anywhere in a line (not only at column 0), which is how a VCR `## Verifies` plain paragraph and a SYSRS `- ` bullet (and nested/indented or mid-prose references) are all caught. The 36-char uuid shape is the false-positive guard; `(?![0-9a-f])` rejects an overlong hex tail. `find_references(text)` yields `(type, id)` pairs with `type`/`id` lowercased, in first-occurrence order; the inline title is deliberately **not** captured.
- **Vocabulary**: the 10 reference *tags* above (the nine SYSRS/VCR validate as targets, plus SYSRS as the free-form aggregator). This is distinct from the set of *source* domains (all 13) and from feat-125's source-domain lists. SOP/TSK are plausible future tag additions; `feat` can never be one (its ids are `feat-NNN-slug`, not uuids).
- **Source read**: `validate_id(type, id)` → the source domain's `load_by_id` (raises the domain not-found error if the source is missing — identical to `get_<d>`) → `assert_within(base_dir, path)` → `body_text(path)` for the raw, frontmatter-stripped markdown to scan. The doc-cache does **not** apply to the source (extraction needs literal markdown; a parsed doc exposes only the H1 via `.body.text` and strips bullet prefixes).
- **Target resolution (v1: naive per-ref)**: for each unique reference, dispatch on the tag to the target domain's cache-backed `load_by_id` and build a row. Nine flat domains use `<d>_base_dir` + the domain's cache-backed `load_by_id`, title `doc.body.text`; ADR is the special case — no doc-cache (ADR bfd76370), `adr_base_dir` (`SPECMGR_ADR_DIR`, default `docs/adr`), title `doc.body.title`. A reference whose target is absent (a `LookupError` from `load_by_id` — every domain not-found error subclasses it) yields a row with `title=None`, `path=None`, `error=str(exc)`; it never raises. This naive strategy resolves every unique reference on each page call (O(#refs × #domain) scans) — an accepted v1 limitation; the per-domain batched optimization is #145.
- **Result model**: `general/models/reference.py` defines Pydantic `ReferenceRow(type: str, id: str, title: str | None, path: str | None, error: str | None)`. The tool materializes the full deduplicated row list (first-occurrence order), then wraps it in `PagedResult[ReferenceRow]` via `normalize_paging` + `paginate` (the exact `list_*` mechanism): `total` = unique-reference count, `error_count` = not-found count, `truncated` when more references exist beyond the page.
- **Command + subagent** (staged ahead of the tool, per `### Decisions Made`): `.opencode/command/refs.md` (`/refs <type> <id>`, frontmatter `agent: ref-finder`) delegating to the read-only `.opencode/agent/ref-finder.md` subagent, both following the `review-feature`/`feat-reviewer` conventions. They live under `.opencode/` (config, not `src/`), so no packaging/CI impact, and are inert until `list_references` is registered.
- **Caveat**: DEC `## Related Artifacts` items are free-form `TYPE-NNNN:` (not uuid-shaped) and are ignored, as are any non-uuid references — only the 10-tag + canonical-uuid shape is extracted.

### Related Decisions

- ADR 36905d5b-8057-4294-8665-c7eed5534db0: dispatch-only convention (the tool is a generic `general/tools/` tool, not a per-domain tool)
- ADR 1af6787b-eaab-4e8f-888f-531c1e76c19d: path-safety guards for id-based tools
- ADR bfd76370-b59b-4d65-b550-a969f6c93c9d: doc cache (target reads route through it; ADR excluded)
- ADR ece4554b-725c-4f76-bc04-5d2b760363d2: domain-first hierarchy (the shared module lives in `general/`)
- ADR ec9f5262-9912-49d0-903f-fcfb54f28c13: `list_*` paging (the tool returns `PagedResult` via `normalize_paging`/`paginate`, the same contract every listing tool uses)

### Task List

#### Phase 1: Design

- [x] Task 1.1: Pin the tool name (`list_references`), the result-row schema (`ReferenceRow(type, id, title, path, error)` wrapped in `PagedResult`), the 10-tag reference vocabulary, the extraction regex, the source raw-read vs. target cached-read split, the naive per-ref resolution strategy (→ `### Decisions Made`), and the follow-up #145. (The `/refs` command + `ref-finder` subagent decision is recorded in `### Decisions Made` at planning time.)
- [x] Task 1.2: Commit the finalized plan + the staged `/refs` command + `ref-finder` subagent artifacts as the feat-144 prep commit (markdown-only; no Python). The full quality gate with the tool's tests runs again in Phase 3/5 once the implementation lands.

#### Phase 2: Implementation

- [ ] Task 2.1: Add the shared reference-extraction regex, 10-tag type vocabulary, and per-domain resolution dispatch in `general/tools/_references.py`
- [ ] Task 2.2: Add the `ReferenceRow` model in `general/models/reference.py`
- [ ] Task 2.3: Implement the `list_references` tool (source `validate_id` + `load_by_id` + `assert_within` + `body_text`; per-ref target resolution; `PagedResult` wrap) with `_path_safety` guards, registered in `general/tools/__init__.py` and `server.py`
- [ ] Task 2.4: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 3: Tests

- [ ] Task 3.1: Unit tests for extraction (per tag + case/dash/anywhere variants), deduplication, resolved-vs-not-found rows, and the empty-list case (tmp `SPECMGR_DOCS_DIR`/`SPECMGR_ADR_DIR` fixtures with real referenced artifacts)
- [ ] Task 3.2: Path-safety tests (invalid source `type`/`id` raise before any filesystem access) and source-missing (raises the domain not-found error)
- [ ] Task 3.3: Paging tests (`total`/`truncated`/`error_count` correct, `offset` advances, `max_results` clamps to [1,100], `offset` floors to 0)
- [ ] Task 3.4: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 4: Command + Subagent

- [x] Task 4.1: Create `.opencode/agent/ref-finder.md` -- a read-only subagent (frontmatter: `mode: subagent`, read-only permission block with `edit`/`write` denied, `feat-reviewer`-style) whose workflow parses `<type> <id>`, calls `list_references`, and reports the rows with not-found references flagged
- [x] Task 4.2: Create `.opencode/command/refs.md` -- the `/refs <type> <id>` slash command with frontmatter `description` + `agent: ref-finder`, `review-feature`-style body
- [ ] Task 4.3: Verify both files follow the conventions of the existing `.opencode/agent`/`.opencode/command` files and smoke-test `/refs` against a real document (deferred: requires `list_references` to exist)
- [ ] Task 4.4: Run the full quality gate with tests and commit the phase (folded into the Phase 5 docs commit once the tool lands)

#### Phase 5: Documentation

- [ ] Task 5.1: Update `server.py`'s module docstring, `AGENTS.md`, `README.md` (new `## Referencing Artifacts` section for `/refs`), and `CHANGELOG.md` (`[Unreleased]` → Added)
- [ ] Task 5.2: Regenerate `docs/MCP.md` (`specmgr mcp-docs`) and `docs/api/` + `docs/GENERATED.md` (`specmgr docs`); update `whitelist.py` if vulture flags a new symbol
- [ ] Task 5.3: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 6: Verification & Closeout

- [ ] Task 6.1: Run the full quality gate with tests as the final verification pass
- [ ] Task 6.2: Update `### Current Status` and `### Updates`, and set the feature status via the generic `set_status` tool (`type="feat"`)
- [ ] Task 6.3: Commit the phase as a single commit (no push)

## Progress

### Current Status

Design complete (Phase 1). All open choices are locked and recorded in the Plan (exact extraction regex, `ReferenceRow` + `PagedResult` shape, the 10-tag vocabulary, the source raw-read vs. target cached-read split, and naive per-ref resolution as a DEC); the follow-up perf issue #145 is opened. The two opencode artifacts (`.opencode/command/refs.md`, `.opencode/agent/ref-finder.md`) are staged. No Python written — implementation (Phases 2, 3), doc registration + regeneration (Phase 5), the `/refs` smoke-test (Task 4.3), and closeout (Phase 6) remain.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-22 05:56:23.152Z - Design locked; plan finalized, follow-up #145 opened, /refs + ref-finder artifacts staged

Locked all Phase 1 open choices in the Plan: the tool is `list_references(type, id, max_results, offset) -> PagedResult[ReferenceRow]`; extraction is a case-insensitive, anywhere-in-body regex over the 10 reference tags (GOL/PRB/QA/UC/REQ/RSK/DEC/ADR/VCR/SYSRS) tolerant of a space or dash separator; the source is read as raw frontmatter-stripped body (`body_text`), targets via cache-backed `load_by_id`; a not-found reference is a row with `error` (list*-style), a missing source raises the domain not-found error (same as `get_<d>`); results are paged with the shared `list_*` mechanism. Resolution is naive per-ref in v1 — recorded as a DEC below, with the per-domain batched optimization tracked in #145. Staged `.opencode/command/refs.md` and `.opencode/agent/ref-finder.md`.

#### 2026-09-21 19:30:35.557Z - Decision: ship the /refs command and the ref-finder subagent

Resolved the issue's secondary request at planning time: ship both an opencode `/refs <type> <id>` slash command (`.opencode/command/refs.md`) and a new read-only `ref-finder` subagent (`.opencode/agent/ref-finder.md`), following the `review-feature`/`feat-reviewer` conventions. The full rationale is in `### Decisions Made`.

#### 2026-09-21 19:10:10.879Z - Created

Drafted the feature plan from GitHub issue #144 'list referenced artifacts': a new dispatch-only `general/tools/` MCP tool that regex-extracts `<TYPE> <uuid>: <title>` cross-references from an artifact's body and resolves each to `type`/`id`/`title`/`path`, plus the issue's `/command` + subagent request (decided: ship both; see `### Decisions Made`).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-22 05:56:23.152Z - Resolution strategy: naive per-reference `load_by_id` (not batched per-domain)

Chosen for v1. `list_references` resolves each unique reference with the target domain's `load_by_id` (a `find_<type>_path` directory scan + cache-backed read), one at a time. Because `paginate` materializes the full row list before slicing, a single call resolves every unique reference in the source — so a SYSRS linking hundreds of artifacts performs hundreds of directory scans per page call. Cost is O(#refs × #domain); the result is correct and identical, so this is a performance tradeoff, not a correctness one. Rationale for v1: it is the simplest path, reuses the proven `get_<d>`/`load_by_id` mechanism verbatim (no new index-building code), and keeps the paging contract (`total`/`error_count`/`truncated`) exactly consistent with every `list_*` tool. The per-domain batched optimization — group refs by target domain, scan each distinct domain once into an `{id -> (title, path)}` index, O(1) lookups, re-emit in first-occurrence order (cost O(#distinct_domains + #refs)) — is deliberately deferred and tracked in #145 so it is not forgotten.

#### 2026-09-21 19:30:35.557Z - Ship the /refs command and the ref-finder subagent (issue #144 secondary request)

Issue #144 asks to also consider adding a `/command` and a subagent for the reference-listing tool. Decision (made at planning time, 2026-09-21): ship both. Rationale: the repo already keeps opencode commands under `.opencode/command/` and subagents under `.opencode/agent/`, and the commands that do real work delegate to a read-only subagent (`/review-feature` -> `feat-reviewer`); the wrapper is thin (one `list_references` call plus a narrated result), so the cost is two markdown config files with no packaging/CI impact; the subagent additionally provides a permission-isolated, reusable read-only agent that is callable via the task tool without a slash command. The task list carries a dedicated Phase 4 (Command + Subagent) for it.

### More Information

- GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/144 (opened by dfch on 2026-09-21).
- Follow-up (per-domain batched resolution for large reference lists): https://github.com/dfch/biz.dfch.SpecMgr/issues/145.
