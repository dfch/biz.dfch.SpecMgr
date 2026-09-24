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

"""Tests for ``telemetry/redact.py`` (feat-139-logging-telemetry, Phase 6, Tasks 6.1-6.3).

Exercises the free-text redaction backstop: the shared ``scrub_paths``
regex (what it catches, what it deliberately does not -- the documented
false-positive/negative limits), the formatter-level scrub on the final
rendered string (the JSON console handler and the file sink, including
formatter-rendered ``exc_text`` tracebacks carrying absolute file paths,
regardless of the record's originating logger), the rich handler's
``render_message`` seam, the Task 6.2 wiring onto the
``setup_logging``-installed handlers and the ``bootstrap_telemetry``
provider, and the global :class:`RedactionSpanProcessor` (a span's
attributes plus each event's attributes -- in particular the
``exception.message``/``exception.stacktrace``/``exception.type`` keys
``record_exception`` sets -- scrubbed even on a span created entirely by
the SDK's own built-in ``OpenTelemetryMiddleware``, not only on spans
this feature's own code would create).

Task 6.3's pinned canary (mirroring Task 4.4's pattern) asserts the
installed SDK's ``ReadableSpan._attributes``/``_events`` and
``Event._attributes`` private containers exist and that the processor's
replacement of them is visible end to end through an
``InMemorySpanExporter``, so a future SDK restructure fails loudly in CI
instead of silently leaking.

Title redaction is verified separately, at the exception-message level,
by ``tests/uc/models/v1/test_parser.py``'s Task 6.7 tests -- not here,
which do not assert the scrub catches an arbitrary title (it does not
attempt to).

Requires the ``mcp`` extra (``rich``, the SDK's lowlevel ``Server``, the
OTel SDK) plus ``opentelemetry-sdk``, same as ``telemetry/redact.py``
itself.
"""

import io
import json
import logging
import sys
import unittest
from pathlib import Path
from types import TracebackType
from unittest import mock

from mcp.server._otel import OpenTelemetryMiddleware
from mcp.server.lowlevel import Server
from opentelemetry import trace as trace_api
from opentelemetry.attributes import BoundedAttributes
from opentelemetry.sdk.trace import Event, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from rich.console import Console

import biz.dfch.specmgr.telemetry.otel as otel
from biz.dfch.specmgr.telemetry import redact
from biz.dfch.specmgr.telemetry.logging import JsonFormatter, SpecmgrRichHandler, setup_logging
from tests.telemetry.test_middleware import _invoke, _make_ctx, _raises
from tests.telemetry.test_otel import _config, _isolated_otel_globals, _parse_json_objects

#: The pinned replacement token (the orchestrator's pin: exactly this string).
TOKEN = redact.REDACTED_PATH_TOKEN
#: A fake POSIX absolute path every scrub case embeds.
FAKE_POSIX_PATH = "/home/agent/docs/uc-1234-5678/README.md"
#: A fake Windows drive path (raw and JSON-escaped spellings).
FAKE_WINDOWS_PATH = "C:\\Users\\agent\\docs\\req-42.md"
FAKE_WINDOWS_PATH_JSON_ESCAPED = "C:\\\\Users\\\\agent\\\\docs\\\\req-42.md"
#: A fake UNC path (raw and JSON-escaped spellings).
FAKE_UNC_PATH = "\\\\fileserver\\share\\doc.md"
FAKE_UNC_PATH_JSON_ESCAPED = "\\\\\\\\fileserver\\\\share\\\\doc.md"

#: This test file's own absolute path: the natural, real path a
#: formatter-rendered ``exc_text`` traceback (or a span's
#: ``exception.stacktrace``) carries for a test-local exception.
TEST_FILE_PATH = str(Path(__file__).resolve())


def _make_record(
    logger_name: str,
    message: str,
    *,
    level: int = logging.ERROR,
    extra: dict[str, object] | None = None,
    exc_info: tuple[type[BaseException] | None, BaseException | None, TracebackType | None] | None = None,
) -> logging.LogRecord:
    """Build a plain ``LogRecord`` under ``logger_name`` (any originating logger)."""
    result = logging.getLogger(logger_name).makeRecord(
        logger_name, level, __file__, 1, message, (), exc_info, extra=extra
    )
    return result


class TestScrubPaths(unittest.TestCase):
    """The shared regex scrub: what it catches and what it deliberately does not (Task 6.1)."""

    def test_the_replacement_token_is_exactly_pinned(self):
        sut = TOKEN

        self.assertEqual(sut, "<redacted-path>")

    def test_a_posix_absolute_path_is_replaced_by_the_token(self):
        sut = redact.scrub_paths

        result = sut(f"failed to delete {FAKE_POSIX_PATH}: no such file")

        self.assertIn(TOKEN, result)
        self.assertNotIn(FAKE_POSIX_PATH, result)

    def test_a_windows_drive_path_is_replaced_in_its_raw_and_json_escaped_spellings(self):
        sut = redact.scrub_paths

        result_raw = sut(f"file missing at {FAKE_WINDOWS_PATH}")
        result_json = sut(f"file missing at {FAKE_WINDOWS_PATH_JSON_ESCAPED}")

        self.assertNotIn(FAKE_WINDOWS_PATH, result_raw)
        self.assertIn(TOKEN, result_raw)
        self.assertNotIn(FAKE_WINDOWS_PATH_JSON_ESCAPED, result_json)
        self.assertIn(TOKEN, result_json)

    def test_a_unc_path_is_replaced_in_its_raw_and_json_escaped_spellings(self):
        sut = redact.scrub_paths

        result_raw = sut(f"file missing at {FAKE_UNC_PATH}")
        result_json = sut(f"file missing at {FAKE_UNC_PATH_JSON_ESCAPED}")

        self.assertNotIn(FAKE_UNC_PATH, result_raw)
        self.assertIn(TOKEN, result_raw)
        self.assertNotIn(FAKE_UNC_PATH_JSON_ESCAPED, result_json)
        self.assertIn(TOKEN, result_json)

    def test_a_file_line_reference_keeps_the_line_number(self):
        sut = redact.scrub_paths

        result = sut("raised at /home/agent/server.py:123")

        self.assertEqual(result, f"raised at {TOKEN}:123")

    def test_a_sentence_final_period_is_not_swallowed(self):
        sut = redact.scrub_paths

        result = sut("deleted /home/agent/a.txt. next sentence")

        self.assertEqual(result, f"deleted {TOKEN}. next sentence")

    def test_a_single_segment_posix_path_is_left_alone(self):
        # Documented false negative: the two-segment minimum is what keeps
        # single-slash tokens like `tools/call` out of the match.
        sut = redact.scrub_paths

        result = sut("the /tmp and /etc and tools/call and rich/json and OTLP/HTTP shapes")

        self.assertEqual(result, "the /tmp and /etc and tools/call and rich/json and OTLP/HTTP shapes")

    def test_url_and_scheme_slash_shapes_are_left_alone(self):
        sut = redact.scrub_paths

        result = sut("uri specmgr://version, url http://127.0.0.1:1, url https://example.com, matrix 3.11/3.12/3.13")

        self.assertEqual(
            result, "uri specmgr://version, url http://127.0.0.1:1, url https://example.com, matrix 3.11/3.12/3.13"
        )

    def test_the_scrub_is_idempotent_on_its_own_token(self):
        sut = redact.scrub_paths

        once = sut(f"at {FAKE_POSIX_PATH} done")
        twice = sut(once)

        self.assertEqual(once, twice)

    def test_non_path_text_is_unchanged(self):
        sut = redact.scrub_paths

        result = sut("a plain message with no paths at all")

        self.assertEqual(result, "a plain message with no paths at all")


class TestFormatterScrub(unittest.TestCase):
    """The formatter-level scrub on the final rendered string, any originating logger (Task 6.1/6.3)."""

    def _render(self, record: logging.LogRecord) -> str:
        buffer = io.StringIO()
        handler = logging.StreamHandler(buffer)
        handler.setFormatter(redact.ScrubbingFormatter(JsonFormatter()))
        handler.emit(record)
        result = buffer.getvalue()
        return result

    def test_a_path_in_the_message_is_scrubbed_from_the_final_rendered_string(self):
        sut = self._render
        record = _make_record("biz.dfch.specmgr.test", f"failed to delete {FAKE_POSIX_PATH}")

        result = sut(record)

        self.assertIn(TOKEN, result)
        self.assertNotIn(FAKE_POSIX_PATH, result)

    def test_a_path_in_the_exception_extra_is_scrubbed_from_the_final_rendered_string(self):
        # The middleware's own error-record shape (Phase 3 pin): an explicit
        # `exception` extra whose message/traceback carry the path.
        sut = self._render
        record = _make_record(
            "biz.dfch.specmgr.telemetry",
            "tool get_req failed",
            extra={
                "correlation_id": "abc123",
                "exception": {
                    "type": "DeleteError",
                    "message": f"failed to delete {FAKE_POSIX_PATH}",
                    "traceback": f'Traceback (most recent call last):\n  File "{TEST_FILE_PATH}", line 1\n',
                },
            },
        )

        result = json.loads(sut(record))

        self.assertEqual(result["exception"]["message"], f"failed to delete {TOKEN}")
        self.assertNotIn(FAKE_POSIX_PATH, json.dumps(result))
        self.assertNotIn(TEST_FILE_PATH, json.dumps(result))

    def test_a_formatter_rendered_exc_text_traceback_is_scrubbed(self):
        # The pinned case: a standard `exc_info` record -- the formatter
        # renders `exc_text`, whose traceback embeds absolute file paths
        # (this test file's own, plus the exception message's fake one).
        # A handler-attached logging.Filter cannot see that `exc_text`.
        sut = self._render
        try:
            raise RuntimeError(f"failed to delete {FAKE_POSIX_PATH}: no such file")
        except RuntimeError:
            exc_info = sys.exc_info()
        record = _make_record("mcp.server.runner", "request failed", exc_info=exc_info)

        result = sut(record)

        self.assertIn(TOKEN, result)
        self.assertNotIn(FAKE_POSIX_PATH, result)
        self.assertNotIn(TEST_FILE_PATH, result)

    def test_a_third_party_originating_logger_is_covered_too(self):
        # The scrub is formatter-level: it applies to every rendered record
        # reaching the handler regardless of the record's logger name
        # (SPECMGR_LOG_ENABLED=true reconfigures the root logger, so
        # third-party/SDK loggers share these handlers).
        sut = self._render
        record = _make_record(
            "opentelemetry.exporter.otlp.proto.http.trace_exporter",
            f"Max retries exceeded with url: {FAKE_POSIX_PATH}",
        )

        result = sut(record)

        self.assertIn(TOKEN, result)
        self.assertNotIn(FAKE_POSIX_PATH, result)

    def test_the_json_console_handler_carries_the_scrubbing_formatter(self):
        # Task 6.2 wiring: the JSON console branch wraps JsonFormatter.
        stderr = io.StringIO()
        with mock.patch.object(sys, "stderr", stderr):
            from biz.dfch.specmgr.telemetry.logging import _build_console_handler

            handler = _build_console_handler(_config(log_enabled=True, log_format="json"))
            handler.close()

        self.assertIsInstance(handler.formatter, redact.ScrubbingFormatter)
        self.assertIsInstance(handler.formatter._delegate, JsonFormatter)

    def test_the_file_sink_handler_carries_the_scrubbing_formatter_and_scrubs_what_it_writes(self):
        # Task 6.2/6.3: the always-JSON file sink wraps JsonFormatter, and a
        # record emitted through it lands in the file with its path scrubbed
        # (ACC-009: the file sink is JSON regardless of the console format).
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            sink_path = str(Path(tmp) / "sink.jsonl")
            from biz.dfch.specmgr.telemetry.logging import _build_file_handler

            handler = _build_file_handler(sink_path)
            record = _make_record("mcp.server.runner", f"failed to delete {FAKE_POSIX_PATH}")
            handler.handle(record)
            handler.close()
            text = Path(sink_path).read_text(encoding="utf-8")

        self.assertIsInstance(handler.formatter, redact.ScrubbingFormatter)
        self.assertIsInstance(handler.formatter._delegate, JsonFormatter)
        self.assertIn(TOKEN, text)
        self.assertNotIn(FAKE_POSIX_PATH, text)


class TestRichHandlerScrub(unittest.TestCase):
    """The rich format's render_message seam scrub (Task 6.1/6.2/6.3)."""

    def setUp(self) -> None:
        self._buffer = io.StringIO()
        # A wide console so the message text is not soft-wrapped mid-token
        # (rich is the local-dev format; the seam under test is the
        # message-text funnel, not the rich-rendered traceback).
        sut_console = Console(file=self._buffer, width=400, force_terminal=False)
        self._handler = redact.ScrubbingSpecmgrRichHandler(console=sut_console, rich_tracebacks=True)

    def tearDown(self) -> None:
        self._handler.close()

    def test_the_rich_console_handler_is_the_scrubbing_subclass(self):
        sut = self._handler

        self.assertIsInstance(sut, SpecmgrRichHandler)
        self.assertIsInstance(sut, redact.ScrubbingSpecmgrRichHandler)

    def test_a_path_in_the_rich_message_text_is_scrubbed(self):
        sut = self._handler
        record = _make_record("biz.dfch.specmgr.test", f"failed to delete {FAKE_POSIX_PATH}")

        sut.handle(record)

        text = self._buffer.getvalue()
        self.assertIn(TOKEN, text)
        self.assertNotIn(FAKE_POSIX_PATH, text)

    def test_a_path_in_the_rich_structured_exception_field_is_scrubbed(self):
        # The exception field renders as `Type: message` into the combined
        # message text (the Phase 2 pin) -- that text goes through the seam.
        sut = self._handler
        record = _make_record(
            "biz.dfch.specmgr.telemetry",
            "tool get_req failed",
            extra={
                "correlation_id": "abc123",
                "exception": {"type": "DeleteError", "message": f"failed to delete {FAKE_POSIX_PATH}"},
            },
        )

        sut.handle(record)

        text = self._buffer.getvalue()
        self.assertIn(TOKEN, text)
        self.assertNotIn(FAKE_POSIX_PATH, text)


class TestLoggingWiring(unittest.TestCase):
    """Task 6.2: every handler setup_logging installs carries the scrub."""

    def setUp(self) -> None:
        self._root = logging.getLogger()
        self._saved_handlers = list(self._root.handlers)
        self._saved_level = self._root.level
        self._root.handlers.clear()

    def tearDown(self) -> None:
        for handler in list(self._root.handlers):
            self._root.removeHandler(handler)
            handler.close()
        self._root.handlers = self._saved_handlers
        self._root.level = self._saved_level

    def test_enabled_json_logging_installs_a_scrubbed_console_formatter(self):
        stderr = io.StringIO()
        with mock.patch.object(sys, "stderr", stderr):
            setup_logging(_config(log_enabled=True, log_format="json"))

        console_handlers = [h for h in self._root.handlers if isinstance(h, logging.StreamHandler)]
        self.assertEqual(len(console_handlers), 1)
        self.assertIsInstance(console_handlers[0].formatter, redact.ScrubbingFormatter)
        self.assertIsInstance(console_handlers[0].formatter._delegate, JsonFormatter)

    def test_enabled_rich_logging_installs_the_scrubbing_rich_handler(self):
        stderr = io.StringIO()
        with mock.patch.object(sys, "stderr", stderr):
            setup_logging(_config(log_enabled=True, log_format="rich"))

        handlers = self._root.handlers
        self.assertEqual(len(handlers), 1)
        self.assertIsInstance(handlers[0], redact.ScrubbingSpecmgrRichHandler)

    def test_enabled_file_sink_installs_a_scrubbed_json_formatter(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            sink_path = str(Path(tmp) / "sink.jsonl")
            stderr = io.StringIO()
            with mock.patch.object(sys, "stderr", stderr):
                setup_logging(
                    _config(log_enabled=True, log_format="json", log_file_enabled=True, log_file_path=sink_path)
                )
            file_handlers = [h for h in self._root.handlers if isinstance(h, logging.FileHandler)]
            self.assertEqual(len(file_handlers), 1)
            self.assertIsInstance(file_handlers[0].formatter, redact.ScrubbingFormatter)
            self.assertIsInstance(file_handlers[0].formatter._delegate, JsonFormatter)

    def test_disabled_logging_installs_no_scrubbed_handler(self):
        stderr = io.StringIO()
        with mock.patch.object(sys, "stderr", stderr):
            setup_logging(_config())

        for handler in self._root.handlers:
            self.assertNotIsInstance(getattr(handler, "formatter", None), redact.ScrubbingFormatter)
            self.assertNotIsInstance(handler, redact.ScrubbingSpecmgrRichHandler)


class TestSpanProcessorScrub(unittest.TestCase):
    """The global SpanProcessor: attributes plus each event's attributes (Task 6.1/6.3)."""

    def _provider_and_exporter(
        self, *, batch: bool = False, schedule_delay_millis: int = 50
    ) -> tuple[TracerProvider, InMemorySpanExporter]:
        # The Task 6.2/1a.3-confirmed order: the redaction processor first,
        # the exporting processor second.
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(redact.RedactionSpanProcessor())
        if batch:
            provider.add_span_processor(BatchSpanProcessor(exporter, schedule_delay_millis=schedule_delay_millis))
        else:
            provider.add_span_processor(SimpleSpanProcessor(exporter))
        result = (provider, exporter)
        return result

    def _exception_event(self, span) -> Event:
        events = [event for event in span.events if event.name == "exception"]
        self.assertEqual(len(events), 1)
        result = events[0]
        return result

    def test_a_span_attribute_carrying_a_path_is_scrubbed_and_non_string_attributes_pass_through(self):
        provider, exporter = self._provider_and_exporter()
        tracer = provider.get_tracer("test")

        try:
            with tracer.start_as_current_span(
                "op", attributes={"mcp.tool.name": "get_req", "doc.path": FAKE_POSIX_PATH, "count": 3}
            ):
                pass
            spans = exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)
            span = spans[0]

            self.assertEqual(span.attributes["doc.path"], TOKEN)
            self.assertNotIn(FAKE_POSIX_PATH, json.dumps(dict(span.attributes)))
            self.assertEqual(span.attributes["mcp.tool.name"], "get_req")
            self.assertEqual(span.attributes["count"], 3)
        finally:
            provider.shutdown()

    def test_a_span_exception_event_message_and_stacktrace_are_scrubbed_and_type_is_not(self):
        provider, exporter = self._provider_and_exporter()
        tracer = provider.get_tracer("test")

        try:
            # The SDK span context manager records the exception (and does
            # not suppress it) -- assertRaises is how the test observes it.
            with self.assertRaises(RuntimeError):
                with tracer.start_as_current_span("op"):
                    raise RuntimeError(f"failed to delete {FAKE_POSIX_PATH}: no such file")
            spans = exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)
            event = self._exception_event(spans[0])
            attributes = event.attributes

            self.assertIn(TOKEN, attributes["exception.message"])
            self.assertNotIn(FAKE_POSIX_PATH, attributes["exception.message"])
            self.assertNotIn(FAKE_POSIX_PATH, attributes["exception.stacktrace"])
            self.assertNotIn(TEST_FILE_PATH, attributes["exception.stacktrace"])
            self.assertIn(TOKEN, attributes["exception.stacktrace"])
            self.assertEqual(attributes["exception.type"], "RuntimeError")
            # The API's use_span (what start_as_current_span and the SDK
            # middleware's otel_span both build on) records the exception
            # with record_exception's default escaped=False -- pinned so a
            # change to that SDK behavior is visible here.
            self.assertEqual(attributes["exception.escaped"], "False")
        finally:
            provider.shutdown()

    def test_the_batch_chain_export_sees_the_scrubbed_containers(self):
        # Task 1a.3 proved the replacement visible in both the simple and
        # the batch chain; the production bootstrap uses the batch one.
        provider, exporter = self._provider_and_exporter(batch=True)
        tracer = provider.get_tracer("test")

        try:
            with tracer.start_as_current_span("op", attributes={"doc.path": FAKE_POSIX_PATH}):
                pass
            provider.force_flush()
            spans = exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)

            self.assertEqual(spans[0].attributes["doc.path"], TOKEN)
        finally:
            provider.shutdown()

    def test_a_span_with_no_path_content_keeps_its_original_container(self):
        # The processor replaces the private containers only when the scrub
        # actually changed a value (no needless container swap per span).
        provider, exporter = self._provider_and_exporter()
        tracer = provider.get_tracer("test")

        try:
            live_attributes = None
            with tracer.start_as_current_span("op", attributes={"mcp.tool.name": "get_req"}) as span:
                live_attributes = span._attributes
            spans = exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)

            self.assertIs(spans[0]._attributes, live_attributes)
        finally:
            provider.shutdown()

    def test_a_span_created_entirely_by_the_sdk_builtin_middleware_is_scrubbed(self):
        # Task 6.3's mandated case: the span is created by the SDK's own
        # built-in OpenTelemetryMiddleware (via the lowlevel Server's
        # seeded middleware list), and its exception is recorded by the
        # middleware's own record_exception/set_status calls -- an
        # exception whose message carries a fake absolute path.
        with _isolated_otel_globals():
            provider, exporter = self._provider_and_exporter()
            trace_api.set_tracer_provider(provider)
            server = Server("redaction-test")
            self.assertIsInstance(server.middleware[0], OpenTelemetryMiddleware)
            sut = server.middleware[0]
            ctx = _make_ctx("tools/call", {"name": "get_feat_template", "arguments": {}})

            with self.assertRaises(RuntimeError):
                _invoke(sut, ctx, _raises(RuntimeError(f"failed to delete {FAKE_POSIX_PATH}: no such file")))

            spans = exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)
            span = spans[0]
            event = self._exception_event(span)
            attributes = event.attributes
            self.assertEqual(span.name, "tools/call get_feat_template")
            self.assertIn(TOKEN, attributes["exception.message"])
            self.assertNotIn(FAKE_POSIX_PATH, attributes["exception.message"])
            self.assertNotIn(FAKE_POSIX_PATH, attributes["exception.stacktrace"])
            self.assertNotIn(TEST_FILE_PATH, attributes["exception.stacktrace"])
            self.assertEqual(attributes["exception.type"], "RuntimeError")
            self.assertEqual(span.attributes["mcp.method.name"], "tools/call")
            self.assertEqual(span.attributes["gen_ai.tool.name"], "get_feat_template")
        provider.shutdown()


class TestSpanProcessorCanary(unittest.TestCase):
    """Task 6.3's pinned canary: the relied-upon private containers exist and the replacement is visible (mirrors Task 4.4's pattern)."""

    def test_the_installed_sdk_span_private_containers_exist(self):
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(redact.RedactionSpanProcessor())
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("canary")

        try:
            with tracer.start_as_current_span("canary", attributes={"doc.path": FAKE_POSIX_PATH}):
                pass
            spans = exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)
            span = spans[0]

            # The processor's mechanism reads these exact private names --
            # a future SDK restructure that renames/relocates them must fail
            # this test loudly instead of silently leaking.
            self.assertTrue(hasattr(span, "_attributes"))
            self.assertTrue(hasattr(span, "_events"))
            self.assertIsInstance(span._attributes, BoundedAttributes)
            for event in span._events:
                self.assertTrue(hasattr(event, "_attributes"))
        finally:
            provider.shutdown()

    def test_the_processor_replacement_is_visible_end_to_end_through_the_exporter(self):
        # The export path stores the very ReadableSpan the processor saw:
        # after the processor replaces span._attributes, the exported
        # span's public attributes view shows the scrubbed value -- and the
        # container is no longer the live span's original one.
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(redact.RedactionSpanProcessor())
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer("canary")

        try:
            live_attributes = None
            with tracer.start_as_current_span("canary", attributes={"doc.path": FAKE_POSIX_PATH}) as span:
                live_attributes = span._attributes
            spans = exporter.get_finished_spans()
            self.assertEqual(len(spans), 1)
            span = spans[0]

            self.assertIsNot(span._attributes, live_attributes)
            self.assertEqual(span.attributes["doc.path"], TOKEN)
        finally:
            provider.shutdown()


class TestSpanProcessorFailOpen(unittest.TestCase):
    """The observability fail-open convention: an unexpected span shape never breaks the request (Task 6.1)."""

    def setUp(self) -> None:
        self._logger = logging.getLogger("biz.dfch.specmgr.telemetry")
        self._saved_handlers = list(self._logger.handlers)
        self._saved_level = self._logger.level
        self._saved_propagate = self._logger.propagate

        class _Capture(logging.Handler):
            """A handler that keeps every message it receives."""

            def __init__(self) -> None:
                super().__init__(level=logging.DEBUG)
                self.messages: list[str] = []

            def emit(self, record: logging.LogRecord) -> None:
                self.messages.append(record.getMessage())

        self._capture = _Capture()
        self._logger.addHandler(self._capture)
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

    def tearDown(self) -> None:
        self._logger.removeHandler(self._capture)
        self._logger.handlers = self._saved_handlers
        self._logger.setLevel(self._saved_level)
        self._logger.propagate = self._saved_propagate

    class _BogusSpan:
        """A span-shaped object carrying none of the SDK's private containers."""

    def test_an_unexpected_span_shape_does_not_propagate(self):
        sut = redact.RedactionSpanProcessor()

        result = sut.on_end(TestSpanProcessorFailOpen._BogusSpan())

        self.assertIsNone(result)

    def test_the_fail_open_warning_is_logged_exactly_once_per_processor(self):
        sut = redact.RedactionSpanProcessor()

        sut.on_end(TestSpanProcessorFailOpen._BogusSpan())
        sut.on_end(TestSpanProcessorFailOpen._BogusSpan())

        self.assertEqual(len(self._capture.messages), 1)
        self.assertIn("span redaction is disabled", self._capture.messages[0])


class TestTelemetryWiring(unittest.TestCase):
    """Task 6.2: the bootstrap's TracerProvider carries the processor before the exporter."""

    def setUp(self) -> None:
        self._isolation = _isolated_otel_globals()
        self._isolation.__enter__()
        self._stderr_buf = io.StringIO()
        self._stdout_buf = io.StringIO()
        self._stderr_patcher = mock.patch.object(sys, "stderr", self._stderr_buf)
        self._stdout_patcher = mock.patch.object(sys, "stdout", self._stdout_buf)
        self._stderr_patcher.start()
        self._stdout_patcher.start()

    def tearDown(self) -> None:
        otel.shutdown_telemetry()
        self._stderr_patcher.stop()
        self._stdout_patcher.stop()
        self._isolation.__exit__(None, None, None)

    def test_the_bootstrap_adds_the_redaction_processor_before_the_batch_processor(self):
        otel.bootstrap_telemetry(_config(otel_enabled=True, otel_exporter="console"))
        assert otel._tracer_provider is not None
        chain = otel._tracer_provider._active_span_processor._span_processors

        self.assertEqual(len(chain), 2)
        self.assertIsInstance(chain[0], redact.RedactionSpanProcessor)
        self.assertIsInstance(chain[1], BatchSpanProcessor)

    def test_a_production_chain_span_with_a_path_and_exception_exports_scrubbed(self):
        # End to end over the real bootstrap: TracerProvider ->
        # RedactionSpanProcessor -> BatchSpanProcessor -> console exporter
        # (out=sys.stderr). The exception's stacktrace carries this test
        # file's own absolute path -- it must not reach the export.
        otel.bootstrap_telemetry(_config(otel_enabled=True, otel_exporter="console"))
        tracer = trace_api.get_tracer("test")

        # The SDK span context manager records the exception (and does not
        # suppress it) -- assertRaises is how the test observes it.
        with self.assertRaises(RuntimeError):
            with tracer.start_as_current_span("scrub-check", attributes={"doc.path": FAKE_POSIX_PATH}):
                raise RuntimeError(f"failed to delete {FAKE_POSIX_PATH}: no such file")
        assert otel._tracer_provider is not None
        otel._tracer_provider.force_flush()

        # Assert on the scrubbed surfaces (the span's attributes plus each
        # event's attributes -- the pinned scope), not on the whole export
        # blob: the span's status *description* (the set_status(str(e))
        # payload) is not an attribute container and is a documented
        # residual outside the scrub's scope (see telemetry/redact.py).
        spans = [obj for obj in _parse_json_objects(self._stderr_buf.getvalue()) if obj.get("name") == "scrub-check"]
        self.assertEqual(len(spans), 1)
        span = spans[0]
        self.assertEqual(span["attributes"]["doc.path"], TOKEN)
        events = [event for event in span["events"] if event["name"] == "exception"]
        self.assertEqual(len(events), 1)
        event_attributes = events[0]["attributes"]
        self.assertIn(TOKEN, event_attributes["exception.message"])
        self.assertNotIn(FAKE_POSIX_PATH, event_attributes["exception.message"])
        self.assertNotIn(FAKE_POSIX_PATH, event_attributes["exception.stacktrace"])
        self.assertNotIn(TEST_FILE_PATH, event_attributes["exception.stacktrace"])
        self.assertIn(TOKEN, event_attributes["exception.stacktrace"])
