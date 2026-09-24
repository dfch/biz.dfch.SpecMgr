---
status: accepted
decision-makers: dfch
id: 750842b2-aca4-4649-ba0c-855ec8e1f505
version: 1.2.0
---

# Add an embedding-based, cross-domain semantic similarity engine (find_related / find_similar_text) with a pluggable CPU-only provider

## Context and Problem Statement

specmgr has no way for an agent to discover artifacts that are "similar" to a given or draft requirement/decision/risk. Today there are only: (a) advisory `## Related Artifacts` bullets on req/gol/dec/sop that carry no format validation and no existence check (feat-135, issue #135, adds format validation but deliberately no semantic or existence matching), and (b) the SYSRS/VCR regex-validated `<TYPE> <uuid>: <title>` cross-reference idiom, which also never checks the referenced id exists. The `create_*` prompts (dec/feat/gol/prb/sop/sysrs/vcr) mitigate near-duplicate creation with an advisory, title-only, single-domain `list_<d>` scan. GitHub issue #134 asks for a generic, cross-domain semantic similarity engine -- offline, CPU-only -- exposed as two new generic MCP tools: `find_related` (by existing document id) and `find_similar_text` (by free-form query text, for pre-creation dedup/discovery).

The design must reconcile with the existing architecture: the base library stays dependency-light (extras split); `@mcp.tool()` registration happens at module-import time, so `server.py`'s unconditional domain-import line can never fail because an optional dependency is missing; the filesystem is the sole source of truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3); repeated reads are content-hash-validated in-memory (ADR bfd76370-b59b-4d65-b550-a969f6c93c9d); cross-domain operations are dispatch-only generic tools (ADR 36905d5b-8057-4294-8665-c7eed5534db0); id resolution is path-safety-guarded (ADR 1af6787b-eaab-4e8f-888f-531c1e76c19d). The ADR domain is being removed as an artifact type entirely (issue #46, branch `feat-46-remove-adr` in flight), so it is excluded from similarity scope.

## Decision Drivers

Local-first and offline at inference time (no API keys, no per-call network; a one-time model download is acceptable, and CI stays offline-by-default). CPU-only with no GPU/torch dependency; the ML dependency must live in a new optional extra so the base/`mcp`/`cli` extras stay dependency-light. Tool *registration* must be independent of dependency *availability* (lazy import; unavailability is a structured result inside the tool body, per the non-raising structured-result precedent of ADR 519d1206-4d2a-4500-9046-6db635209996/b399f1ce-ed42-4929-b01c-7a57d18e8014 and ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6). No staleness: any cache must be content-hash-validated, refining ADR 33c5ab08 exactly as ADR bfd76370 did for parsing. Cross-domain without per-domain code sprawl: one shared domain registry (the 12-domain set is currently copy-pasted across the five generic tools). Bounded latency: MCP clients time out tool calls, and the full-corpus embed (current corpus: ~22 short spec docs + ~52 feat READMEs ~ 330k tokens) must not block one. Testable in CI without the model; the real-backend test is gated behind its own pytest marker.

## Considered Options

(1) An embedding-based semantic engine with a local CPU-only ONNX backend (`fastembed` + `BAAI/bge-small-en-v1.5`), a pluggable provider protocol, chunk + mean-pool long-document strategy, a content-hash-validated in-memory vector cache, a shared domain registry, and background warmup. (2) Lexical keyword retrieval (TF-IDF/BM25, e.g. sqlite FTS5). (3) API-based (hosted) embeddings. (4) Do nothing -- keep the advisory title scans.

## Decision Outcome

Chosen option: (1), with these sub-decisions (each normative for implementation):

- **Backend:** `fastembed` wrapping `BAAI/bge-small-en-v1.5` (ONNX Runtime, CPU-only, 384-dim). The model is fixed for v1; configurability is deferred.
- **Provider seam:** an `EmbeddingProvider` protocol in `general/tools/_embedding.py` with `embed` (document-side) and `embed_query` (query-side; `bge-small`'s retrieval instruction prefix "Represent this sentence for searching relevant passages:"). `FastEmbedProvider` is constructed lazily via `get_default_provider()` guarded by a load lock; `fastembed` is never imported at module level, so `server.py`'s unconditional domain-import line never fails without the extra.
- **Availability:** both tools always register. A shared `_similarity_availability()` helper checked first in both tool bodies returns a structured `{available: false, reason: "disabled" | "backend-unavailable", message: <enablement hint>}` result (never raising) when (a) the backend fails to import or load (including first-use download failure), or (b) `SPECMGR_SIMILARITY_DISABLED` is present (presence-based, matching the `specmgr://config` env-flag convention).
- **Long documents:** input exceeding the model max (512 tokens) is split into ~2000-character whitespace-boundary chunks, each chunk embedded, and the document vector computed as `normalize(mean(chunk_vectors))` -- never silent truncation. `_MAX_CHUNKS_PER_DOC = 128` (evenly sampled above it) bounds worst-case cost. Input at/below the max takes a single-embed fast path (every current spec artifact does).
- **Cache:** a single global, process-local, `blake2b` content-hash-validated in-memory vector cache (`general/tools/_embedding_cache.py`), keyed `(domain, resolved path) -> (hash, vector, similarity_text)` -- the entry carries the candidate's result-row metadata (`SimilarityText`: the exact embedding input plus the validated `id`/`title`/`status`) alongside its vector, since the metadata is a pure function of the hashed text (a hash match means the text is byte-identical, so the stored metadata is still exactly valid) and serving it from the entry removes the demand path's redundant second file read and parse (a warm candidate is one read and no parse, a cold one one of each -- feat-134 Phase 6, ACC-017) -- mirroring ADR bfd76370's validation guarantee and its lock-ordering rule (cache lock innermost, never held across embedding computation). Vectors are stored in the provider's native arrays. No on-disk persistence. Lifecycle wiring: the generic `delete` tool invalidates the removed path's entry; `set_feat_id` moves it.
- **Corpus and registry:** the default target set is every whole-body domain (req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs) via a new shared `WHOLE_BODY_DOMAINS` registry in `general/tools` -- per-domain base-dir resolver, path iterator (`feat`'s `<base>/<id>/README.md` folder shape the one bespoke iterator), and `load_by_id`. The five existing generic tools (`update`, `set_status`, `set_classification`, `delete`, `validate`) are re-pointed at it. `adr` is excluded structurally (issue #46). The registry deliberately includes the dev docs under `.specmgr/feat` (`DEFAULT_FEAT_DIR`).
- **Embedding input:** title + frontmatter minus bookkeeping keys `{id, type, version, created, updated, status}` + the raw frontmatter-stripped body (split via the base-dependency `python-frontmatter`; across all 12 domains only `classification` survives the exclusion). Unparseable documents embed their full raw file text and surface in results with the `FAILED_TO_PARSE_MARKER` title/status and `id = None`.
- **Ranking:** dot product on normalized vectors (== cosine), sorted descending; `top_k` default 10, validated 1..100 (the `list_*` cap); optional `min_score`; `find_related` excludes the source document itself.
- **Warmup:** `server.py`'s `_lifespan` starts a daemon thread at startup that embeds the full default corpus. The startup gate is the `SPECMGR_SIMILARITY_DISABLED` flag only (lightweight and synchronous); the full availability probe (the extra importable, the model loadable -- including the one-time first-use download) runs inside the daemon thread, so server startup is never blocked by the embedding backend. When unavailable the thread exits immediately without cache writes. It never raises out of startup and is a no-op (no thread) when the flag is present. This is safe to background because ONNX Runtime runs its inference in C++ outside the GIL -- unlike the GIL-holding markdown/Pydantic parsing that ADR bfd76370 addresses.
- **Tests:** deterministic fake-provider unit tests in CI; a `FastEmbedProvider` wrapper unit test with `fastembed.TextEmbedding` monkeypatched (CI-covered); one real (non-mocked) backend test under the `embedding_model` pytest marker, excluded from every default pytest invocation via `[tool.pytest.ini_options] addopts` (no `ci.yml`/`.pre-commit-config.yaml` edits).

### Consequences

Positive: semantic discovery and pre-creation dedup across all 12 whole-body domains, including drafts; zero hard-dependency cost to the base/`mcp`/`cli` extras; no staleness -- the hash-validated cache refines, not replaces, ADR 33c5ab08 (a stale entry is structurally impossible); the first-call timeout hazard is removed by warmup; one place to add a future domain (e.g. `ac`) to both the existing generic tools and the similarity engine.

Negative / trade-offs: a one-time model download and ~minutes of CPU per process for the full corpus at current scale; English-optimized model quality; the single-vector-per-document recall ceiling (chunk + mean-pool mitigates; multi-vector retrieval and longer-context models such as bge-m3 are deferred); new global process state (vector cache, warmup thread); `bge-small` is fixed for v1, so quality upgrades mean a provider substitution (which the protocol exists to allow).

Follow-ups (explicitly out of scope, file separately): `create_*` prompt adoption of `find_similar_text`; longer-context/multi-vector retrieval if recall proves insufficient; cross-reference existence-checking (adjacent to feat-135); ADR-domain removal (issue #46) leaves the structural exclusion intact.

### Confirmation

To be confirmed by the feat-134 acceptance criteria (ACC-001..ACC-015) as the implementation lands.

## Pros and Cons of the Options

### Option 1: Local embedding engine (fastembed + bge-small, CPU-only)

- Good: semantic recall across all 12 domains, including paraphrased content and draft text that is not yet a saved document; no runtime network or keys; no new hard dependency (optional `similarity` extra); provider protocol keeps the backend swappable; hash-validated cache integrates with the DocCache discipline.
- Bad: one-time model download required before first use; the first full-corpus embed costs minutes of CPU (mitigated by background warmup); `bge-small` is English-optimized, degrading non-English artifacts; single-vector-per-document recall has a ceiling (mitigated by chunk + mean-pool; multi-vector deferred).
- Neutral: adds one global cache singleton and one `_lifespan` background thread -- the same class of process-local state the per-domain `DocCache` and per-id locks already introduce.

### Option 2: Lexical retrieval (TF-IDF/BM25)

- Good: zero ML dependency, no download, deterministic, fast.
- Bad: no paraphrase/semantic recall -- the core gap of issue #134 (draft-vs-saved similarity, "find related risks"); keyword overlap is a weak signal on short spec artifacts; does not serve `find_similar_text`'s free-form query phrasing.
- Neutral: could later complement embeddings as a recall layer -- a separate decision.

### Option 3: API-based embeddings

- Good: often higher-quality models, no local compute.
- Bad: network at inference time, API keys, per-call cost; breaks the local-first/offline posture (CI, air-gapped use); tool availability depends on an external service.
- Neutral: the provider protocol keeps this a future substitution, not a re-architecture.

### Option 4: Do nothing

- Good: no new code or dependencies.
- Bad: leaves issue #134 open; `create_*` prompts keep their weak title-only dedup; agents must hand-grep.
- Neutral: feat-135's format validation improves explicit links but not discovery.

## More Information

Revised 2026-09-23 (v1.2.0): rewrote the **Cache** sub-decision's entry shape from `(hash, vector)` to `(hash, vector, similarity_text)`. The second feat-reviewer pass over feat-134 (2026-09-23) found that the demand path (`collect_candidates`) read and parsed each candidate's file a second time -- separately from the embedding cache's own read -- for the result-row metadata (`id`/`title`/`status`). The entry now stores the candidate's `SimilarityText` row metadata alongside its vector: `SimilarityText` is a pure function of `(domain, text)` (the text the entry's hash was computed over), so a hash match means the stored metadata is byte-identically valid and can be served without re-reading or re-parsing. Consequence: a warm candidate is one file read and no parse; a cold candidate one file read and one parse (the `embed_fn` closure's own `candidate_similarity_text` run on the cache's read text) -- instead of the prior two reads and up to two parses per candidate. Tracked in `.specmgr/feat/feat-134-related-artifact-similarity/README.md` (Phase 6, Task 6.6; GitHub issue #134).

Revised 2026-09-21 (v1.1.0): rewrote the **Warmup** sub-decision to match the shipped implementation after the feat-134 feat-reviewer pass (2026-09-21) found that `start_similarity_warmup` ran the full availability probe (`_similarity_availability()`, i.e. `get_default_provider()`'s eager model load, including the one-time first-use download) on the server's startup path, so server readiness could be delayed on a first/air-gapped run (a gap against the feature plan's REQ-011 "Warmup MUST NOT block server startup" strict reading). The startup gate is now the `SPECMGR_SIMILARITY_DISABLED` flag only (lightweight and synchronous); the full probe runs inside the daemon thread (`warmup_similarity_cache`'s first step), where unavailability is an info-logged early return with no cache writes. No behavior change when available; the tools' own REQ-003 demand-path contract is untouched. Tracked in `.specmgr/feat/feat-134-related-artifact-similarity/README.md` (Phase 5, Task 5.2; GitHub issue #134).

GitHub issue #134; `.specmgr/feat/feat-134-related-artifact-similarity/README.md` (full plan: REQ-001..REQ-012, ACC-001..ACC-015, phased task list); siblings feat-133-tags-dec-rsk (#133) and feat-135-related-artifacts-risks (#135); ADRs 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (filesystem sole source of truth), bfd76370-b59b-4d65-b550-a969f6c93c9d (DocCache), 36905d5b-8057-4294-8665-c7eed5534db0 (dispatch-only generic tools), 1af6787b-eaab-4e8f-888f-531c1e76c19d (path safety), 519d1206-4d2a-4500-9046-6db635209996/b399f1ce-ed42-4929-b01c-7a57d18e8014 (non-raising structured results), 078bf395-0a5f-4afd-84f6-b7a2191a00e6 (generic validate); `BAAI/bge-small-en-v1.5` model card; `fastembed` project.
