---
status: accepted
decision-makers: dfch
id: 3982712a-a46b-4b2b-809f-9c6925a49b44
version: 1.0.0
---

# Two-Stage Dirty/Clean DocCache Staging and a Unified Startup Warmup Thread to Fix list_feat's Cold-Scan Timeout (#187)

## Context and Problem Statement

GitHub issue #187: `list_feat` intermittently fails with `MCP error -32001: Request timed out`. Reproduced in-session twice (2026-10-03, 2026-10-04). `list_feat` performs a lock-free, full-directory sweep that fully parses every `<base>/*/README.md` on a cold cache (`python-frontmatter`/PyYAML frontmatter, pure-Python `markdown_it("commonmark")` body tokenizing, nested Pydantic validation). The MCP client (OpenCode 1.18.34) gives up long before a full sweep ends, and the published `uvx biz-dfch-specmgr[mcp, similarity]` entry point starts a fresh process per client session, so feat-107-doc-cache's process-local content-hash cache (ADR bfd76370-b59b-4d65-b550-a969f6c93c9d) never helps a session's first call -- exactly the one call that times out.

Measured at initial reproduction (2026-10-03, this worktree, `uv run --frozen python`): a cold full-parse sweep of all 70 `README.md` files took 348.6 s (roughly 10-13 KB/s on large files; slowest: feat-6-requirement-artifact 146 KB / 24.0 s, feat-32-sysrs 243 KB / 19.5 s); the warm floor (full read plus `blake2b` content hash of the entire corpus, no parsing) is 0.007 s, proving the parses -- not the I/O -- are the bottleneck; a frontmatter-only sweep (read plus PyYAML frontmatter parse plus an H1 line scan, no body parse) completes in well under 1 s for the whole corpus; 5 of 70 folders failed a full parse at that time (`feat-5-md-model-parser`, `feat-29-dec-source-roles`, `feat-50-confluence`, `feat-132-prb-update`, `feat-177-list-ref-feat`). `server.py`'s lifespan hook is not a no-op: it already starts feat-134's similarity warmup (ADR 750842b2-aca4-4649-ba0c-855ec8e1f505), which fully parses every whole-body domain's corpus (feat included, via `parse_feat`) for embedding purposes in a background daemon thread, without ever warming the `DocCache` the request path could otherwise reuse. On 2026-10-04 re-reproduction, the first `list_feat` call eventually returned but two subsequent *concurrent* calls both still timed out -- evidence the timeout is not a first-call-only phenomenon, consistent with this pre-existing similarity thread holding the GIL against a cold request-path sweep.

The corpus grew, and was re-measured, across this feature's three structured review rounds: 71 folders / 4,073,256 README bytes / 6 failures (2026-10-04, `feat-180-updates` having joined the failure set); 73 folders / 4,202,118 bytes / 6 failures (2026-10-05, round-3 review). **Re-verified again at this ADR's own authoring time, 2026-10-05 (later the same day), directly against the live corpus rather than inherited from any prior snapshot: 73 folders, 4,210,674 README bytes total, and 6 full-parse failures** -- confirmed via both `find`/`wc -c` over `.specmgr/feat/*/README.md` and a live `list_feat` call against this repo's own corpus. The failure set is unchanged from every prior measurement: `feat-5-md-model-parser` (legacy Requirements shape), `feat-29-dec-source-roles` (missing Task List), `feat-50-confluence` (legacy task-item shape), `feat-132-prb-update` (legacy Updates timestamp form), `feat-177-list-ref-feat` (raw HTML inline token), `feat-180-updates` (stray list marker inside an UpdateEntry's content). The corpus is live and growing -- by the time this ADR is read, these exact numbers will already be stale again; they are recorded here as a dated data point, not a standing fact, per this feature's own convention of re-verifying rather than silently inheriting a prior snapshot.

Question: how do we make `list_feat`'s very first call, from a cold/fresh server process, return the complete directory listing well within a typical MCP client's request timeout -- independent of corpus size or shape -- without weakening ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3's "filesystem is the sole source of truth" invariant, without permanently regressing the full-fidelity failure reporting `list_feat`/`get_feat` give today, and without conflicting with the already-running feat-134 similarity warmup thread?

## Decision Drivers

- Bound the very first `list_feat` call's wall time independent of corpus size/shape: zero full markdown-it/Pydantic body parses on the request path, for any file, healthy or defective.
- Never weaken ADR 33c5ab08 (filesystem is the sole source of truth) or ADR bfd76370's content-hash-validation guarantee -- a stale cached value must stay structurally impossible at every new cache layer this feature adds.
- Preserve ADR ec9f5262's materialize-then-paginate contract unconditionally: `total` must always reflect the whole on-disk directory on every call.
- Converge to today's exact full-fidelity failure reporting as fast as reasonably possible, without permanently hiding any body-level defect.
- Minimize GIL contention: avoid ever running two CPU-bound, GIL-holding background threads in parallel against the already-shipped feat-134 similarity warmup.
- Keep the fix feat-local and additive: zero new MCP tools, and the generic `build_summaries` helper (and the other 11 whole-body domains) left untouched.
- Stay testable without a real MCP client/server subprocess, since no such test harness exists in this repo today.

## Considered Options

1. Two-stage dirty/clean `DocCache` staging plus a unified three-phase startup warmup thread (CHOSEN).
2. A pure frontmatter-only request path with no warmup at all.
3. A `stat()` (mtime/size) pre-check fast path in the cache.
4. A process-pool-parallelized cold sweep.
5. A lazy per-page sweep.
6. A persisted/disk-backed warm cache surviving process restarts.
7. A free-threaded (no-GIL) CPython 3.13t/3.14t runtime.
8. A frontmatter-only warmup phase only, with no full-parse phase.

## Decision Outcome

Chosen option: (1), two-stage `DocCache` staging plus a unified startup warmup thread, with these sub-decisions (each normative for implementation, settled with the maintainer across three structured review rounds, 2026-10-03 through 2026-10-05):

- **Two-stage DocCache staging:** `feat` gains a second, feat-local `DocCache` instance ("dirty") alongside the existing full-parse instance ("clean"). The dirty stage's `parse_fn` is frontmatter-only: the exact same `parse_frontmatter(text, FeatFrontmatter, domain="feat", stringify_metadata=...)` call `parse_feat` itself makes (so tier-1 error text is byte-identical to `get_feat`'s by construction), followed by the existing `general.tools._similarity_text.first_h1` fence-aware line scan plus the `^Feature: .+$` alias check -- producing a small, frozen frontmatter-summary payload (`id`/`status` from frontmatter, `title` from the scanned H1, `ref`/`path` from the folder). The dirty stage is hash-validated exactly like the clean stage (the same `blake2b` content-hash guarantee, the same cacheable-failure-plus-fresh-exception semantics), so an on-disk edit between the warmup's frontmatter phase and a `list_feat` call always re-reads that file's frontmatter -- a stale dirty-stage summary is structurally impossible, extending rather than weakening ADR 33c5ab08's invariant down to the frontmatter level.

- **Unified startup thread (`specmgr-startup-warmup`):** `server.py`'s lifespan hook -- never actually a no-op, since it already started feat-134's `start_similarity_warmup` -- is rewired to a single daemon thread running three phases, strictly in order: (1) the feat frontmatter phase (every live `*/README.md` read through the dirty stage; well under 1 s for this repo's corpus); (2) the feat sequential full-parse phase (every path read through the existing cache-backed `read_feat`, one after another, on the order of several minutes for this repo's corpus, entirely in the background, off the request path); (3) the pre-existing, unchanged feat-134 `warmup_similarity_cache()` body, invoked inline exactly as it runs today. Running phases 1-2 before phase 3 means `list_feat` is already fast within roughly a second of server start, well before the heavier phases even begin.

- **Per-phase flag gating and the no-thread invariant:** gating is per-phase, not per-thread. A new presence flag `SPECMGR_FEAT_WARMUP_DISABLED` (default absent = feat phases run) gates phases 1-2; the pre-existing `SPECMGR_SIMILARITY_DISABLED` flag gates phase 3 only, unchanged in meaning. When both flags are present, no thread is started at all -- a true no-op under which the server behaves exactly as it did before this feature shipped (one of the four flag-combination cases the new lifespan unit test asserts directly).

- **Crash containment:** every per-file exception the warmup thread encounters that is one of the three cacheable parse-failure channels (`AssertionError`/`pydantic.ValidationError`/`yaml.YAMLError`) is the normal, expected, cacheable outcome -- stored in the relevant `DocCache` stage exactly as it is today, never treated as a crash. Any other, truly unexpected exception (e.g. a file vanishing mid-warmup, a transient `OSError`) is logged via the standard library `logging` module -- a named logger mirroring the feat-134 `specmgr-similarity-warmup` thread's own precedent: an unexpected per-file exception at `WARNING` with the offending path and `exc_info=True`, a phase start/finish at `INFO` -- and then swallowed: it never propagates out of the thread, never stalls it, and never prevents it from reaching later files or the server from serving requests throughout.

- **Lifespan hook rewire:** `start_similarity_warmup` is retired and replaced by a single `start_startup_warmup()` spawner, kept function-level-imported from `_lifespan` exactly as its predecessor was (no circular import risk: the spawner's own `feat.tools` import only resolves once `server`'s `mcp` object already exists). The feat phases themselves live in a plain, synchronously callable `warmup_feat_caches()` function, independent of the spawner/thread, so tests (and any future caller) can drive the phases directly and deterministically rather than only through a real thread; it returns a small per-phase summary (paths warmed, parse failures stored) for both the phase-finish log line and test assertions.

- **Three-tier failure-visibility contract (Option A, chosen over Option B):** `list_feat`'s request path resolves every folder from one file read plus `clean.peek_preloaded(path, text)` (a valid full-parse entry, success or cacheable failure, or `None` -- never parses), falling back to `dirty.read_preloaded(path, text, parse_fn)` (which on a miss runs the cheap frontmatter-only derivation and populates the dirty stage). Each summary is built from whichever stage answered, under three tiers: **tier 1** (frontmatter-level: malformed/missing YAML, frontmatter schema violations) is a `<failed to parse>` row with `error` text byte-identical to `get_feat`'s from the very first call -- both stages run the identical `parse_frontmatter` call, so these are identical by construction, with no fallback needed. **Tier 2** (H1-level: a missing `# Feature:` H1, or an H1 failing the `^Feature: .+$` alias) is a `<failed to parse>` row from the very first call too (the dirty stage detects both cheaply via the fence-aware `first_h1` scan plus the alias regex), but with dirty-stage-specific `error` text that converges to byte-identical to today's full-parse sweep only once the clean stage has passed that file -- byte-identity from call one is deliberately sacrificed here, because the full-parse error text for a missing/invalid H1 is built from the markdown-it-normalized body (e.g. "...remaining text starts at line N of the normalized body...") and cannot be produced without running a full body parse. **Tier 3** (body-level: everything deeper -- the current six-folder failure set, and any future body-level breakage) transiently appears as a *healthy* row during the warmup window if its frontmatter and H1 are well-formed (the documented dirty-stage limitation), converging to a `<failed to parse>` row byte-identical to today's full-parse sweep once the clean stage passes it. **Option B** -- a dirty-stage full-parse fallback specifically for H1-defective files, which would have kept tier 2 byte-identical from call one too -- was considered and rejected: it reintroduces exactly the corpus-shape-dependent cost this feature exists to remove (a 146 KB README with a missing H1 would cost roughly 24 s to full-parse on the request path under Option B -- the very exposure issue #187 reports), and reintroduces GIL contention for precisely the files a broken corpus is most likely to contain. `get_feat` remains the full-fidelity authority throughout every tier and every window: it always fully parses on demand (warmed or not), so a dirty-stage `list_feat` row may only ever *under*-report a tier-2/tier-3 defect, never over-report one.

- **`DocCache` API additions (`peek_preloaded`/`read_preloaded`) and their single-read rationale:** `general/tools/_doc_cache.py::DocCache` gains two additive read primitives. `peek_preloaded(path, text)` returns a valid stored result (a successfully parsed document or one of the three cacheable failure exceptions) if the hash of the *already-read* `text` matches the stage's stored hash for `path`, or `None` otherwise -- it never parses, and never re-reads the file; on a hit it materializes exactly like `read`'s own hit branch (a fresh `model_copy` for a document, a fresh equivalent exception for a failure, per feat-107's REQ-008/REQ-011 guarantees). `read_preloaded(path, text, parse_fn)` has hit/miss semantics identical to `read`, except it is handed the text the caller already read rather than reading it itself. `read` itself is refactored to be implemented in terms of `read_preloaded` (behavior-preserving; the existing `test__doc_cache.py` suite, including the feat-162 footer-reconstruction tests, is the regression guard). The point of both additions is the same: `list_feat`'s request path reads each folder's `README.md` exactly once per call (one `path.read_text()`), and passes that one in-memory `text` value to both the clean-stage peek and, on a miss, the dirty-stage read -- never a second, independent re-read of the same file for the second cache query. This follows the feat-107 Phase 6 TOCTOU standard exactly (the same text that is hashed is the only text that is ever parsed, with zero intervening file I/O): a naive `clean.peek(path)` (hashing by re-reading `path` itself) plus the existing `read(path, parse_fn)` would have reopened the same hash/parse-atomicity race feat-107 Phase 6 closed, this time between the clean-stage peek and the dirty-stage read of one cold folder.

- **Convergence semantics:** `total` is complete from call one -- the live directory scan always enumerates every on-disk folder, and the dirty-stage inline fallback resolves any folder the warmup has not yet reached, so the *entry count* never lags the directory; what converges over time is each entry's *validation depth* (tier 1/2/3), not its presence (ADR ec9f5262's materialize-then-paginate contract, unchanged). `error_count` converges monotonically (non-decreasing) toward today's full-parse value as the warmup progresses, under exactly three convergence triggers: (a) the warmup thread's own startup directory snapshot reaching a file in its sequential full-parse phase; (b) the two-stage write-path warming a tool-written file immediately after `create_feat`/the generic `update`/`set_status`/`set_classification`/`delete` tools/`set_feat_id` act on it; (c) any on-demand clean-stage read of a file outside those two triggers (most notably a `get_feat` call). A folder created by hand after the warmup's startup snapshot, and never subsequently touched by a tool call, only converges at its *next* on-demand clean read, not automatically or immediately.

- **GIL-contention treatment:** with the unified thread, at most one heavy, GIL-holding background thread is ever active during the warmup window (replacing the pre-refinement design's two threads running in parallel), so a concurrent `get_*`/`list_*` request shares CPU with the feat phases and then, separately, with the similarity phase -- never with both simultaneously. Total parse CPU per process is unchanged versus today for any session that actually uses the feat tools: in an mcp-only install, a used session parses the feat corpus exactly once per process either way (today on the request path; now in the background); a session that never touches a feat document now pays one background sweep it would not have paid before (bounded by the measured sweep time, daemon-only, and exactly what `SPECMGR_FEAT_WARMUP_DISABLED` opts out of). In a `similarity`-extra install, the duplicate feat parse already exists today (the similarity warmup parses the feat corpus in the background *and* the first `list_feat` parses it again, cold, on the request path) -- this design only relocates the second parse off the request path and serializes the two background phases instead of running them in parallel. One behavioral concession of that serialization: the similarity warm state now arrives after the feat phases complete (delayed by the measured sweep duration on this corpus), so a `find_related`/`find_similar_text` call issued inside that window pays its own demand-path cold-parse/embed/first-session-model-load cost on the request path -- an exposure that already exists today in every mcp-only install, and in fact a *lower*-contention situation during that window than today's parallel-threads setup. **Request-preemptive pausing** (the warmup voluntarily idling whenever a tool call is in flight, to minimize GIL contention further) is explicitly **deferred**, not adopted, by this ADR: the contention this design leaves behind is bounded, one-thread-at-a-time, and opt-out-able via `SPECMGR_FEAT_WARMUP_DISABLED`; adding pause/resume coordination between the warmup thread and every tool-call entry point is nontrivial additional machinery (a new synchronization primitive, additional thread-state bookkeeping, and interaction with every `@mcp.tool()` call site) for a contention class not yet shown by measurement to need it. If a future measurement (e.g. ACC-006's live one-shot run, repeated as the corpus grows) shows request latency during the warmup window to be unacceptable, request-preemptive pausing is the documented next lever to pull -- an explicit follow-up, not a Phase 110/120 deliverable of this feature.

- **In-process test strategy:** the ACC-001..ACC-005/ACC-009 suite runs entirely in-process, with no real subprocess MCP server: `SPECMGR_FEAT_DIR` is pointed at a fixture corpus generated deterministically at test-setup time into a per-test temp directory by a tests-space-only helper module (no committed fixture bytes, never co-located with the live `.specmgr/feat` corpus; generation cost excluded from ACC-001's wall-time assertion), mirroring the isolation pattern feat-134's `SimilarityTestCase` already establishes. Both feat cache stages are reset per test. The warmup is driven by calling `warmup_feat_caches()` (and, where needed, the spawner) directly and synchronously rather than through a real thread/server. ACC-001's "zero full body parses on the request path" claim is proven by a parse-count seam wrapping the clean stage's `parse_fn`, which the request path must never invoke (the warmup invokes it by design). The lifespan itself gets a dedicated unit test asserting the startup wiring (thread started; per-phase flag gating across all four flag combinations; both-flags-set => no thread at all) built on the same fixture, with `SPECMGR_FEAT_WARMUP_DISABLED` saved/restored alongside the existing `SPECMGR_SIMILARITY_DISABLED` restore. A real subprocess `specmgr mcp` server in CI was considered and rejected: this repo has no MCP-client test harness today (every existing test calls tool functions in-process), `pytest-xdist` would multiply the spawn cost across workers, and a spawned child's lifespan would inherit the similarity warmup unless `SPECMGR_SIMILARITY_DISABLED=1` were set in its environment -- which, with CI's `--all-extras` install, means a real model load/download inside a test child, a flakiness vector this feature does not need to accept. The one genuinely end-to-end proof -- a fresh `uvx` session against the live corpus -- stays ACC-006's manual, one-shot, non-flaky measurement recorded in the feature's own `### Updates`, not asserted in CI.

- **Time-qualified list/get error byte-identity property:** ADR 9080b37c establishes that `ParseFailureResult.error` (from `get_<d>`) and a `list_<d>` failed row's `error` are byte-identical for the same broken file, for every whole-body domain, unconditionally. This feature narrows that guarantee for `feat` specifically: the property now holds unconditionally only (a) outside the tier-2/tier-3 convergence window (once the clean stage has passed a given file), and (b) whenever `SPECMGR_FEAT_WARMUP_DISABLED` is set, under which no background warmup runs at all and convergence depends solely on on-demand clean reads -- time-qualified the same way, just without a dirty-stage interim text ever appearing. During the tier-2/tier-3 window, `list_feat`'s row may read differently from `get_feat`'s `ParseFailureResult.error` for the same file -- by design, per the three-tier contract above. `get_feat` remains, unconditionally, the full-fidelity authority for `feat`; every user-facing text asserting the list/get byte-identity property unconditionally must be updated (Task 110.140) to state it as time-qualified for `feat`, unconditional for every other domain (which continues to hold the property untouched).

- **Relationships to prior ADRs:** **ADR 33c5ab08** (filesystem is the sole source of truth) is preserved, and extended one level deeper: both the dirty and clean stages re-validate by content hash on every access, so the request path's dirty-stage fallback is exactly as staleness-proof as the existing clean-stage read. **ADR bfd76370** (per-domain `DocCache`) is extended, not replaced: this feature adds a second, feat-local `DocCache` instance (the same class, the same lock-ordering rule, the same reconcile/invalidate/move/reset semantics) plus two additive read primitives on the shared `DocCache` class itself (`peek_preloaded`/`read_preloaded`), with `read` refactored onto `read_preloaded` behavior-preservingly; the other 11 domains, and ADR bfd76370's own text, are otherwise untouched. **ADR ec9f5262** (materialize-then-paginate listing) is preserved exactly: `list_feat` still scans the live directory and materializes the complete list before paginating on every call; `total` is unconditionally complete from call one; only `error_count`'s convergence behavior is new, and it is additive (today's single-call, synchronous full-parse `error_count` is the special case where every tier has already converged). **ADR 9080b37c** (`get_<d>`/`list_<d>` error byte-identity) is qualified, not violated, for `feat` only, exactly as described above; every other domain's property is untouched. **ADR 750842b2** (feat-134's similarity engine) is refined, not replaced: this ADR forward-references a **v1.4.0** revision note that Phase 110 (Task 110.120) will write directly into ADR 750842b2's own Warmup sub-decision paragraph -- not into this ADR -- rewriting it to describe the new unified `specmgr-startup-warmup` thread sequencing (feat frontmatter phase -> feat full-parse phase -> the unchanged similarity warmup body) in place of the single similarity-only daemon thread the sub-decision currently describes (v1.2.0/v1.3.0 having already been consumed by feat-134's own Phase 6/7 revisions, so this is correctly a v1.4.0 note, not v1.2.0). This ADR does not itself edit ADR 750842b2; it only records that the edit is owed, and by which task.

### Consequences

Positive: the very first `list_feat` call from a cold server process returns the complete directory listing in well under any realistic MCP client timeout, independent of corpus size or shape, closing GitHub issue #187 at the root rather than symptomatically. `get_feat` calls made after (or during) the warmup increasingly hit pre-parsed, warm documents at zero additional parsing cost. The already-shipped feat-134 similarity warmup is subsumed into one coherent, deterministically-ordered startup sequence instead of running as an independent, contention-causing second background thread. The two additive `DocCache` primitives (`peek_preloaded`/`read_preloaded`) are reusable building blocks any future per-domain two-stage caching need can reuse without re-deriving the single-read, TOCTOU-safe pattern.

Negative / trade-offs: `list_feat`'s failure-visibility contract is now time-qualified and three-tiered instead of a single, always-byte-identical-to-`get_feat` shape -- a caller inspecting `list_feat`'s output during the warmup window may see transiently-healthy tier-3 rows, or tier-2 rows whose `error` text differs from `get_feat`'s. The whole-body-domain generalization of the "`list_<d>`/`get_<d>` error byte-identity" property (ADR 9080b37c) must now be read as "feat only, time-qualified" rather than universal -- a nuance a future contributor must remember. A new presence flag (`SPECMGR_FEAT_WARMUP_DISABLED`) and a new background daemon thread add process-level state and a bounded, opt-out-able background CPU cost to every server process that did not opt out, even one that never calls a feat tool. Request-preemptive pausing is explicitly deferred, so a tool call issued during the feat full-parse phase still shares the GIL with it (mitigated versus today by it being the single heaviest phase running, not two phases in parallel).

### Confirmation

Not yet confirmed at this ADR's authoring time: the design was settled with the maintainer across three structured review rounds (2026-10-03, 2026-10-04, 2026-10-05), and `status: accepted` reflects that design consensus, not a shipped, test-verified implementation. To be confirmed by Phase 110/120's acceptance criteria (ACC-001 through ACC-009 of `.specmgr/feat/feat-187-list-feat-timeout/README.md`) as the implementation lands, including the live one-shot `uvx` measurement (ACC-006) against the then-current corpus.

## Pros and Cons of the Options

### Option 1: Two-stage dirty/clean DocCache staging plus a unified three-phase startup warmup thread (chosen)

#### Pros

- Directly fixes issue #187 at the root: zero full body parses on the request path, for any file, independent of corpus shape.
- Preserves ADR 33c5ab08/bfd76370/ec9f5262 unqualified, and only explicitly, narrowly time-qualifies ADR 9080b37c for `feat`.
- Converges to full fidelity automatically, via the background warmup plus any on-demand read, under a documented, testable three-tier contract.
- Reuses and extends the existing `DocCache` machinery (two additive read primitives) rather than inventing a new caching mechanism.
- Unifies the pre-existing, previously-undocumented similarity warmup into one coherent, deterministically-ordered sequence, reducing GIL contention versus today's two-parallel-thread reality.

#### Cons

- Three-tier, time-qualified failure visibility is more nuanced than today's single-shot, always-accurate semantics.
- Adds a new opt-out flag and a new background daemon thread -- new process-level state in every server process.
- Defers, rather than eliminates, request-preemptive GIL-contention mitigation.

### Option 2: A pure frontmatter-only request path with no warmup at all

#### Pros

- Simplest possible fix: no new background thread, no startup sequencing, no convergence semantics to document or test.
- Still delivers the headline `list_feat` speed-up (frontmatter-only sweep measured at well under 1 s for the whole corpus).

#### Cons

- Body-level failures (the current six folders, and any future hand-edit breakage) become permanently, silently invisible in `list_feat`'s output -- a real regression of the `repair` skill's list-based discovery mechanism, which depends on `list_<d>` surfacing broken documents.
- Rejected/subsumed: kept only as the request path's own behavior, as half of the chosen two-stage design, with the warmup added back specifically to restore full fidelity over time.

### Option 3: A stat() (mtime/size) pre-check fast path in the cache

#### Pros

- Trivial to implement; no new cache instance, no new background thread.

#### Cons

- Only trims the already-negligible warm path (measured at 0.007 s); does nothing at all for the cold sweep that actually causes issue #187's timeout.
- Already explicitly deferred by feat-107-doc-cache/ADR bfd76370-b59b-4d65-b550-a969f6c93c9d itself, for the same reason.

### Option 4: A process-pool-parallelized cold sweep

#### Pros

- No new per-domain cache machinery; parallelizes the existing full-parse sweep as-is.

#### Cons

- 348.6 s / N is still roughly 45 s at N=8 -- still well above typical client request timeouts on anything but a very high-core machine.
- Adds pickling and a cross-process error-reporting channel for the three cacheable failure types, real implementation complexity for a constant-factor gain.
- Cost still grows unbounded with corpus size; it mitigates, but does not actually bound, the request-path cost.

### Option 5: A lazy per-page sweep

#### Pros

- Would bound the parse cost per call to roughly one page's worth of folders.

#### Cons

- Directly breaks ADR ec9f5262-9912-49d0-903f-fcfb54f28c13's materialize-then-paginate contract: `total` would no longer reliably reflect the whole on-disk directory on every call.
- Rejected outright as incompatible with an existing, accepted ADR, not merely as a weaker option.

### Option 6: A persisted/disk-backed warm cache surviving process restarts

#### Pros

- Would let a warm state survive process restarts entirely, including the very first call of a brand-new process on a machine that has run the server before.

#### Cons

- A fresh checkout, or the very first run ever on a machine, still pays one full cold sweep regardless -- it does not solve the worst case issue #187 reports.
- Adds serialization-format design, invalidation-on-external-edit, and cross-process-concurrency concerns well beyond this feature's scope.
- A plausible future complement to, not a replacement for, the in-memory two-stage design; remains deferred.

### Option 7: A free-threaded (no-GIL) CPython 3.13t/3.14t runtime

#### Pros

- On a very high-core host (this repo's own dev machine: 120 cores) could in principle bound wall time by the single largest file's own parse time (measured 24.0 s).

#### Cons

- On a typical 4-8-core laptop the same fan-out approach still lands at roughly 44-87 s, with no bound as the corpus continues to grow -- it does not solve the problem at typical deployment scale.
- Blocked today by `pydantic-core` (Rust, measured at version 2.46.4) lacking free-threaded build support -- a hard dependency blocker to re-verify before any investment.
- A deployment/runtime decision every consumer of this package would have to make for themselves, not a fix this repo can ship centrally.
- Explicitly deferred on maintainer direction ("stay away from Py 3.14 for now", 2026-10-03).

### Option 8: A frontmatter-only warmup phase only, with no full-parse phase

#### Pros

- Roughly half the implementation cost of the chosen design; still gives `list_feat` its fast-first-call benefit via the warmed dirty stage.

#### Cons

- Body-level failures (the current six folders, and any future hand-edit breakage) remain permanently invisible forever, not just during a convergence window -- the same defect as Option 2, just with a fast-path benefit layered on top.
- Ships instead as phase 1 of the full three-phase warmup in the chosen design, not as a standalone option on its own.

## More Information

GitHub issue #187: https://github.com/dfch/biz.dfch.SpecMgr/issues/187. Feature plan and progress: `.specmgr/feat/feat-187-list-feat-timeout/README.md` (REQ-001..REQ-008, ACC-001..ACC-009, phased Task List, and the Design Notes section this ADR summarizes and formalizes). Related ADRs: 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (filesystem is the sole source of truth), bfd76370-b59b-4d65-b550-a969f6c93c9d (per-domain content-hash DocCache, feat-107), ec9f5262-9912-49d0-903f-fcfb54f28c13 (materialize-then-paginate list_<d> tools), 9080b37c-82b3-4f63-81f1-79641d0bf14c (get_<d>/list_<d> error byte-identity, feat-150/feat-162), 750842b2-aca4-4649-ba0c-855ec8e1f505 (feat-134's embedding-based similarity engine, whose Warmup sub-decision this feature's Phase 110 Task 110.120 will revise with a v1.4.0 note). The reproduction environment and the exact OpenCode client-timeout duration that produces the `-32001` error were never directly measured (recorded honestly in the feature's own More Information section as an open gap, round-3 finding I1); the bound this ADR's implementation targets (under 5 s for the first `list_feat` call) is a conservative, round-number safety margin, not a value derived from a measured client timeout. Every measured figure this ADR cites (folder count, README byte total, failure set) was re-verified directly against the live `.specmgr/feat` corpus at this ADR's own authoring time, 2026-10-05, via `find`/`wc -c` and a live `list_feat` call, rather than inherited from any of this feature's prior Design Notes snapshots.
