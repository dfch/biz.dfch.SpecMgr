---
classification: null
created: '2026-09-17 07:40:37.439+02:00'
id: feat-134-related-artifact-similarity
status: planning
type: feat
updated: '2026-09-17 07:40:37.439+02:00'
version: 1.0.0
---

# Feature: Embedding-Based Related-Artifact Similarity Engine

## Plan

### Overview

specmgr currently has no way for an agent to discover artifacts that are "similar" or related to a given (or draft) requirement/decision/risk/etc. -- only advisory, unvalidated `## Related Artifacts` bullets on a few domains and one regex-validated (but never existence-checked) SYSRS cross-reference idiom. This feature adds a generic, cross-domain semantic similarity engine backed by local, offline sentence embeddings, exposed via two new generic MCP tools (mirroring the existing `update`/`set_status`/`delete` dispatch-tool pattern): `find_related` (by existing document id) and `find_similar_text` (by free-form query text, for pre-creation dedup/discovery checks).

### Requirements

- REQ-001: The default embedding model MUST be runnable CPU-only (no GPU dependency, no torch) -- an ONNX-runtime-backed local model via `fastembed` (e.g. `BAAI/bge-small-en-v1.5`) satisfies this.
- REQ-002: The embedding backend MUST be pluggable behind an `EmbeddingProvider` protocol, with the CPU-only offline backend above as the shipped default, so a different backend can be substituted later without changing tool code.
- REQ-003: The feature MUST support being made unavailable at runtime, either because the optional dependency isn't installed, or via an explicit opt-out, and MUST NOT rely on the dependency being absent to hide the tools from clients. specmgr's `@mcp.tool()` decorators register tools via introspection at module-import time, independent of whether any runtime dependency the tool body needs is actually installed -- `find_related`/`find_similar_text` will always appear in the tool list once this module is imported by `server.py`. Therefore the embedding import itself MUST be lazy (deferred to first call, not at module import time, so a missing dependency never breaks tool *registration*), and both tools MUST return the same structured "unavailable" result (not raise) whenever either (a) the embedding backend fails to import/load, or (b) an explicit env var (e.g. `SPECMGR_SIMILARITY_DISABLED=1`) is set -- one code path, two triggers, consistent with the project's existing non-raising structured-result precedent (e.g. `set_status`'s `InvalidStatusResult`).
- REQ-004: Computed embeddings MUST be cached in-memory, per process, content-hash validated (mirroring the existing `DocCache` design from feat-107) -- no on-disk persistence.
- REQ-005: The embedding input text for a document is: its title, plus its frontmatter fields excluding bookkeeping-only keys (`id`, `type`, `version`, `created`, `updated`), plus its raw frontmatter-stripped body text (the same text `raw=True` reads already expose).
- REQ-006: `find_related`/`find_similar_text` MUST default to searching every whole-body domain (req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs) and MUST exclude `adr` by default -- ADR is being removed as an artifact type entirely (see issue #46, "Remove adr artifact type"), so it is not a useful similarity target/source.
- REQ-007: A new optional dependency extra (proposed name: `similarity`) MUST hold the default embedding backend's dependency (`fastembed`), keeping the base library and the `mcp`/`cli` extras dependency-light.

### Acceptance Criteria

- [ ] ACC-001: `find_related(type, id, target_types=None, top_k=10, min_score=None)` returns ranked hits (type, id, title, ref, path, score) across the default (non-adr) domain set, excluding the source document itself.
- [ ] ACC-002: `find_similar_text(query, target_types=None, top_k=10, min_score=None)` returns the same shape of ranked hits for a free-text query.
- [ ] ACC-003: With the `similarity` extra not installed, both tools still appear in the registered tool list and return the structured "unavailable" result when called (never raise, never disappear from the tool list).
- [ ] ACC-004: Setting `SPECMGR_SIMILARITY_DISABLED=1` produces the same structured "unavailable" result even when the extra IS installed.
- [ ] ACC-005: Repeated calls against unchanged documents reuse cached embeddings (verified via a cache-hit counter/spy in tests) rather than recomputing.
- [ ] ACC-006: Changing a document's content invalidates its cached embedding (content-hash mismatch triggers recompute).
- [ ] ACC-007: `adr` never appears as a candidate and is rejected as a `type`/`target_types` value.
- [ ] ACC-008: A dedicated, real (non-mocked) test against the actual `fastembed` backend exists, gated behind its own pytest marker, and is excluded from the CI matrix.

### Scope

#### Included

- `EmbeddingProvider` protocol plus default `FastEmbedProvider` (lazy import, CPU-only, offline).
- In-memory, content-hash-validated, process-local embedding cache (global, cross-domain).
- Embedding input extraction (title plus filtered frontmatter plus raw body).
- Pure-Python cosine-similarity ranking.
- `find_related`/`find_similar_text` generic MCP tools in `general/tools/`.
- New `similarity` optional extra in `pyproject.toml`.
- `SPECMGR_SIMILARITY_DISABLED` env var support.
- Unit tests (deterministic fake `EmbeddingProvider`, no real model/no network) plus one gated real-backend test excluded from CI.
- An ADR documenting this design (pluggable embedding-based semantic similarity, in-memory-only cache, new optional extra, ADR-domain exclusion) -- this is architecture-level per this repo's own ADR-vs-feature-log guidance.
- Docs: `server.py` docstring, `AGENTS.md` `general/` bullet, `docs/GENERATED.md`/`docs/api/` regeneration.

#### Explicitly Out Of Scope

- Persisting embeddings to disk across process restarts.
- Any structured/validated explicit cross-reference section on req/dec/rsk (a SYSRS-style curated `<TYPE> <uuid>: <title>` list) -- this is a distinct "explicit linking plus traceability validation" feature, deferred to a future issue if discovery proves useful.
- Supporting `adr` as a source or target domain.
- Any non-offline (API-based) embedding backend.
- The `## Tags` addition to `dec`/`rsk` -- tracked separately in feat-133-tags-dec-rsk (issue #133); this feature's embedding input extraction works generically off raw body text regardless of whether Tags exists on a given domain.

### Dependencies

#### Depends On

- None strictly, though feat-133-tags-dec-rsk (issue #133), if shipped first, gives `dec`/`rsk` an extra structured signal that naturally flows into this feature's generic raw-body embedding input with no extra work required here.

#### Blocks

- None.

### Design Notes

Provider interface (`general/tools/_embedding.py`): an `EmbeddingProvider` protocol exposing `embed(self, texts: list[str]) -> list[list[float]]`. The default `FastEmbedProvider` wraps `fastembed.TextEmbedding`, constructed lazily via a `get_default_provider()` factory, never imported at module level, so `server.py`'s unconditional domain-import line never fails even without the `similarity` extra installed.

Availability check (REQ-003): a single shared helper, e.g. `_similarity_availability()`, checked first thing inside both tool bodies: if `SPECMGR_SIMILARITY_DISABLED` is truthy, return the structured unavailable result; else attempt to obtain the default provider (lazy import), and on import/model-load failure return the same structured unavailable result; else proceed with the real ranking logic.

Cache (`general/tools/_embedding_cache.py`): a single global instance, keyed by `(domain, resolved path)` to `(content_hash, vector)`, mirroring `DocCache`'s hash-check-then-recompute pattern but standalone, since a search call spans multiple domains at once, unlike per-domain parsing.

Embedding input (`general/tools/_similarity_text.py`): title, plus frontmatter (minus `id`/`type`/`version`/`created`/`updated`, see the open question below re: `status`), plus raw frontmatter-stripped body -- all generic, no per-domain field extraction, keeping the tool domain-agnostic by design.

Ranking: pure-Python cosine similarity (dot product / norms), no new dependency beyond the embedding backend itself; sorted descending, capped at `top_k`.

Real-backend test marker: name it after the feature/mechanism, not a generic informal term -- e.g. `@pytest.mark.embedding_model` (a real, non-mocked test that loads the actual `fastembed` model and asserts end-to-end ranking behavior). Register the marker in `pyproject.toml`'s pytest config; exclude it from the default `pytest -n auto` invocation used in CI/pre-commit (e.g. `-m "not embedding_model"`), documented as a manual/local-only check to run before releases (first use requires a one-time model download from the Hub, which is why it's excluded from CI's offline-by-default posture).

Open questions/TODOs, not yet decided, to resolve during Phase 1/2/3 below: (1) does `find_related`/`find_similar_text` need additional or different ranking parameters beyond `target_types`/`top_k`/`min_score`, e.g. a per-domain result cap, a score-normalization method, or an explicit "exclude these ids" list; (2) should the embedding model be configurable (env var to select an alternate `fastembed` model), or is `BAAI/bge-small-en-v1.5` fixed for v1; (3) should `status` be excluded from the embedded frontmatter alongside `id`/`type`/`version`/`created`/`updated` (it's a closed, low-cardinality enum with arguably little semantic value), or kept in along with `classification`.

### Related Decisions

- New ADR to be written as part of Phase 1 (see Task List) -- not yet assigned an id.

### Task List

#### Phase 1: Provider + Cache + Availability

- [ ] Task 1.1: Write the ADR for this design (pluggable embedding provider, in-memory cache, new extra, ADR-domain exclusion, registration-vs-availability distinction from REQ-003).
- [ ] Task 1.2: Add `similarity` extra to `pyproject.toml` with `fastembed`.
- [ ] Task 1.3: Implement `EmbeddingProvider` protocol plus `FastEmbedProvider` plus `get_default_provider()` (lazy import).
- [ ] Task 1.4: Implement `SPECMGR_SIMILARITY_DISABLED` plus `_similarity_availability()` shared helper and its structured "unavailable" result type.
- [ ] Task 1.5: Implement the global in-memory embedding cache.

#### Phase 2: Text Extraction + Ranking

- [ ] Task 2.1: Resolve the open question on `status` inclusion/exclusion (see Design Notes).
- [ ] Task 2.2: Implement embedding-input text extraction.
- [ ] Task 2.3: Implement pure-Python cosine similarity ranking.

#### Phase 3: Tools

- [ ] Task 3.1: Implement `find_related(type, id, target_types=None, top_k=10, min_score=None)`.
- [ ] Task 3.2: Implement `find_similar_text(query, target_types=None, top_k=10, min_score=None)`.
- [ ] Task 3.3: Resolve the open question on additional/different ranking parameters (see Design Notes) before finalizing tool signatures.
- [ ] Task 3.4: Wire `adr` exclusion/rejection into both tools' `target_types`/`type` validation.

#### Phase 4: Tests & Docs

- [ ] Task 4.1: Unit tests with a deterministic fake `EmbeddingProvider` (cache hit/miss/invalidation, ranking correctness, `target_types` filtering, `top_k`/`min_score`, self-exclusion, `adr` rejection, unavailable-result paths for both triggers).
- [ ] Task 4.2: Real-backend test under the `embedding_model` marker, excluded from CI.
- [ ] Task 4.3: Update `server.py` docstring and `AGENTS.md`'s `general/` bullet.
- [ ] Task 4.4: Regenerate docs via `specmgr docs`.

## Progress

### Current Status

**As of 2026-09-17**: Planning stage; not started.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-17 00:00:00.000Z - Created

Feature created from GitHub issue #134 to track the embedding-based related-artifact similarity engine, split out of a broader related-artifact discovery request alongside the smaller, independent feat-133-tags-dec-rsk (issue #133).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-17 00:00:00.000Z - Tool registration is independent of dependency availability

Because `@mcp.tool()` registration happens via decorator introspection at module-import time, `find_related`/`find_similar_text` will always be visible in the tool list regardless of whether the `similarity` extra is installed. Runtime unavailability (missing dependency or explicit `SPECMGR_SIMILARITY_DISABLED` env var) is therefore handled inside the tool bodies via a shared structured "unavailable" result, not by conditionally registering the tools.

#### 2026-09-17 00:00:00.000Z - ADR excluded from similarity scope

`adr` is excluded as both a source and target domain, since it is being removed as an artifact type entirely (issue #46).

#### 2026-09-17 00:00:00.000Z - Offline real-backend test kept, but out of CI

A genuine (non-mocked) test against the real `fastembed` backend will exist, under a feature-named pytest marker (not "smoke"), but is excluded from the CI matrix and run manually/locally only, since first use requires a one-time model download.

### Related PRs / Commits

- [Issue #134](https://github.com/dfch/biz.dfch.SpecMgr/issues/134): tracking issue for this feature.

### More Information

See feat-133-tags-dec-rsk (issue #133) for the companion, independent Tags-on-dec/rsk feature that was split out of the same original request.
