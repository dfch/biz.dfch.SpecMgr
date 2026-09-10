---
classification: null
created: '2026-09-09 22:40:39.484+02:00'
id: feat-107-doc-cache
status: planning
type: feat
updated: '2026-09-09 22:40:39.484+02:00'
version: 1.0.0
---

# Feature: Per-Domain Content-Hash Read Cache

## Plan

### Overview

`get_*`/`list_*` MCP tool calls currently re-scan and fully re-parse an entire domain directory on every single invocation (`general/tools/_doc_paths.py:find_doc_path_by_id`, `general/tools/_listing.py:build_summaries`), since ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3 deliberately rejected an in-memory id-to-document cache to guarantee correctness under concurrent hand-edits. This makes every read CPU-bound (markdown-it tokenizing plus nested Pydantic validation), which serializes on CPython's GIL regardless of how many threads/cores are available, and is the real cause behind GitHub issue #107's reported timeouts under parallel `get_*` calls -- not a lack of a thread pool, since the MCP SDK already offloads every sync tool call to an `anyio` worker thread (`anyio.to_thread.run_sync`, `CapacityLimiter(40)`). This feature introduces a process-local, per-domain, in-memory read cache keyed by file path and validated on every access against the file's current content hash, so a file is only ever re-parsed when its on-disk content actually changed -- preserving ADR 33c5ab08's "filesystem is the sole source of truth" invariant (a stale entry is structurally impossible, it can only ever cause an extra parse) while eliminating almost all repeated-call parsing cost. As a direct side effect, this also fixes an existing bug where `get_*` parses its matched file twice per call (once during the `find_doc_path_by_id` scan, again when the matched path is loaded). This feature is scoped to the 12 generic whole-body domains only; ADR is deliberately excluded, since it is expected to be phased out later and is not worth the extra, independently-implemented cache module its lack of dependency on `general` would require.

### Requirements

- REQ-001: A process-local, per-domain, content-hash-validated in-memory cache must skip re-parsing a file whose current on-disk content hash matches the hash recorded the last time that path was read, and must always trigger a fresh parse on any hash mismatch or cache miss. This applies symmetrically to a file that currently fails to parse: a hash whose read previously raised must not be re-parsed on a subsequent access with the same hash -- the cache records and re-surfaces the previously-raised exception instead, and only a hash change triggers a fresh parse attempt.

- REQ-002: Both `get_*`'s `find_doc_path_by_id` scan and its final matched-file load, and `list_*`'s `build_summaries` read callback, must route through the same per-domain cache instance, so a file parsed once during a single `get_*` call's scan is never parsed a second time within that same call.

- REQ-003: Every write path (`create_<domain>` and the generic `update`/`set_status`/`set_classification` tools) must warm the cache entry for the file it just wrote by invoking the domain's cache-backed `read_fn` on that path once, immediately after the write succeeds -- one extra parse per write, not a shortcut reconstructed in-process from the frontmatter object and raw body string already in memory, since neither `update`/`set_status`/`set_classification` nor `create_<domain>` actually holds a single, fully-validated document object at the point of writing (only a separate `Frontmatter` object and a body string, and in `update`'s range-splice mode only a sub-object, not the whole document, is validated). Re-parsing via the same `read_fn` the cache already uses guarantees the warmed entry went through identical validation to a normal read.

- REQ-004: The generic `delete` tool must invalidate the cache entry for the file it removes, and `set_feat_id` must move the cache entry from the old path to the newly written one -- only after `write_feat_file` succeeds, not at the earlier `old_path.parent.rename(...)` step -- so neither a deleted nor a renamed document's stale entry is ever served, and a failure between the rename and the write never leaves a cache entry pointing at a file that was never actually written.

- REQ-005: Both `get_*`'s directory scan and `list_*` must reconcile the cache against the current on-disk directory listing on every call, dropping any cached entry whose path no longer exists, so a file deleted outside specmgr's own tooling does not leak in memory indefinitely.

- REQ-006: The cache's own internal lock must guard only its dict lookups/inserts/deletes, never the file read or `parse_fn` call itself, so concurrent reads of different files never block each other on the cache's own bookkeeping. The cache lock must also always be the innermost lock in any call stack -- acquired after any domain-level per-id lock (`req_lock`, `feat_create_lock`/`feat_lock`, etc.), never before -- introducing no lock-ordering rule inconsistent with `set_feat_id`'s existing fixed `feat_create_lock` -> `feat_lock` order.

### Acceptance Criteria

- [ ] ACC-001: A test asserts a `get_req` call against a fixture directory invokes the underlying `parse_req` function exactly once per call, not twice, verifying the existing matched-file double-parse bug is fixed.

- [ ] ACC-002: A test asserts N sequential `get_req(id)` calls against an unchanged file invoke `parse_req` exactly once total across all N calls, not once per call.

- [ ] ACC-003: A test asserts that modifying a cached file's content directly on disk, bypassing every specmgr tool, causes the next `get_*`/`list_*` call touching that file to re-parse it and return the updated content.

- [ ] ACC-004: A test asserts that deleting a file directly on disk, bypassing the generic `delete` tool, causes the cache to no longer hold an entry for that path after the next `get_*`/`list_*` call that scans its directory.

- [ ] ACC-005: A test asserts that calling the generic `delete` tool immediately invalidates that document's cache entry.

- [ ] ACC-006: A concurrency test asserts N threads calling `get_req` on the same already-warm id simultaneously invoke `parse_req` at most once total, allowing only for a small, bounded number of legitimate cold-start races.

- [ ] ACC-007: The new ADR documenting this cache design and its relationship to ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3 is created before Phase 2's implementation work begins.

- [ ] ACC-008: A structural test enumerates all 12 generic whole-body domains and confirms each one's `read_<domain>` helper and `find_doc_path_by_id` scan are routed through that domain's cache instance.

### Scope

#### Included

- A new generic `general/tools/_doc_cache.py` module implementing a per-domain, content-hash-validated, in-memory read cache (read/store/invalidate/reconcile), one module-level singleton instance per domain (mirroring the existing per-domain `threading.Lock` registries in each domain's `_lock.py`), caching both successful parses and parse failures (keyed by hash, storing the raised exception for the latter), plus a test-only reset/clear hook since the singleton otherwise persists for the process's lifetime.

- Changing `general/tools/_doc_paths.py`'s `find_doc_path_by_id` from a bare `parse_fn: Callable[[str], T]` (text in) to a cache-backed `read_fn: Callable[[Path], T]` (path in) -- a signature change touching every one of the 11 non-`feat` domains' own `_paths.py` wrapper functions that call it.

- Wiring the cache into every one of the 12 generic domains' `read_<domain>` helper, `find_doc_path_by_id`'s scan, and `list_<domain>`'s summary-building read callback -- except `feat`, whose own hand-rolled `_paths.py`/`set_feat_id` never route through `general.tools._doc_paths` and need their own bespoke integration point, consistent with `feat`'s existing bespoke addressing (ADR 8cf940c5-3100-485c-a12d-14b59b631712).

- Wiring cache invalidation/update into `create_<domain>`, the generic `update`/`set_status`/`set_classification`/`delete` tools, and `set_feat_id`.

- Reconcile-on-scan logic in both `get_*`'s directory scan and `list_*`, dropping orphaned entries for files deleted outside specmgr's own tooling.

- A new ADR documenting this design and its relationship to ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3.

- Unit, correctness, and concurrency tests for the new cache module and its wiring across all 12 generic domains.

#### Explicitly Out Of Scope

- ADR (`models/adr/v1`) entirely; it is not wired into this cache mechanism at all, since ADR is expected to be phased out later and does not justify its own independently-implemented cache module (it has no dependency on `general`, unlike the 12 generic domains).

- Any time-based (TTL) or size-based (LRU) eviction policy; deferred as a future escape valve, only to be added if real-world corpus size later exceeds the "dozens to low hundreds of files per domain" scale this codebase already assumes.

- A `stat()`-based (mtime/size) pre-check fast path; content-hash-only for v1, since measured file sizes make the marginal savings negligible at this codebase's scale.

- The separately-considered frontmatter-only parsing optimization for the id-lookup scan; the cache subsumes its benefit for any workload with repeated calls.

- Any change to the MCP SDK's own thread-pool/concurrency model (`anyio.to_thread.run_sync`, `CapacityLimiter(40)`); this feature does not implement GitHub issue #107's literal ask of a separate thread pool, since one already exists at the framework level and would not help CPU-bound, GIL-holding work anyway.

- Cross-process cache sharing; the cache remains process-local, the same limitation as the existing per-id `threading.Lock` registries.

### Dependencies

#### Depends On

- ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3: this feature must refine, not violate, its "filesystem is the sole source of truth" invariant.

### Design Notes

Measured (not assumed) memory footprint: parsing this repo's 32 real ADR documents (208,057 raw bytes) purely as a large, real, readily available sample dataset and measuring with `tracemalloc` showed the parsed Pydantic object graph occupies 386,761 bytes, a ~1.86x multiplier over raw text; this measurement is unrelated to whether ADR itself is cached, since ADR is explicitly excluded from this feature's scope. This repo's entire current real document corpus across the 12 in-scope domains totals well under 407 KB raw, so caching everything currently on disk would cost under 1 MB. Even at 10x this codebase's own stated scale assumption ("dozens to low hundreds of files" per domain, `AGENTS.md`), the projected footprint is on the order of 70-110 MB, which is not a practical concern.

Cache shape: `dict[Path, tuple[content_hash, result]]`, where `result` is either the parsed document or the exception a failed parse raised (see Failure caching below), one instance per domain, guarded by a `threading.Lock` that protects only the dict's own get/set/pop operations, never the file read or `parse_fn` call. Hash function: a fast, well-distributed content hash (e.g. `hashlib.blake2b`) over the file's full text, computed on every read regardless of hit/miss, and compared against the stored hash before deciding whether to skip parsing.

Reconcile approach: since `iter_doc_paths`/`iter_<domain>_paths` already performs a cheap directory glob (no file content read) to produce the candidate path list, both `find_doc_path_by_id`'s scan and `list_<domain>` materialize that full path list up front and reconcile the cache against it (dropping any cached path absent from the live listing) before doing any per-file work, so orphan cleanup costs only a set comparison, not additional file reads.

Wiring `find_doc_path_by_id` through the cache requires no change to its return type (still a bare `Path`) and therefore no change to the `update`/`delete`/`set_status` call sites that only ever wanted the path -- only the internal parse call, and the `read_fn` parameter it now takes instead of a bare `parse_fn`, change. This is what makes the existing matched-file double-parse bug (the scan parses a file, discards the result, and the caller re-reads and re-parses the same file again) disappear as a structural consequence rather than needing its own separate fix.

Cache instance ownership: each domain owns exactly one module-level singleton cache object (e.g. `req/tools/_io.py` module-level, analogous to `req/tools/_lock.py`'s module-level `_locks` registry), not an instance explicitly threaded through call sites -- this needs no signature changes to `read_<domain>`/`find_doc_path_by_id`'s existing callers beyond the `read_fn` swap above, at the cost of needing an explicit, test-only reset/clear function per domain so tests don't leak cached entries across test cases within the same process.

Failure caching: the cache stores, per path, `(content_hash, result)` where `result` is either the successfully parsed document or the exception a failed parse raised. A hash match on a previously-failing entry re-raises the stored exception without re-invoking `read_fn`; only a hash change triggers a fresh attempt. This keeps a persistently malformed file from being re-parsed on every `list_*`/scan that touches it, while still recovering automatically the moment its content changes.

Post-write cache warming (REQ-003) always re-parses once via the domain's own cache-backed `read_fn`, immediately after the write succeeds, rather than constructing a document object from the `Frontmatter` + body string already in memory -- see REQ-003 for why no single fully-validated document object survives to the write point in `update`/`set_status`/`set_classification`/`create_<domain>` today.

`feat`'s cache integration is necessarily bespoke: its `_paths.py` performs its own folder-based scan rather than calling `iter_doc_paths`/`find_doc_path_by_id`, and `set_feat_id`'s cache-entry move (old path -> new path) must be hooked in only after `write_feat_file` succeeds -- never at the earlier `old_path.parent.rename(new_path.parent)` step -- so a failure in between never leaves a cache entry addressing a file that was never written.

Lock ordering: the cache's own lock (REQ-006) is always the innermost lock acquired in any call stack, after any domain-level per-id lock. `set_feat_id` already documents and enforces a fixed `feat_create_lock` -> `feat_lock` order; the cache lock must not invent a conflicting order, so it is always acquired last, held only for the instant of a dict get/set/pop, and never held across a domain lock acquisition.

### Related Decisions

- 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (ADR): filesystem is the sole source of truth; this feature's cache design must refine this invariant via hash validation, not remove it.

- bfd76370-b59b-4d65-b550-a969f6c93c9d (ADR): "Add a content-hash-validated, per-domain in-memory read cache for the 12 generic whole-body domains" -- the ADR this feature's Phase 1 produced, establishing the cache design, its reconciliation with ADR 33c5ab08, the ADR domain's explicit exclusion from scope, and the cache lock's fixed innermost-ordering rule.

### Task List

#### Phase 1: ADR and Design Lock-in

- [x] Task 1.1: Draft and create the new ADR describing the content-hash-validated per-domain read cache, explicitly referencing and reconciling with ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3, explicitly recording that the ADR domain itself is out of scope, and explicitly pinning the cache lock's fixed ordering rule (always innermost, after any domain-level per-id lock, consistent with `set_feat_id`'s existing `feat_create_lock` -> `feat_lock` order).

- [x] Task 1.2: Update this feature's Related Decisions section with the new ADR's id once created.

#### Phase 2: Generic Cache Module

- [x] Task 2.1: Implement `general/tools/_doc_cache.py`'s domain cache (content-hash read/store/invalidate/reconcile, caching both successful parses and parse failures keyed by hash, plus a test-only reset/clear hook per instance), with its own unit tests using a counting fake `parse_fn` (covering both the success and failure caching paths).

#### Phase 3: Wire req as the Pilot Domain

- [ ] Task 3.1: Route `req/tools/_io.py`'s `read_req` through the cache.

- [ ] Task 3.2: Change `general/tools/_doc_paths.py`'s `find_doc_path_by_id` signature from a bare `parse_fn: Callable[[str], T]` to a cache-backed `read_fn: Callable[[Path], T]` -- a breaking signature change requiring every one of req's (and, in Phase 4, the other 10 non-`feat` domains') own `_paths.py` wrapper call sites to pass `read_<domain>` instead of `parse_<domain>` -- materialize the full path listing up front, reconcile the cache against it before scanning, and confirm `update`/`delete`/`set_status` call sites (which only ever consume the returned `Path`) are unaffected.

- [ ] Task 3.3: Wire cache updates into `create_req` and req's adapters inside the generic `update`/`set_status`/`set_classification` tools, warming each entry by calling `read_req(path)` once immediately after each successful write (per REQ-003), not by reconstructing a document in-process from the frontmatter object and body string already in memory.

- [ ] Task 3.4: Wire cache invalidation into `delete`'s req adapter.

- [ ] Task 3.5: Add reconcile-on-scan to `list_req` using the same materialized listing `build_summaries` already receives.

- [ ] Task 3.6: Add tests covering ACC-001 through ACC-006 for req specifically.

#### Phase 4: Roll Out to the Remaining 11 Generic Domains

- [ ] Task 4.1: Repeat Phase 3's wiring pattern (including the `find_doc_path_by_id` `read_fn` signature change) for uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, and sysrs, which all route through the shared `find_doc_path_by_id`/`iter_doc_paths` helpers unchanged from Phase 3.

- [ ] Task 4.1a: Implement `feat`'s own bespoke cache integration, since its `_paths.py`/`set_feat_id` never route through `general.tools._doc_paths` (per the Scope and Design Notes sections above): wire its cache into `feat`'s hand-rolled scan and `read_feat`-equivalent load, and hook `set_feat_id`'s cache-entry move (old path -> new path) in only after `write_feat_file` succeeds, never at the earlier `old_path.parent.rename(...)` step.

- [ ] Task 4.2: Add the structural test from ACC-008 covering all 12 generic domains, including `feat`'s bespoke integration point from Task 4.1a.

#### Phase 5: Verification and Docs

- [ ] Task 5.1: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture`, full `pytest -n auto` suite).

- [ ] Task 5.2: Update `AGENTS.md` noting the new cache module, its wiring, and that ADR is deliberately excluded; additionally grep for and update the near-verbatim "always re-reads from disk, no in-memory cache" claim repeated across ~40+ per-domain docstrings (every in-scope domain's `get_<d>.py`, `_paths.py`, etc.) so documentation no longer contradicts the shipped behavior.

- [ ] Task 5.3: Regenerate `docs/GENERATED.md`/`docs/api/` via `specmgr docs` if any touched docstrings changed.

## Progress

### Current Status

**As of 2026-09-10**: Phase 2 complete -- the generic `DocCache` module and its unit tests are implemented and green; Phase 3 (wiring `req` as the pilot domain) may now begin.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-10 10:30:00.000Z - Phase 2 complete: generic DocCache module implemented and tested

Implemented `general/tools/_doc_cache.py`'s `DocCache[_DocT]` class exactly per the illustrative API sketch (`read`/`invalidate`/`reconcile`/`move`/`reset`), with one small addition beyond the sketch: a module-level `CACHEABLE_ERROR_TYPES` constant (`(AssertionError, ValidationError, yaml.YAMLError)`, mirroring `general.tools._listing.DEFAULT_ERROR_TYPES`'s precedent exactly) fixes which `parse_fn` failures `read` caches as a "failure" rather than letting the caller parameterize it per call -- every `parse_<domain>` function in this codebase raises the same fixed failure channel, so no per-call override was needed. `read(path, parse_fn)` hashes `path`'s full text with `hashlib.blake2b` on every call (inside the lock only for the dict get/set, never around the file read or the `parse_fn` call itself), returns/re-raises the cached `(hash, result)` entry on a hash match, and otherwise calls `parse_fn(path)` fresh and stores the new `(hash, result_or_exception)` pair; a read failure before `parse_fn` even runs (e.g. `path.read_text()` raising `OSError`/`FileNotFoundError` for a missing file) propagates uncaught and is never cached, exactly per the design brief. `move(old_path, new_path)` relocates the dict entry as-is without re-hashing, so a post-rename `read` of `new_path` naturally hits (byte-identical content, the realistic `set_feat_id` case) or misses and reparses (differing content) through the same `read` path every other call uses -- no special-cased validation logic in `move` itself. Added `tests/general/tools/test__doc_cache.py` (17 tests, `unittest.TestCase`-based per this codebase's convention, real `tmp_path`-style temp files via `tempfile.TemporaryDirectory()`, no mocks) covering: single-call cache miss; unchanged-content cache hit (fake not re-invoked); changed-content cache miss (fake re-invoked); `AssertionError` failure caching and re-raising on unchanged content, with automatic recovery on content change; a non-cacheable failure type (`RuntimeError`) correctly NOT cached; a missing-file `OSError` before `parse_fn` runs correctly NOT cached; `invalidate` forcing a re-parse; `reconcile` dropping an orphaned path while keeping a still-live one cached; `move`'s identical-content-survives-as-hit and differing-content-misses-and-reparses contracts, plus old_path no longer serving a cached hit post-move; and `reset` clearing everything. Quality gate green: `ruff format --check` (1665 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean after adding a phase-scoped `whitelist.py` entry for `invalidate`/`reconcile`/`move`/`reset` -- these four methods have no caller in `src/` yet by design, since Phase 3/4 is what wires them into each domain's `read_<domain>`/`create_<domain>`/the generic `update`/`set_status`/`set_classification`/`delete` tools/`set_feat_id`; `reset` itself is permanently test-only), full `pytest -n auto --cov=src --cov-report=` suite (3383 passed, no regressions). No domain wiring was touched -- Phase 3/4 remain untouched, per this phase's scope.

#### 2026-09-10 09:15:00.000Z - Phase 1 complete: ADR created and design locked in

Created ADR bfd76370-b59b-4d65-b550-a969f6c93c9d ("Add a content-hash-validated, per-domain in-memory read cache for the 12 generic whole-body domains"), documenting the cache design, its reconciliation with ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (the cache refines rather than violates the "filesystem is the sole source of truth" invariant, since a stale entry is structurally impossible under hash validation), the explicit exclusion of the ADR domain from this cache mechanism, and the cache lock's fixed always-innermost ordering rule (after any domain-level per-id lock, consistent with `set_feat_id`'s existing `feat_create_lock` -> `feat_lock` order). Regenerated `docs/adr/README.md` via `specmgr adr-toc` to list the new ADR. ACC-007 is satisfied; Phase 2 implementation work may now begin.

#### 2026-09-09 13:00:00.000Z - Plan refined against actual code before implementation

Investigated the real current code behind every REQ/Task (`_doc_paths.py`, `_listing.py`, per-domain `_io.py`/`_write.py`, the per-id `threading.Lock` registries, `set_feat_id`, ADR 33c5ab08) and found the plan needed eight refinements before implementation could safely begin: REQ-003's "document object already validated in memory" doesn't exist at write time (no domain ever holds a full parsed document right before writing, only a separate frontmatter object and body string) -- resolved as a single post-write re-parse via `read_fn`; `find_doc_path_by_id`'s `parse_fn: Callable[[str], T]` must become a `Path`-taking `read_fn`, a breaking signature change across 11 domains' `_paths.py`; `feat` cannot follow the other domains' rollout pattern since its `_paths.py`/`set_feat_id` never route through `general.tools._doc_paths`; `set_feat_id`'s cache-move hook must fire only after `write_feat_file` succeeds, not at the earlier folder-rename step; the cache lock must be explicitly pinned as always-innermost in the new ADR, consistent with `set_feat_id`'s existing fixed lock order; the cache is a module-level singleton per domain (mirroring the existing `_lock.py` registries) with a test-only reset hook; the cache stores parse failures as well as successes, keyed by hash; and Task 5.2's docstring-update scope was expanded from `AGENTS.md` alone to the ~40+ per-domain docstrings making the now-inaccurate "no in-memory cache" claim.

#### 2026-09-09 12:00:00.000Z - Created

Created this feature to reframe GitHub issue #107 ("Use a thread pool with concurrent workers for artifact tool calls"): investigation showed the MCP SDK already thread-pools every sync tool call, so the real fix is a content-hash-validated per-domain read cache rather than an additional thread pool.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-09 13:00:00.000Z - Four open design questions resolved before implementation

Resolved via direct code investigation and explicit confirmation: (1) post-write cache warming re-parses once via the domain's own `read_fn` immediately after a successful write, rather than reconstructing a document object from the frontmatter + body string already in memory, since no write path actually holds one unified, fully-validated document object at write time and a shortcut reconstruction risks caching an object that skipped `parse_fn`'s own structural validation; (2) each domain's cache is a module-level singleton, mirroring the existing per-domain `threading.Lock` registries in `_lock.py`, rather than an instance explicitly threaded through call sites, trading a small amount of test-isolation ceremony (an explicit reset hook) for zero signature changes to existing callers beyond the `read_fn` swap; (3) the cache stores parse failures as well as successes (keyed by content hash, storing the raised exception), so a persistently malformed file isn't re-parsed on every scan that touches it, and automatically retries the moment its content changes; (4) Task 5.2's docstring-update scope is expanded to cover the ~40+ per-domain docstrings repeating the "always re-reads, no in-memory cache" claim, not just `AGENTS.md`, so shipped documentation doesn't contradict shipped behavior.

#### 2026-09-09 12:05:00.000Z - ADR excluded from the cache mechanism entirely

Decided to exclude ADR (`models/adr/v1`) from this feature's scope entirely, rather than giving it its own independently-implemented cache module as originally sketched, since ADR is expected to be phased out later and the extra, separately-maintained cache module its lack of dependency on `general` would require is not worth building for a domain with a limited remaining lifetime.

#### 2026-09-09 12:00:00.000Z - Content-hash cache chosen over a literal thread pool for issue #107

Confirmed via direct inspection of the installed MCP SDK that sync tool calls are already offloaded to `anyio.to_thread.run_sync` with a 40-thread `CapacityLimiter`, so adding a separate thread pool would be redundant and would not help the actual bottleneck, which is CPU-bound, GIL-holding full-directory re-parsing on every `get_*`/`list_*` call. Chose a content-hash-validated per-domain cache over a frontmatter-only scan optimization, since the cache subsumes that benefit for any repeated-call workload and additionally speeds up `list_*`, which needs body-derived fields (the `# {title}` H1) that a frontmatter-only parse cannot provide. Chose no time-based/size-based eviction for v1, since the cache's key space is bounded by the number of files that actually exist on disk rather than by request history, and measured memory footprint at this codebase's own stated scale is negligible; a reconcile-on-scan step (in both `get_*` and `list_*`) instead closes the one real leak scenario, files deleted outside specmgr's own tooling. Chose to fold the fix for `get_*`'s existing matched-file double-parse bug into this same change, since sharing one cache between the id-lookup scan and the final matched-file load eliminates it as a structural consequence, with no return-type/call-site changes needed elsewhere.

### Related PRs / Commits

- [Issue #107](https://github.com/dfch/biz.dfch.SpecMgr/issues/107): tracking issue this feature reframes from "add a thread pool" to "add a content-hash-validated read cache".
