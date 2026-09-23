# `biz.dfch.specmgr.telemetry.otel`

OpenTelemetry SDK bootstrap (feat-139-logging-telemetry, Phase 4, Task 4.1).

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

## Classes

### `OtlpExporterWrapper`

A thin wrapper around one OTLP exporter de-duplicating its failure noise (Task 4.5).

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

**Methods:**

- `export(self, *args: 'Any', **kwargs: 'Any') -> 'Any'`
  Export one batch, tracking the armed/failing state around the attempt.

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

- `force_flush(self, *args: 'Any', **kwargs: 'Any') -> 'bool'`
  Pass ``force_flush`` through to the wrapped exporter unchanged.

  Args:
      *args: The wrapped exporter's positional ``force_flush`` arguments.
      **kwargs: The wrapped exporter's keyword ``force_flush`` arguments.

  Returns:
      The wrapped exporter's return value.

- `shutdown(self, *args: 'Any', **kwargs: 'Any') -> 'None'`
  End any in-progress episode, then pass ``shutdown`` through unchanged.

  The episode ends at provider shutdown (the pin): the suppression
  filter is detached, and a ``FAILURE`` return from a later
  ``export()`` call (e.g. the processor's final flush racing the
  shutdown) starts no new episode and emits no message.

  Args:
      *args: The wrapped exporter's positional ``shutdown`` arguments.
      **kwargs: The wrapped exporter's keyword ``shutdown`` arguments.


### `_ExporterEpisodeFilter`

The state-gated filter suppressing an OTLP exporter's own failure noise.

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

**Methods:**

- `filter(self, record: 'logging.LogRecord') -> 'bool'`
  Pass the record only when the wrapper has not armed the suppression.

  Args:
      record: The record the owning exporter logger is about to emit.

  Returns:
      ``False`` (suppressed) while the wrapper is armed (an export
      attempt is in progress or a failure episode is active),
      ``True`` otherwise.


## Functions

### `_build_metric_exporter(config: 'TelemetryConfig') -> 'MetricExporter'`

Build the configured metric exporter (console raw, OTLP wrapped).

The console exporter is constructed with its output stream explicitly
redirected to stderr (``out=`` by keyword); the OTLP exporter is
wrapped in the Task 4.5 :class:`OtlpExporterWrapper`.

Args:
    config: The parsed, validated telemetry configuration.

Returns:
    The metric exporter to hand to the
    ``PeriodicExportingMetricReader``.


### `_build_span_exporter(config: 'TelemetryConfig') -> 'SpanExporter'`

Build the configured span exporter (console raw, OTLP wrapped).

The console exporter (the default) is constructed with its output
stream explicitly redirected to stderr -- ``out=`` by keyword, since
``ConsoleSpanExporter``'s first positional arg is ``service_name``
(Task 1a.2's confirmed finding). The OTLP exporter is wrapped in the
Task 4.5 :class:`OtlpExporterWrapper`.

Args:
    config: The parsed, validated telemetry configuration.

Returns:
    The span exporter to hand to the ``BatchSpanProcessor``.


### `_instrument_views() -> 'list[View]'`

The explicit-bucket :class:`View`s the ``MeterProvider`` is built with (Task 5.2/5.5).

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


### `_with_otlp_path(base_url: 'str', export_path: 'str') -> 'str'`

Extend an OTLP base URL with the spec-mandated export path.

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


### `bootstrap_telemetry(config: 'TelemetryConfig') -> 'None'`

Configure the global OpenTelemetry providers for this process (Task 4.1, extended by Task 5.2/5.4/5.5).

Called unconditionally at ``server.py``'s module scope (Task 4.9,
after the config validation and the logging setup, before
``MCPServer(...)`` is constructed). When ``config.otel_enabled`` is
``False`` (the default) this sets nothing and returns -- the default
must produce zero telemetry, and the SDK's built-in
``OpenTelemetryMiddleware`` then keeps creating inert non-recording
spans through the API's no-provider proxy.

When enabled, it installs -- via the global API, which the SDK's
import-time-fetched proxy tracer/meter resolve against -- a
``TracerProvider`` (a ``BatchSpanProcessor`` with the configured span
exporter) and a ``MeterProvider`` (a ``PeriodicExportingMetricReader``
with the configured metric exporter), both carrying a ``Resource``
with the fixed ``service.name = "specmgr"`` attribute, and fetches the
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


### `shutdown_telemetry() -> 'None'`

Shut down the providers :func:`bootstrap_telemetry` created (Task 4.1's exit pin).

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

