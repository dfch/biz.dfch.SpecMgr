# `biz.dfch.specmgr.telemetry.redact`

Free-text redaction backstop for log records and spans (feat-139-logging-telemetry, Phase 6, Tasks 6.1/6.2).

The Design Notes' "Redaction scope and limits" bullet splits the
redaction guarantee into two components: (1) a *structured*-attribute
guarantee -- this feature's own code never attaches a full body, path,
or title as a dedicated field/attribute value (fully achievable); and
(2) a *free-text* backstop, which is what this module implements:

- :func:`scrub_paths` -- the shared, best-effort, regex-based scrub for
  absolute-filesystem-path-shaped substrings (POSIX ``/...``, Windows
  drive ``X:\...``, UNC ``\\host\...``), each replaced by the fixed
  :data:`REDACTED_PATH_TOKEN`. It deliberately does not attempt title
  detection: a document/artifact title is arbitrary free text with no
  distinguishing shape, so no generic filter can reliably detect it --
  the title-embedding exception call sites in non-deprecated domains
  are reworded at their source instead (Task 6.7).
- :class:`ScrubbingFormatter` -- the log-side hook. It wraps a delegate
  formatter and runs the scrub on the delegate's *final rendered
  string*, i.e. at formatter level: a handler-attached ``logging.
  Filter`` would see ``LogRecord.msg``/``args``/``exc_info`` but not the
  ``exc_text`` the formatter renders afterwards, and tracebacks embed
  absolute file paths. Wired by Task 6.2 onto every specmgr-installed
  handler that renders through a formatter -- the JSON console handler
  and the always-JSON file sink (both ``JsonFormatter``-based) -- so it
  covers every rendered record reaching those handlers regardless of
  originating logger (``SPECMGR_LOG_ENABLED=true`` reconfigures the root
  logger, so third-party/SDK loggers share the same handlers).
- :class:`ScrubbingSpecmgrRichHandler` -- the rich-format hook. The
  pinned rich seam is ``render_message`` (the single message-text
  funnel of ``RichHandler.emit``); the subclass scrubs the combined
  message text (the message plus the record's structured fields, incl.
  the ``exception`` field's message) at that seam. Residual, documented
  limit: the rich-rendered traceback itself (frame file paths and the
  exception's own line) is produced by rich's ``Traceback`` renderable
  outside that seam and is not scrubbed -- the JSON path, which is what
  production and the file sink use, is fully scrubbed.
- :class:`RedactionSpanProcessor` -- the span-side hook (ACC-012): a
  global, ``TracerProvider``-level ``SpanProcessor`` whose ``on_end``
  applies the same scrub to every ended span's attributes and to each
  of its events' attributes -- in particular the
  ``exception.message``/``exception.stacktrace``/``exception.type`` keys
  the SDK's ``record_exception`` sets on the spans the SDK's own
  built-in ``OpenTelemetryMiddleware`` creates (essentially all spans;
  this feature creates none of its own). Scope is exactly those two
  surfaces (the orchestrator's pin): a span's ``status`` *description*
  (the ``set_status(StatusCode.ERROR, str(e))`` payload) is not an
  attribute container and is not scrubbed -- a documented residual on
  par with the rich-traceback one, since the title-embedding exception
  messages of the mandatory Task 6.7 set are reworded at the source so
  their ``str(e)`` no longer carries a title.

The span-side mechanism (confirmed by Task 1a.3's spike against the
installed ``opentelemetry-sdk`` 1.44.0): ``on_end`` receives a
``ReadableSpan`` with no public mutation API -- no ``set_attribute``,
the ``attributes`` property is a ``MappingProxyType``, the span's
``BoundedAttributes`` is locked immutable at ``end()`` (before
processors are notified), and event attributes are immutable from
construction -- so the processor scrubs by *replacing the private
containers* before any later exporter reads the span:
``readable_span._attributes = BoundedAttributes(None, scrubbed,
immutable=False)`` and, per event, ``event._attributes =
BoundedAttributes(None, scrubbed, immutable=False)``. Both export paths
(the in-memory/console exporters' ``to_json`` and the OTLP protobuf
encoder) read the *live* ``self._attributes``/``self._events``
containers at export time (the ``ReadableSpan.attributes``/``events``
properties re-wrap them on every access), so the replacement is visible
end to end. Two consequences are carried into the tests (Task 6.3):
(a) the processor must be added to the ``TracerProvider`` *before* the
exporting ``BatchSpanProcessor`` -- ``TracerProvider`` uses a
``SynchronousMultiSpanProcessor`` that invokes ``on_end`` on its
processors in add order (verified against the installed 1.44.0 source),
so the scrub runs before the batch processor enqueues the span; and
(b) the reliance on the private field names ``ReadableSpan.
_attributes``/``_events`` and ``Event._attributes`` is a canary test's
job to fail loudly on, since a future SDK restructure would otherwise
silently stop redacting (spans leak, no error) -- hence Task 7.1's
``opentelemetry-sdk<2.0.0`` narrowing. The processor itself
fail-opens (one warning per process, per the "Observability Degrades
Gracefully, Application Logic Never Does" convention) if the expected
containers are missing, rather than breaking the ending span's request.

Unlike ``telemetry/config.py`` (stdlib-only), this module imports
``opentelemetry.*`` and ``rich``: it is only imported from
``telemetry/logging.py`` (its handler wiring), ``telemetry/otel.py``
(its bootstrap wiring), ``server.py`` (through those two), and its
tests -- never from the base library.

## Classes

### `RedactionSpanProcessor`

A global, ``TracerProvider``-level ``SpanProcessor`` scrubbing every ended span (ACC-012).

Added by :func:`telemetry.otel.bootstrap_telemetry` *before* the
exporting ``BatchSpanProcessor`` (Task 6.2), so -- ``TracerProvider``
uses a ``SynchronousMultiSpanProcessor`` that invokes ``on_end`` on
its processors in add order -- the scrub runs before the span is
handed to the export path. It applies the same :func:`scrub_paths`
logic to every span the process creates, including the SDK's own
built-in ``OpenTelemetryMiddleware``'s spans (this feature creates
no spans of its own): every attribute value plus each event's
attributes, in particular the ``exception.message``/
``exception.stacktrace``/``exception.escaped``/``exception.type``
keys ``record_exception`` sets.

Like every observability path in this feature, it fail-opens: if the
installed SDK's private containers are not in the expected shape (a
future restructure -- Task 6.3's canary test exists to catch exactly
that in CI first), :meth:`on_end` logs one warning per process and
leaves the span unscrubbed instead of propagating into the ending
span's request.

**Methods:**

- `force_flush(self, timeout_millis: int = 30000) -> bool`
  Export all ended spans to the configured Exporter that have not yet
  been exported.

  Args:
      timeout_millis: The maximum amount of time to wait for spans to be
          exported.

  Returns:
      False if the timeout is exceeded, True otherwise.

- `on_end(self, readable_span: 'ReadableSpan') -> 'None'`
  Scrub the ended span's attributes and events (fail-open on an unexpected shape).

  Args:
      readable_span: The ended span (a ``ReadableSpan``; see the
          class docstring for the private-container mechanism).

- `on_start(self, span: 'Span', parent_context: opentelemetry.context.context.Context | None = None) -> None`
  Called when a :class:`opentelemetry.trace.Span` is started.

  This method is called synchronously on the thread that starts the
  span, therefore it should not block or throw an exception.

  Args:
      span: The :class:`opentelemetry.trace.Span` that just started.
      parent_context: The parent context of the span that just started.

- `shutdown(self) -> None`
  Called when a :class:`opentelemetry.sdk.trace.TracerProvider` is shutdown.


### `ScrubbingFormatter`

A ``logging.Formatter`` that scrubs the final rendered string of a delegate.

The Task 6.2 wiring wraps the specmgr-installed handlers' formatters
(the JSON console handler's and the file sink's ``JsonFormatter``)
with this class, so the scrub runs on the delegate's *final*
rendered string -- the point where ``exc_text`` (a traceback that
embeds absolute file paths) exists, which a handler-attached
``logging.Filter`` cannot see. Every record reaching a handler that
carries this formatter is covered, regardless of the record's
originating logger.

Attributes:
    _delegate: The wrapped formatter (the real renderer; this class
        adds nothing to its output except the scrub).

**Methods:**

- `converter(...)`

- `format(self, record: 'logging.LogRecord') -> 'str'`
  Render via the delegate, then scrub the final rendered string.

  Args:
      record: The log record to format.

  Returns:
      The delegate's rendered string with every absolute-path-shaped
      substring replaced by :data:`REDACTED_PATH_TOKEN`.

- `formatException(self, ei)`
  Format and return the specified exception information as a string.

  This default implementation just uses
  traceback.print_exception()

- `formatMessage(self, record)`

- `formatStack(self, stack_info)`
  This method is provided as an extension point for specialized
  formatting of stack information.

  The input data is a string as returned from a call to
  :func:`traceback.print_stack`, but with the last trailing newline
  removed.

  The base implementation just returns the value passed in.

- `formatTime(self, record, datefmt=None)`
  Return the creation time of the specified LogRecord as formatted text.

  This method should be called from format() by a formatter which
  wants to make use of a formatted time. This method can be overridden
  in formatters to provide for any specific requirement, but the
  basic behaviour is as follows: if datefmt (a string) is specified,
  it is used with time.strftime() to format the creation time of the
  record. Otherwise, an ISO8601-like (or RFC 3339-like) format is used.
  The resulting string is returned. This function uses a user-configurable
  function to convert the creation time to a tuple. By default,
  time.localtime() is used; to change this for a particular formatter
  instance, set the 'converter' attribute to a function with the same
  signature as time.localtime() or time.gmtime(). To change it for all
  formatters, for example if you want all logging times to be shown in GMT,
  set the 'converter' attribute in the Formatter class.

- `usesTime(self)`
  Check if the format uses the creation time of the record.


### `ScrubbingSpecmgrRichHandler`

The rich console handler with the path scrub applied at the ``render_message`` seam.

The pinned rich seam (the Phase 2 decision): ``RichHandler.emit``
funnels both the plain-message and the ``rich_tracebacks`` exception
paths through ``render_message(record, message)`` as the single
message-text point. This subclass scrubs the handler's *combined*
message text (the message plus the record's structured fields,
incl. the ``exception`` field's ``Type: message`` rendering) at that
seam, so the message-level content of every record the rich console
renders is covered. Documented residual: the rich-rendered traceback
itself (frame file paths, the exception's own line) is produced by
rich's ``Traceback`` renderable outside the seam and is not scrubbed
-- the JSON path is fully scrubbed and is what production and the
file sink use (rich is the local-dev format).

**Methods:**

- `acquire(self)`
  Acquire the I/O thread lock.

- `addFilter(self, filter)`
  Add the specified filter to this handler.

- `close(self)`
  Tidy up any resources used by the handler.

  This version removes the handler from an internal map of handlers,
  _handlers, which is used for handler lookup by name. Subclasses
  should ensure that this gets called from overridden close()
  methods.

- `createLock(self)`
  Acquire a thread lock for serializing access to the underlying I/O.

- `emit(self, record: 'LogRecord') -> 'None'`
  Invoked by logging.

- `filter(self, record)`
  Determine if a record is loggable by consulting all the filters.

  The default is to allow the record to be logged; any filter can veto
  this by returning a false value.
  If a filter attached to a handler returns a log record instance,
  then that instance is used in place of the original log record in
  any further processing of the event by that handler.
  If a filter returns any other true value, the original log record
  is used in any further processing of the event by that handler.

  If none of the filters return false values, this method returns
  a log record.
  If any of the filters return a false value, this method returns
  a false value.

  .. versionchanged:: 3.2

     Allow filters to be just callables.

  .. versionchanged:: 3.12
     Allow filters to return a LogRecord instead of
     modifying it in place.

- `flush(self)`
  Ensure all logging output has been flushed.

  This version does nothing and is intended to be implemented by
  subclasses.

- `format(self, record)`
  Format the specified record.

  If a formatter is set, use it. Otherwise, use the default formatter
  for the module.

- `get_level_text(self, record: 'LogRecord') -> 'Text'`
  Get the level name from the record.

  Args:
      record (LogRecord): LogRecord instance.

  Returns:
      Text: A tuple of the style and level name.

- `get_name(self)`

- `handle(self, record)`
  Conditionally emit the specified logging record.

  Emission depends on filters which may have been added to the handler.
  Wrap the actual emission of the record with acquisition/release of
  the I/O thread lock.

  Returns an instance of the log record that was emitted
  if it passed all filters, otherwise a false value is returned.

- `handleError(self, record)`
  Handle errors which occur during an emit() call.

  This method should be called from handlers when an exception is
  encountered during an emit() call. If raiseExceptions is false,
  exceptions get silently ignored. This is what is mostly wanted
  for a logging system - most users will not care about errors in
  the logging system, they are more interested in application errors.
  You could, however, replace this with a custom handler if you wish.
  The record which was being processed is passed in to this method.

- `release(self)`
  Release the I/O thread lock.

- `removeFilter(self, filter)`
  Remove the specified filter from this handler.

- `render(self, *, record: 'LogRecord', traceback: 'Optional[Traceback]', message_renderable: 'ConsoleRenderable') -> 'ConsoleRenderable'`
  Render log for display.

  Args:
      record (LogRecord): logging Record.
      traceback (Optional[Traceback]): Traceback instance or None for no Traceback.
      message_renderable (ConsoleRenderable): Renderable (typically Text) containing log message contents.

  Returns:
      ConsoleRenderable: Renderable to display log.

- `render_message(self, record: 'logging.LogRecord', message: 'str') -> 'ConsoleRenderable'`
  Scrub the combined message text, then render it via rich.

  Args:
      record: The log record being rendered.
      message: The record's message text so far.

  Returns:
      The rich renderable for the scrubbed (extended) message.

- `setFormatter(self, fmt)`
  Set the formatter for this handler.

- `setLevel(self, level)`
  Set the logging level of this handler.  level must be an int or a str.

- `set_name(self, name)`


## Functions

### `_scrub_attribute_value(value: 'object') -> 'object'`

Scrub one span-attribute value: strings (and string sequence items) only.

Non-string attributes pass through untouched; a ``list``/``tuple``
value gets its string items scrubbed and is only replaced when
something actually changed (the installed SDK 1.44.0's
``record_exception`` sets single-string values for
``exception.type``/``exception.message``/``exception.stacktrace``/
``exception.escaped`` -- no sequences -- but the guard costs nothing
for a future SDK that stores some differently).

Args:
    value: The attribute value to scrub.

Returns:
    The scrubbed value (a new object only when something changed;
    the same object otherwise).


### `_scrub_attributes(attributes: 'Mapping[str, object]') -> 'dict[str, object] | None'`

Scrub a mapping's values; return the new mapping only when something changed.

Args:
    attributes: The attribute mapping to scrub.

Returns:
    A plain dict of the scrubbed values, or ``None`` when nothing
    matched (the caller then keeps the original container).


### `_scrub_span(readable_span: 'ReadableSpan') -> 'None'`

Replace the span's private attribute containers with scrubbed copies.

The Task 1a.3-confirmed mechanism: ``ReadableSpan`` has no public
mutation API and its ``BoundedAttributes`` are locked immutable by
the time ``on_end`` runs, so the scrub rebinds the *private*
containers -- ``readable_span._attributes`` and each
``event._attributes`` -- to fresh ``BoundedAttributes`` copies
(``immutable=False``) whenever (and only whenever) the scrub
actually changed a value. The SDK's export paths read those live
containers at export time (``ReadableSpan.attributes``/``events``
re-wrap ``self._attributes``/``self._events`` on every access), so
the replacement is what the exporter sees.

Args:
    readable_span: The ended span the processor's ``on_end`` received.


### `scrub_paths(text: 'str') -> 'str'`

Replace every absolute-filesystem-path-shaped substring by the redaction token.

Best-effort by design (the Design Notes' "Redaction scope and limits"
bullet documents the limits): it catches POSIX (two-or-more-segment)
absolute paths, Windows drive paths (``X:\...``/``X:/...``, raw or
JSON-escaped), and UNC paths (``\\host\...``, raw or JSON-escaped);
it does not catch single-segment POSIX paths (``/tmp``), paths
containing spaces or backslashes inside a POSIX segment, or anything
that is not path-shaped -- and a URL path with two or more segments
(``https://host/a/b``) is a known false positive. It never attempts
to detect a document/artifact title (Task 6.7's job, at the source).
The scrub is safe on already-JSON-rendered text: a matched substring
never consumes an escape backslash (e.g. the ``"`` of a closed JSON
string), so scrubbing the final rendered string cannot corrupt it.

Args:
    text: The rendered text to scrub.

Returns:
    The text with every matched substring replaced by
    :data:`REDACTED_PATH_TOKEN` (idempotent: the token itself
    matches nothing).

