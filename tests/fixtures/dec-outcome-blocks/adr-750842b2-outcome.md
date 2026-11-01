---
created: '2026-11-01T00:00:00.000Z'
id: 750842b2-aca4-4649-ba0c-855ec8e1f505
status: accepted
type: dec
updated: '2026-11-01T00:00:00.000Z'
version: 1.0.0
---

# Regression fixture: Add an embedding-based, cross-domain semantic similarity engine (find_related / find_similar_text) with a pluggable CPU-only provider (outcome of ADR 750842b2)

## Context and Problem Statement

This document is a committed regression fixture for feat-247-dec-outcome-blocks (GitHub issue #247): it carries the real `## Decision Outcome` section of ADR 750842b2-aca4-4649-ba0c-855ec8e1f505 verbatim inside a minimal-but-valid `dec` body, to prove that the relaxed `DecisionOutcome` lead (a mandatory paragraph plus zero or more further blocks) parses this outcome without "text left over".

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
- **Warmup (rewritten by the v1.4.0 note below -- feat-187-list-feat-timeout, ADR 3982712a-a46b-4b2b-809f-9c6925a49b44):** `server.py`'s `_lifespan` starts a single, unified daemon thread (`specmgr-startup-warmup`) at startup running three phases in strict order: (1) a `feat`-domain frontmatter warmup phase (every live feature folder's frontmatter + H1 only, cheap); (2) a `feat`-domain full-parse warmup phase (the same folders, fully parsed through the content-hash-validated `feat` `DocCache`, expensive); (3) this ADR's own, unchanged similarity warmup body (`warmup_similarity_cache`, embedding the full default corpus). Phase gating is per-phase, not per-thread: the new `SPECMGR_FEAT_WARMUP_DISABLED` presence flag gates phases 1-2 only; the pre-existing `SPECMGR_SIMILARITY_DISABLED` flag gates phase 3 only (unchanged in meaning); when both flags are present, no thread is started at all (a true no-op, and the server runs exactly as before either feature shipped). `warmup_similarity_cache` itself -- its own availability probe (the extra importable, the model loadable, including the one-time first-use download) running inside its own phase so server startup is never blocked by the embedding backend, its crash containment (logged and swallowed, no cache writes on an unavailable probe), and the demand path it shares the cache with -- is unchanged by this move; only the startup orchestration (the thread name, the gate, and where the thread is spawned from, now `general.tools._startup_warmup.start_startup_warmup`) relocated out of this feature's own `general.tools._similarity_search.start_similarity_warmup`, which is retired. This remains safe to background for the same reason as before: ONNX Runtime runs its inference in C++ outside the GIL -- unlike the GIL-holding markdown/Pydantic parsing the new `feat` phases (and ADR bfd76370) address -- and with the unified thread, at most one heavy, GIL-holding background phase now runs at any one time (the `feat` phases, then separately the similarity phase), never two in parallel as the pre-unification two-thread design could.
- **Tests:** deterministic fake-provider unit tests in CI; a `FastEmbedProvider` wrapper unit test with `fastembed.TextEmbedding` monkeypatched (CI-covered); one real (non-mocked) backend test under the `embedding_model` pytest marker, excluded from every default pytest invocation via `[tool.pytest.ini_options] addopts` (no `ci.yml`/`.pre-commit-config.yaml` edits).

## Roles and Responsibilities

### Accountable

The platform architecture lead.

### Responsible

- The order service team.

## Source

Regression fixture derived from the `## Decision Outcome` section of ADR 750842b2-aca4-4649-ba0c-855ec8e1f505.
