---
classification: null
created: '2026-10-03T22:09:42.529+02:00'
id: feat-187-list-feat-timeout
status: planning
type: feat
updated: '2026-10-03T22:13:55.907+02:00'
version: 1.0.0
---

# Feature: list_feat Cold-Scan Timeout

## Plan

### Overview

The `list_feat` MCP tool intermittently fails with `MCP error -32001: Request timed out` (GitHub issue #187). Reproduced in-session on 2026-10-03: two consecutive `list_feat` calls against this worktree both timed out. The quantified root cause: `list_feat` performs a lock-free, full-directory sweep that fully parses every `<base>/*/README.md` on a cold cache (`python-frontmatter`/PyYAML frontmatter, pure-Python `markdown_it("commonmark")` body tokenizing, nested Pydantic validation) -- 348.6 s measured over this repo's 70-folder / 3.95 MB corpus, at roughly 10-13 KB/s on large READMEs (a single 146 KB README takes 24.0 s). The MCP client (OpenCode 1.18.34) gives up far earlier, and the server process the published `uvx biz-dfch-specmgr[mcp, similarity]` entry point starts is fresh per client session, so the process-local content-hash cache added by feat-107-doc-cache (issue #107, the same timeout symptom) never helps a session's first call. The warm floor -- full read plus blake2b content hash of the entire corpus with no parsing -- is 0.007 s, proving the parses, not the I/O, are the bottleneck. The design (settled with the maintainer, 2026-10-03) is two-stage: (1) the request path never runs a full body parse -- `list_feat` resolves every folder from a fast frontmatter-level read (`parse_frontmatter` plus an H1 line scan, milliseconds per file) with an inline fallback for any path the warmup has not yet reached, so the very first call already returns the complete directory (`total` correct from call one) in well under any client request timeout; (2) at MCP server startup, a crash-contained background warmer thread first reads all FEAT frontmatters into a second, hash-validated, frontmatter-stage cache (the "dirty" stage, under a second for this corpus) and then sequentially full-parses every FEAT document into the existing content-hash cache (the "clean" stage, roughly 348 s for this corpus, in the background and off the request path) -- so `list_feat`'s output, including byte-identical `<failed to parse>` rows and their `error` text, converges to today's full-fidelity output within minutes of session start, and `get_feat` calls additionally hit pre-parsed, warm documents. Neither stage weakens ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3's "filesystem is the sole source of truth" invariant: every cached value is content-hash-validated on every access.

### Requirements

- REQ-001: The first `list_feat` call from a fresh server process (empty caches) over this repo's 70-folder / ~4 MB `.specmgr/feat` corpus (348.6 s full-parse sweep measured pre-fix) must return a complete page -- `total` equal to the on-disk folder count -- in under 5 s wall time, with zero full markdown-it/Pydantic body parses on the request path.

- REQ-002: The same bound must hold regardless of how far the background warmup (REQ-007) has progressed: any folder not yet in the frontmatter stage is resolved by the request path's own inline frontmatter read, so the entry count never lags the directory (what converges over time is each entry's validation depth, not its presence).

- REQ-003: The request path's per-file summary derivation must be bounded by the file's frontmatter and H1 -- the dirty stage's payload -- never by the body, so `list_feat`'s cost does not grow with corpus body size (ADR bfd76370's full cache only memoizes repeats within one process and cannot bound a first call; the dirty stage is what bounds it).

- REQ-004: Failure visibility must converge to today's exact output: frontmatter-level failures (malformed or missing YAML frontmatter, missing `# Feature:` H1) must appear as `<failed to parse>` rows with `error` text byte-identical to `get_feat`'s from the very first call; body-level failures -- including all five folders that currently fail a full parse in this repo (`feat-5-md-model-parser`, `feat-29-dec-source-roles`, `feat-50-confluence`, `feat-132-prb-update`, `feat-177-list-ref-feat`) -- must appear as `<failed to parse>` rows with `error` text byte-identical to today's full-parse sweep once the warmup's clean stage has passed them; during the warmup window, a document with a broken body but well-formed frontmatter transiently appears healthy (the documented dirty-stage limitation, recorded in the ADR).

- REQ-005: The paging contract is unchanged (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13): `list_feat` scans the live directory on every call, materializes the complete list before paginating, and `total` always reflects the whole directory; `error_count` converges monotonically toward today's full-parse value as the warmup completes.

- REQ-006: `get_feat`'s contract is unchanged: it returns the fully parsed document, or `ParseFailureResult` for a document that exists but fails to parse, with its `raw`/`numbered`/`offset`/`limit` semantics intact -- the only difference is that warmed documents are served from a pre-parsed cache hit instead of an on-demand parse.

- REQ-007: The warmup must run as a daemon background thread started at MCP server startup (the lifespan hook in `server.py`, currently a no-op), for the `feat` domain only: first a frontmatter phase (every live `*/README.md` read through the dirty-stage cache, under a second for this corpus), then a sequential full-parse phase (every path through the existing cache-backed `read_feat`, one after another, ~348 s for this corpus, in the background). The thread must be crash-contained: an unexpected per-file exception (e.g. a file vanishing mid-warmup, an `OSError`) is logged to stderr and swallowed, never propagates out of the thread, and never prevents the server from serving or the warmup from reaching later files; parse failures are the normal, cacheable outcome and are stored like today.

- REQ-008: The dirty stage must be hash-validated exactly like the clean stage: a feat-local second `DocCache` instance (the same class, the same innermost-lock-ordering rule, the same reconcile/invalidate/move semantics) keyed by content hash, so an on-disk edit between the warmup's frontmatter phase and a `list_feat` call re-reads that file's frontmatter -- a stale summary is structurally impossible, mirroring ADR 33c5ab08's invariant at the frontmatter level.

### Acceptance Criteria

- [ ] ACC-001: A test asserts that the first `list_feat` (fresh process, empty caches) over a fixture corpus mirroring this repo's measured profile (~4 MB of realistic feature READMEs across 70 folders, including ACC-002's failure shapes) returns `total == 70` in under 5 s and performs zero full body parses on the request path -- a direct regression guard for issue #187's 348.6 s cold sweep.

- [ ] ACC-002: A table-driven test over a fixture corpus covering (a) malformed YAML frontmatter, (b) a missing H1, (c) a legacy Requirements shape, (d) a missing Task List, (e) a legacy task-item shape, (f) a legacy Updates timestamp form, (g) a raw-HTML inline token, and (h) a healthy folder, asserts: (a)-(b) appear as `<failed to parse>` rows with `error` text byte-identical to `get_feat`'s before the warmup completes (frontmatter-stage failures); (c)-(g) appear healthy before the warmup's clean stage passes them (the documented transient) and appear as `<failed to parse>` rows with `error` text byte-identical to today's full-parse sweep after it does; (h) appears healthy in both states with `id`/`title`/`status` matching its frontmatter/H1; and no uncaught exception propagates out of `list_feat` or the warmup thread in either state.

- [ ] ACC-003: A convergence test asserts that once the warmup's full-parse phase has completed, `list_feat`'s entire output (every row's `id`/`title`/`status`/`ref`/`path`/`error`, plus `total` and `error_count`) is byte-identical to what today's full-parse sweep produces for the same fixture corpus -- verified by running both implementations over the same fixture and diffing the serialized `PagedResult`.

- [ ] ACC-004: A crash-containment test asserts that a warmup thread encountering an unexpected (non-parse) exception on one file neither dies nor stalls: later files still warm, and subsequent `list_feat` calls are unaffected.

- [ ] ACC-005: A consistency test asserts that the write paths keep both cache stages coherent: `create_feat` warms both stages for the new file; the generic `update`/`set_status`/`set_classification` tools warm both; the generic `delete` tool invalidates both; `set_feat_id` moves both -- each followed by a `list_feat` call that reflects the new on-disk state immediately.

- [ ] ACC-006: A one-shot, non-flaky measurement (recorded in `### Updates`, not asserted in CI) of a fresh `uvx` server session over this repo's live 70-folder corpus shows: first `list_feat` wall time under 5 s with `total == 70`, the measured convergence time of the full-parse phase (expected ~348 s), and `error_count == 5` after convergence with the five known folders flagged -- i.e. issue #187's reproduction steps now succeed on the first call of a new session.

- [ ] ACC-007: The full gate set is green: `uv run --frozen ruff format --check && uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen pytest -n auto --cov=src`, and `specmgr docs` regeneration where docstrings changed.

- [ ] ACC-008: The ADR documenting the two-stage design (dirty/clean staging, warmup thread, convergence semantics, GIL-contention treatment, relationship to ADR 33c5ab08 / bfd76370 / ec9f5262) exists (created via the `create_adr` tool) before Phase 110 implementation begins.

### Scope

#### Included

- The feat-local, hash-validated, frontmatter-stage (dirty) `DocCache` and the fast summary read it serves (`parse_frontmatter` plus H1 line scan), with the inline fallback in `list_feat`'s request path.
- Rewiring `list_feat`'s summary construction: live directory scan, then clean-to-dirty-to-inline resolution per folder, producing `PagedResult` with the convergence semantics (frontmatter-level failed rows byte-identical to `get_feat`; clean-stage rows identical to today's sweep).
- The startup warmup thread (frontmatter phase, then sequential full-parse phase, crash-contained, daemon) and its start hook in `server.py`'s lifespan.
- The two-stage write-path integration: `create_feat`, the generic `update`/`set_status`/`set_classification`/`delete` tools, and `set_feat_id`.
- The ADR (Phase 100) settling the design, the transient failure-visibility contract, and the GIL-contention treatment.
- The ACC-001..006 tests, plus docstring updates (`list_feat`, `feat/tools/_cache.py`, `server.py`'s module docstring), AGENTS.md's `feat` bullet, and `docs/` regeneration where applicable.
- A before/after one-shot measurement over the live repo corpus, recorded in this feature's `### Updates`.

#### Explicitly Out Of Scope

- Any change to `get_feat`'s return contract or `ParseFailureResult` shape (only its cache hit/miss profile changes).
- Changing the paging contract (`total` always reflects the whole directory; only `error_count` converges -- ADR ec9f5262's materialize-then-paginate stands).
- Warming any domain other than `feat`: the other `list_<d>` tools (and `list_adr`, whose ADR domain is excluded from the doc cache and whose 412 KB corpus shows the same latent cold cost) keep today's on-demand behavior -- track separately if/when they bite.
- Client-side (OpenCode) request-timeout configuration or MCP-protocol-level timeout negotiation.
- A free-threaded (no-GIL) Python 3.13t/3.14t runtime for the server -- deferred on maintainer direction (2026-10-03: "stay away from Py 3.14 for now"); recorded in the Design Notes with the pydantic-core dependency blocker.
- TTL/size eviction, or a persisted/disk-backed warm cache surviving process restarts (the disk-cache option remains deferred in the Design Notes).
- In-flight deduplication (single-flight) of `DocCache` reads -- subsumed: the request path no longer full-parses, so concurrent requests can no longer multiply the expensive work; the warmup is sequential by design.
- Repairing the five currently-failing legacy feature folders themselves (they are flagged again once the warmup passes them; this feature only guarantees the flagging).
- Request-preemptive pausing of the warmup (it idles while a tool call is in flight) -- a GIL-contention refinement considered in the Design Notes; the default is "always run" unless the Phase 100 ADR decides otherwise.

### Dependencies

#### Depends On

- feat-107-doc-cache (done): the `DocCache` class and the `reconcile_feat_cache` integration this feature extends with a second, frontmatter-stage instance and the warmup thread, plus ADR bfd76370's design constraints (content-hash validation, innermost lock ordering, ADR-domain exclusion).

### Design Notes

Measurements (2026-10-03, this worktree, `uv run --frozen python`): the cold full-parse sweep of all 70 READMEs -- exactly what `list_feat`'s cold path does today -- took 348.6 s, at roughly 10-13 KB/s on large files (slowest: feat-6-requirement-artifact 146 KB / 24.0 s, feat-32-sysrs 243 KB / 19.5 s); the warm floor (full read plus blake2b over the entire corpus, no parsing) is 0.007 s; a frontmatter-only sweep (read plus PyYAML frontmatter parse plus H1 line scan, no body parse) completes in well under 1 s for the whole corpus; the current full-parse failure set -- what today's `list_feat` reports as `error_count` -- is 5 of 70 folders: feat-5-md-model-parser (legacy Requirements shape), feat-29-dec-source-roles (missing Task List), feat-50-confluence (legacy task-item shape), feat-132-prb-update (legacy Updates timestamp form), feat-177-list-ref-feat (raw HTML inline token). All five have valid frontmatter and H1. The host has 120 cores, but the sweep is GIL-bound pure-Python parsing, so core count does not help today's serial code.

The chosen design (settled with the maintainer, 2026-10-03) is a two-stage cache plus a startup warmup. Stage 1 ("dirty"): a feat-local second `DocCache` instance whose `parse_fn` is the frontmatter-only read (`parse_frontmatter` plus H1 line scan, producing exactly the five summary fields plus the frontmatter-level error channel). It is hash-validated exactly like the existing full cache, so an on-disk edit re-reads that file's frontmatter; a stale summary is structurally impossible. Stage 2 ("clean"): the existing `DocCache` full-parse cache, unchanged. `list_feat`'s request path resolves each folder clean, then dirty, then inline frontmatter read (populating stage 1 on the way), and builds each summary from whichever stage answered: a clean hit yields today's exact row (including a byte-identical failed row for a body failure, because the stored exception is the same one today's sweep would raise), and a dirty hit yields the frontmatter-derived row (correct `id`/`title`/`status`/`ref`/`path`; a body failure not yet visible -- the documented transient). Because the live directory scan always enumerates every folder and the inline fallback covers any path the warmup has not reached, `total` is complete from call one: what improves as the warmup progresses is each entry's validation depth, not the entry count.

The warmup thread starts in `server.py`'s lifespan hook (currently a no-op) as a daemon, for the `feat` domain only: a frontmatter phase over every live `*/README.md` (under a second for this corpus, so the dirty stage is essentially complete before any client call arrives), then a sequential full-parse phase through the existing `read_feat` (~348 s for this corpus, in the background, off the request path). The thread is crash-contained: per file, parse failures are the normal, cacheable outcome (the full cache already stores them and re-raises fresh equivalents on hit, feat-107's REQ-011 and feat-162), and any unexpected error (a file vanishing mid-warmup, an `OSError`) is logged to stderr and skipped, never killing the thread. Side benefit: `get_feat` calls during and after the warmup hit pre-parsed full documents, so an agent that lists and then reads a feature pays no parsing at all in the common case.

GIL contention: the full-parse phase holds the GIL while parsing (up to 24 s per file), so concurrent `get_*`/`list_*` requests share CPU with it during the ~6-minute warmup window. The default is "always run": total CPU is identical to today's on-demand behavior (the same parses, moved off the request path). The Phase 100 ADR decides whether to add request-preemptive pausing (the warmup idles while a tool call is in flight) as a refinement.

Options evaluated and rejected or deferred: (1) a pure frontmatter-only request path with no warmup -- simplest, but body-level failures would then never be visible in the listing (the five legacy folders, and every future hand-edit breakage, would silently become healthy rows, regressing the `repair` skill's list-based discovery); subsumed by the two-stage design, which keeps it as the request path and adds the warmup for full fidelity. (2) A `stat()` (mtime/size) pre-check in the cache -- trims the warm path only (already 0.007 s) and does nothing for the cold sweep; explicitly deferred by feat-107. (3) A process-pool-parallelized cold sweep -- 348.6 s / N is still ~45 s at N=8, above typical client timeouts on small machines, adds pickling/error-channel complexity, and stays unbounded as the corpus grows. (4) A lazy per-page sweep -- breaks ADR ec9f5262's materialize-then-paginate contract. (5) A persisted/disk-backed warm cache -- carries the warm state across restarts, but a fresh checkout still pays one full cold sweep, and it adds serialization/invalidation/concurrency concerns; a deferred complement, not the primary fix. (6) A free-threaded (no-GIL) CPython 3.13t/3.14t runtime with explicit thread fan-out -- on this 120-core host it would bound wall time by the largest single file (24.0 s), but on a typical 4-8 core laptop it still lands at 44-87 s with no bound as the corpus grows; it is blocked today by pydantic-core (Rust, 2.46.4) lacking free-threaded support -- a hard dependency blocker to re-verify before any investment; and it is a deployment/runtime decision for every consumer, not a fix in this repo. Deferred on maintainer direction ("stay away from Py 3.14 for now", 2026-10-03). (7) A startup frontmatter-only warmup without the full-parse phase -- half of the chosen design; alone it would leave body failures permanently invisible (the same defect as option 1), so it ships as the first phase of the full warmup, not as a separate option.

### Related Decisions

- ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3: the filesystem is the sole source of truth -- preserved at both stages: the request path re-reads every file's frontmatter (hash-validated) on every call, and the warmup re-validates every full document by content hash.
- ADR bfd76370-b59b-4d65-b550-a969f6c93c9d: the per-domain content-hash read cache (feat-107) -- this feature adds a second, frontmatter-stage instance for `feat` and a warmup thread feeding the existing instance; the lock-ordering rule (cache locks always innermost) extends unchanged to the new instance.
- ADR ec9f5262-9912-49d0-903f-fcfb54f28c13: listing is a tool with materialize-then-paginate semantics -- preserved: `total` is complete from call one; `error_count` converges as the warmup progresses (documented in the new ADR).
- A new ADR (created in Phase 100): the two-stage `list_feat` design (dirty/clean staging, startup warmup, convergence semantics, GIL-contention treatment) and the options rejected above.

### Task List

#### Phase 100: Diagnosis and ADR

- [ ] Task 100.100: Formalize the in-session diagnosis into the feature record: reproduction (fresh `uvx` server, first `list_feat` -> `-32001`), the measured 348.6 s full-parse sweep / 0.007 s warm floor / sub-1 s frontmatter sweep, and the current five-folder failure set.

- [ ] Task 100.110: Create the ADR (via the `create_adr` tool) settling the two-stage design: dirty/clean cache staging, the warmup thread (phases, crash containment, lifespan hook), the convergence semantics (`total` complete from call one, `error_count` converging, the transient body-failure visibility), the GIL-contention default (and the request-preemptive pause as a decided-or-deferred refinement), and the relationships to ADR 33c5ab08 / bfd76370 / ec9f5262 -- before any Phase 110 code.

#### Phase 110: Implementation

- [ ] Task 110.100: Implement the frontmatter-stage (dirty) cache: the feat-local second `DocCache` instance with the frontmatter-only `parse_fn` (`parse_frontmatter` plus H1 line scan), and its reconcile/invalidate/move wiring mirroring the existing full cache.

- [ ] Task 110.110: Rewire `list_feat`'s request path: live directory scan, then clean-to-dirty-to-inline resolution per folder, then summary construction with the convergence semantics (frontmatter-level failed rows byte-identical to `get_feat`; clean-stage rows identical to today's sweep).

- [ ] Task 110.120: Implement the startup warmup thread (frontmatter phase, then sequential full-parse phase, crash-contained, daemon) and start it from `server.py`'s lifespan hook.

- [ ] Task 110.130: Wire the write paths to keep both stages coherent: `create_feat` warms both; the generic `update`/`set_status`/`set_classification` tools warm both; the generic `delete` tool invalidates both; `set_feat_id` moves both.

- [ ] Task 110.140: Update the affected docstrings (`list_feat`, `feat/tools/_cache.py`, `server.py`'s module docstring), AGENTS.md's `feat` bullet, and regenerate `docs/` where applicable.

#### Phase 120: Verification and closeout

- [ ] Task 120.100: Add the ACC-001..006 tests (first-call timing plus zero full parses on the request path, the transient-versus-converged failure-visibility table, the byte-identical convergence diff, crash containment, the two-stage write-path consistency, and the live-corpus one-shot measurement protocol).

- [ ] Task 120.110: Run the full gate set (ruff format/check, vulture, `pytest -n auto`) and record the before/after one-shot live measurement (ACC-006: first-call wall time, convergence time, `error_count == 5` after convergence) in `### Updates`.

- [ ] Task 120.120: Verify issue #187's reproduction end-to-end (fresh `uvx` session, first `list_feat` returns the complete page in under 5 s, no `-32001`; the five legacy folders are flagged again after convergence), mark the ACCs done, and update the feature status.

## Progress

### Current Status

**As of 2026-10-03**: Planning. Issue #187 reproduced in-session (two consecutive `list_feat` calls -> `MCP error -32001: Request timed out`). Root cause quantified: a 348.6 s cold full-parse sweep of this repo's 70-folder / ~4 MB `.specmgr/feat` corpus versus a 0.007 s warm floor and a sub-1 s frontmatter-only sweep, with a fresh `uvx` server process per client session making every session's first call cold. The design was settled with the maintainer the same day: a two-stage (dirty frontmatter / clean full-parse) cache plus a crash-contained startup warmup thread, with `list_feat`'s request path never full-parsing. No code changes yet; the Phase 100 ADR is the next gate.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-03T20:09:42.529Z - Created

Feature created for GitHub issue #187 (`list_feat` intermittently returns `MCP error -32001: Request timed out`), reproduced in-session, with the root cause quantified: a 348.6 s cold full-parse sweep over this repo's 70-folder / ~4 MB `.specmgr/feat` corpus, a 0.007 s warm floor, and five folders currently failing full parse.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-03T20:09:42.529Z - Settled the two-stage design with a startup warmup, with the maintainer

The maintainer proposed, and the discussion settled on, a startup-warming design: at MCP startup, all FEAT frontmatters are read into the doc cache first (the "dirty" stage), then all FEAT documents are sequentially fully read and parsed into the cache (the "clean" stage), and `list_feat` at any time serves what the cache holds. Refined during the discussion: (1) `list_feat`'s request path carries an inline frontmatter fallback for any not-yet-warmed path, so `total` is complete from call one -- what improves over time is each entry's validation depth, not the entry count; (2) dirty/clean is realized as a second, hash-validated, feat-local `DocCache` instance alongside the existing full cache, not as a flag; (3) the warmup thread is crash-contained (unexpected per-file errors go to stderr and never kill the thread); (4) body-level failure rows converge to byte-identical output with today's sweep once the clean stage passes them (the five currently-failing folders included), while frontmatter-level failures are flagged from call one. Free-threaded Python (3.13t/3.14t) was considered and deferred on maintainer direction (pydantic-core has no free-threaded build; machine-dependent worst case).

### Related PRs / Commits

- [Issue #187](https://github.com/dfch/biz.dfch.SpecMgr/issues/187): the tracking bug.

### More Information

Reproduction environment: OpenCode 1.18.34, the `specmgr` MCP server v0.34.0 started via `uvx --from "biz-dfch-specmgr[mcp, similarity]" specmgr mcp` (fresh process per client session; the `similarity` extra is installed with fastembed/BAAI-bge-small in `/tmp/fastembed_cache`, unrelated to the sweep cost), working directory this git worktree, `SPECMGR_FEAT_DIR` unset, so the base directory is the default `.specmgr/feat`. Host: 120 cores (the sweep is GIL-bound, so core count does not help today's serial code).
