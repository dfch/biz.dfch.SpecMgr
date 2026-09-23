# `biz.dfch.specmgr.telemetry.metrics`

Shared metric names, instrument slots, and the lock-wait helper (feat-139 Phase 5, Tasks 5.2-5.5).

This module is the single, import-safe home for everything about this
feature's OTel metrics that the *base library* may need:

- the MCP-specific metric *names* (the Design Notes' "Metric/span naming
  scheme" bullet: ``mcp.tool.duration``, ``mcp.tool.call.count``,
  ``mcp.tool.error.count``, ``mcp.cache.hit``/``mcp.cache.miss``,
  ``mcp.lock.wait_time``), the attribute *keys* (``mcp.tool.name``,
  ``mcp.domain``, ``mcp.item.type``, ``error.type``), the ``ms`` unit, and
  the pinned explicit histogram bucket boundaries ("OTel bootstrap pins"
  bullet);
- the module-level *instrument slots* the ``telemetry/otel.py`` bootstrap
  fills: the ``Meter`` (for the middleware's lazily created tool metrics)
  and the ``mcp.lock.wait_time`` histogram (for :func:`record_lock_wait`),
  both ``None`` while telemetry is disabled;
- :func:`record_lock_wait`, the one shared timing helper every domain's
  ``<domain>/tools/_lock.py`` context manager calls to record its lock's
  acquire wait time ("Domain-lock wait time" bullet);
- the two observable-counter callbacks (``mcp.cache.hit``/``mcp.cache.
  miss``) the bootstrap registers at instrument creation (Task 5.4, coded
  against Task 1a.5's confirmed SDK 1.44.0 observable-instrument API:
  callbacks are registered at creation time, invoked only at
  collection/export time, and must return an iterable of
  ``Observation``).

**Import safety (the orchestrator's Phase 5 pins):** this module is
base-library-safe -- it imports nothing from ``opentelemetry.*`` at module
level (``from __future__ import annotations`` keeps every annotation a
string, and the slot values are typed ``object``), so the thirteen
``<domain>/tools/_lock.py`` modules -- which must stay pure-stdlib plus
this one import -- can call :func:`record_lock_wait` without pulling the
``mcp``/OpenTelemetry extras onto the base library. It also imports
nothing from ``general/`` or any domain package at module level: the
callbacks' access to the ``DocCache`` registry in ``general/tools/
_doc_cache.py`` is a *lazy import inside the callback body* (the callbacks
run at metric collection time -- per Task 1a.5, never at registration --
by which point ``server.py`` has finished importing the domain packages;
a module-level import here would break ``server.py``'s own import order,
which imports ``telemetry/*`` before its final-line domain imports).

**Fail-open (`.specmgr/conventions.md`, "Observability Degrades
Gracefully, Application Logic Never Does"):** while a slot is ``None``
(the default) every function here is a pure no-op that allocates nothing;
a recording failure once a slot is set never propagates to the caller --
:func:`record_lock_wait` in particular must never raise, because its
callers run inside the lock's acquire/release control flow, where a
propagated exception would leak the acquired lock. The first such failure
logs one warning; later failures are silent.

## Functions

### `_cache_observations(stats_key: 'str') -> 'list[object]'`

Build one collection cycle's ``Observation`` list for one cache instrument.

Iterates the ``general/tools/_doc_cache.py`` registry of live,
domain-named ``DocCache`` instances and yields one ``Observation`` per
live entry (Task 1a.5's confirmed requirement: a series the callback
does not yield is absent from that collection, so every entry must be
yielded every cycle, even at an unchanged cumulative value). The
registry import is lazy -- see the module docstring's import-safety
note -- and the iteration is defensive: a raising registry entry is
skipped (a raising *callback* would make the SDK log ``Callback
failed for instrument ...`` and drop the instrument's entire
collection cycle).

Args:
    stats_key: The ``DocCache.stats()`` key to read (``"hits"`` or
        ``"misses"``).

Returns:
    One ``Observation`` per live registry entry (empty when the
    registry is empty or the imports are unavailable).


### `cache_hit_callback(options: 'object') -> 'list[object]'`

The ``mcp.cache.hit`` observable counter's callback (registered at creation, Task 5.4).

Invoked by the SDK at collection/export time (never at registration);
``options`` is the SDK's ``CallbackOptions`` (typed ``object`` -- this
module must not import ``opentelemetry.*`` at module level).

Args:
    options: The SDK's collection options (unused).

Returns:
    One ``Observation`` per live registry entry, carrying the
    cumulative hit count and the ``mcp.domain`` attribute.


### `cache_miss_callback(options: 'object') -> 'list[object]'`

The ``mcp.cache.miss`` observable counter's callback (registered at creation, Task 5.4).

Invoked by the SDK at collection/export time (never at registration);
``options`` is the SDK's ``CallbackOptions`` (typed ``object`` -- this
module must not import ``opentelemetry.*`` at module level).

Args:
    options: The SDK's collection options (unused).

Returns:
    One ``Observation`` per live registry entry, carrying the
    cumulative miss count and the ``mcp.domain`` attribute.


### `clear_instrument_slots() -> 'None'`

Clear every instrument slot back to its ``None`` no-op state.

Called by ``telemetry/otel.py``'s ``shutdown_telemetry`` so a
re-bootstrap (tests) or a process with telemetry disabled starts from
a clean slate.

Returns:
    ``None``.


### `meter_slot() -> 'object | None'`

Return the module-level ``Meter`` slot (``None`` while unset).

Returns:
    The ``Meter`` the bootstrap stored, or ``None`` (telemetry
    disabled, or after shutdown).


### `record_lock_wait(domain: 'str', duration_ms: 'float') -> 'None'`

Record one domain-lock acquire wait time (Task 5.5's shared helper).

Called by every domain's ``<domain>/tools/_lock.py`` context manager
immediately after the per-id (or, for ``feat``'s ``feat_create_lock``,
the global) lock's ``acquire()`` returns: ``duration_ms`` is the
acquire wait only (not the hold time the old ``with lock:`` shape
would have measured), in the histogram's ``ms`` unit. While the slot
is ``None`` (telemetry disabled) this is a pure no-op that allocates
nothing.

This function never raises: its callers run inside the lock's
acquire/release control flow, where a propagated exception would leak
the just-acquired lock. A recording failure disables lock-wait
recording for the rest of the process and logs exactly one warning
(the fail-open convention).

Args:
    domain: The document domain the lock belongs to (the
        ``mcp.domain`` attribute value; the one-word domain name, e.g.
        ``"req"``).
    duration_ms: The measured acquire wait in milliseconds (>= 0).


### `set_lock_wait_histogram(histogram: 'object') -> 'None'`

Store the bootstrap's ``mcp.lock.wait_time`` histogram in the module-level slot.

Args:
    histogram: The ``opentelemetry.metrics.Histogram`` (typed
        ``object`` -- see the module docstring for why).


### `set_meter(meter: 'object') -> 'None'`

Store the bootstrap's ``Meter`` in the module-level slot.

Called once by ``telemetry/otel.py``'s ``bootstrap_telemetry`` (Task
4.1's meter-slot pin, now shared with the middleware's lazy
instrument creation).

Args:
    meter: The ``opentelemetry.metrics.Meter`` (typed ``object`` --
        this module must not import ``opentelemetry.*`` at module
        level, see the module docstring).

