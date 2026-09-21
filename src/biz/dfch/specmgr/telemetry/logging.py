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

"""Structured logging for the MCP server (feat-139-logging-telemetry, Phase 2, Task 2.1).

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
"""

from __future__ import annotations

import json
import logging
import sys
import traceback
from datetime import datetime, timezone

from rich.console import Console, ConsoleRenderable
from rich.logging import RichHandler

from .config import TelemetryConfig

#: The console format that renders each record as one JSON object (per line).
FORMAT_JSON = "json"
#: The console format that renders records human-readably via rich.
FORMAT_RICH = "rich"

#: The structured fields a specmgr log record may carry as ``extra=`` kwargs
#: (the pinned record shape, in render order; Phase 3's middleware sets them).
_STRUCTURED_EXTRA_FIELDS = (
    "correlation_id",
    "method",
    "item_type",
    "item_name",
    "domain",
    "status",
    "duration_ms",
)


def _structured_fields(record: logging.LogRecord) -> dict[str, object]:
    """Return the record's structured ``extra=`` fields, in pinned order.

    Only the fields the record actually carries are returned, so records
    that carry none (e.g. the MCP SDK's own) yield an empty mapping.

    Args:
        record: The log record to inspect.

    Returns:
        A mapping of field name to value holding only the structured
        fields present on the record.
    """
    result: dict[str, object] = {}
    for name in _STRUCTURED_EXTRA_FIELDS:
        value = getattr(record, name, None)
        if value is not None:
            result[name] = value
    return result


def _exception_field(record: logging.LogRecord) -> object | None:
    """Return the record's ``exception`` field, or ``None`` when absent.

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
    """
    value = getattr(record, "exception", None)
    if value is not None:
        return value
    exc_info = getattr(record, "exc_info", None)
    if exc_info is None:
        return None
    exc_type, exc_value, exc_traceback = exc_info
    if exc_type is None or exc_value is None:
        return None
    result = {
        "type": exc_type.__qualname__,
        "message": str(exc_value),
        "traceback": "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)),
    }
    return result


def _exception_text(exception: object) -> str:
    """Render an :func:`_exception_field` value human-readably as ``Type: message``.

    Args:
        exception: The exception field value (a mapping with ``type``/
            ``message`` keys, or any other value carried verbatim).

    Returns:
        The human-readable rendering.
    """
    if isinstance(exception, dict):
        exc_type = exception.get("type", "exception")
        exc_message = exception.get("message")
        if exc_message:
            result = f"{exc_type}: {exc_message}"
            return result
        result = str(exc_type)
        return result
    result = str(exception)
    return result


def _structured_field_text(record: logging.LogRecord) -> str:
    """Render the record's structured fields as ``key=value`` pairs (the rich format).

    Args:
        record: The log record to inspect.

    Returns:
        The ``key=value`` pairs joined by single spaces, or ``""`` when
        the record carries no structured fields and no exception.
    """
    parts: list[str] = []
    for name, value in _structured_fields(record).items():
        parts.append(f"{name}={value}")
    exception = _exception_field(record)
    if exception is not None:
        parts.append(f"exception={_exception_text(exception)}")
    result = " ".join(parts)
    return result


class JsonFormatter(logging.Formatter):
    """A ``logging.Formatter`` rendering each record as one JSON object.

    The record shape is the pinned one (see the module docstring): the
    four base fields always, the structured fields and ``exception`` only
    when the record carries them. The output is always a single physical
    line (embedded newlines JSON-escaped), so records written by a file
    sink are line-delimited JSON (JSONL).

    ``format`` is the formatter's final rendered string -- the seam the
    Task 6.2 (Phase 6) path scrub hooks onto for the JSON console handler
    and the file sink.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Render the record as one JSON object.

        Args:
            record: The log record to format.

        Returns:
            The single-line JSON object as a string.
        """
        entry: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for name, value in _structured_fields(record).items():
            entry[name] = value
        exception = _exception_field(record)
        if exception is not None:
            entry["exception"] = exception
        result = json.dumps(entry, ensure_ascii=False, default=str)
        return result


class SpecmgrRichHandler(RichHandler):
    """The rich console handler: the SDK's own rich handler plus the structured fields.

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
    """

    def render_message(self, record: logging.LogRecord, message: str) -> ConsoleRenderable:
        """Append the record's structured fields to the message, then delegate to rich.

        Args:
            record: The log record being rendered.
            message: The record's message text so far.

        Returns:
            The rich renderable for the (extended) message.
        """
        fields = _structured_field_text(record)
        if fields:
            message = f"{message} {fields}"
        result = super().render_message(record, message)
        return result


def _build_console_handler(config: TelemetryConfig) -> logging.Handler:
    """Build the stderr console handler for the config's selected format.

    Args:
        config: The parsed, validated telemetry configuration.

    Returns:
        A :class:`SpecmgrRichHandler` (mirroring the SDK's own rich
        handler) for ``FORMAT_RICH``, or a ``StreamHandler`` on
        ``sys.stderr`` with a :class:`JsonFormatter` for ``FORMAT_JSON``.
    """
    if config.log_format == FORMAT_RICH:
        result: logging.Handler = SpecmgrRichHandler(console=Console(stderr=True), rich_tracebacks=True)
        return result
    if config.log_format == FORMAT_JSON:
        result = logging.StreamHandler(stream=sys.stderr)
        result.setFormatter(JsonFormatter())
        return result
    raise ValueError(f"unreachable: log_format is validated to {FORMAT_RICH}/{FORMAT_JSON} by telemetry/config.py")


def _build_file_handler(path: str) -> logging.Handler:
    """Build the opt-in file-sink handler: always JSON, regardless of the console format (ACC-009).

    Args:
        path: The file-sink path (``SPECMGR_LOG_FILE_PATH``; guaranteed
            non-blank by the config's pairing rule when the file sink is
            enabled).

    Returns:
        A ``FileHandler`` (append mode, UTF-8) with a
        :class:`JsonFormatter`.
    """
    assert path.strip(), path
    result = logging.FileHandler(path, mode="a", encoding="utf-8")
    result.setFormatter(JsonFormatter())
    return result


def setup_logging(config: TelemetryConfig) -> None:
    """Apply the config's logging half to the root logger, explicitly and idempotently.

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
    """
    assert isinstance(config, TelemetryConfig), type(config)
    if not config.log_enabled:
        return
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()
    root.setLevel(config.log_level)
    root.addHandler(_build_console_handler(config))
    if config.log_file_enabled:
        assert config.log_file_path is not None, "config validation guarantees a non-blank path with log_file_enabled"
        root.addHandler(_build_file_handler(config.log_file_path))
