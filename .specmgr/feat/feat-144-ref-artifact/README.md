---
classification: null
created: '2026-09-21 21:31:30.254+02:00'
id: feat-144-ref-artifact
status: done
type: feat
updated: '2026-10-07T06:21:40.899Z'
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
- **Target resolution (v1: naive per-ref)**: for each unique reference, dispatch on the tag to the target domain's cache-backed `load_by_id` and build a row. Nine flat domains use `<d>_base_dir` + the domain's cache-backed `load_by_id`, title `doc.body.text`; ADR is the special case — no doc-cache (ADR bfd76370), `adr_base_dir` (`SPECMGR_ADR_DIR`, default `docs/adr`), title `doc.body.title`. A reference whose target is absent (a `LookupError` from `load_by_id` — every domain not-found error subclasses it) yields a row with `title=None`, `path=None`, `error=str(exc)`; it never raises. This naive strategy resolves every unique reference on each page call (O(#refs) scans) — an accepted v1 limitation; the per-domain batched optimization is #145.
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

#### Phase 100: Design

- [x] Task 100.100: Pin the tool name (`list_references`), the result-row schema (`ReferenceRow(type, id, title, path, error)` wrapped in `PagedResult`), the 10-tag reference vocabulary, the extraction regex, the source raw-read vs. target cached-read split, the naive per-ref resolution strategy (→ `### Decisions Made`), and the follow-up #145. (The `/refs` command + `ref-finder` subagent decision is recorded in `### Decisions Made` at planning time.)
- [x] Task 100.110: Commit the finalized plan + the staged `/refs` command + `ref-finder` subagent artifacts as the feat-144 prep commit (markdown-only; no Python). The full quality gate with the tool's tests runs again in Phase 3/5 once the implementation lands.

#### Phase 110: Implementation

- [x] Task 110.100: Add the shared reference-extraction regex, 10-tag type vocabulary, and per-domain resolution dispatch in `general/tools/_references.py`
- [x] Task 110.110: Add the `ReferenceRow` model in `general/models/reference.py`
- [x] Task 110.120: Implement the `list_references` tool (source `validate_id` + `load_by_id` + `assert_within` + `body_text`; per-ref target resolution; `PagedResult` wrap) with `_path_safety` guards, registered in `general/tools/__init__.py` and `server.py`
- [x] Task 110.130: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 120: Tests

- [x] Task 120.100: Unit tests for extraction (per tag + case/dash/anywhere variants), deduplication, resolved-vs-not-found rows, and the empty-list case (tmp `SPECMGR_DOCS_DIR`/`SPECMGR_ADR_DIR` fixtures with real referenced artifacts)
- [x] Task 120.110: Path-safety tests (invalid source `type`/`id` raise before any filesystem access) and source-missing (raises the domain not-found error)
- [x] Task 120.120: Paging tests (`total`/`truncated`/`error_count` correct, `offset` advances, `max_results` clamps to [1,100], `offset` floors to 0)
- [x] Task 120.130: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 130: Command + Subagent

- [x] Task 130.100: Create `.opencode/agent/ref-finder.md` -- a read-only subagent (frontmatter: `mode: subagent`, read-only permission block with `edit`/`write` denied, `feat-reviewer`-style) whose workflow parses `<type> <id>`, calls `list_references`, and reports the rows with not-found references flagged
- [x] Task 130.110: Create `.opencode/command/refs.md` -- the `/refs <type> <id>` slash command with frontmatter `description` + `agent: ref-finder`, `review-feature`-style body
- [x] Task 130.120: Verify both files follow the conventions of the existing `.opencode/agent`/`.opencode/command` files and smoke-test `/refs` against a real document (deferred: requires `list_references` to exist)
- [x] Task 130.130: Run the full quality gate with tests and commit the phase (folded into the Phase 5 docs commit once the tool lands)

#### Phase 140: Documentation

- [x] Task 140.100: Update `server.py`'s module docstring, `AGENTS.md`, `README.md` (new `## Referencing Artifacts` section for `/refs`), and `CHANGELOG.md` (`[Unreleased]` → Added)
- [x] Task 140.110: Regenerate `docs/MCP.md` (`specmgr mcp-docs`) and `docs/api/` + `docs/GENERATED.md` (`specmgr docs`); update `whitelist.py` if vulture flags a new symbol
- [x] Task 140.120: Run the full quality gate with tests and commit the phase as a single commit (no push)

#### Phase 150: Verification & Closeout

- [x] Task 150.100: Run the full quality gate with tests as the final verification pass
- [x] Task 150.110: Update `### Current Status` and `### Updates`, and set the feature status via the generic `set_status` tool (`type="feat"`)
- [x] Task 150.120: Commit the phase as a single commit (no push)

#### Phase 160: Follow-Up Fixes (Review Remediation)

- [x] Task 160.100: Fix the docstring splice in `general/tools/__init__.py` (stray leading-space artifact from inserting the `list_references` paragraph mid-sentence into the existing `validate` docstring text); regenerate `docs/api/biz.dfch.specmgr.general.tools.md` (`specmgr docs`).
- [x] Task 160.110: Replace `list_references.py`'s hand-written `Literal["req", "uc", ..., "adr"]` `type` parameter with `Literal[*ALL_DOMAINS]` (imported from `general.tools._domains`), matching `set_status.py`/`update.py`/`delete.py`/`set_classification.py`/`validate.py`'s existing pattern (feat-125-domain-lists).
- [x] Task 160.120: Add the missing drift guard for `_SOURCE_LOADERS` in `list_references.py`: `assert set(_SOURCE_LOADERS) == set(ALL_DOMAINS), "..."` at module scope, identical in shape to `set_status.py`'s `_ADAPTERS`/`ALL_DOMAINS` guard. No restructuring of the data-driven dict itself (Phase 2's documented design choice stands).
- [x] Task 160.130: In `_references.py`, add `assert set(_TARGET_RESOLVERS) == set(REFERENCE_TYPES), "..."` at module scope, and narrow `resolve_reference`'s `except LookupError` so a `KeyError` from a missing `_TARGET_RESOLVERS` entry (a programming error) is not silently folded into the same not-found `ReferenceRow` path as a legitimate domain `XNotFoundError`.
- [x] Task 160.140: Tick `ACC-001`..`ACC-009` to `[x]` in the Acceptance Criteria section, each with an inline evidence sentence (repo convention, e.g. `feat-36-delete/README.md:52-59`). (Done in this same doc-only edit.)
- [x] Task 160.150: Document the accepted code-fence/inline-code-span extraction caveat in `_references.py`'s module docstring (the Design Notes bullet above is staged); add one test in `test__references.py` pinning the (accepted) behavior of a reference-shaped string inside a fenced/inline code span.
- [x] Task 160.160: Replace the Unicode em dash "—" with ASCII "--" in `.opencode/agent/ref-finder.md`'s `description` field and `.opencode/command/refs.md`'s body, matching `feat-reviewer.md`/`review-feature.md`/`phase-implementer.md`'s typographic convention.
- [x] Task 160.170: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`); reopen the feature status via `set_status` (`type="feat"`, `done` -> `progress`) at phase start (done in this edit) and set it back to `done` on closeout; update `### Current Status`/`### Updates`; commit as a single phase commit on the existing `feat-144-ref-artifact` branch (amending open PR #147, no push unless instructed).

#### Phase 170: Minor Cleanup Fixes

- [x] Task 170.100: Fix the stale req-first/adr-last domain-list ordering in `list_references.py`'s `@mcp.tool()` `description=` (replace the hand-written list with a dynamic `f"{', '.join(ALL_DOMAINS)}"` interpolation, mirroring `set_status.py`'s own pattern) and in its function docstring's `Parameters` section (correct the literal order to match `ALL_DOMAINS`'s adr-first order); apply the same adr-first ordering correction at the three other sites that hand-write this list in the stale order: `server.py`'s module docstring, `AGENTS.md`, and `CHANGELOG.md`; regenerate `docs/MCP.md`/`docs/api/` to pick up the description-text change.
- [x] Task 170.110: Fix the complexity-note overstatement in the plan's Design Notes ("Target resolution" bullet) and Decisions Made ("Resolution strategy" entry): `O(#refs × #domain) scans`/`Cost is O(#refs × #domain)` corrected to `O(#refs) scans`/`Cost is O(#refs)` (`resolve_reference` is an O(1) dict dispatch per reference, not a scan across domains).
- [x] Task 170.120: Replace the Unicode ellipsis "…" with ASCII "..." in `.opencode/agent/ref-finder.md` and `.opencode/command/refs.md`'s truncated-uuid examples, matching the ASCII convention already used in `feat-reviewer.md`/`phase-orchestrator.md`.
- [x] Task 170.130: Extend `TestListReferencesSourceMissing` in `test_list_references.py` to cover the six source domains it was missing (`tsk`, `qa`, `prb`, `dec`, `sop`, `vcr`), in the exact same parametrized-cases style already used for the other 7 domains, asserting the same not-found-raises-identical-to-`get_<d>` contract for all 13 supported source domains.
- [x] Task 170.140: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`, `specmgr docs`, `specmgr adr-toc`); confirm `docs/api/`/`docs/MCP.md` show only the Task 8.1 description-text diff; update `### Current Status`/`### Updates` and bump the frontmatter `updated` timestamp.

## Progress

### Current Status

Phase 8 (Minor Cleanup Fixes) is complete: all four cosmetic/consistency findings from a second independent review of PR #147 (the stale req-first/adr-last domain-list ordering in `list_references.py`'s description/docstring plus the three other sites that mirrored it, the `O(#refs × #domain)` complexity-note overstatement in the plan, the Unicode ellipsis in the `/refs` command + `ref-finder` subagent examples, and the missing `tsk`/`qa`/`prb`/`dec`/`sop`/`vcr` source-domain coverage in `TestListReferencesSourceMissing`) are resolved, the full quality gate is green, and `docs/MCP.md`/`docs/api/` show only the expected Task 8.1 description-text diff. See the dated entries below for the exact fixes (Phase 8) and the separately-landed Phase 7 review remediation.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-23 16:28:40.635Z - Phase 8 minor cleanup fixes complete: stale domain-list ordering, complexity-note overstatement, Unicode ellipsis, and missing ACC-006 coverage all resolved, full gate green

Implemented Tasks 8.1-8.5, a second independent review's four cosmetic/consistency findings on PR #147. **Task 8.1** (Inconsistency): `list_references.py`'s `@mcp.tool()` `description=` hand-wrote a stale req-first/adr-last domain list (`req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs, adr`); it now interpolates `f"{', '.join(ALL_DOMAINS)}"`, byte-identical in spirit to `set_status.py`'s own pattern, so it can never drift from the shared source of truth again. The function's own docstring `Parameters` section hand-writes a literal list (a docstring cannot cleanly interpolate an f-string), so it was corrected in place to `adr`-first order matching `ALL_DOMAINS`. The same stale req-first/adr-last ordering was corrected (literal reordering only, no prose changes) at the three other sites that hand-write this same list: `server.py`'s module docstring (`list_references` entry), `AGENTS.md` (line ~567), and `CHANGELOG.md` (line ~17). `specmgr docs` and `specmgr mcp-docs` were regenerated; `git diff` confirms `docs/api/biz.dfch.specmgr.general.tools.list_references.md`, `docs/api/biz.dfch.specmgr.server.md`, and `docs/MCP.md` show exactly the expected description-text diff (the domain list reordered), nothing else -- `docs/GENERATED.md` and `docs/adr/README.md` are unchanged (no-op). Two docstring sites in the same file that phrase the domain set as "every whole-body domain (req/.../sysrs) plus adr" (the module docstring and the tool docstring's opening paragraph) were deliberately left alone: they describe `WHOLE_BODY_DOMAINS` (its own, legitimately req-first canonical order) plus `adr` appended as a separate clause, not a flat enum-order list, so they were not the "stale enum order" bug the other four sites had. **Task 8.2** (Improvement): the Design Notes "Target resolution (v1: naive per-ref)" bullet's `O(#refs × #domain) scans` and the Decisions Made "Resolution strategy" entry's `Cost is O(#refs × #domain)` both overstated the cost -- `resolve_reference` is an O(1) dict dispatch per reference (`_TARGET_RESOLVERS[ref_type]`), not a scan across domains -- corrected to `O(#refs) scans`/`Cost is O(#refs)`, rest of each sentence unchanged. **Task 8.3** (Improvement): the Unicode ellipsis "…" in `.opencode/agent/ref-finder.md`'s (line 37) and `.opencode/command/refs.md`'s (line 6) truncated-uuid examples (`sysrs 3f2a1b3c-…`, `dec 9c1f…`) is replaced with ASCII "..." throughout both files, matching the convention already used in `feat-reviewer.md`/`phase-orchestrator.md`. **Task 8.4** (Gap): `TestListReferencesSourceMissing` only exercised 7 of the 13 supported source domains (`req`/`uc`/`sysrs`/`gol`/`rsk`/`feat`/`adr`) even though `_SOURCE_LOADERS` dispatches all 13 through the identical generic code path; extended the same parametrized `cases` list (same fixture, same subtest-per-domain style) with `tsk`/`qa`/`prb`/`dec`/`sop`/`vcr` (all UUID-shaped, `_MISSING_UUID` + the domain's own `XNotFoundError`), importing the six additional `XNotFoundError` classes at the top of the file alongside the existing ones -- no new test pattern introduced. Gate green: `ruff format --check` (1709 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean, no new whitelist entries), `pytest -n auto --cov=src --cov-report=` (3402 passed, up from 3401 -- the six new subtests run under the same parametrized test method), `specmgr docs`, `specmgr adr-toc` (no-op). Files touched: `src/biz/dfch/specmgr/general/tools/list_references.py`, `src/biz/dfch/specmgr/server.py`, `AGENTS.md`, `CHANGELOG.md`, `.specmgr/feat/feat-144-ref-artifact/README.md`, `.opencode/agent/ref-finder.md`, `.opencode/command/refs.md`, `tests/general/tools/test_list_references.py`, plus the regenerated `docs/MCP.md`/`docs/api/biz.dfch.specmgr.general.tools.list_references.md`/`docs/api/biz.dfch.specmgr.server.md`. No feature status change (`set_status`) was needed -- the feature was already `done` and stays `done`; this phase's remediation did not reopen the status per the phase-implementer instructions it was scoped under.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-23 15:34:38.242Z - Phase 7 implementation choices

Choices beyond the plan's wording: (1) the two new drift guards sit at module scope, directly after their respective table definitions (`_SOURCE_LOADERS` in `list_references.py`, `_TARGET_RESOLVERS` in `_references.py`), in the exact sibling shape `assert set(_TABLE) == set(<source>), ("...")`, with the trailing reference "(feat-144-ref-artifact, Task 7.3/7.4)" in place of the siblings' "(feat-125-domain-lists, REQ-006)"; the guard messages name the table, the drifted source, and the concrete fix action (add/remove the domain's `(<d>_base_dir, load_<d>_by_id)` pair or `_load_<d>` resolver); (2) the KeyError narrowing (Task 7.4) keeps a single `except LookupError` clause around only the resolver call -- `resolver = _TARGET_RESOLVERS[ref_type]` is hoisted above the `try`, so a `KeyError` from a missing entry propagates loudly as a programming error -- with two short inline comments marking the intent; no new exception type is introduced, matching the repo's message-only convention, and `resolve_reference` gains a `KeyError` `Raises` section plus the "never raises for a missing document" wording in both docstrings; (3) the Phase 3 registration test's hand-listed 13-name enum literal was replaced by `list(ALL_DOMAINS)` (imported from `general.tools._domains`) -- the feat-125 sweep ruling explicitly forbids hand-listed domain-name sets in `tests/` modules too, and `test_delete.py`/`test_update.py`'s registration tests already assert their enums derived from the shared tuples; the test's name/docstring ("13 value type enum") stays accurate since `ALL_DOMAINS` has 13 members; (4) Task 7.7's em-dash replacement was scoped to ALL occurrences of "—" in both `.opencode/` files (10 in `ref-finder.md`'s frontmatter description and body, 1 in `refs.md`'s body), not just the fields the plan text names -- the review finding was typographic and the plan's own NOTE confirms both files' description AND body carry em dashes; both files are now fully convention-conformant (verified: zero "—" remain; the "…" ellipses in example uuids are a distinct character and were left alone, as were the plan README's own pre-existing em dashes, which are out of Task 7.7's scope); (5) the new plan-README paragraphs (this Updates entry and the Decisions entry) use ASCII "--" to match the immediately-preceding Phase 7 staging entry and the repo convention the review cited, even though older Phase 1-6 entries in the same file use "—"; (6) the Plan section's staged "Caveat (code spans, planned — Phase 7)" Design Notes bullet was left byte-identical per the phase instructions -- it records the same substance as the new module-docstring caveat, and "planned" is a historical staging marker superseded by this entry rather than a Plan text to be retro-edited.

#### 2026-09-23 06:16:53.813Z - Documentation placement choices (Phase 5)

Choices beyond the plan's wording: (1) `server.py`'s docstring entry is placed after the `validate` entry and before the existing Path-safety paragraph and carries its own one-sentence `_path_safety` clause rather than amending that paragraph's list of covered tools — the surrounding prose stays byte-identical; (2) `AGENTS.md`'s new item is spliced into the same semicolon-separated enumeration sentence as `update`/`set_status`/`validate` (the period before "On a successful write" becomes a semicolon) instead of starting a new sentence; (3) `README.md`'s one-line pointer is a standalone sentence after Usage's example list (rather than a new example bullet) so the list keeps its purely plain-request shape, and the section's opencode paragraph names both config file paths (`.opencode/command/refs.md`, `.opencode/agent/ref-finder.md`) per the plan's Task 5.1 content spec; (4) `CHANGELOG.md` keeps the tool and the command + subagent as two separate `### Added` entries (rather than one combined) so release-notes curation can attribute each to its own ask.

#### 2026-09-23 05:27:27.086Z - Not-found smoke-test method: a throwaway `SPECMGR_FEAT_DIR` source doc (Phase 4)

The verification checklist preferred exercising the not-found path without creating fixtures (i.e. from an existing document that references a missing uuid) but marked the exercise optional. A repo-wide scan (running `list_references` on every feat document: 19 parseable documents, 21 references total, all `error_count=0`) showed no existing document references a missing uuid, so proving the real tool end-to-end (rather than just the `resolve_reference` engine helper) required one throwaway source. Choice: a copy of this feature's own README at `/tmp/opencode/refs-notfound/feat-0-notfound/` (frontmatter `id` renamed to match the folder; one extra all-zero-uuid `ADR` bullet in `### Related Decisions`), pointed at via the domain's own documented test-isolation env var `SPECMGR_FEAT_DIR` — the repo gains no fixture, the subagent-facing semantics (a row, not a raise; null `title`/`path`; the not-found message in `error`; `error_count` incremented) are proven through the actual `list_references` call, and the temp directory was removed after the run.

#### 2026-09-23 04:34:19.374Z - Test fixture strategy choices (Phase 3)

Choices beyond what the Plan locked: (1) the ACC-005 path-safety fixture points `SPECMGR_DOCS_DIR`/`SPECMGR_FEAT_DIR`/`SPECMGR_ADR_DIR` at paths that **do not exist** — a source lookup that ever reached the filesystem would surface as the domain's own `LookupError` (not-found), not `ValueError`, so asserting `ValueError` on those roots proves the guard fires before any filesystem access; (2) the ACC-001 SYSRS fixture puts the `RSK` reference in the optional `## Risks` section (SYSRS's `## Requirements` H3s accept only `REQ` bullets and `### Goals` only `GOL` bullets), so the canonical `GOL`/`RSK`/`REQ` bullet spread stays a *valid* SYSRS body; (3) the engine's resolved-row test exercises every one of the nine flat target domains (the Plan required two) plus the ADR special case — each `_load_<d>` is a four-line dispatcher, so the loop is cheap and takes `_references.py` to 100% coverage; (4) REQ-source fixtures place their reference lines in the free-form `## Description`/`## More Information` sections (a structurally-checked REQ section cannot hold a `<TAG> <uuid>` line).

#### 2026-09-22 21:02:41.263Z - Helper naming and two implementation-shape choices (Phase 2)

Choices beyond what the Plan locked: engine function names `find_references(text) -> list[tuple[str, str]]` (pairs lowercased, first-occurrence order, no dedup) and `resolve_reference(ref_type, ref_id) -> ReferenceRow`, with the vocabulary constant `REFERENCE_TYPES`. `_REFERENCE_PATTERN`'s tag group is **derived** from `REFERENCE_TYPES` (`"|".join(tag.upper() ...)`), so the vocabulary and the pattern cannot drift apart; the expanded regex is byte-identical to the Plan's literal `GOL|PRB|QA|UC|REQ|RSK|DEC|ADR|VCR|SYSRS` alternation. The 13-source-domain read is implemented as a data-driven `_SOURCE_LOADERS` table of `(<d>_base_dir, load_<d>_by_id)` pairs plus a single `_load_source_path` helper rather than 13 named adapter functions — every adapter body would have been the identical two lines, and the table keeps the source set visible in one place (the import style still mirrors `set_status.py`).

#### 2026-09-22 05:56:23.152Z - Resolution strategy: naive per-reference `load_by_id` (not batched per-domain)

Chosen for v1. `list_references` resolves each unique reference with the target domain's `load_by_id` (a `find_<type>_path` directory scan + cache-backed read), one at a time. Because `paginate` materializes the full row list before slicing, a single call resolves every unique reference in the source — so a SYSRS linking hundreds of artifacts performs hundreds of directory scans per page call. Cost is O(#refs); the result is correct and identical, so this is a performance tradeoff, not a correctness one. Rationale for v1: it is the simplest path, reuses the proven `get_<d>`/`load_by_id` mechanism verbatim (no new index-building code), and keeps the paging contract (`total`/`error_count`/`truncated`) exactly consistent with every `list_*` tool. The per-domain batched optimization — group refs by target domain, scan each distinct domain once into an `{id -> (title, path)}` index, O(1) lookups, re-emit in first-occurrence order (cost O(#distinct_domains + #refs)) — is deliberately deferred and tracked in #145 so it is not forgotten.

#### 2026-09-21 19:30:35.557Z - Ship the /refs command and the ref-finder subagent (issue #144 secondary request)

Issue #144 asks to also consider adding a `/command` and a subagent for the reference-listing tool. Decision (made at planning time, 2026-09-21): ship both. Rationale: the repo already keeps opencode commands under `.opencode/command/` and subagents under `.opencode/agent/`, and the commands that do real work delegate to a read-only subagent (`/review-feature` -> `feat-reviewer`); the wrapper is thin (one `list_references` call plus a narrated result), so the cost is two markdown config files with no packaging/CI impact; the subagent additionally provides a permission-isolated, reusable read-only agent that is callable via the task tool without a slash command. The task list carries a dedicated Phase 4 (Command + Subagent) for it.

### More Information

- GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/144 (opened by dfch on 2026-09-21).
- Follow-up (per-domain batched resolution for large reference lists): https://github.com/dfch/biz.dfch.SpecMgr/issues/145.
- Pull request (Phases 1-6, opened against `dev` from branch `feat-144-ref-artifact`): https://github.com/dfch/biz.dfch.SpecMgr/pull/147. Phase 7 (this branch's follow-up remediation) lands as additional commits on the same branch/PR -- it is not a separate PR or feature id.
