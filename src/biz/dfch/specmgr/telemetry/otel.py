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

"""OpenTelemetry SDK bootstrap (feat-139-logging-telemetry, Phase 4, Task 4.1).

``telemetry/config.py`` parses the ``SPECMGR_LOG_*``/``SPECMGR_OTEL_*``
environment into a validated :class:`~biz.dfch.specmgr.telemetry.config.
TelemetryConfig`; this module applies that config's telemetry half to the
process: :func:`bootstrap_telemetry` configures the OpenTelemetry SDK's
``TracerProvider``/``MeterProvider`` plus the ``SPECMGR_OTEL_EXPORTER``
selected exporter (``console``/``otlp``), but only when
``SPECMGR_OTEL_ENABLED=true`` -- the default config sets nothing, so the
SDK's built-in ``OpenTelemetryMiddleware`` keeps creating inert
non-recording spans through the API's no-provider proxy (ACC-001).

Activating the providers is all this feature does for tracing: no new span
is created by this feature's own code (the Design Notes' "Redaction scope
and limits" bullet) -- the SDK's already-present, built-in
``OpenTelemetryMiddleware`` (outermost in the middleware chain) starts
recording its request spans into the provider this bootstrap installs,
because ``mcp/shared/_otel.py``'s tracer is fetched at ``mcp`` import time
and the OTel API's proxy resolution makes a tracer fetched before
``set_tracer_provider`` record into the provider configured later (Task
4.2 confirms the span-ID branch of the correlation-ID helper engages
end to end under that real import order).

Bootstrap pins (the Design Notes' "OTel bootstrap pins" bullet, plus
Task 1a.2/1a.4's confirmed spike findings):

- the ``TracerProvider`` uses a :class:`BatchSpanProcessor`, not a
  ``SimpleSpanProcessor`` -- with a simple processor, an unreachable OTLP
  endpoint would block each span's ``end()`` synchronously for the
  exporter's timeout, stalling every tool call; the batch path's
  background failure is what :class:`OtlpExporterWrapper` de-duplicates.
- the ``TracerProvider`` also carries the Task 6.1/6.2
  :class:`~biz.dfch.specmgr.telemetry.redact.RedactionSpanProcessor`,
  added *before* the ``BatchSpanProcessor`` (the provider invokes
  ``on_end`` on its processors in add order, so the scrub of every
  ended span's attributes/exception events runs before the span reaches
  the export path -- covering the SDK's own built-in
  ``OpenTelemetryMiddleware``'s spans, ACC-012).
- the ``console`` exporter (the default ``SPECMGR_OTEL_EXPORTER`` value)
  is constructed with its output stream explicitly redirected to stderr --
  ``ConsoleSpanExporter(out=sys.stderr)`` / ``ConsoleMetricExporter(
  out=sys.stderr)``, ``out=`` passed by keyword (``ConsoleSpanExporter``'s
  first positional arg is ``service_name``). Both default to stdout, and
  mcp 2.0.0's stdio transport diverts fd 1 to stderr only *while
  serving*, so default-stream exports after serving ends (e.g. the
  ``PeriodicExportingMetricReader``'s final collection at
  ``MeterProvider.shutdown()``) would reach the real stdout -- required
  for ACC-001/ACC-003 to hold.
- the ``MeterProvider`` uses a :class:`PeriodicExportingMetricReader`
  (default 60 s interval).
- both providers are built with a :class:`Resource` carrying a fixed
  ``service.name = "specmgr"`` attribute (no env var override), so
  exported spans/metrics are identifiable at a shared OTLP
  collector/backend.
- the ``otlp`` exporter is the OTLP/HTTP+protobuf one (Task 1a.1's
  decision), constructed with the ``SPECMGR_OTEL_ENDPOINT`` base URL
  extended by the spec-mandated ``/v1/traces`` / ``/v1/metrics`` paths --
  the installed SDK only appends those paths to its own
  ``OTEL_EXPORTER_OTLP_ENDPOINT`` env-var fallback, not to an explicit
  ``endpoint=`` argument (verified against the 1.44.0 source; the
  ``endpoint=`` value is POSTed as-is), so the bootstrap appends them.
- the Phase 3/Phase 5 division of labor for counters, as Phase 5 landed
  it (the orchestrator's instrument-creation pin): the ``Meter`` is
  fetched once, via the global API, into the module-level
  :data:`_meter` slot (``None`` when telemetry is disabled) *and* the
  ``telemetry/metrics.py`` slot the middleware and the ``_lock.py``
  helpers read; this bootstrap creates the ``mcp.lock.wait_time``
  histogram (with the ``telemetry/metrics.py`` slot set to it) and the
  ``mcp.cache.hit``/``mcp.cache.miss`` observable counters (callbacks
  registered at instrument creation), and builds the ``MeterProvider``
  with the pinned explicit-bucket Views for ``mcp.tool.duration``/
  ``mcp.lock.wait_time`` (registered before any instrument is created);
  the middleware's own ``mcp.tool.duration``/``mcp.tool.call.count``/
  ``mcp.tool.error.count`` instruments are created lazily by the
  middleware on first observation from that same slot (a no-op path that
  allocates nothing while the slot is ``None``).
- :func:`shutdown_telemetry` shuts both providers down -- ``server.py``'s
  ``_lifespan`` post-``yield`` section calls it at process exit, which is
  where the ``MeterProvider``'s final metric collection and the
  ``BatchSpanProcessor``'s final span flush land on the real stderr (the
  stdio transport has already restored fd 1 by then).

Task 4.5 (graceful OTLP-unreachable degradation): an installed SDK's
OTLP HTTP exporters log 3x WARNING + 1x ERROR per failed export cycle, on
every cycle, under their own module loggers, and return ``FAILURE``
without raising (Task 1a.4's confirmed finding) -- so a bare
``logging.Filter`` cannot meet "at most one message per failure episode".
:class:`OtlpExporterWrapper` is the thin wrapper that tracks
first-failure/recovery transitions itself: an episode runs from the first
``FAILURE`` return until the first ``SUCCESS`` or ``shutdown``; exactly
one warning (via this feature's own ``biz.dfch.specmgr.telemetry``
logger) is emitted at the first ``FAILURE`` return of an episode and a
further single one at the start of any subsequent episode; a
state-gated ``logging.Filter`` on exactly the two exporters' own logger
names is armed at the start of every ``export()`` attempt (the SDK logs
its per-attempt failure lines *during* the attempt, before the first
``FAILURE`` return) and disarmed on a ``SUCCESS`` return or ``shutdown``,
so across a whole failure episode the only failure-attributable stderr
output is the single wrapper message. The wrapper is applied to both OTLP
exporters (two instances); the console exporter needs no wrapper.

Like ``telemetry/logging.py`` and ``telemetry/middleware.py``, this module
imports ``opentelemetry.*`` and is only imported from ``server.py`` (which
already requires the ``mcp`` extra) and its tests -- it is not
base-library-safe.
"""

from __future__ import annotations

import logging
import sys
import threading
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.metrics import Histogram, Meter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    MetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.metrics.view import ExplicitBucketHistogramAggregation, View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SpanExporter

from . import metrics as telemetry_metrics
from .config import TelemetryConfig
from .redact import RedactionSpanProcessor

#: The logger this module emits its single fail-open/episode warnings on
#: (the same ``biz.dfch.specmgr.telemetry`` logger the middleware uses).
logger = logging.getLogger("biz.dfch.specmgr.telemetry")

# ---------------------------------------------------------------------------
# Bootstrap constants (comparison values per the repo convention)
# ---------------------------------------------------------------------------

#: The fixed ``service.name`` resource attribute (no env var override; a
#: fixed value is sufficient to identify specmgr's telemetry at a shared
#: OTLP collector/backend).
SERVICE_NAME = "specmgr"
#: The resource-attribute key carrying :data:`SERVICE_NAME`.
_SERVICE_NAME_KEY = "service.name"
#: The ``Meter`` name fetched once at bootstrap into :data:`_meter`.
_METER_NAME = "specmgr"

#: The ``SPECMGR_OTEL_EXPORTER`` value selecting the console exporters.
_EXPORTER_CONSOLE = "console"
#: The ``SPECMGR_OTEL_EXPORTER`` value selecting the OTLP/HTTP exporters.
_EXPORTER_OTLP = "otlp"

#: The spec-mandated OTLP export path the traces endpoint is extended with.
_OTLP_TRACES_PATH = "v1/traces"
#: The spec-mandated OTLP export path the metrics endpoint is extended with.
_OTLP_METRICS_PATH = "v1/metrics"

#: The OTLP/HTTP span exporter's own module logger (Task 1a.4's confirmed
#: name for the per-cycle failure logging).
OTLP_TRACE_EXPORTER_LOGGER_NAME = "opentelemetry.exporter.otlp.proto.http.trace_exporter"
#: The OTLP/HTTP metric exporter's own module logger (Task 1a.4's confirmed
#: name for the per-cycle failure logging).
OTLP_METRIC_EXPORTER_LOGGER_NAME = "opentelemetry.exporter.otlp.proto.http.metric_exporter"
#: The exactly two exporter logger names the Task 4.5 state-gated
#: suppression filter is attached to.
_OTLP_EXPORTER_LOGGER_NAMES = (OTLP_TRACE_EXPORTER_LOGGER_NAME, OTLP_METRIC_EXPORTER_LOGGER_NAME)

#: The export-result enum member name for a successful export (both the
#: span and the metric result enums use the same member names).
_RESULT_SUCCESS_NAME = "SUCCESS"
#: The export-result enum member name for a failed export.
_RESULT_FAILURE_NAME = "FAILURE"

#: The single stderr message emitted at the start of each OTLP span-export
#: failure episode (Task 4.5 / ACC-010): names the condition, states that
#: it repeats only for a subsequent episode.
_SPAN_EXPORT_FAILURE_MESSAGE = (
    "OTLP span export is failing (the configured endpoint is unreachable or not accepting "
    "exports); spans will not reach the collector until export recovers -- this message "
    "repeats only for a subsequent failure episode"
)
#: The single stderr message emitted at the start of each OTLP metric-export
#: failure episode (Task 4.5 / ACC-010).
_METRIC_EXPORT_FAILURE_MESSAGE = (
    "OTLP metric export is failing (the configured endpoint is unreachable or not accepting "
    "exports); metrics will not reach the collector until export recovers -- this message "
    "repeats only for a subsequent failure episode"
)


# ---------------------------------------------------------------------------
# Task 4.5: the OTLP-exporter de-duplication wrapper
# ---------------------------------------------------------------------------


class _ExporterEpisodeFilter(logging.Filter):
    """The state-gated filter suppressing an OTLP exporter's own failure noise.

    Attached (by :class:`OtlpExporterWrapper`) to exactly the two
    exporters' own logger names for the duration of each export attempt
    (armed at the attempt's start, disarmed on a ``SUCCESS`` return or
    ``shutdown``), it drops every record those loggers emit while the
    wrapper's armed state is ``True`` -- the SDK never logs a successful
    export, so only the per-attempt 3x WARNING + 1x ERROR noise (Task
    1a.4) can be affected. The armed window deliberately starts *before*
    the first ``FAILURE`` return, because the SDK logs its per-attempt
    lines during the attempt itself; gating on the (later) failing state
    would leak the first cycle's raw lines (the Phase 4 re-evaluation's
    reproduced ACC-010 violation).
    """

    def __init__(self, wrapper: OtlpExporterWrapper) -> None:
        """Build the filter for the wrapper whose state gates it.

        Args:
            wrapper: The wrapper instance; the filter suppresses while
                ``wrapper.armed`` is ``True``.
        """
        super().__init__()
        self._wrapper = wrapper

    def filter(self, record: logging.LogRecord) -> bool:
        """Pass the record only when the wrapper has not armed the suppression.

        Args:
            record: The record the owning exporter logger is about to emit.

        Returns:
            ``False`` (suppressed) while the wrapper is armed (an export
            attempt is in progress or a failure episode is active),
            ``True`` otherwise.
        """
        result = not self._wrapper.armed
        return result


class OtlpExporterWrapper(SpanExporter, MetricExporter):
    """A thin wrapper around one OTLP exporter de-duplicating its failure noise (Task 4.5).

    One shared class applied to both the OTLP span and the OTLP metric
    exporter (two instances). The installed SDK's OTLP HTTP exporters
    return ``FAILURE`` without raising and log 3x WARNING + 1x ERROR per
    failed export cycle, on every cycle, under their own module loggers --
    with no success ever logged, recovery is not observable from the log
    stream, so the wrapper tracks the transitions itself:

    - an *episode* runs from the first ``FAILURE`` return until the first
      ``SUCCESS`` return or :meth:`shutdown`;
    - exactly one warning (via this feature's own ``biz.dfch.specmgr.
      telemetry`` logger, the wrapper's own ``episode_message``) is
      emitted at the first ``FAILURE`` return of an episode, and a
      further single one at the start of any subsequent episode -- never
      repeating while the condition persists (ACC-010);
    - a state-gated :class:`_ExporterEpisodeFilter` on exactly the two
      exporters' own logger names is *armed at the start of every
      ``export()`` attempt* (before delegating to the wrapped exporter)
      and disarmed on a ``SUCCESS`` return or :meth:`shutdown` -- the SDK
      logs its per-attempt failure lines during the attempt, i.e. before
      the first ``FAILURE`` return, so arming only on that return would
      leak the first cycle's raw lines; while armed the filter suppresses
      the SDK's per-attempt noise, so the only failure-attributable
      stderr output across a whole episode is the single wrapper message.

    The wrapper passes ``export()``'s result, and the
    ``force_flush()``/``shutdown()`` signatures, through to the wrapped
    exporter unchanged, so the ``BatchSpanProcessor``/
    ``PeriodicExportingMetricReader`` keep working unmodified. It
    subclasses both SDK exporter base classes (``SpanExporter``/
    ``MetricExporter``) so it inherits their internal surface: the
    installed 1.44.0 ``PeriodicExportingMetricReader.__init__`` reads
    ``exporter._preferred_temporality``/``exporter._preferred_aggregation``
    off the exporter instance (set by ``MetricExporter.__init__``, which
    this wrapper calls with the wrapped exporter's own values), and a
    plain delegating object without those attributes crashes the
    bootstrap with an ``AttributeError``. ``__getattr__`` additionally
    falls back to the wrapped exporter for any attribute the wrapper does
    not define itself, so a future SDK-internal read of an exporter
    attribute keeps working. All state transitions are serialized by one
    lock: the span and metric exporter run on the SDK's own background
    threads.

    Attributes:
        exporter: The wrapped OTLP exporter (read-only inspection seam).
    """

    def __init__(self, exporter: SpanExporter | MetricExporter, *, episode_message: str) -> None:
        """Wrap one configured OTLP exporter.

        Args:
            exporter: The OTLP span or metric exporter to wrap.
            episode_message: The single warning emitted at each failure
                episode's start (names the span/metric condition).
        """
        assert isinstance(exporter, (SpanExporter, MetricExporter)), type(exporter)
        assert episode_message.strip(), episode_message
        # Inherit the SDK base classes' internal state (see the class
        # docstring): ``MetricExporter.__init__`` sets the
        # ``_preferred_temporality``/``_preferred_aggregation`` attributes
        # the ``PeriodicExportingMetricReader`` reads off the exporter
        # instance; copy them from the wrapped exporter (``None`` for a
        # span exporter, which carries no such attributes).
        MetricExporter.__init__(
            self,
            preferred_temporality=getattr(exporter, "_preferred_temporality", None),
            preferred_aggregation=getattr(exporter, "_preferred_aggregation", None),
        )
        self._exporter = exporter
        self._episode_message = episode_message
        self._lock = threading.Lock()
        self._failing = False
        self._filter_attached = False
        self._shutdown_done = False
        self._filter = _ExporterEpisodeFilter(self)

    def __getattr__(self, name: str) -> Any:
        """Fall back to the wrapped exporter for attributes this wrapper does not define.

        Only invoked for names the normal lookup missed (never for
        dunder/implicit-lookup names), so the wrapper's own state and
        pass-through methods always win; an attribute the wrapped exporter
        also lacks raises ``AttributeError`` as usual.

        Args:
            name: The missing attribute's name.

        Returns:
            The wrapped exporter's attribute of that name.
        """
        result = getattr(object.__getattribute__(self, "_exporter"), name)
        return result

    @property
    def exporter(self) -> SpanExporter | MetricExporter:
        """The wrapped OTLP exporter."""
        result = self._exporter
        return result

    @property
    def failing(self) -> bool:
        """Whether a failure episode is currently in progress."""
        with self._lock:
            result = self._failing
        return result

    @property
    def armed(self) -> bool:
        """Whether the suppression filter is currently attached (armed).

        Armed at the start of every ``export()`` attempt, disarmed on a
        ``SUCCESS`` return or :meth:`shutdown` -- see the class docstring
        for why the window starts before the first ``FAILURE`` return.
        """
        with self._lock:
            result = self._filter_attached
        return result

    def export(self, *args: Any, **kwargs: Any) -> Any:
        """Export one batch, tracking the armed/failing state around the attempt.

        Arms the suppression filter *before* delegating to the wrapped
        exporter (the SDK logs its per-attempt failure lines during the
        attempt, before any result is returned), then updates the episode
        state from the return value: a ``FAILURE``-named result starts (or
        continues) a failure episode -- exactly one warning on the first
        failure of the episode -- and a ``SUCCESS``-named result ends the
        episode (no message) and disarms the filter. All arguments and the
        wrapped exporter's return value pass through unchanged. After
        :meth:`shutdown`, ``export()`` is a pure pass-through (no arming,
        no episode, no message).

        Args:
            *args: The wrapped exporter's positional ``export`` arguments
                (the span batch, or the ``MetricsData``).
            **kwargs: The wrapped exporter's keyword ``export`` arguments
                (e.g. ``timeout_millis`` for the metric exporter).

        Returns:
            The wrapped exporter's export result, unmodified.
        """
        with self._lock:
            active = not self._shutdown_done
        if active:
            self._arm()
        result = self._exporter.export(*args, **kwargs)
        if active:
            result_name = getattr(result, "name", None)
            if result_name == _RESULT_FAILURE_NAME and self._on_failure_return():
                logger.warning(self._episode_message)
            elif result_name == _RESULT_SUCCESS_NAME:
                self._on_success_return()
        return result

    def force_flush(self, *args: Any, **kwargs: Any) -> bool:
        """Pass ``force_flush`` through to the wrapped exporter unchanged.

        Args:
            *args: The wrapped exporter's positional ``force_flush`` arguments.
            **kwargs: The wrapped exporter's keyword ``force_flush`` arguments.

        Returns:
            The wrapped exporter's return value.
        """
        result = self._exporter.force_flush(*args, **kwargs)
        return result

    def shutdown(self, *args: Any, **kwargs: Any) -> None:
        """End any in-progress episode, then pass ``shutdown`` through unchanged.

        The episode ends at provider shutdown (the pin): the suppression
        filter is detached, and a ``FAILURE`` return from a later
        ``export()`` call (e.g. the processor's final flush racing the
        shutdown) starts no new episode and emits no message.

        Args:
            *args: The wrapped exporter's positional ``shutdown`` arguments.
            **kwargs: The wrapped exporter's keyword ``shutdown`` arguments.
        """
        with self._lock:
            self._shutdown_done = True
            self._failing = False
            if self._filter_attached:
                self._detach_filter_locked()
        self._exporter.shutdown(*args, **kwargs)

    def _arm(self) -> None:
        """Attach the suppression filter (idempotent) at an export attempt's start.

        Called from :meth:`export` before delegating to the wrapped
        exporter, so the SDK's own per-attempt failure lines -- logged
        during the attempt, before any result is returned -- are
        suppressed from the very first cycle of an episode.

        Called with no lock held; takes :attr:`_lock` itself.
        """
        with self._lock:
            if not self._filter_attached:
                self._attach_filter_locked()

    def _on_failure_return(self) -> bool:
        """Mark a ``FAILURE`` return: start a new episode when this is the first one.

        The filter is already attached (armed at the attempt's start) and
        stays attached for the rest of the episode. Returns ``True`` only
        when this failure started a new episode (the caller then emits the
        single warning); a no-op -- returning ``False`` -- when the
        episode is already in progress (never repeating while the
        condition persists) or the wrapper is shut down.

        Called with no lock held; takes :attr:`_lock` itself.
        """
        with self._lock:
            if self._shutdown_done or self._failing:
                result = False
                return result
            self._failing = True
            if not self._filter_attached:  # defensive: export() arms first
                self._attach_filter_locked()
            result = True
        return result

    def _on_success_return(self) -> None:
        """Mark a ``SUCCESS`` return: end the episode (no message) and disarm.

        Recovery emits no message (the pin: exactly one message at each
        episode's *start*). Disarming detaches the filter so a future
        episode starts fresh with its own single message.

        Called with no lock held; takes :attr:`_lock` itself.
        """
        with self._lock:
            self._failing = False
            if self._filter_attached:
                self._detach_filter_locked()

    def _attach_filter_locked(self) -> None:
        """Attach the state-gated filter to exactly the two exporter loggers.

        Must be called with :attr:`_lock` held.
        """
        for name in _OTLP_EXPORTER_LOGGER_NAMES:
            logging.getLogger(name).addFilter(self._filter)
        self._filter_attached = True

    def _detach_filter_locked(self) -> None:
        """Detach the state-gated filter from the two exporter loggers.

        Must be called with :attr:`_lock` held.
        """
        for name in _OTLP_EXPORTER_LOGGER_NAMES:
            logging.getLogger(name).removeFilter(self._filter)
        self._filter_attached = False


# ---------------------------------------------------------------------------
# Module-level bootstrap state
# ---------------------------------------------------------------------------

#: The ``TracerProvider`` :func:`bootstrap_telemetry` installed, or
#: ``None`` when telemetry is disabled (or after :func:`shutdown_telemetry`).
_tracer_provider: TracerProvider | None = None
#: The ``MeterProvider`` :func:`bootstrap_telemetry` installed, or ``None``.
_meter_provider: MeterProvider | None = None
#: The ``Meter`` fetched once at bootstrap (via the global API) for Phase 5's
#: increments; ``None`` when telemetry is disabled (slot-guarded no-op
#: semantics there) or after :func:`shutdown_telemetry`.
_meter: Meter | None = None
#: Serializes the bootstrap/shutdown state transitions (module scope and the
#: ``_lifespan`` shutdown run on different threads in tests).
_bootstrap_lock = threading.Lock()


def _with_otlp_path(base_url: str, export_path: str) -> str:
    """Extend an OTLP base URL with the spec-mandated export path.

    The installed SDK appends ``/v1/traces``/``/v1/metrics`` only to its
    own ``OTEL_EXPORTER_OTLP_ENDPOINT`` env-var fallback, not to an explicit
    ``endpoint=`` constructor argument (which is POSTed as-is), so the
    bootstrap extends ``SPECMGR_OTEL_ENDPOINT`` (documented as a base URL)
    itself -- with the SDK's own trailing-slash semantics.

    Args:
        base_url: The ``SPECMGR_OTEL_ENDPOINT`` base URL (non-blank,
            guaranteed by the config's pairing rule).
        export_path: The path to append (``v1/traces``/``v1/metrics``).

    Returns:
        The complete endpoint URL.
    """
    assert base_url.strip(), base_url
    if base_url.endswith("/"):
        result = base_url + export_path
        return result
    result = base_url + f"/{export_path}"
    return result


def _build_span_exporter(config: TelemetryConfig) -> SpanExporter:
    """Build the configured span exporter (console raw, OTLP wrapped).

    The console exporter (the default) is constructed with its output
    stream explicitly redirected to stderr -- ``out=`` by keyword, since
    ``ConsoleSpanExporter``'s first positional arg is ``service_name``
    (Task 1a.2's confirmed finding). The OTLP exporter is wrapped in the
    Task 4.5 :class:`OtlpExporterWrapper`.

    Args:
        config: The parsed, validated telemetry configuration.

    Returns:
        The span exporter to hand to the ``BatchSpanProcessor``.
    """
    if config.otel_exporter == _EXPORTER_CONSOLE:
        result: SpanExporter = ConsoleSpanExporter(out=sys.stderr)
        return result
    assert config.otel_exporter == _EXPORTER_OTLP, config.otel_exporter
    assert config.otel_endpoint is not None, "config validation guarantees an endpoint with the otlp exporter"
    exporter = OTLPSpanExporter(endpoint=_with_otlp_path(config.otel_endpoint, _OTLP_TRACES_PATH))
    result = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)
    return result


def _build_metric_exporter(config: TelemetryConfig) -> MetricExporter:
    """Build the configured metric exporter (console raw, OTLP wrapped).

    The console exporter is constructed with its output stream explicitly
    redirected to stderr (``out=`` by keyword); the OTLP exporter is
    wrapped in the Task 4.5 :class:`OtlpExporterWrapper`.

    Args:
        config: The parsed, validated telemetry configuration.

    Returns:
        The metric exporter to hand to the
        ``PeriodicExportingMetricReader``.
    """
    if config.otel_exporter == _EXPORTER_CONSOLE:
        result: MetricExporter = ConsoleMetricExporter(out=sys.stderr)
        return result
    assert config.otel_exporter == _EXPORTER_OTLP, config.otel_exporter
    assert config.otel_endpoint is not None, "config validation guarantees an endpoint with the otlp exporter"
    exporter = OTLPMetricExporter(endpoint=_with_otlp_path(config.otel_endpoint, _OTLP_METRICS_PATH))
    result = OtlpExporterWrapper(exporter, episode_message=_METRIC_EXPORT_FAILURE_MESSAGE)
    return result


def _instrument_views() -> list[View]:
    """The explicit-bucket :class:`View`s the ``MeterProvider`` is built with (Task 5.2/5.5).

    The Design Notes' "OTel bootstrap pins" bucket advice, expressed in
    the installed SDK 1.44.0's API: one ``View`` per pinned histogram,
    matched by instrument type + name + unit and carrying an
    ``ExplicitBucketHistogramAggregation`` with the pinned boundaries
    (``mcp.tool.duration``: 5..10000 ms; ``mcp.lock.wait_time``: 1..500
    ms). Views must be registered *before* the instruments are created
    -- so the bootstrap passes them to the ``MeterProvider``
    constructor, and the middleware's own ``mcp.tool.duration`` histogram
    (created lazily from the same provider's ``Meter`` on first
    observation) picks its View up automatically.

    Returns:
        The two pinned Views.
    """
    result = [
        View(
            instrument_type=Histogram,
            instrument_name=telemetry_metrics.MCP_TOOL_DURATION,
            instrument_unit=telemetry_metrics.UNIT_MS,
            aggregation=ExplicitBucketHistogramAggregation(boundaries=telemetry_metrics.TOOL_DURATION_BUCKET_BOUNDS),
        ),
        View(
            instrument_type=Histogram,
            instrument_name=telemetry_metrics.MCP_LOCK_WAIT,
            instrument_unit=telemetry_metrics.UNIT_MS,
            aggregation=ExplicitBucketHistogramAggregation(boundaries=telemetry_metrics.LOCK_WAIT_BUCKET_BOUNDS),
        ),
    ]
    return result


def bootstrap_telemetry(config: TelemetryConfig) -> None:
    """Configure the global OpenTelemetry providers for this process (Task 4.1, extended by Task 5.2/5.4/5.5).

    Called unconditionally at ``server.py``'s module scope (Task 4.9,
    after the config validation and the logging setup, before
    ``MCPServer(...)`` is constructed). When ``config.otel_enabled`` is
    ``False`` (the default) this sets nothing and returns -- the default
    must produce zero telemetry, and the SDK's built-in
    ``OpenTelemetryMiddleware`` then keeps creating inert non-recording
    spans through the API's no-provider proxy.

    When enabled, it installs -- via the global API, which the SDK's
    import-time-fetched proxy tracer/meter resolve against -- a
    ``TracerProvider`` (the Task 6.2 :class:`RedactionSpanProcessor`
    first, then the ``BatchSpanProcessor`` with the configured span
    exporter -- add order matters, see the module docstring) and a
    ``MeterProvider`` (a ``PeriodicExportingMetricReader`` with the
    configured metric exporter), both carrying a ``Resource`` with the
    fixed ``service.name = "specmgr"`` attribute, and fetches the
    ``Meter`` once. Phase 5's instrument split (the orchestrator's pin)
    then runs from that ``Meter``: the ``MeterProvider`` is built with
    the pinned explicit-bucket :func:`_instrument_views`; the
    ``mcp.lock.wait_time`` histogram and the ``mcp.cache.hit``/
    ``mcp.cache.miss`` observable counters (the ``telemetry/metrics.py``
    callbacks, registered at instrument creation per Task 1a.5's
    confirmed SDK 1.44.0 API) are created here, at bootstrap; the
    middleware's own ``mcp.tool.duration``/``mcp.tool.call.count``/
    ``mcp.tool.error.count`` instruments stay middleware-created on first
    observation. The ``Meter`` and the ``mcp.lock.wait_time`` histogram
    are stored in the ``telemetry/metrics.py`` slots (this module's own
    :data:`_meter` keeps mirroring the ``Meter`` for the Phase 4 tests'
    assertions). A repeated call in an already-bootstrapped process is a
    no-op (the global setters are set-once per process).

    Args:
        config: The parsed, validated telemetry configuration (``
            telemetry/config.py``).
    """
    global _tracer_provider, _meter_provider, _meter
    assert isinstance(config, TelemetryConfig), type(config)
    if not config.otel_enabled:
        return
    with _bootstrap_lock:
        if _tracer_provider is not None and _meter_provider is not None:
            return
        resource = Resource.create({_SERVICE_NAME_KEY: SERVICE_NAME})
        tracer_provider = TracerProvider(resource=resource)
        # Task 6.2 (Phase 6): the redaction SpanProcessor is added BEFORE
        # the exporting BatchSpanProcessor -- the provider's
        # SynchronousMultiSpanProcessor invokes on_end on its processors
        # in add order, so the scrub (which replaces the span's private
        # attribute containers; see telemetry/redact.py) runs before the
        # span is handed to the export path.
        tracer_provider.add_span_processor(RedactionSpanProcessor())
        tracer_provider.add_span_processor(BatchSpanProcessor(_build_span_exporter(config)))
        meter_provider = MeterProvider(
            metric_readers=[PeriodicExportingMetricReader(_build_metric_exporter(config))],
            resource=resource,
            views=_instrument_views(),
        )
        trace.set_tracer_provider(tracer_provider)
        metrics.set_meter_provider(meter_provider)
        _tracer_provider = tracer_provider
        _meter_provider = meter_provider
        meter = metrics.get_meter(_METER_NAME)
        _meter = meter
        telemetry_metrics.set_meter(meter)
        lock_wait_histogram = meter.create_histogram(
            telemetry_metrics.MCP_LOCK_WAIT,
            unit=telemetry_metrics.UNIT_MS,
            description="Time a domain-lock acquire() waited before the lock was granted",
        )
        telemetry_metrics.set_lock_wait_histogram(lock_wait_histogram)
        meter.create_observable_counter(
            telemetry_metrics.MCP_CACHE_HIT,
            description="Doc-cache reads served from a hash-matched entry without re-parsing",
            callbacks=[telemetry_metrics.cache_hit_callback],
        )
        meter.create_observable_counter(
            telemetry_metrics.MCP_CACHE_MISS,
            description="Doc-cache reads that had to (re-)parse",
            callbacks=[telemetry_metrics.cache_miss_callback],
        )


def shutdown_telemetry() -> None:
    """Shut down the providers :func:`bootstrap_telemetry` created (Task 4.1's exit pin).

    Called from ``server.py``'s ``_lifespan`` post-``yield`` section at
    process exit: the ``MeterProvider``'s shutdown performs its final
    metric collection and the ``BatchSpanProcessor``'s shutdown its final
    span flush -- after the stdio transport has restored fd 1, so both
    must go to the ``out=sys.stderr``-redirected console exporters (or
    over OTLP), never to the real stdout. The wrappers' own
    ``shutdown()`` calls (via the processor/reader) end any in-progress
    Task 4.5 failure episode and detach the suppression filters. A no-op
    when telemetry was disabled (or already shut down).

    Returns:
        ``None``.
    """
    global _tracer_provider, _meter_provider, _meter
    with _bootstrap_lock:
        tracer_provider = _tracer_provider
        meter_provider = _meter_provider
        _tracer_provider = None
        _meter_provider = None
        _meter = None
    if meter_provider is not None:
        meter_provider.shutdown()
    if tracer_provider is not None:
        tracer_provider.shutdown()
    telemetry_metrics.clear_instrument_slots()
