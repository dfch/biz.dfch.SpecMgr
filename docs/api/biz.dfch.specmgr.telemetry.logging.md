# `biz.dfch.specmgr.telemetry.logging`

Structured logging for the MCP server (feat-139-logging-telemetry, Phase 2, Task 2.1).

``telemetry/config.py`` parses the ``SPECMGR_LOG_*``/``SPECMGR_OTEL_*``
environment into a validated :class:`~biz.dfch.specmgr.telemetry.config.
TelemetryConfig`; this module applies that config's logging half to the
process's root logger:

- :func:`setup_logging` -- the explicit, idempotent root-logger setup.
  Gated by ``config.log_enabled``: a no-op when disabled (leaving whatever
  handlers exist untouched, so the default configuration keeps the MCP
  SDK's own ``configure_logging()`` behavior byte-for-byte -- ACC-001's
  zero-log-records baseline). When enabled, it replaces the root handler
  set with exactly the intended one(s) at the configured level -- the
  stderr console handler in the format ``config.log_format`` selects,
  plus, when ``config.log_file_enabled`` and ``config.log_file_path`` are
  set, a file handler that is always the JSON formatter regardless of the
  console format (ACC-009). Replacing the handler set rather than calling
  ``logging.basicConfig`` is what keeps the setup effective in either
  handler state: a bare ``basicConfig`` would silently no-op against the
  handlers the SDK's own ``configure_logging()`` already installed (which
  ``MCPServer.__init__`` calls unconditionally), leaving
  ``SPECMGR_LOG_FORMAT``/``SPECMGR_LOG_LEVEL`` without effect. A repeated
  call converges on the same intended handler set (idempotent).
  ``server.py``'s module scope calls :func:`setup_logging` before
  ``mcp = MCPServer(...)`` is constructed (Task 2.5), so the SDK's own
  ``basicConfig``-based call runs afterwards and cannot override the
  enabled configuration.
- :class:`JsonFormatter` -- one JSON object per record (line-delimited,
  for the JSON console format and the always-JSON file sink).
- :class:`SpecmgrRichHandler` -- the rich console format: the SDK's own
  rich handler construction plus the same structured fields, rendered
  human-readably.

The pinned record shape (Task 2.1): ``timestamp`` (ISO 8601, UTC),
``level``, ``logger``, ``message`` -- always -- plus, only when the
record carries them, the structured fields ``correlation_id``,
``method``, ``item_type``, ``item_name``, ``domain``, ``status`` (only
for ``set_status`` invocations), ``duration_ms``, and ``exception``
(``type`` + ``message`` + ``traceback``). Phase 3's middleware sets those
as ``extra=`` kwargs on the ``LogRecord``; a record that carries none or
only some of them (e.g. the MCP SDK's own records) renders with only
what is present, and an ``exception`` the record does not carry as an
explicit extra is derived from the standard ``exc_info`` when that is set.

Unlike ``telemetry/config.py`` (stdlib-only), this module imports
``rich`` (pulled in by the ``mcp`` extra via ``cli``): it is only
imported from ``server.py`` (which already requires the ``mcp`` extra)
and its tests, so it is not base-library-safe.

The formatter-level absolute-path scrub the Design Notes' "Redaction
scope and limits" bullet defines is wired onto these same handlers'
formatters by Task 6.2 (Phase 6); each formatter here keeps its final
rendered string in a single seam (``JsonFormatter.format``,
``SpecmgrRichHandler.render_message``) so that hook slots in cleanly.

## Classes

### `JsonFormatter`

A ``logging.Formatter`` rendering each record as one JSON object.

The record shape is the pinned one (see the module docstring): the
four base fields always, the structured fields and ``exception`` only
when the record carries them. The output is always a single physical
line (embedded newlines JSON-escaped), so records written by a file
sink are line-delimited JSON (JSONL).

``format`` is the formatter's final rendered string -- the seam the
Task 6.2 (Phase 6) path scrub hooks onto for the JSON console handler
and the file sink.

**Methods:**

- `converter(...)`

- `format(self, record: 'logging.LogRecord') -> 'str'`
  Render the record as one JSON object.

  Args:
      record: The log record to format.

  Returns:
      The single-line JSON object as a string.

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


### `SpecmgrRichHandler`

The rich console handler: the SDK's own rich handler plus the structured fields.

Mirrors the MCP SDK's ``configure_logging()`` construction (a
``RichHandler`` on a ``Console(stderr=True)`` with
``rich_tracebacks=True``) and extends the rendered message with the
same structured fields the :class:`JsonFormatter` emits, so the rich
format carries the same information human-readably (``key=value``
pairs appended to the message). The ``exception`` field renders as
``Type: message``; its traceback is not re-rendered inline, since
``rich_tracebacks`` already displays the ``exc_info`` traceback
separately when the record carries one.

:meth:`render_message` is the handler's single message-text funnel
(both the plain and the ``exc_info`` paths of ``RichHandler.emit``
pass through it) -- the rich-format seam the Task 6.2 (Phase 6) path
scrub hooks onto.

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
  Append the record's structured fields to the message, then delegate to rich.

  Args:
      record: The log record being rendered.
      message: The record's message text so far.

  Returns:
      The rich renderable for the (extended) message.

- `setFormatter(self, fmt)`
  Set the formatter for this handler.

- `setLevel(self, level)`
  Set the logging level of this handler.  level must be an int or a str.

- `set_name(self, name)`


## Functions

### `_build_console_handler(config: 'TelemetryConfig') -> 'logging.Handler'`

Build the stderr console handler for the config's selected format.

Args:
    config: The parsed, validated telemetry configuration.

Returns:
    A :class:`SpecmgrRichHandler` (mirroring the SDK's own rich
    handler) for ``FORMAT_RICH``, or a ``StreamHandler`` on
    ``sys.stderr`` with a :class:`JsonFormatter` for ``FORMAT_JSON``.


### `_build_file_handler(path: 'str') -> 'logging.Handler'`

Build the opt-in file-sink handler: always JSON, regardless of the console format (ACC-009).

Args:
    path: The file-sink path (``SPECMGR_LOG_FILE_PATH``; guaranteed
        non-blank by the config's pairing rule when the file sink is
        enabled).

Returns:
    A ``FileHandler`` (append mode, UTF-8) with a
    :class:`JsonFormatter`.


### `_exception_field(record: 'logging.LogRecord') -> 'object | None'`

Return the record's ``exception`` field, or ``None`` when absent.

An explicit ``exception=`` extra (this feature's own code sets a
``{"type": ..., "message": ..., "traceback": ...}`` mapping) is
returned verbatim. Otherwise, when the record carries a standard
``exc_info`` (e.g. the MCP SDK's own ``logger.exception`` records),
the field is derived from it. A record that carries neither returns
``None`` -- the field is simply absent from the rendered record.

Args:
    record: The log record to inspect.

Returns:
    The exception field value, or ``None``.


### `_exception_text(exception: 'object') -> 'str'`

Render an :func:`_exception_field` value human-readably as ``Type: message``.

Args:
    exception: The exception field value (a mapping with ``type``/
        ``message`` keys, or any other value carried verbatim).

Returns:
    The human-readable rendering.


### `_structured_field_text(record: 'logging.LogRecord') -> 'str'`

Render the record's structured fields as ``key=value`` pairs (the rich format).

Args:
    record: The log record to inspect.

Returns:
    The ``key=value`` pairs joined by single spaces, or ``""`` when
    the record carries no structured fields and no exception.


### `_structured_fields(record: 'logging.LogRecord') -> 'dict[str, object]'`

Return the record's structured ``extra=`` fields, in pinned order.

Only the fields the record actually carries are returned, so records
that carry none (e.g. the MCP SDK's own) yield an empty mapping.

Args:
    record: The log record to inspect.

Returns:
    A mapping of field name to value holding only the structured
    fields present on the record.


### `setup_logging(config: 'TelemetryConfig') -> 'None'`

Apply the config's logging half to the root logger, explicitly and idempotently.

When ``config.log_enabled`` is ``False`` this is a no-op: whatever
handlers exist are left untouched, so the default (all-off)
configuration keeps the MCP SDK's own ``configure_logging()``
behavior byte-for-byte (ACC-001's zero-log-records baseline).

When enabled, the root logger's entire handler set is replaced with
exactly the intended one(s) at the configured level: the stderr
console handler in the format ``config.log_format`` selects, plus --
when ``config.log_file_enabled`` and ``config.log_file_path`` are set
-- the always-JSON file sink (ACC-009). Replacing the handler set
(rather than calling ``logging.basicConfig``, which silently no-ops
once the root already has handlers) is what makes the setup
effective in either handler state -- correct whether the SDK's own
``configure_logging()`` has run yet or not -- and idempotent: a
repeated call converges on the same intended handler set.

``server.py``'s module scope calls this before ``mcp = MCPServer(...)``
is constructed (Task 2.5), so the SDK's own ``basicConfig``-based call
inside ``MCPServer.__init__`` runs afterwards and cannot override the
enabled configuration.

Args:
    config: The parsed, validated telemetry configuration (``
        telemetry/config.py``).

Returns:
    ``None``.

