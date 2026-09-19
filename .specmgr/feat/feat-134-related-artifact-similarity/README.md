---
classification: null
created: '2026-09-17 07:40:37.439+02:00'
id: feat-134-related-artifact-similarity
status: planning
type: feat
updated: '2026-09-18 17:29:13.993+02:00'
version: 1.0.0
---

# Feature: Embedding-Based Related-Artifact Similarity Engine

## Plan

### Overview

specmgr currently has no way for an agent to discover artifacts that are "similar" or related to a given (or draft) requirement/decision/risk/etc. -- only advisory, unvalidated `## Related Artifacts` bullets on a few domains (that shape is scheduled for format validation in feat-135, issue #135) and one regex-validated (but never existence-checked) SYSRS cross-reference idiom. This feature adds a generic, cross-domain semantic similarity engine backed by local sentence embeddings (offline at inference time; one-time model download on first use), exposed via two new generic MCP tools (mirroring the existing `update`/`set_status`/`delete` dispatch-tool pattern): `find_related` (by existing document id) and `find_similar_text` (by free-form query text, for pre-creation dedup/discovery checks).

### Requirements

- REQ-001: The default embedding model MUST be runnable CPU-only (no GPU dependency, no torch) -- an ONNX-runtime-backed local model via `fastembed` (e.g. `BAAI/bge-small-en-v1.5`) satisfies this. First use requires a one-time model download from the Hub; inference itself is fully local.
- REQ-002: The embedding backend MUST be pluggable behind an `EmbeddingProvider` protocol exposing `embed` (document-side) and `embed_query` (query-side), with the CPU-only backend above as the shipped default, so a different backend can be substituted later without changing tool code.
- REQ-003: The feature MUST support being made unavailable at runtime, either because the optional dependency isn't installed (or the model fails to load, including first-use download failure), or via an explicit opt-out, and MUST NOT rely on the dependency being absent to hide the tools from clients. specmgr's `@mcp.tool()` decorators register tools via introspection at module-import time, independent of whether any runtime dependency the tool body needs is actually installed -- `find_related`/`find_similar_text` will always appear in the tool list once this module is imported by `server.py`. Therefore the embedding import itself MUST be lazy (deferred to first call, not at module import time, so a missing dependency never breaks tool *registration*), and both tools MUST return the same structured "unavailable" result (not raise) whenever either (a) the embedding backend fails to import or to load, or (b) the env var `SPECMGR_SIMILARITY_DISABLED` is present (presence-based, `os.environ.get(name) is not None` -- the repo's existing env-flag convention, `general/resources/config.py`) -- one code path, two triggers, consistent with the project's existing non-raising structured-result precedent (e.g. `set_status`'s `InvalidStatusResult`).
- REQ-004: Computed embeddings MUST be cached in-memory, per process, content-hash validated (mirroring the existing `DocCache` design from feat-107) -- no on-disk persistence.
- REQ-005: The embedding input text for a document is: its title, plus its frontmatter fields excluding bookkeeping-only keys (`id`, `type`, `version`, `created`, `updated`, `status`), plus its raw frontmatter-stripped body text (the same text `raw=True` reads already expose). Across all 12 whole-body domains the only surviving non-bookkeeping frontmatter field is `classification` (verified against every domain's frontmatter subclass). For a document that fails to parse, the input degrades to the file's full raw text (REQ-009).
- REQ-006: `find_related`/`find_similar_text` MUST default to searching every whole-body domain (req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs) and MUST exclude `adr` -- ADR is being removed as an artifact type entirely (see issue #46, "Remove adr artifact type"), so it is not a useful similarity target/source. The default set MUST be derived from the shared `WHOLE_BODY_DOMAINS` registry (REQ-012), which structurally excludes `adr`.
- REQ-007: A new optional dependency extra (name: `similarity`) MUST hold the default embedding backend's dependency (`fastembed`), keeping the base library and the `mcp`/`cli` extras dependency-light; the `dev` extra MUST include `similarity`, and the committed `uv.lock` MUST be regenerated in the same change.
- REQ-008: The embedding cache MUST be wired into the document lifecycle: the generic `delete` tool MUST invalidate the deleted path's entry, and `set_feat_id` MUST move (or invalidate) the old path's entry to the new one -- mirroring feat-107's `DocCache` integration, which this feature claims to follow.
- REQ-009: Error contract: an invalid `type`/`target_types` value or a `top_k` outside 1..100 MUST be rejected with `ValueError` before any filesystem access (path-safety convention); `find_related` with a missing source id MUST raise the domain's own `XNotFoundError` (like `get_<d>`); unparseable candidate documents MUST still appear in results, embedded from their full raw file text, with the `FAILED_TO_PARSE_MARKER` (`<failed to parse>`) title/status convention and `id = None`.
- REQ-010: Long documents MUST NOT be silently truncated at the model's max sequence length (512 tokens for `bge-small-en-v1.5`). Input exceeding the max length MUST be chunked, each chunk embedded, and the document vector computed as the renormalized mean of the chunk vectors (chunk + mean-pool, inside the default provider -- the protocol still returns one vector per input). Queries MUST go through `embed_query`, which applies the backend's retrieval instruction prefix (`bge-small`'s "Represent this sentence for searching relevant passages:"). A safety cap (`_MAX_CHUNKS_PER_DOC`, e.g. 128, evenly sampled above it) MUST bound worst-case per-document cost.
- REQ-011: The server MUST begin embedding the default corpus into the cache in a background thread at startup (lifespan), gated on the extra being importable and `SPECMGR_SIMILARITY_DISABLED` being absent. Warmup MUST NOT block server startup, MUST NOT raise out of startup, and MUST be a no-op when the feature is unavailable.
- REQ-012: A single shared `WHOLE_BODY_DOMAINS` registry in `general/tools` (the 12-domain tuple plus per-domain adapters: base-dir resolver, path iterator, `load_by_id`) MUST be the one source of the domain set; the five existing generic tools (`update`, `set_status`, `set_classification`, `delete`, `validate`) MUST be re-pointed at it alongside the two new similarity tools, so a future domain (e.g. `ac`) is added in one place.

### Acceptance Criteria

- [ ] ACC-001: `find_related(type, id, target_types=None, top_k=10, min_score=None)` returns ranked hits `(type, id, title, status, path, score)` across the default (non-adr) domain set, excluding the source document itself; unparseable candidates appear with `id = None` and marker title/status.
- [ ] ACC-002: `find_similar_text(query, target_types=None, top_k=10, min_score=None)` returns the same shape of ranked hits for a free-text query.
- [ ] ACC-003: With the `similarity` extra not installed, both tools still appear in the registered tool list and return the structured "unavailable" result when called (never raise, never disappear from the tool list).
- [ ] ACC-004: Setting `SPECMGR_SIMILARITY_DISABLED` (any value, presence-based) produces the same structured "unavailable" result even when the extra IS installed.
- [ ] ACC-005: Repeated calls against unchanged documents reuse cached embeddings (verified via a cache-hit counter/spy in tests) rather than recomputing.
- [ ] ACC-006: Changing a document's content invalidates its cached embedding (content-hash mismatch triggers recompute).
- [ ] ACC-007: `adr` never appears as a candidate and is rejected as a `type`/`target_types` value.
- [ ] ACC-008: A dedicated, real (non-mocked) test against the actual `fastembed` backend exists, gated behind its own pytest marker, and is excluded from the CI matrix; it asserts end-to-end ranking including retrieval of a >512-token document via mid-document content.
- [ ] ACC-009: With the extra installed but the model failing to load (e.g. no network for the first-use download), both tools return the same structured "unavailable" result (never raise).
- [ ] ACC-010: The `FastEmbedProvider` wrapper is unit-tested in CI with `fastembed.TextEmbedding` monkeypatched at the import boundary -- the gated real-backend test is the only similarity test CI excludes.
- [ ] ACC-011: The generic `delete` tool invalidates the deleted document's embedding-cache entry and `set_feat_id` moves/invalidates the renamed document's entry (no stale vector served, no leaked entry).
- [ ] ACC-012: Chunker + mean-pool unit tests cover: short input takes the single-embed fast path; long input splits at whitespace boundaries with each chunk within the model max length; the pooled vector is the renormalized mean (verified against a deterministic fake); the `_MAX_CHUNKS_PER_DOC` cap engages by even sampling.
- [ ] ACC-013: All five existing generic tools plus both similarity tools derive their domain set from the shared `WHOLE_BODY_DOMAINS` registry; the existing full test suite stays green after the re-pointing.
- [ ] ACC-014: At server startup, warmup populates the embedding cache in the background when enabled; with the extra missing or `SPECMGR_SIMILARITY_DISABLED` set, warmup is a no-op and the server starts normally; warmup never raises out of startup.
- [ ] ACC-015: `top_k` outside 1..100, an unknown `type`/`target_types` value, and a missing `find_related` source id are each rejected per REQ-009 (`ValueError` before filesystem access; the domain's `XNotFoundError` for the missing id).

### Scope

#### Included

- `EmbeddingProvider` protocol (`embed` + `embed_query`) plus default `FastEmbedProvider` (lazy import, CPU-only, BGE retrieval instruction prefix for queries, model-load lock for concurrent first calls).
- Chunk + mean-pool long-document strategy inside `FastEmbedProvider` (whitespace-boundary character chunks, single-embed fast path at/below the model max length, `_MAX_CHUNKS_PER_DOC` safety cap).
- Global in-memory, content-hash-validated, process-local embedding cache (DocCache blake2b pattern, innermost-lock ordering rule, provider-native vector storage, `reset()` test-only hook) -- no on-disk persistence.
- Embedding cache lifecycle wiring: generic `delete` invalidation, `set_feat_id` entry move.
- Embedding input extraction (title plus frontmatter minus bookkeeping keys incl. `status` plus raw body; unparseable documents embed their full raw text with marker title/status).
- Candidate enumeration registry: per-domain base-dir resolver + path iterator (the 11 flat domains via `iter_doc_paths`; `feat`'s `<base>/<id>/README.md` folder shape the one bespoke case), plus source resolution via per-domain `load_by_id` and the existing `_path_safety` guards.
- Pure-Python cosine-similarity ranking (dot product on normalized vectors), `top_k` capped at 1..100, optional `min_score`.
- Shared `WHOLE_BODY_DOMAINS` registry in `general/tools/` plus re-pointing of the five existing generic tools (`update`, `set_status`, `set_classification`, `delete`, `validate`).
- `find_related`/`find_similar_text` generic MCP tools in `general/tools/` (one module per tool, matching the `delete.py`/`update.py` convention).
- New `similarity` optional extra in `pyproject.toml` (holding `fastembed`), `dev` extra including it, `uv.lock` regeneration.
- `SPECMGR_SIMILARITY_DISABLED` env var support (presence-based).
- Background embedding warmup in `server.py`'s `_lifespan` (gated, never-raising).
- Unit tests (deterministic fake `EmbeddingProvider`, no real model/no network; `FastEmbedProvider` wrapper test with monkeypatched `fastembed`; warmup tests) plus one gated real-backend test excluded from CI via `pyproject.toml` `addopts`.
- pytest `embedding_model` marker registration + `addopts` exclusion in `[tool.pytest.ini_options]` (covers the CI and pre-commit pytest invocations without editing either).
- `whitelist.py` entries for test-only hooks (cache `reset`, provider seams).
- An ADR documenting this design (pluggable embedding-based semantic similarity, chunk + mean-pool long-document strategy, in-memory-only cache with delete/rename lifecycle wiring, new optional extra, ADR-domain exclusion, registration-vs-availability distinction from REQ-003, background warmup, and the corpus boundary -- the default set includes the dev docs under `.specmgr/feat` via `DEFAULT_FEAT_DIR`, which is intentional) -- this is architecture-level per this repo's own ADR-vs-feature-log guidance.
- Docs: `server.py` docstring, `AGENTS.md` `general/` bullet (plus fixing its stale feat status vocabulary `in-progress` -> `progress` while there), and `specmgr docs` + `specmgr mcp-docs` + `specmgr adr-toc` regeneration.

#### Explicitly Out Of Scope

- Persisting embeddings to disk across process restarts.
- Any structured/validated explicit cross-reference section on req/gol/dec/sop/rsk (a SYSRS-style curated `<TYPE> <uuid>: <title>` list) -- this work is already filed as feat-133-tags-dec-rsk (issue #133, Tags) and feat-135-related-artifacts-risks (issue #135, cross-reference format validation); this feature stays discovery-only (no existence-checking, no link validation).
- Multi-vector retrieval (ColBERT-style per-chunk max-sim) or a longer-context model (e.g. bge-m3, 8192 tokens) -- revisit only if chunk + mean-pool recall proves insufficient in practice.
- Supporting `adr` as a source or target domain.
- Any non-offline (API-based) embedding backend.
- Prompt changes: the `create_*` prompts' advisory near-duplicate `list_<d>` title checks adopting `find_similar_text` is a follow-up issue, not part of this feature.
- The `## Tags` addition to `dec`/`rsk` -- tracked separately in feat-133-tags-dec-rsk (issue #133); this feature's embedding input extraction works generically off raw body text regardless of whether Tags exists on a given domain.

### Dependencies

#### Depends On

- None strictly, though feat-133-tags-dec-rsk (issue #133), if shipped first, gives `dec`/`rsk` an extra structured signal that naturally flows into this feature's generic raw-body embedding input with no extra work required here. feat-135-related-artifacts-risks (issue #135) is adjacent, not a dependency: it format-validates the `## Related Artifacts` sub-lists on req/gol/dec/sop. If it ships first, this feature's Overview wording ("advisory, unvalidated bullets") goes stale and should be reworded.

#### Blocks

- None.

### Design Notes

Provider interface (`general/tools/_embedding.py`): an `EmbeddingProvider` protocol exposing `embed(self, texts: list[str]) -> list[list[float]]` (document-side) and `embed_query(self, texts: list[str]) -> list[list[float]]` (query-side). The default `FastEmbedProvider` wraps `fastembed.TextEmbedding`, constructed lazily via a `get_default_provider()` factory guarded by a load lock (the MCP SDK thread-pools every sync tool call, so concurrent first calls must not double-load the model), never imported at module level, so `server.py`'s unconditional domain-import line never fails even without the `similarity` extra installed.

Long documents (REQ-010): input longer than the model's max sequence (512 tokens for `bge-small`) is split into ~2000-character whitespace-boundary chunks (character-based on purpose -- no private tokenizer API; the backend's own `truncation=True` guards any slight overflow), each chunk is embedded, and the document vector is `normalize(mean(chunk_vectors))` -- renormalizing after the mean keeps cosine == dot-product comparability across documents of different lengths. Input at/below the max length takes a single-embed fast path (every current spec artifact does: 129-246 tokens measured across `docs/req`, `docs/gol`, `docs/sop`, `docs/sysrs`, `docs/tsk`; the documents that chunk are the 5k-40k-token `.specmgr/feat` READMEs). `_MAX_CHUNKS_PER_DOC = 128` with even sampling above it bounds worst-case per-document cost. `embed_query` prepends `bge-small`'s retrieval instruction ("Represent this sentence for searching relevant passages:") and never chunks (queries are short). Note the embedding cost per document is capped at `min(len, 128)` chunks regardless of file size, so first-call latency scales with document count, not total corpus size.

Availability check (REQ-003): a single shared helper, e.g. `_similarity_availability()`, checked first thing inside both tool bodies: if `SPECMGR_SIMILARITY_DISABLED` is present (`os.environ.get(name) is not None`), return the structured unavailable result; else attempt to obtain the default provider (lazy import), and on import/model-load failure (including first-use download failure) return the same structured unavailable result; else proceed with the real ranking logic. The unavailable result carries `{available: false, reason: "disabled" | "backend-unavailable", message: <enablement hint, e.g. install `biz-dfch-specmgr[similarity]` / unset the flag>}`.

Cache (`general/tools/_embedding_cache.py`): a single global instance, keyed by `(domain, resolved path)` to `(content_hash, vector)`, mirroring `DocCache`'s blake2b hash-check-then-recompute pattern but standalone, since a search call spans multiple domains at once, unlike per-domain parsing. `DocCache`'s lock-ordering rule applies: the cache lock guards dict bookkeeping only -- never file reads, never embedding computation -- and is always the innermost lock in any call stack. Vectors are stored in the provider's native arrays (numpy), not converted to Python `list[float]` (~7x memory bloat). `reset()` exists as a test-only hook (needs a `whitelist.py` entry, same precedent as `DocCache.reset`).

Background warmup (REQ-011): `server.py`'s currently no-op `_lifespan` starts a daemon thread at startup that embeds the full default corpus into the cache. Gated on the extra being importable and the flag being absent; every failure is swallowed (logged, and the demand path keeps working). This is safe to background precisely because ONNX Runtime runs its inference in C++ outside the GIL -- unlike the markdown-it/Pydantic parsing that feat-107's ADR (bfd76370) identified as the GIL-holding bottleneck. Rationale: the current default corpus is ~22 short spec docs plus ~52 feat READMEs totaling ~330k tokens (estimate: minutes of CPU, once per process); without warmup, that first call would likely exceed an MCP client's tool timeout even though the server-side work would continue and cache.

Candidate enumeration (REQ-012): the shared `WHOLE_BODY_DOMAINS` registry holds the 12-domain tuple plus, per domain, the base-dir resolver, the path iterator (flat `*.md` via the existing `iter_doc_paths` for the 11 flat domains; `<base>/<id>/README.md` for `feat`), and `load_by_id` -- the same per-domain adapter shape `general/tools/delete.py` already imports at module level. The five existing generic tools' copy-pasted domain sets (`_DELETE_TYPES`, `_VALIDATE_TYPES`, the `update`/`set_status`/`set_classification` `Literal[...]`s) are re-pointed at the registry's tuple.

Embedding input (`general/tools/_similarity_text.py`): `python-frontmatter` (already a base dependency) splits frontmatter from body; title = first H1 (it is also present in the body text -- deliberate double weighting of the title signal, no dedup); frontmatter keys minus `{id, type, version, created, updated, status}` -- across all 12 domains only `classification` survives (verified). Unparseable documents (parse failure of any channel) embed the full raw file text instead, and their result rows carry the `FAILED_TO_PARSE_MARKER` title/status with `id = None` (REQ-009). No per-domain field extraction, keeping the tool domain-agnostic by design.

Ranking: dot product on normalized vectors (== cosine), sorted descending, capped at `top_k` (validated 1..100, the same cap the `list_*` tools apply to `max_results`), optional `min_score` filter (cosine in [-1, 1]; `None` returns up to `top_k` hits regardless of score).

Real-backend test marker: name it after the feature/mechanism, not a generic informal term -- `@pytest.mark.embedding_model` (a real, non-mocked test that loads the actual `fastembed` model and asserts end-to-end ranking behavior, including mid-document retrieval of a long doc). Registered in `pyproject.toml`'s `[tool.pytest.ini_options]` `markers` and excluded from every default pytest invocation via `addopts = '-m "not embedding_model"'` -- one line covering both the CI matrix step and the pre-commit pytest hook without editing either file; developers opt in locally with `-m embedding_model` (first use requires a one-time model download from the Hub, which is why it is excluded from CI's offline-by-default posture).

Open questions/TODOs, not yet decided, to resolve during Phase 3: (1) does `find_related`/`find_similar_text` need additional or different ranking parameters beyond `target_types`/`top_k`/`min_score`, e.g. a per-domain result cap or an explicit "exclude these ids" list (score normalization is settled: dot product on normalized vectors); (2) should the embedding model be configurable (env var to select an alternate `fastembed` model), or is `BAAI/bge-small-en-v1.5` fixed for v1 -- the chunk-size/max-length constants live in the provider and would need updating alongside a model swap, so v1 fixes the model.

(Former open question 3 -- `status` inclusion in the embedded frontmatter -- is resolved: excluded. See Decisions Made.)

### Related Decisions

- New ADR to be written as part of Phase 1 (see Task List) -- not yet assigned an id. It will document the chunk + mean-pool strategy, the background warmup and its GIL rationale, the shared registry, the cache lifecycle wiring, and the corpus boundary (including the dev docs under `.specmgr/feat`).

### Task List

#### Phase 1: Provider + Cache + Availability + Registry

- [ ] Task 1.1: Write the ADR for this design (pluggable embedding provider with `embed`/`embed_query`, chunk + mean-pool long-document strategy, in-memory cache with delete/`set_feat_id` lifecycle wiring, new extra, ADR-domain exclusion, registration-vs-availability distinction from REQ-003, background warmup, shared `WHOLE_BODY_DOMAINS` registry, corpus boundary).
- [ ] Task 1.2: Add `similarity` extra to `pyproject.toml` with `fastembed`; add it to the `dev` extra; regenerate `uv.lock`.
- [ ] Task 1.3: Implement `EmbeddingProvider` protocol (`embed` + `embed_query`) plus `FastEmbedProvider` plus `get_default_provider()` (lazy import, model-load lock).
- [ ] Task 1.4: Implement `SPECMGR_SIMILARITY_DISABLED` (presence-based) plus `_similarity_availability()` shared helper and its structured "unavailable" result type (`{available, reason, message}` with enablement hint).
- [ ] Task 1.5: Implement the global in-memory embedding cache (blake2b content-hash validation, innermost-lock ordering, native-array vector storage, `reset()` test hook).
- [ ] Task 1.6: Extract the shared `WHOLE_BODY_DOMAINS` registry in `general/tools`; re-point `update`/`set_status`/`set_classification`/`delete`/`validate` at it; full suite stays green.

#### Phase 2: Text Extraction + Chunking + Ranking

- [ ] Task 2.1: Implement the candidate enumeration registry (per-domain base-dir + path iterator, `feat` folder-shape bespoke) plus source resolution via per-domain `load_by_id` with the existing `_path_safety` guards.
- [ ] Task 2.2: Implement embedding-input text extraction (title, frontmatter minus bookkeeping keys incl. `status`, raw body; unparseable -> full raw text + marker fields).
- [ ] Task 2.3: Implement the chunker + mean-pool in `FastEmbedProvider` (whitespace-boundary character chunks, single-embed fast path, `_MAX_CHUNKS_PER_DOC` even-sampling cap) plus `embed_query` with the BGE retrieval instruction prefix.
- [ ] Task 2.4: Implement pure-Python cosine (dot-on-normalized) ranking with `top_k` 1..100 validation and the `min_score` filter.

#### Phase 3: Tools + Wiring

- [ ] Task 3.1: Implement `find_related(type, id, target_types=None, top_k=10, min_score=None)`.
- [ ] Task 3.2: Implement `find_similar_text(query, target_types=None, top_k=10, min_score=None)`.
- [ ] Task 3.3: Resolve the open question on additional/different ranking parameters (see Design Notes) before finalizing tool signatures.
- [ ] Task 3.4: Wire `adr` rejection into both tools' `type`/`target_types` validation (via the shared registry).
- [ ] Task 3.5: Implement the error contract (REQ-009): `ValueError` for bad `type`/`target_types`/`top_k` before any filesystem access; the domain's `XNotFoundError` for a missing `find_related` source.
- [ ] Task 3.6: Wire the embedding cache into the generic `delete` tool (invalidate) and `set_feat_id` (move/invalidation).
- [ ] Task 3.7: Implement the `_lifespan` background warmup (gated on extra present + flag absent, daemon thread, never raising).

#### Phase 4: Tests & Docs

- [ ] Task 4.1: Unit tests with a deterministic fake `EmbeddingProvider` (cache hit/miss/invalidation, chunker + mean-pool math, ranking correctness, `target_types` filtering, `top_k`/`min_score`, self-exclusion, `adr` rejection, unavailable-result paths for all three triggers, error contract).
- [ ] Task 4.2: `FastEmbedProvider` wrapper unit test with `fastembed.TextEmbedding` monkeypatched at the import boundary (CI-covered).
- [ ] Task 4.3: Real-backend test under the `embedding_model` marker (end-to-end ranking incl. mid-document retrieval of a >512-token document); register the marker and the `addopts` exclusion in `pyproject.toml` (must precede the first commit of any marked test).
- [ ] Task 4.4: Warmup tests (enabled populates cache in background; flag set / extra missing -> no-op; never raises out of startup).
- [ ] Task 4.5: Update `server.py` docstring and `AGENTS.md`'s `general/` bullet (plus the `in-progress` -> `progress` status-vocabulary fix).
- [ ] Task 4.6: Regenerate docs via `specmgr docs` + `specmgr mcp-docs` + `specmgr adr-toc`.
- [ ] Task 4.7: Add `whitelist.py` entries for the test-only hooks (cache `reset`, provider seams).
- [ ] Task 4.8: Final gate: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, full `pytest -n auto --cov=src`, `specmgr coverage-badge`.

## Progress

### Current Status

**As of 2026-09-18**: Planning stage; plan refined after an internal review (chunk + mean-pool long-document strategy, shared `WHOLE_BODY_DOMAINS` registry, embedding-cache lifecycle wiring, background warmup, error contract, pytest `addopts` exclusion, doc-regeneration trio). Not started.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-18 15:29:13.994Z - Plan refined after internal review

Reviewed the plan against the codebase and the sibling features (feat-133, feat-135). Changes: (1) long documents are now chunked + mean-pooled in the default provider instead of silently truncated at 512 tokens, with a query-side `embed_query` method carrying the BGE retrieval instruction, plus a gated `_MAX_CHUNKS_PER_DOC` cap; (2) background embedding warmup in `_lifespan` so the full-corpus first call (~330k tokens across the feat READMEs, estimated minutes on CPU) never blocks a tool call or exceeds client timeouts -- safe to background because ONNX Runtime inference runs outside the GIL; (3) a shared `WHOLE_BODY_DOMAINS` registry in `general/tools` re-pointed at by all five existing generic tools plus both new ones; (4) embedding-cache lifecycle wiring into generic `delete` (invalidate) and `set_feat_id` (move); (5) explicit error contract (`ValueError` for bad `type`/`target_types`/`top_k` bounds before filesystem access, domain `XNotFoundError` for missing sources, unparseable candidates included with marker fields); (6) `status` excluded from the embedded frontmatter (resolves former open question 3); (7) `top_k` capped at 1..100; (8) CI exclusion of the real-backend test via `addopts` in `pyproject.toml` instead of editing ci.yml/pre-commit; (9) hit shape drops redundant `ref`, adds `status`; (10) `dev` extra gains `similarity`, `uv.lock` regenerated, `whitelist.py` entries planned; (11) doc regeneration expanded to `specmgr docs` + `specmgr mcp-docs` + `specmgr adr-toc`; (12) feat-135 cross-referenced as adjacent work. Requirements grew from 7 to 12, acceptance criteria from 8 to 15.

#### 2026-09-17 00:00:00.000Z - Created

Feature created from GitHub issue #134 to track the embedding-based related-artifact similarity engine, split out of a broader related-artifact discovery request alongside the smaller, independent feat-133-tags-dec-rsk (issue #133).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-18 15:29:13.994Z - Long documents are chunked + mean-pooled, never silently truncated

`fastembed`/`bge-small` would otherwise silently cut input at 512 tokens. Measured corpus: every current spec artifact (129-246 tokens) fits, but the ~52 `.specmgr/feat` READMEs (5k-40k tokens, ~330k total) would be reduced to their opening sections. Decision: chunk + mean-pool inside `FastEmbedProvider` (whitespace-boundary character chunks, `normalize(mean(chunk_vectors))`, `_MAX_CHUNKS_PER_DOC = 128` even-sampling cap) so the protocol still returns one vector per input and tool code stays unchanged; queries use a separate `embed_query` method carrying the BGE retrieval instruction prefix. Consequence: the full-corpus first call costs estimated minutes of CPU, so the server warms the cache in a background thread at startup -- safe because ONNX Runtime inference runs outside the GIL (unlike the markdown/Pydantic parsing feat-107 identified as the GIL-holding bottleneck). Multi-vector retrieval and longer-context models remain explicitly out of scope (revisit only if recall proves insufficient).

#### 2026-09-18 15:29:13.994Z - `status` is excluded from the embedded frontmatter

Resolves the former open question 3. `status` is a closed, low-cardinality enum with near-zero semantic signal for similarity; verified that across all 12 whole-body domains the only surviving non-bookkeeping frontmatter field after the exclusion is `classification` (free-text, meaningful when present).

#### 2026-09-18 15:29:13.994Z - Unparseable candidates are included, not excluded

A document that fails to parse still embeds (its full raw file text) and can appear in results with the `FAILED_TO_PARSE_MARKER` title/status and `id = None`, so broken artifacts stay discoverable instead of vanishing from similarity searches. The `find_related` source itself must be parseable (id lookup already skips unparseable files, so a missing/unparseable source raises the domain's `XNotFoundError`).

#### 2026-09-18 15:29:13.994Z - One shared `WHOLE_BODY_DOMAINS` registry, existing tools re-pointed

The 12-domain set was copy-pasted as `Literal`/tuples across the five existing generic tools; similarity would have been the sixth copy (and it must grow when the reserved `ac` domain lands). The registry is extracted in `general/tools` and all seven tools derive their domain set from it -- one place to add a domain, and `adr`'s exclusion becomes structural rather than per-tool.

#### 2026-09-18 15:29:13.994Z - Real-backend test excluded via `pyproject.toml` `addopts`

Registering `embedding_model` in `[tool.pytest.ini_options]` `markers` plus `addopts = '-m "not embedding_model"'` excludes the model-loading test from every default pytest invocation (CI matrix step and pre-commit hook) with one line, without editing `.github/workflows/ci.yml` or `.pre-commit-config.yaml`, and keeps the AGENTS.md dev command from accidentally triggering a model download. Developers opt in locally with `-m embedding_model`.

#### 2026-09-18 15:29:13.994Z - `SPECMGR_SIMILARITY_DISABLED` is presence-based

The flag is checked as `os.environ.get(name) is not None`, matching the repo's only existing env-flag convention (`specmgr://config` reports env vars by presence, never value). No truthy-string vocabulary to document or drift.

#### 2026-09-17 00:00:00.000Z - Tool registration is independent of dependency availability

Because `@mcp.tool()` registration happens via decorator introspection at module-import time, `find_related`/`find_similar_text` will always be visible in the tool list regardless of whether the `similarity` extra is installed. Runtime unavailability (missing dependency or explicit `SPECMGR_SIMILARITY_DISABLED` env var) is therefore handled inside the tool bodies via a shared structured "unavailable" result, not by conditionally registering the tools.

#### 2026-09-17 00:00:00.000Z - ADR excluded from similarity scope

`adr` is excluded as both a source and target domain, since it is being removed as an artifact type entirely (issue #46).

#### 2026-09-17 00:00:00.000Z - Offline real-backend test kept, but out of CI

A genuine (non-mocked) test against the real `fastembed` backend will exist, under a feature-named pytest marker (not "smoke"), but is excluded from the CI matrix and run manually/locally only, since first use requires a one-time model download.

### Related PRs / Commits

- [Issue #134](https://github.com/dfch/biz.dfch.SpecMgr/issues/134): tracking issue for this feature.

### More Information

- See feat-133-tags-dec-rsk (issue #133) for the companion, independent Tags-on-dec/rsk feature that was split out of the same original request.
- See feat-135-related-artifacts-risks (issue #135), the other sibling from the same design discussion: it removes the never-implemented `### Acceptance Criteria` sub-list from req/gol/dec/sop's `## Related Artifacts`, replaces it with a validated `### Risks` reference, and enforces a shared `"<TYPE> <uuid>: <title>"` format across those sub-lists. No dependency in either direction; it stays purely format-validation (no existence-checking), deliberately mirroring this feature's discovery-only scope. If feat-135 ships first, this feature's Overview wording ("advisory, unvalidated bullets") goes stale and should be reworded.
- Follow-up opportunity (not this feature, file separately once this ships): the seven `create_*` prompts (dec/feat/gol/prb/sop/sysrs/vcr) currently do advisory near-duplicate checks by scanning `list_<d>` titles; they are natural `find_similar_text` adopters.
