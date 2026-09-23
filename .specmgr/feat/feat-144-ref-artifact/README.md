---
classification: null
created: '2026-09-21 21:31:30.254+02:00'
id: feat-144-ref-artifact
status: progress
type: feat
updated: '2026-09-23 13:38:41.899+02:00'
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

- [x] ACC-001: `list_references(type, id)` on a fixture SYSRS document referencing REQ/GOL/RSK artifacts returns a `PagedResult` with one row per unique reference, each carrying the correct `type`, `id`, `title` (from the resolved document), and `path` (resolved absolute). Verified in `tests/general/tools/test_list_references.py` (ACC-001 fixture).
- [x] ACC-002: A document with no cross-references returns an empty `results` list (`total` 0, `truncated` false), not an error. Verified in `test_list_references.py` (ACC-002 fixture).
- [x] ACC-003: A reference to a uuid that does not exist on disk appears as a row with null `title`/`path` and an `error` carrying the domain not-found message, and does not raise. Verified in `test_list_references.py` (ACC-003 fixture) and end-to-end via the Phase 4 `/refs` not-found smoke exercise.
- [x] ACC-004: Duplicate references to the same `(type, id)` yield exactly one row. Verified in `test_list_references.py` (ACC-004 fixture).
- [x] ACC-005: An invalid source `type` or `id` raises ValueError before any filesystem access. Verified in `test_list_references.py` (ACC-005 fixture: nonexistent domain-root env vars prove the guard fires before any read).
- [x] ACC-006: A source document that does not exist on disk (valid shape, no file) raises the domain's not-found error, identical to `get_<d>`. Verified in `test_list_references.py` across req/uc/sysrs/gol/rsk/feat/adr sources.
- [x] ACC-007: `specmgr mcp-docs`/`specmgr docs` output regenerated; `server.py` docstring, `AGENTS.md`, `README.md`, and `CHANGELOG.md` list the tool and command; and the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`) is green. Verified in Phase 5 (Tasks 5.1-5.2) and the Phase 6 closeout gate (Task 6.1).
- [x] ACC-008: The `/refs <type> <id>` command resolves through the `ref-finder` subagent and reports the `list_references` rows (flagging any not-found references); `ref-finder.md` declares read-only permissions (`edit`/`write` denied), consistent with `feat-reviewer.md`. Verified in Phase 4 (Task 4.3 conformance check + end-to-end smoke test against a live document).
- [x] ACC-009: Paging mirrors the `list_*` tools: a source with more than 25 unique references returns `truncated=true` and a page of at most `max_results` rows with correct `total`; `offset` advances the window; `max_results` clamps to [1,100] and `offset` floors to 0 (out-of-range values clamp, never error). Verified in `test_list_references.py` (30-unique-reference paging test).

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
- **Caveat (code spans, planned — Phase 7)**: the extraction regex scans the raw body text unconditionally, including inside fenced code blocks and inline code spans; a document that *quotes/illustrates* the `<TAG> <uuid>` syntax as a literal example (rather than a live reference) is still picked up and resolved/reported as if it were real. This is an accepted v1 tradeoff of the regex-based, schema-agnostic extractor (matching the DEC caveat above) — to be pinned by a dedicated test rather than left silently unspecified (Task 7.6).

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

- [x] Task 2.1: Add the shared reference-extraction regex, 10-tag type vocabulary, and per-domain resolution dispatch in `general/tools/_references.py`
- [x] Task 2.2: Add the `ReferenceRow` model in `general/models/reference.py`
- [x] Task 2.3: Implement the `list_references` tool (source `validate_id` + `load_by_id` + `assert_within` + `body_text`; per-ref target resolution; `PagedResult` wrap) with `_path_safety` guards, registered in `general/tools/__init__.py` and `server.py`
- [x] Task 2.4: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 3: Tests

- [x] Task 3.1: Unit tests for extraction (per tag + case/dash/anywhere variants), deduplication, resolved-vs-not-found rows, and the empty-list case (tmp `SPECMGR_DOCS_DIR`/`SPECMGR_ADR_DIR` fixtures with real referenced artifacts)
- [x] Task 3.2: Path-safety tests (invalid source `type`/`id` raise before any filesystem access) and source-missing (raises the domain not-found error)
- [x] Task 3.3: Paging tests (`total`/`truncated`/`error_count` correct, `offset` advances, `max_results` clamps to [1,100], `offset` floors to 0)
- [x] Task 3.4: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 4: Command + Subagent

- [x] Task 4.1: Create `.opencode/agent/ref-finder.md` -- a read-only subagent (frontmatter: `mode: subagent`, read-only permission block with `edit`/`write` denied, `feat-reviewer`-style) whose workflow parses `<type> <id>`, calls `list_references`, and reports the rows with not-found references flagged
- [x] Task 4.2: Create `.opencode/command/refs.md` -- the `/refs <type> <id>` slash command with frontmatter `description` + `agent: ref-finder`, `review-feature`-style body
- [x] Task 4.3: Verify both files follow the conventions of the existing `.opencode/agent`/`.opencode/command` files and smoke-test `/refs` against a real document (deferred: requires `list_references` to exist)
- [x] Task 4.4: Run the full quality gate with tests and commit the phase (folded into the Phase 5 docs commit once the tool lands)

#### Phase 5: Documentation

- [x] Task 5.1: Update `server.py`'s module docstring, `AGENTS.md`, `README.md` (new `## Referencing Artifacts` section for `/refs`), and `CHANGELOG.md` (`[Unreleased]` → Added)
- [x] Task 5.2: Regenerate `docs/MCP.md` (`specmgr mcp-docs`) and `docs/api/` + `docs/GENERATED.md` (`specmgr docs`); update `whitelist.py` if vulture flags a new symbol
- [x] Task 5.3: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 6: Verification & Closeout

- [x] Task 6.1: Run the full quality gate with tests as the final verification pass
- [x] Task 6.2: Update `### Current Status` and `### Updates`, and set the feature status via the generic `set_status` tool (`type="feat"`)
- [x] Task 6.3: Commit the phase as a single commit (no push)

#### Phase 7: Follow-Up Fixes (Review Remediation)

- [ ] Task 7.1: Fix the docstring splice in `general/tools/__init__.py` (stray leading-space artifact from inserting the `list_references` paragraph mid-sentence into the existing `validate` docstring text); regenerate `docs/api/biz.dfch.specmgr.general.tools.md` (`specmgr docs`).
- [ ] Task 7.2: Replace `list_references.py`'s hand-written `Literal["req", "uc", ..., "adr"]` `type` parameter with `Literal[*ALL_DOMAINS]` (imported from `general.tools._domains`), matching `set_status.py`/`update.py`/`delete.py`/`set_classification.py`/`validate.py`'s existing pattern (feat-125-domain-lists).
- [ ] Task 7.3: Add the missing drift guard for `_SOURCE_LOADERS` in `list_references.py`: `assert set(_SOURCE_LOADERS) == set(ALL_DOMAINS), "..."` at module scope, identical in shape to `set_status.py`'s `_ADAPTERS`/`ALL_DOMAINS` guard. No restructuring of the data-driven dict itself (Phase 2's documented design choice stands).
- [ ] Task 7.4: In `_references.py`, add `assert set(_TARGET_RESOLVERS) == set(REFERENCE_TYPES), "..."` at module scope, and narrow `resolve_reference`'s `except LookupError` so a `KeyError` from a missing `_TARGET_RESOLVERS` entry (a programming error) is not silently folded into the same not-found `ReferenceRow` path as a legitimate domain `XNotFoundError`.
- [x] Task 7.5: Tick `ACC-001`..`ACC-009` to `[x]` in the Acceptance Criteria section, each with an inline evidence sentence (repo convention, e.g. `feat-36-delete/README.md:52-59`). (Done in this same doc-only edit.)
- [ ] Task 7.6: Document the accepted code-fence/inline-code-span extraction caveat in `_references.py`'s module docstring (the Design Notes bullet above is staged); add one test in `test__references.py` pinning the (accepted) behavior of a reference-shaped string inside a fenced/inline code span.
- [ ] Task 7.7: Replace the Unicode em dash "—" with ASCII "--" in `.opencode/agent/ref-finder.md`'s `description` field and `.opencode/command/refs.md`'s body, matching `feat-reviewer.md`/`review-feature.md`/`phase-implementer.md`'s typographic convention.
- [ ] Task 7.8: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`); reopen the feature status via `set_status` (`type="feat"`, `done` -> `progress`) at phase start (done in this edit) and set it back to `done` on closeout; update `### Current Status`/`### Updates`; commit as a single phase commit on the existing `feat-144-ref-artifact` branch (amending open PR #147, no push unless instructed).

## Progress

### Current Status

Phase 6 (Verification & Closeout) landed and the feature was marked `done`; a subsequent independent `feat-reviewer` review of open PR #147 found two Gaps (a hand-rolled domain `Literal` and a missing drift-guard `assert`, both diverging from the feat-125-domain-lists convention every sibling generic tool already follows), one Code Smell (`_TARGET_RESOLVERS` dispatch silently folding a hypothetical `KeyError` into the not-found row path), one Inconsistency (ACC-001..009 left unticked despite the narrative claiming all satisfied), one Error (a cosmetic docstring-splice whitespace artifact), and two Improvements (an undocumented/untested code-span extraction caveat; em-dash vs. this repo's ASCII "--" convention in the new `.opencode/` files). Phase 7 (Follow-Up Fixes) was added to track remediation on the same branch/PR. **This edit is doc-only**: ACC-001..009 are now ticked with evidence (Task 7.5), the code-span caveat is recorded in Design Notes, and Phase 7's task list is staged — none of Tasks 7.1-7.4/7.6-7.8's actual code/test/docstring changes have been made yet. Status is reopened `done` -> `progress` to reflect the outstanding Phase 7 work.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-23 11:36:14.148Z - Phase 7 staged (doc-only): review findings recorded, ACC checkboxes ticked with evidence, code-span caveat added; no code changes yet

An independent `feat-reviewer` review of open PR #147 (post-Phase-6) reported: **Errors** -- a stray leading-space artifact in `general/tools/__init__.py`'s docstring where the `list_references` paragraph was spliced mid-sentence into the existing `validate` text. **Gaps** -- `list_references.py`'s `type` parameter is a hand-written 13-name `Literal` instead of `Literal[*ALL_DOMAINS]` (the `general.tools._domains` single source every sibling generic tool -- `set_status`/`update`/`delete`/`set_classification`/`validate` -- already uses post-feat-125); `_SOURCE_LOADERS` has no `assert set(_SOURCE_LOADERS) == set(ALL_DOMAINS)` drift guard, unlike every sibling adapter table. **Code Smell** -- `_references.py`'s `resolve_reference` catches `LookupError` around a `_TARGET_RESOLVERS[ref_type]` dict lookup; since `KeyError` subclasses `LookupError`, a future `REFERENCE_TYPES` addition missing a resolver entry would silently become a bogus not-found row instead of failing loudly, and there is no `assert set(_TARGET_RESOLVERS) == set(REFERENCE_TYPES)` guard. **Inconsistency** -- the Acceptance Criteria checkboxes were all left `[ ]` despite Phase 6's own narrative asserting all nine were satisfied, diverging from this repo's tick-with-evidence convention (e.g. `feat-36-delete`). **Improvements** -- the extraction regex matches inside fenced/inline code spans unconditionally, an accepted but previously undocumented/untested tradeoff; `.opencode/agent/ref-finder.md`/`.opencode/command/refs.md` use a Unicode em dash where the rest of the `.opencode/` convention set uses ASCII "--". Agreed remediation: a new Phase 7 (Follow-Up Fixes) on this same branch, amending PR #147 rather than opening a new feature/issue. This edit implements only the documentation-safe portion of that remediation: ACC-001..ACC-009 ticked `[x]` with inline evidence sentences (Task 7.5, done), a new Design Notes "Caveat (code spans)" bullet recording the code-span tradeoff (staging Task 7.6's docstring/test follow-up), and Phase 7's full task list (7.1-7.8) staged with 7.1-7.4/7.6-7.8 left unchecked -- no `src/`/`tests/`/`.opencode/` file was touched, and the quality gate was not re-run, since no code changed. Frontmatter `status` reopened `done` -> `progress` via the generic `set_status` tool (`type="feat"`) to reflect that Phase 7 is now open with outstanding work.

#### 2026-09-23 06:35:52.091Z - Phase 6 verification and closeout: final gate green, feature marked done (this phase's commit is the closeout commit)

Implemented Tasks 6.1-6.3. Task 6.1 (final verification pass): the full quality gate run from the worktree root, every command exit 0 — `uv run --frozen ruff format --check` (1705 files already formatted), `uv run --frozen ruff check` (all checks passed), `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (clean, no new `whitelist.py` entries), `uv run --frozen pytest -n auto --cov=src --cov-report=` (3401 passed in ~42 s). Task 6.2: `### Current Status` rewritten as the final closeout paragraph (all phases complete, gate green, feature ready for review; the only outstanding item is the #145 follow-up, explicitly out of scope by design), this entry prepended, and the frontmatter `updated` bumped in the same edit. Status change: `status: planning` → `status: done` via the generic `set_status` tool (`type="feat"`, `id="feat-144-ref-artifact"`) — frontmatter-only, body untouched; the document parses before the change (PARSE_OK) and after it (PARSE_OK again). End-to-end smoke of the feature itself against this plan document: `list_references(type='feat', id='feat-144-ref-artifact')` → `total=5, truncated=False, error_count=0` — the five `### Related Decisions` ADR references all resolve on disk. Task 6.3: the phase commit (single commit, no push) is the closeout commit — the checked Task 6.3 box above documents the intent it fulfills. No new design decisions were made in this phase (verification/closeout only), so `### Decisions Made` is unchanged. ACC-001..ACC-009: all satisfied (ACC-001..ACC-006/ACC-009 via the Phase 3 test classes, ACC-007 via the Phase 2/5 registrations + this green gate, ACC-008 via the Phase 4 conformance + smoke verification).

#### 2026-09-23 06:16:53.813Z - Phase 5 documentation complete; full quality gate green (Phase 4 folded into this commit)

Implemented Tasks 5.1-5.2 and ran Task 5.3's gate. Registered `list_references` in four places: `server.py`'s module docstring (a new entry in the general-tools paragraph, between the `validate` entry and the existing Path-safety discussion — same `--`/double-backtick prose style, carrying its own `_path_safety` clause so the surrounding prose stays byte-identical); `AGENTS.md` (spliced into the `general/tools/` semicolon-separated enumeration between `validate` and the "On a successful write" sentence — same voice: em-dashes, single backticks); the root `README.md` (new `## Referencing Artifacts` section between `## Usage` and `## Development`, a table-of-contents entry after `[Usage](#usage)`, and a one-line pointer sentence after Usage's plain-language example list); and `CHANGELOG.md` (the previously empty `[Unreleased]` gains a `### Added` with two entries — the tool: 10-tag reference vocabulary, `PagedResult[ReferenceRow]` shape, the never-raises not-found-row semantics, the shared `list_*` paging contract, the path-safety guards, and the #145 follow-up pointer; and the `/refs <type> <id>` opencode slash command + read-only `ref-finder` subagent (issue #144's secondary request)). Regeneration: `specmgr docs` — `docs/api/biz.dfch.specmgr.server.md` is purely additive (25-line insertion); `docs/GENERATED.md`'s test-file count moved 358 → 361, picking up the three Phase 3 test files not regenerated at their commit time; `specmgr mcp-docs` — `docs/MCP.md` unchanged (a no-op, registration has not changed since Phase 2). `vulture src/ whitelist.py --min-confidence 60` clean: no new `whitelist.py` entries. Full gate green: `ruff format --check` (1705 files already formatted), `ruff check` (all checks passed), `pytest -n auto --cov=src --cov-report=` (3401 passed). Per Task 4.4's own wording, Phase 4's changes (`.opencode/command/refs.md` and `.opencode/agent/ref-finder.md`, verified in the Phase 4 entry above) ship in this same (folded) commit; Phase 6 (Verification & Closeout) remains.

#### 2026-09-23 05:27:27.086Z - Phase 4 verified: conformance + factual accuracy clean, /refs smoke test green (commit folded into Phase 5)

Implemented Task 4.3 and ran Task 4.4's gate. Conformance (no drift, no edits): `ref-finder.md` compared against the full agent set (`feat-reviewer.md`, `phase-orchestrator.md`, `phase-implementer.md`) — frontmatter key vocabulary and order match the `feat-reviewer.md` read-only subagent precedent exactly; the single difference is `bash: "*": deny` (a stricter variant of `feat-reviewer`'s ask+allow shell list), consistent with its own body (no shell; only consequential action is the `list_references` call) and leaving no file-mutation or shell-execution permission. `refs.md` compared against the full command set (`review-feature.md`, `implement-feature.md`, `release.md`) — `description` + `agent: ref-finder` (exactly the sibling file name `.opencode/agent/ref-finder.md`), a `$ARGUMENTS`-passing body that delegates to the subagent's own workflow and closes with the same do-not-edit/write/commit wording. Factual accuracy (all statements verified, no corrections): the tool name `list_references`; the source `type` list (13: req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs/adr) matching the tool's `Literal`; the documented `PagedResult` field set `{ total, offset, max_results, truncated, error_count, results }` matching `general/models/paged_result.py` (same six fields) and `ReferenceRow`'s `{ type, id, title, path, error }` matching `general/models/reference.py`; the error semantics matching — `validate_id` `ValueError` before any filesystem access, the source domain's `XNotFoundError` for a missing source (a repo-wide scan of every parseable feat document independently corroborated the raise path: unparseable legacy sources surface as `FeatNotFoundError`), and `resolve_reference`'s never-raising not-found rows with `title`/`path` null exactly when `error` is set; the paging contract matching `normalize_paging` (default 25, clamped to [1,100], offset floored to 0). Smoke test: `uv run --frozen python -c "from biz.dfch.specmgr.general.tools import list_references; r = list_references(type='feat', id='feat-144-ref-artifact'); ..."` → `5 False 0` plus five `adr` rows, each with a non-null H1 title and an existing absolute `docs/adr/` path (the plan's own `### Related Decisions` ADR set). Supplementary not-found exercise: a throwaway copy of this README under `/tmp/opencode` (one extra all-zero-uuid `ADR` bullet; no repo fixture — the same scan showed all 19 parseable feat documents carry `error_count=0` across their 21 references, so no existing document exercises this path) pointed at via `SPECMGR_FEAT_DIR` → `6 False 1`, the missing reference returned as a row with `title`/`path` null and the `AdrNotFoundError` message in `error` — exactly the row the subagent's **NOT FOUND** flagging is written for. Task 4.4 gate green: `ruff format --check` (1705 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no findings, exit 0), `pytest -n auto --cov=src --cov-report=` (3401 passed in 42.25s; no `src/` change this phase). Per Task 4.4's own wording, this phase's commit is folded into the Phase 5 docs commit. Correction: the two Phase 3 entry headings were mislabeled with local `+02:00` time under a `Z` suffix, and after verification caught the resulting newest-first parse failure they were corrected to true UTC (`2026-09-23 04:34:19.374Z`).

#### 2026-09-23 04:34:19.374Z - Phase 3 tests landed; full quality gate green with 100% coverage on the new src files (commit deferred to orchestrator)

Implemented Tasks 3.1-3.3: `tests/general/tools/test__references.py` (engine: `find_references` per all 10 tags + case/separator/anywhere-in-line variants + non-match guards (out-of-vocabulary tags, non-hex uuids, overlong hex tail, feat-NNN-slug ids), first-occurrence order, no engine-level dedup; `resolve_reference` resolved rows for every flat target domain + the ADR special case + never-raising not-found rows), `tests/general/tools/test_list_references.py` (ACC-001/002/003/004/005/006/009, the feat/ADR source-domain spread, and a live-`mcp` registration smoke test), and `tests/general/models/test_reference.py` (`ReferenceRow` field order, defaults, and `model_dump()` shape). 36 tests / 153 subtests, all passing; no implementation bug was exposed, so no `src/` change was needed. Gate green: `ruff format --check`, `ruff check`, `vulture` (no new whitelist entries), `pytest -n auto --cov=src` (3401 passed; 100% coverage on `_references.py`/`list_references.py`/`reference.py`). Task 3.4's commit is deferred to the orchestrator per the phase instructions.

#### 2026-09-22 21:02:41.263Z - Phase 2 implementation landed; full quality gate green (commit deferred to orchestrator)

Implemented Tasks 2.1-2.3: the new `ReferenceRow` model (`general/models/reference.py`, exported from `general/models/__init__.py`); the private, no-`mcp`-import engine `general/tools/_references.py` (`REFERENCE_TYPES` 10-tag vocabulary, the derived `_REFERENCE_PATTERN`, `find_references`, and `resolve_reference` plus per-target-domain `_load_<d>` resolvers — ADR special-cased: no doc-cache, `doc.body.title`); and the public `@mcp.tool()` module `general/tools/list_references.py` (source `validate_id` -> source-domain `load_by_id` -> `assert_within` -> raw `body_text`; first-occurrence dedup; per-ref resolution; `PagedResult[ReferenceRow]` wrap via `normalize_paging`/`paginate`). Registered in `general/tools/__init__.py` (docstring + import + `__all__`); `server.py` itself needed no change (its `general` import cascades) — tool registration verified against the live MCP server. Gate green: `ruff format --check`, `ruff check`, `vulture` (no new whitelist entries needed), `pytest -n auto` (3365 passed). Task 2.4's commit is deferred to the orchestrator per the phase instructions.

#### 2026-09-22 05:56:23.152Z - Design locked; plan finalized, follow-up #145 opened, /refs + ref-finder artifacts staged

Locked all Phase 1 open choices in the Plan: the tool is `list_references(type, id, max_results, offset) -> PagedResult[ReferenceRow]`; extraction is a case-insensitive, anywhere-in-body regex over the 10 reference tags (GOL/PRB/QA/UC/REQ/RSK/DEC/ADR/VCR/SYSRS) tolerant of a space or dash separator; the source is read as raw frontmatter-stripped body (`body_text`), targets via cache-backed `load_by_id`; a not-found reference is a row with `error` (list\*-style), a missing source raises the domain not-found error (same as `get_<d>`); results are paged with the shared `list_*` mechanism. Resolution is naive per-ref in v1 — recorded as a DEC below, with the per-domain batched optimization tracked in #145. Staged `.opencode/command/refs.md` and `.opencode/agent/ref-finder.md`.

#### 2026-09-21 19:30:35.557Z - Decision: ship the /refs command and the ref-finder subagent

Resolved the issue's secondary request at planning time: ship both an opencode `/refs <type> <id>` slash command (`.opencode/command/refs.md`) and a new read-only `ref-finder` subagent (`.opencode/agent/ref-finder.md`), following the `review-feature`/`feat-reviewer` conventions. The full rationale is in `### Decisions Made`.

#### 2026-09-21 19:10:10.879Z - Created

Drafted the feature plan from GitHub issue #144 'list referenced artifacts': a new dispatch-only `general/tools/` MCP tool that regex-extracts `<TYPE> <uuid>: <title>` cross-references from an artifact's body and resolves each to `type`/`id`/`title`/`path`, plus the issue's `/command` + subagent request (decided: ship both; see `### Decisions Made`).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-23 06:16:53.813Z - Documentation placement choices (Phase 5)

Choices beyond the plan's wording: (1) `server.py`'s docstring entry is placed after the `validate` entry and before the existing Path-safety paragraph and carries its own one-sentence `_path_safety` clause rather than amending that paragraph's list of covered tools — the surrounding prose stays byte-identical; (2) `AGENTS.md`'s new item is spliced into the same semicolon-separated enumeration sentence as `update`/`set_status`/`validate` (the period before "On a successful write" becomes a semicolon) instead of starting a new sentence; (3) `README.md`'s one-line pointer is a standalone sentence after Usage's example list (rather than a new example bullet) so the list keeps its purely plain-request shape, and the section's opencode paragraph names both config file paths (`.opencode/command/refs.md`, `.opencode/agent/ref-finder.md`) per the plan's Task 5.1 content spec; (4) `CHANGELOG.md` keeps the tool and the command + subagent as two separate `### Added` entries (rather than one combined) so release-notes curation can attribute each to its own ask.

#### 2026-09-23 05:27:27.086Z - Not-found smoke-test method: a throwaway `SPECMGR_FEAT_DIR` source doc (Phase 4)

The verification checklist preferred exercising the not-found path without creating fixtures (i.e. from an existing document that references a missing uuid) but marked the exercise optional. A repo-wide scan (running `list_references` on every feat document: 19 parseable documents, 21 references total, all `error_count=0`) showed no existing document references a missing uuid, so proving the real tool end-to-end (rather than just the `resolve_reference` engine helper) required one throwaway source. Choice: a copy of this feature's own README at `/tmp/opencode/refs-notfound/feat-0-notfound/` (frontmatter `id` renamed to match the folder; one extra all-zero-uuid `ADR` bullet in `### Related Decisions`), pointed at via the domain's own documented test-isolation env var `SPECMGR_FEAT_DIR` — the repo gains no fixture, the subagent-facing semantics (a row, not a raise; null `title`/`path`; the not-found message in `error`; `error_count` incremented) are proven through the actual `list_references` call, and the temp directory was removed after the run.

#### 2026-09-23 04:34:19.374Z - Test fixture strategy choices (Phase 3)

Choices beyond what the Plan locked: (1) the ACC-005 path-safety fixture points `SPECMGR_DOCS_DIR`/`SPECMGR_FEAT_DIR`/`SPECMGR_ADR_DIR` at paths that **do not exist** — a source lookup that ever reached the filesystem would surface as the domain's own `LookupError` (not-found), not `ValueError`, so asserting `ValueError` on those roots proves the guard fires before any filesystem access; (2) the ACC-001 SYSRS fixture puts the `RSK` reference in the optional `## Risks` section (SYSRS's `## Requirements` H3s accept only `REQ` bullets and `### Goals` only `GOL` bullets), so the canonical `GOL`/`RSK`/`REQ` bullet spread stays a *valid* SYSRS body; (3) the engine's resolved-row test exercises every one of the nine flat target domains (the Plan required two) plus the ADR special case — each `_load_<d>` is a four-line dispatcher, so the loop is cheap and takes `_references.py` to 100% coverage; (4) REQ-source fixtures place their reference lines in the free-form `## Description`/`## More Information` sections (a structurally-checked REQ section cannot hold a `<TAG> <uuid>` line).

#### 2026-09-22 21:02:41.263Z - Helper naming and two implementation-shape choices (Phase 2)

Choices beyond what the Plan locked: engine function names `find_references(text) -> list[tuple[str, str]]` (pairs lowercased, first-occurrence order, no dedup) and `resolve_reference(ref_type, ref_id) -> ReferenceRow`, with the vocabulary constant `REFERENCE_TYPES`. `_REFERENCE_PATTERN`'s tag group is **derived** from `REFERENCE_TYPES` (`"|".join(tag.upper() ...)`), so the vocabulary and the pattern cannot drift apart; the expanded regex is byte-identical to the Plan's literal `GOL|PRB|QA|UC|REQ|RSK|DEC|ADR|VCR|SYSRS` alternation. The 13-source-domain read is implemented as a data-driven `_SOURCE_LOADERS` table of `(<d>_base_dir, load_<d>_by_id)` pairs plus a single `_load_source_path` helper rather than 13 named adapter functions — every adapter body would have been the identical two lines, and the table keeps the source set visible in one place (the import style still mirrors `set_status.py`).

#### 2026-09-22 05:56:23.152Z - Resolution strategy: naive per-reference `load_by_id` (not batched per-domain)

Chosen for v1. `list_references` resolves each unique reference with the target domain's `load_by_id` (a `find_<type>_path` directory scan + cache-backed read), one at a time. Because `paginate` materializes the full row list before slicing, a single call resolves every unique reference in the source — so a SYSRS linking hundreds of artifacts performs hundreds of directory scans per page call. Cost is O(#refs × #domain); the result is correct and identical, so this is a performance tradeoff, not a correctness one. Rationale for v1: it is the simplest path, reuses the proven `get_<d>`/`load_by_id` mechanism verbatim (no new index-building code), and keeps the paging contract (`total`/`error_count`/`truncated`) exactly consistent with every `list_*` tool. The per-domain batched optimization — group refs by target domain, scan each distinct domain once into an `{id -> (title, path)}` index, O(1) lookups, re-emit in first-occurrence order (cost O(#distinct_domains + #refs)) — is deliberately deferred and tracked in #145 so it is not forgotten.

#### 2026-09-21 19:30:35.557Z - Ship the /refs command and the ref-finder subagent (issue #144 secondary request)

Issue #144 asks to also consider adding a `/command` and a subagent for the reference-listing tool. Decision (made at planning time, 2026-09-21): ship both. Rationale: the repo already keeps opencode commands under `.opencode/command/` and subagents under `.opencode/agent/`, and the commands that do real work delegate to a read-only subagent (`/review-feature` -> `feat-reviewer`); the wrapper is thin (one `list_references` call plus a narrated result), so the cost is two markdown config files with no packaging/CI impact; the subagent additionally provides a permission-isolated, reusable read-only agent that is callable via the task tool without a slash command. The task list carries a dedicated Phase 4 (Command + Subagent) for it.

### More Information

- GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/144 (opened by dfch on 2026-09-21).
- Follow-up (per-domain batched resolution for large reference lists): https://github.com/dfch/biz.dfch.SpecMgr/issues/145.
- Pull request (Phases 1-6, opened against `dev` from branch `feat-144-ref-artifact`): https://github.com/dfch/biz.dfch.SpecMgr/pull/147. Phase 7 (this branch's follow-up remediation) lands as additional commits on the same branch/PR -- it is not a separate PR or feature id.
