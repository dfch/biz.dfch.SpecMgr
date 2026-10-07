# `biz.dfch.specmgr.general.tools._startup_warmup`

The unified MCP server startup warmup spawner (feat-187-list-feat-timeout, Task 110.120).

Replaces ``general.tools._similarity_search.start_similarity_warmup`` (now
removed) as the single entry point ``server.py``'s ``_lifespan`` calls at
startup. ``server.py``'s lifespan hook was never actually a no-op -- it
already started feat-134's similarity warmup -- and this module's own
addition (the ``feat`` two-stage cache warmup, GitHub issue #187) would
otherwise be a *second*, independently-scheduled background thread
competing for the GIL with the first one. ADR
3982712a-a46b-4b2b-809f-9c6925a49b44 instead unifies both into a single
daemon thread (``specmgr-startup-warmup``) running three phases, strictly
in order:

1. The ``feat`` frontmatter phase (cheap: frontmatter + H1 only).
2. The ``feat`` full-parse phase (expensive: the full corpus, sequentially).
3. The pre-existing, unchanged feat-134 similarity warmup body
   (:func:`~biz.dfch.specmgr.general.tools._similarity_search.warmup_similarity_cache`).

Both ``feat`` phases live in :func:`~biz.dfch.specmgr.feat.tools._warmup.warmup_feat_caches`,
a plain, synchronously runnable function this module merely calls -- this
module owns only the **gating** (per-phase opt-out flags) and the
**thread** (a single daemon, named and started here), never the phase
bodies themselves.

**Per-phase gating, not per-thread (REQ-007).** :data:`FEAT_WARMUP_DISABLED_ENV_VAR`
(``SPECMGR_FEAT_WARMUP_DISABLED``, new) gates phases 1-2; the pre-existing
``SPECMGR_SIMILARITY_DISABLED`` (:data:`~biz.dfch.specmgr.general.tools._embedding.SIMILARITY_DISABLED_ENV_VAR`)
gates phase 3 only, unchanged in meaning. When both flags are present, no
thread is started at all -- a true no-op, and the server behaves exactly as
it did before this feature shipped (one of the four flag-combination cases
the lifespan unit test asserts directly, ACC-009).

With the unified thread, at most one heavy, GIL-holding background phase
ever runs at a time during the warmup window (replacing the pre-refinement
design's two independent threads running in parallel) -- see the feature's
own Design Notes for the full GIL-contention analysis.

## Functions

### `_run_all_phases() -> 'None'`

The unified thread body: feat frontmatter phase -> feat full-parse phase -> similarity warmup.

Each phase is independently crash-contained by its own body
(:func:`~biz.dfch.specmgr.feat.tools._warmup.warmup_feat_caches` and
:func:`~biz.dfch.specmgr.general.tools._similarity_search.warmup_similarity_cache`
both already never raise) -- this function adds only the per-phase
gating, strictly in order.


### `start_startup_warmup() -> 'threading.Thread | None'`

Start the unified daemon warmup thread, unless both opt-out flags are set (REQ-007).

The entry point ``server.py``'s ``_lifespan`` calls at startup (kept
function-level-imported there, mirroring the predecessor
``start_similarity_warmup`` it replaces -- no circular import risk:
this module's own ``feat.tools``/``general.tools`` imports resolve once
``server``'s ``mcp`` object already exists).

Checks only the two lightweight, synchronous presence flags
(:data:`FEAT_WARMUP_DISABLED_ENV_VAR`/``SPECMGR_SIMILARITY_DISABLED``):
when *both* are present, no thread is started at all -- a true no-op,
and the server runs exactly as it did before this feature shipped.
Otherwise a single daemon thread is started running
:func:`_run_all_phases` (which re-checks each flag independently, so a
single flag disables only its own phase(s)) and returned **without
joining it** -- server startup is never blocked by either warmup.

Returns
-------
threading.Thread | None
    The started daemon thread, or ``None`` when both opt-out flags are
    present and no thread was started.

