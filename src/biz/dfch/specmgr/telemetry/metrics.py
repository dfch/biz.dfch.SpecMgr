# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Shared metric names, instrument slots, and the lock-wait helper (feat-139 Phase 5, Tasks 5.2-5.5).

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
"""

from __future__ import annotations

import logging

# ---------------------------------------------------------------------------
# Metric names (the Design Notes' "Metric/span naming scheme" bullet)
# ---------------------------------------------------------------------------

#: The observed-invocation latency histogram (unit ``ms``).
MCP_TOOL_DURATION = "mcp.tool.duration"
#: The observed-invocation counter (one increment per invocation, whatever its outcome).
MCP_TOOL_CALL_COUNT = "mcp.tool.call.count"
#: The failed-invocation counter (attributed by ``error.type``).
MCP_TOOL_ERROR_COUNT = "mcp.tool.error.count"
#: The doc-cache hit observable counter (one series per registered domain).
MCP_CACHE_HIT = "mcp.cache.hit"
#: The doc-cache miss observable counter (one series per registered domain).
MCP_CACHE_MISS = "mcp.cache.miss"
#: The domain-lock acquire wait-time histogram (unit ``ms``).
MCP_LOCK_WAIT = "mcp.lock.wait_time"

# ---------------------------------------------------------------------------
# Attribute keys (the naming-scheme bullet plus the orchestrator's pin for
# ``error.type``)
# ---------------------------------------------------------------------------

#: The attribute carrying the invoked item's identity (tool/prompt ``name``, resource ``uri``).
ATTR_TOOL_NAME = "mcp.tool.name"
#: The attribute carrying the item's document domain (omitted, never empty, when there is none).
ATTR_DOMAIN = "mcp.domain"
#: The attribute carrying the item type (``tool``/``resource``/``prompt``).
ATTR_ITEM_TYPE = "mcp.item.type"
#: The attribute carrying the per-channel error-type signal (the OTel semconv key the SDK's own middleware uses).
ATTR_ERROR_TYPE = "error.type"

#: The unit every one of this feature's histogram instruments is created with.
UNIT_MS = "ms"

# ---------------------------------------------------------------------------
# Pinned explicit histogram bucket boundaries (the Design Notes' "OTel
# bootstrap pins" bullet)
# ---------------------------------------------------------------------------

#: The ``mcp.tool.duration`` histogram's bucket boundaries (``ms``).
TOOL_DURATION_BUCKET_BOUNDS = (5.0, 10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 2500.0, 5000.0, 10000.0)
#: The ``mcp.lock.wait_time`` histogram's bucket boundaries (``ms``).
LOCK_WAIT_BUCKET_BOUNDS = (1.0, 5.0, 10.0, 25.0, 50.0, 100.0, 250.0, 500.0)

# ---------------------------------------------------------------------------
# DocCache ``stats()`` keys (``general/tools/_doc_cache.py``'s pinned shape)
# ---------------------------------------------------------------------------

#: The ``stats()`` mapping's hit-counter key.
STATS_KEY_HITS = "hits"
#: The ``stats()`` mapping's miss-counter key.
STATS_KEY_MISSES = "misses"

#: The logger the fail-open warnings go to (the feature's own logger).
logger = logging.getLogger("biz.dfch.specmgr.telemetry")

#: The single warning emitted when lock-wait recording fails (fail-open).
_LOCK_WAIT_FAILURE_MESSAGE = (
    "recording the domain-lock wait time to the mcp.lock.wait_time histogram failed; "
    "lock-wait recording is disabled for the rest of this process (one message per episode)"
)

# ---------------------------------------------------------------------------
# Module-level instrument slots (set by the telemetry/otel.py bootstrap,
# cleared by its shutdown; ``None`` while telemetry is disabled)
# ---------------------------------------------------------------------------

#: The ``Meter`` the middleware lazily creates its own instruments from;
#: ``None`` until the bootstrap runs (or after ``shutdown_telemetry``).
_meter: object | None = None
#: The ``mcp.lock.wait_time`` histogram :func:`record_lock_wait` records to;
#: ``None`` until the bootstrap runs (or after ``shutdown_telemetry``).
_lock_wait_histogram: object | None = None
#: Whether the one fail-open warning for :func:`record_lock_wait` has been
#: emitted already (one message per episode, never repeating).
_lock_wait_failure_warned = False


def set_meter(meter: object) -> None:
    """Store the bootstrap's ``Meter`` in the module-level slot.

    Called once by ``telemetry/otel.py``'s ``bootstrap_telemetry`` (Task
    4.1's meter-slot pin, now shared with the middleware's lazy
    instrument creation).

    Args:
        meter: The ``opentelemetry.metrics.Meter`` (typed ``object`` --
            this module must not import ``opentelemetry.*`` at module
            level, see the module docstring).
    """
    global _meter
    assert meter is not None, "a set slot must hold a live meter"
    _meter = meter


def meter_slot() -> object | None:
    """Return the module-level ``Meter`` slot (``None`` while unset).

    Returns:
        The ``Meter`` the bootstrap stored, or ``None`` (telemetry
        disabled, or after shutdown).
    """
    result = _meter
    return result


def set_lock_wait_histogram(histogram: object) -> None:
    """Store the bootstrap's ``mcp.lock.wait_time`` histogram in the module-level slot.

    Args:
        histogram: The ``opentelemetry.metrics.Histogram`` (typed
            ``object`` -- see the module docstring for why).
    """
    global _lock_wait_histogram
    assert histogram is not None, "a set slot must hold a live histogram"
    _lock_wait_histogram = histogram


def clear_instrument_slots() -> None:
    """Clear every instrument slot back to its ``None`` no-op state.

    Called by ``telemetry/otel.py``'s ``shutdown_telemetry`` so a
    re-bootstrap (tests) or a process with telemetry disabled starts from
    a clean slate.

    Returns:
        ``None``.
    """
    global _meter, _lock_wait_histogram, _lock_wait_failure_warned
    _meter = None
    _lock_wait_histogram = None
    _lock_wait_failure_warned = False


def record_lock_wait(domain: str, duration_ms: float) -> None:
    """Record one domain-lock acquire wait time (Task 5.5's shared helper).

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
    """
    global _lock_wait_failure_warned
    assert isinstance(domain, str) and domain, domain
    assert isinstance(duration_ms, (int, float)) and duration_ms >= 0, duration_ms
    histogram = _lock_wait_histogram
    if histogram is None:
        return
    try:
        histogram.record(float(duration_ms), {ATTR_DOMAIN: domain})
    except Exception as exc:
        if not _lock_wait_failure_warned:
            _lock_wait_failure_warned = True
            logger.warning(_LOCK_WAIT_FAILURE_MESSAGE + " (%s: %s)", type(exc).__qualname__, exc)


def _cache_observations(stats_key: str) -> list[object]:
    """Build one collection cycle's ``Observation`` list for one cache instrument.

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
    """
    try:
        from opentelemetry.metrics import Observation

        from ..general.tools._doc_cache import DOC_CACHE_REGISTRY
    except Exception:
        result: list[object] = []
        return result
    result = []
    for domain, cache in list(DOC_CACHE_REGISTRY.items()):
        try:
            stats = cache.stats()
            value = stats[stats_key]
        except Exception:
            continue
        result.append(Observation(value, {ATTR_DOMAIN: domain}))
    return result


def cache_hit_callback(options: object) -> list[object]:
    """The ``mcp.cache.hit`` observable counter's callback (registered at creation, Task 5.4).

    Invoked by the SDK at collection/export time (never at registration);
    ``options`` is the SDK's ``CallbackOptions`` (typed ``object`` -- this
    module must not import ``opentelemetry.*`` at module level).

    Args:
        options: The SDK's collection options (unused).

    Returns:
        One ``Observation`` per live registry entry, carrying the
        cumulative hit count and the ``mcp.domain`` attribute.
    """
    result = _cache_observations(STATS_KEY_HITS)
    return result


def cache_miss_callback(options: object) -> list[object]:
    """The ``mcp.cache.miss`` observable counter's callback (registered at creation, Task 5.4).

    Invoked by the SDK at collection/export time (never at registration);
    ``options`` is the SDK's ``CallbackOptions`` (typed ``object`` -- this
    module must not import ``opentelemetry.*`` at module level).

    Args:
        options: The SDK's collection options (unused).

    Returns:
        One ``Observation`` per live registry entry, carrying the
        cumulative miss count and the ``mcp.domain`` attribute.
    """
    result = _cache_observations(STATS_KEY_MISSES)
    return result
