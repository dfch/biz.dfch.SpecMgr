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

"""Free-text redaction backstop for log records and spans (feat-139-logging-telemetry, Phase 6, Tasks 6.1/6.2).

The Design Notes' "Redaction scope and limits" bullet splits the
redaction guarantee into two components: (1) a *structured*-attribute
guarantee -- this feature's own code never attaches a full body, path,
or title as a dedicated field/attribute value (fully achievable); and
(2) a *free-text* backstop, which is what this module implements:

- :func:`scrub_paths` -- the shared, best-effort, regex-based scrub for
  absolute-filesystem-path-shaped substrings (POSIX ``/...``, Windows
  drive ``X:\\...``, UNC ``\\\\host\\...``), each replaced by the fixed
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
"""

from __future__ import annotations

import logging
import re
import threading
from collections.abc import Mapping
from typing import Any

from opentelemetry.attributes import BoundedAttributes
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanProcessor
from rich.console import ConsoleRenderable
from rich.logging import RichHandler

from .logging import SpecmgrRichHandler

__all__ = [
    "REDACTED_PATH_TOKEN",
    "RedactionSpanProcessor",
    "ScrubbingFormatter",
    "ScrubbingSpecmgrRichHandler",
    "scrub_paths",
]

#: The single, fixed replacement token every scrubbed path becomes (the
#: orchestrator's pin: exactly ``<redacted-path>``).
REDACTED_PATH_TOKEN = "<redacted-path>"

#: The logger this module's fail-open warning is emitted on (the same
#: ``biz.dfch.specmgr.telemetry`` logger the middleware/otel wrappers use).
logger = logging.getLogger("biz.dfch.specmgr.telemetry")

# ---------------------------------------------------------------------------
# The absolute-path scrub pattern (comparison values per the repo convention)
# ---------------------------------------------------------------------------

# One path *segment* character: anything but whitespace, quotes,
# brackets/parens/angle braces, pipes, semicolons, commas, colons, and
# backslashes. Excluding quotes keeps a match inside a JSON string value;
# excluding the colon keeps a ``file:line`` reference's line number; and
# excluding the backslash is structural, not cosmetic: in the final rendered
# JSON string a closing quote is spelled ``\"`` (escape backslash + quote),
# so a segment class that admitted ``\`` would swallow that backslash and
# corrupt the JSON (verified failure mode) -- backslashes enter the pattern
# only as explicit separator runs below.
_SEGMENT_CHAR = r"[^\s\"'`()\[\]{}<>|;:,\\]"
# One separator: a backslash run (covering both the raw ``\`` and the
# JSON-escaped ``\\`` spelling of one logical backslash) or a slash.
_SEPARATOR = r"(?:\\+|/)"

# POSIX absolute path: at least two ``/``-separated segments (``/a/b``) --
# the two-segment minimum is what keeps single-slash tokens like
# ``tools/call``/``rich/json``/``OTLP/HTTP`` from matching. The initial ``/``
# must not be preceded by ``:`` or ``/`` (guards URL ``scheme://`` shapes and
# ``specmgr://``), the first segment must not start with a digit (guards
# version-matrix tokens like ``3.11/3.12/3.13``), and a trailing sentence
# dot is not absorbed. A POSIX path whose segment itself contains a backslash
# is a documented false negative (only the prefix up to the backslash
# matches).
_POSIX_PATH = r"(?<![:/])/(?!\d)(?:" + _SEGMENT_CHAR + r"+/)+(?:" + _SEGMENT_CHAR + r"+)(?<!\.)"
# Windows drive path: a single letter (not preceded by a word character)
# plus ``:`` plus separator/segment chains (``C:\a\b`` raw, ``C:\\a\\b``
# JSON-escaped, and the mixed ``C:/a/b`` spelling all match).
_DRIVE_PATH = (
    r"(?<![A-Za-z0-9])[A-Za-z]:"
    + _SEPARATOR
    + r"+"
    + _SEGMENT_CHAR
    + r"+(?:"
    + _SEPARATOR
    + r"+"
    + _SEGMENT_CHAR
    + r"+)*(?<!\.)"
)
# UNC path: a run of two or more backslashes (the raw ``\\host\share`` and
# JSON-escaped ``\\\\host\\share`` spellings alike), a host, then
# backslash/segment chains.
_UNC_PATH = r"\\{2,}" + _SEGMENT_CHAR + r"+(?:\\+" + _SEGMENT_CHAR + r"+)+(?<!\.)"

#: The combined absolute-path pattern the scrub compiles once at import.
_ABSOLUTE_PATH_PATTERN = re.compile(f"(?:{_UNC_PATH}|{_DRIVE_PATH}|{_POSIX_PATH})")


def scrub_paths(text: str) -> str:
    """Replace every absolute-filesystem-path-shaped substring by the redaction token.

    Best-effort by design (the Design Notes' "Redaction scope and limits"
    bullet documents the limits): it catches POSIX (two-or-more-segment)
    absolute paths, Windows drive paths (``X:\\...``/``X:/...``, raw or
    JSON-escaped), and UNC paths (``\\\\host\\...``, raw or JSON-escaped);
    it does not catch single-segment POSIX paths (``/tmp``), paths
    containing spaces or backslashes inside a POSIX segment, or anything
    that is not path-shaped -- and a URL path with two or more segments
    (``https://host/a/b``) is a known false positive. It never attempts
    to detect a document/artifact title (Task 6.7's job, at the source).
    The scrub is safe on already-JSON-rendered text: a matched substring
    never consumes an escape backslash (e.g. the ``\"`` of a closed JSON
    string), so scrubbing the final rendered string cannot corrupt it.

    Args:
        text: The rendered text to scrub.

    Returns:
        The text with every matched substring replaced by
        :data:`REDACTED_PATH_TOKEN` (idempotent: the token itself
        matches nothing).
    """
    assert isinstance(text, str), type(text)
    result = _ABSOLUTE_PATH_PATTERN.sub(REDACTED_PATH_TOKEN, text)
    return result


# ---------------------------------------------------------------------------
# The log-side hooks (formatter level on the final rendered string)
# ---------------------------------------------------------------------------


class ScrubbingFormatter(logging.Formatter):
    """A ``logging.Formatter`` that scrubs the final rendered string of a delegate.

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
    """

    def __init__(self, delegate: logging.Formatter) -> None:
        """Wrap the delegate formatter with the path scrub.

        Args:
            delegate: The formatter whose final rendered string is scrubbed.
        """
        assert isinstance(delegate, logging.Formatter), type(delegate)
        super().__init__()
        self._delegate = delegate

    def format(self, record: logging.LogRecord) -> str:
        """Render via the delegate, then scrub the final rendered string.

        Args:
            record: The log record to format.

        Returns:
            The delegate's rendered string with every absolute-path-shaped
            substring replaced by :data:`REDACTED_PATH_TOKEN`.
        """
        result = scrub_paths(self._delegate.format(record))
        return result

    def __getattr__(self, name: str) -> Any:
        """Forward any attribute the delegate defines (e.g. ``usesTime``) to it.

        Only invoked for names the normal lookup missed (never for
        dunder/implicit-lookup names), so the wrapper's own state always
        wins; a name the delegate also lacks raises ``AttributeError``
        as usual. Mirrors ``telemetry/otel.py``'s
        ``OtlpExporterWrapper.__getattr__`` pattern.

        Args:
            name: The missing attribute's name.

        Returns:
            The delegate's attribute of that name.
        """
        result = getattr(object.__getattribute__(self, "_delegate"), name)
        return result


class ScrubbingSpecmgrRichHandler(SpecmgrRichHandler):
    """The rich console handler with the path scrub applied at the ``render_message`` seam.

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
    """

    def render_message(self, record: logging.LogRecord, message: str) -> ConsoleRenderable:
        """Scrub the combined message text, then render it via rich.

        Args:
            record: The log record being rendered.
            message: The record's message text so far.

        Returns:
            The rich renderable for the scrubbed (extended) message.
        """
        combined = scrub_paths(self._combined_message(record, message))
        result = RichHandler.render_message(self, record, combined)
        return result


# ---------------------------------------------------------------------------
# The span-side hook (global SpanProcessor, private-container replacement)
# ---------------------------------------------------------------------------


def _scrub_attribute_value(value: object) -> object:
    """Scrub one span-attribute value: strings (and string sequence items) only.

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
    """
    if isinstance(value, str):
        result: object = scrub_paths(value)
        return result
    if isinstance(value, (list, tuple)):
        items = [_scrub_attribute_value(item) for item in value]
        if items != list(value):
            result = items if isinstance(value, list) else tuple(items)
            return result
    result = value
    return result


def _scrub_attributes(attributes: Mapping[str, object]) -> dict[str, object] | None:
    """Scrub a mapping's values; return the new mapping only when something changed.

    Args:
        attributes: The attribute mapping to scrub.

    Returns:
        A plain dict of the scrubbed values, or ``None`` when nothing
        matched (the caller then keeps the original container).
    """
    scrubbed: dict[str, object] = {}
    changed = False
    for key, value in attributes.items():
        new_value = _scrub_attribute_value(value)
        if new_value != value:
            changed = True
        scrubbed[key] = new_value
    if not changed:
        result: dict[str, object] | None = None
        return result
    result = scrubbed
    return result


def _scrub_span(readable_span: ReadableSpan) -> None:
    """Replace the span's private attribute containers with scrubbed copies.

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
    """
    attributes = readable_span._attributes
    if attributes is not None:
        scrubbed = _scrub_attributes(attributes)
        if scrubbed is not None:
            readable_span._attributes = BoundedAttributes(None, scrubbed, immutable=False)
    for event in readable_span._events or ():
        event_attributes = event._attributes
        if event_attributes is None:
            continue
        scrubbed = _scrub_attributes(event_attributes)
        if scrubbed is not None:
            event._attributes = BoundedAttributes(None, scrubbed, immutable=False)


class RedactionSpanProcessor(SpanProcessor):
    """A global, ``TracerProvider``-level ``SpanProcessor`` scrubbing every ended span (ACC-012).

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
    """

    def __init__(self) -> None:
        """Build the processor (no configuration; the scrub is fixed)."""
        super().__init__()
        # One-shot fail-open flag: at most one warning per process (the
        # "at most one message per failure episode" convention). ``on_end``
        # can run concurrently (each thread ends its own spans), so the
        # flag's check-and-set takes the lock -- the same discipline as the
        # other fail-open sites in this feature (the middleware's
        # ``_disable_lock``, the OTLP wrapper's episode lock).
        self._fail_open_announced = False
        self._fail_open_lock = threading.Lock()

    def on_end(self, readable_span: ReadableSpan) -> None:
        """Scrub the ended span's attributes and events (fail-open on an unexpected shape).

        Args:
            readable_span: The ended span (a ``ReadableSpan``; see the
                class docstring for the private-container mechanism).
        """
        try:
            _scrub_span(readable_span)
        except Exception as ex:  # noqa: BLE001 -- observability fail-open, never breaks the request
            self._fail_open(ex)

    def _fail_open(self, ex: Exception) -> None:
        """Log the one-per-process fail-open warning (the observability convention).

        Args:
            ex: The unexpected exception the scrub hit.
        """
        with self._fail_open_lock:
            if self._fail_open_announced:
                return
            self._fail_open_announced = True
        logger.warning(
            "span redaction is disabled for the rest of this process: the installed "
            "OpenTelemetry SDK's private span containers are not in the expected shape "
            "(%s: %s) -- spans may leak absolute paths again",
            type(ex).__qualname__,
            ex,
        )
