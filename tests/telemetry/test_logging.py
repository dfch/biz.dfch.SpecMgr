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

"""Tests for ``telemetry/logging.py`` (feat-139-logging-telemetry, Phase 2, Task 2.2).

Covers VCR ``0a1c2f63-9576-4463-bf40-8f771f14fefb``'s acceptance
criteria AC-001 (logging off by default: the setup is a no-op when
disabled and, in the default config, leaves the SDK's own default
handler set in place) and AC-005 (the file sink's behavior), plus the
pinned record shape and the two invariants Task 2.2 requires: stdout is
never written to in either format, and enabling ``SPECMGR_LOG_ENABLED``
after the SDK's own default ``configure_logging()`` call actually changes
the effective format/handlers (no silent no-op).

Requires the ``mcp`` extra (``rich``/the SDK's own ``configure_logging``),
same as ``telemetry/logging.py`` itself.
"""

import importlib
import io
import json
import logging
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from types import TracebackType
from unittest import mock

from rich.console import Console
from rich.logging import RichHandler

from biz.dfch.specmgr.telemetry.config import (
    ENV_LOG_ENABLED,
    ENV_LOG_FILE_ENABLED,
    ENV_LOG_FILE_PATH,
    ENV_LOG_FORMAT,
    ENV_LOG_LEVEL,
    ENV_OTEL_ENABLED,
    ENV_OTEL_ENDPOINT,
    ENV_OTEL_EXPORTER,
    TelemetryConfig,
)
from biz.dfch.specmgr.telemetry.logging import (
    JsonFormatter,
    SpecmgrRichHandler,
    setup_logging,
)

#: The logger name used for every test record (no specmgr handler is ever
#: attached to it; records are emitted through the root logger).
_LOGGER_NAME = "biz.dfch.specmgr.test"

#: All eight telemetry env vars, removed from the env below so the server
#: re-import tests pin exactly the environment they assert on.
_ALL_TELEMETRY_ENV_VARS = (
    ENV_LOG_ENABLED,
    ENV_LOG_LEVEL,
    ENV_LOG_FORMAT,
    ENV_LOG_FILE_ENABLED,
    ENV_LOG_FILE_PATH,
    ENV_OTEL_ENABLED,
    ENV_OTEL_EXPORTER,
    ENV_OTEL_ENDPOINT,
)


def _config(**overrides: object) -> TelemetryConfig:
    """Build a default (disabled) ``TelemetryConfig`` with the given overrides applied."""
    base: dict[str, object] = {
        "log_enabled": False,
        "log_level": "INFO",
        "log_format": "rich",
        "log_file_enabled": False,
        "log_file_path": None,
        "otel_enabled": False,
        "otel_exporter": "console",
        "otel_endpoint": None,
    }
    base.update(overrides)
    return TelemetryConfig(**base)


def _record(
    message: str,
    *,
    level: int = logging.INFO,
    args: tuple[object, ...] = (),
    extra: dict[str, object] | None = None,
) -> logging.LogRecord:
    """Build a plain ``LogRecord`` (no ``exc_info``) with optional structured extras."""
    result = logging.getLogger(_LOGGER_NAME).makeRecord(
        _LOGGER_NAME, level, __file__, 1, message, args, None, extra=extra
    )
    return result


def _record_with_runtime_error(message: str) -> logging.LogRecord:
    """Build a ``LogRecord`` whose standard ``exc_info`` is a ``RuntimeError("derp")``."""
    exc_info: tuple[type[BaseException] | None, BaseException | None, TracebackType | None]
    try:
        raise RuntimeError("derp")
    except RuntimeError:
        exc_info = sys.exc_info()
    result = logging.getLogger(_LOGGER_NAME).makeRecord(_LOGGER_NAME, logging.ERROR, __file__, 1, message, (), exc_info)
    return result


class _RootLoggerTestCase(unittest.TestCase):
    """Save/restore the root logger's handler set and level so no handler leaks between tests."""

    def setUp(self) -> None:
        self.root = logging.getLogger()
        self.saved_handlers = list(self.root.handlers)
        self.saved_level = self.root.level

    def tearDown(self) -> None:
        for handler in list(self.root.handlers):
            if handler not in self.saved_handlers:
                self.root.removeHandler(handler)
                handler.close()
        self.root.handlers = self.saved_handlers
        self.root.level = self.saved_level

    def _clear_root_handlers(self) -> None:
        """Remove (and close) every handler currently on the root logger.

        Makes emit-capture tests deterministic no matter what the earlier
        server import in this test worker left behind; :meth:`tearDown`
        restores the saved set afterwards.
        """
        for handler in list(self.root.handlers):
            self.root.removeHandler(handler)
            handler.close()


class TestJsonFormatter(unittest.TestCase):
    """The JSON formatter's pinned record shape (Task 2.1)."""

    def test_plain_record_renders_valid_json_with_the_pinned_base_fields(self):
        sut = JsonFormatter()
        record = _record("hello world")

        formatted = sut.format(record)

        parsed = json.loads(formatted)
        self.assertEqual(set(parsed), {"timestamp", "level", "logger", "message"})
        self.assertEqual(parsed["message"], "hello world")
        self.assertEqual(parsed["level"], "INFO")
        self.assertEqual(parsed["logger"], _LOGGER_NAME)
        timestamp = datetime.fromisoformat(parsed["timestamp"])
        self.assertEqual(timestamp.tzinfo, timezone.utc)

    def test_every_structured_extra_is_carried(self):
        sut = JsonFormatter()
        extra = {
            "correlation_id": "abcdef12",
            "method": "tools/call",
            "item_type": "tool",
            "item_name": "set_status",
            "domain": "req",
            "status": "accepted",
            "duration_ms": 12.5,
            "exception": {
                "type": "ValueError",
                "message": "boom",
                "traceback": "Traceback (most recent call last): ...",
            },
        }
        record = _record("invocation", extra=extra)

        parsed = json.loads(sut.format(record))

        for name, value in extra.items():
            self.assertEqual(parsed[name], value, name)

    def test_only_present_extras_are_carried(self):
        sut = JsonFormatter()
        record = _record("partial", extra={"correlation_id": "abc", "duration_ms": 3.0})

        parsed = json.loads(sut.format(record))

        self.assertEqual(parsed["correlation_id"], "abc")
        self.assertEqual(parsed["duration_ms"], 3.0)
        for absent in ("method", "item_type", "item_name", "domain", "status", "exception"):
            self.assertNotIn(absent, parsed)

    def test_exception_is_derived_from_exc_info_when_no_extra_is_present(self):
        sut = JsonFormatter()
        record = _record_with_runtime_error("it failed")

        parsed = json.loads(sut.format(record))

        exception = parsed["exception"]
        self.assertEqual(exception["type"], "RuntimeError")
        self.assertEqual(exception["message"], "derp")
        self.assertIn("RuntimeError: derp", exception["traceback"])

    def test_explicit_exception_extra_is_carried_verbatim(self):
        sut = JsonFormatter()
        exception = {"type": "ReqNotFoundError", "message": "no such req", "traceback": None}
        record = _record("x", extra={"exception": exception})

        parsed = json.loads(sut.format(record))

        self.assertEqual(parsed["exception"], exception)

    def test_message_args_are_interpolated(self):
        sut = JsonFormatter()
        record = _record("count %d", args=(3,))

        parsed = json.loads(sut.format(record))

        self.assertEqual(parsed["message"], "count 3")

    def test_output_is_a_single_physical_line(self):
        sut = JsonFormatter()
        record = _record("line one\nline two")

        formatted = sut.format(record)

        self.assertNotIn("\n", formatted)
        self.assertEqual(json.loads(formatted)["message"], "line one\nline two")

    def test_non_ascii_message_round_trips(self):
        sut = JsonFormatter()
        record = _record("über")

        formatted = sut.format(record)

        self.assertEqual(json.loads(formatted)["message"], "über")


class TestSpecmgrRichHandler(unittest.TestCase):
    """The rich console handler renders the same fields human-readably (Task 2.1)."""

    def _handler_with_buffer(self) -> tuple[SpecmgrRichHandler, io.StringIO]:
        buffer = io.StringIO()
        result = SpecmgrRichHandler(console=Console(file=buffer, width=200), rich_tracebacks=True)
        return result, buffer

    def test_plain_record_renders_just_the_message(self):
        handler, buffer = self._handler_with_buffer()

        handler.handle(_record("plain message"))

        output = buffer.getvalue()
        self.assertIn("plain message", output)
        self.assertNotIn("correlation_id", output)
        self.assertNotIn("exception=", output)

    def test_structured_fields_render_human_readably(self):
        handler, buffer = self._handler_with_buffer()
        extra = {
            "correlation_id": "abcdef12",
            "method": "tools/call",
            "item_type": "tool",
            "item_name": "set_status",
            "domain": "req",
            "status": "accepted",
            "duration_ms": 12.5,
            "exception": {"type": "ValueError", "message": "boom"},
        }

        handler.handle(_record("invocation", extra=extra))

        output = buffer.getvalue()
        for part in (
            "correlation_id=abcdef12",
            "method=tools/call",
            "item_type=tool",
            "item_name=set_status",
            "domain=req",
            "status=accepted",
            "duration_ms=12.5",
            "exception=ValueError: boom",
        ):
            self.assertIn(part, output, part)

    def test_exception_record_renders_type_and_message_plus_the_rich_traceback(self):
        handler, buffer = self._handler_with_buffer()

        handler.handle(_record_with_runtime_error("it failed"))

        output = buffer.getvalue()
        self.assertIn("it failed", output)
        self.assertIn("exception=RuntimeError: derp", output)
        self.assertIn("Traceback", output)


class TestSetupDisabled(_RootLoggerTestCase):
    """``log_enabled=False``: the setup is a no-op (ACC-001's baseline)."""

    def test_disabled_config_is_a_no_op_on_the_root_logger(self):
        sentinel = logging.StreamHandler(stream=io.StringIO())
        self.root.addHandler(sentinel)
        self.root.setLevel(logging.WARNING)
        before = list(self.root.handlers)

        setup_logging(_config())

        self.assertEqual(self.root.handlers, before)
        self.assertIn(sentinel, self.root.handlers)
        self.assertEqual(self.root.level, logging.WARNING)

    def test_disabled_config_with_the_file_switch_on_installs_nothing(self):
        sentinel = logging.StreamHandler(stream=io.StringIO())
        self.root.addHandler(sentinel)
        before = list(self.root.handlers)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sink.jsonl")

            setup_logging(_config(log_file_enabled=True, log_file_path=path))

            self.assertEqual(self.root.handlers, before)
            self.assertFalse(os.path.exists(path))


class TestStdoutSafety(_RootLoggerTestCase):
    """stdout is never written to, in either format (Task 2.2)."""

    def _emit_through_setup(self, config: TelemetryConfig, message: str) -> tuple[str, str]:
        self._clear_root_handlers()
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch.object(sys, "stdout", stdout),
            mock.patch.object(sys, "stderr", stderr),
        ):
            setup_logging(config)
            logging.getLogger(_LOGGER_NAME).info(message)
        return stdout.getvalue(), stderr.getvalue()

    def test_rich_format_never_writes_stdout(self):
        stdout, stderr = self._emit_through_setup(_config(log_enabled=True, log_format="rich"), "hello rich")

        self.assertEqual(stdout, "")
        self.assertIn("hello rich", stderr)

    def test_json_format_never_writes_stdout(self):
        stdout, stderr = self._emit_through_setup(_config(log_enabled=True, log_format="json"), "hello json")

        self.assertEqual(stdout, "")
        parsed = json.loads(stderr.strip())
        self.assertEqual(parsed["message"], "hello json")

    def test_file_sink_never_writes_stdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sink.jsonl")
            stdout, stderr = self._emit_through_setup(
                _config(log_enabled=True, log_format="rich", log_file_enabled=True, log_file_path=path),
                "hello both",
            )
            self.assertEqual(stdout, "")
            self.assertIn("hello both", stderr)
            with open(path, encoding="utf-8") as f:
                parsed = json.loads(f.readline())
        self.assertEqual(parsed["message"], "hello both")


class TestFileSink(_RootLoggerTestCase):
    """The opt-in file sink (AC-005): JSON-only, active only under both switches."""

    def _setup_with_file_sink(self, tmp: str, *, log_format: str = "rich") -> str:
        path = os.path.join(tmp, "sink.jsonl")
        self._clear_root_handlers()
        setup_logging(_config(log_enabled=True, log_format=log_format, log_file_enabled=True, log_file_path=path))
        return path

    def _read_records(self, path: str) -> list[dict[str, object]]:
        with open(path, encoding="utf-8") as f:
            lines = [line for line in f.read().splitlines() if line.strip()]
        result = [json.loads(line) for line in lines]
        return result

    def test_file_sink_receives_json_records_when_both_switches_are_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._setup_with_file_sink(tmp)
            logging.getLogger(_LOGGER_NAME).info("file record")
            records = self._read_records(path)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["message"], "file record")
        self.assertEqual(set(records[0]), {"timestamp", "level", "logger", "message"})

    def test_file_sink_is_json_even_when_the_console_format_is_rich(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._setup_with_file_sink(tmp, log_format="rich")
            stderr = io.StringIO()
            with mock.patch.object(sys, "stderr", stderr):
                logging.getLogger(_LOGGER_NAME).info("dual record")
            records = self._read_records(path)

        self.assertEqual(records[0]["message"], "dual record")
        with self.assertRaises(json.JSONDecodeError):
            json.loads(stderr.getvalue().strip())

    def test_file_sink_writes_one_json_object_per_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._setup_with_file_sink(tmp, log_format="json")
            logger = logging.getLogger(_LOGGER_NAME)
            logger.info("first")
            logger.warning("second")
            logger.error("third")
            records = self._read_records(path)

        self.assertEqual([record["message"] for record in records], ["first", "second", "third"])
        self.assertEqual([record["level"] for record in records], ["INFO", "WARNING", "ERROR"])

    def test_file_sink_inactive_when_logging_is_disabled(self):
        sentinel = logging.StreamHandler(stream=io.StringIO())
        self.root.addHandler(sentinel)
        before = list(self.root.handlers)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sink.jsonl")

            setup_logging(_config(log_enabled=False, log_file_enabled=True, log_file_path=path))

            self.assertEqual(self.root.handlers, before)
            self.assertFalse(os.path.exists(path))

    def test_file_sink_inactive_when_the_file_switch_is_off(self):
        self._clear_root_handlers()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sink.jsonl")

            setup_logging(_config(log_enabled=True, log_file_enabled=False, log_file_path=path))

            self.assertEqual(len(self.root.handlers), 1)
            self.assertFalse(os.path.exists(path))


class TestSetupOverridesSdkDefault(_RootLoggerTestCase):
    """Enabling after the SDK's own ``configure_logging()`` is effective, not a silent no-op (Task 2.2)."""

    def test_enabled_json_setup_replaces_the_sdk_default_configure_logging(self):
        from mcp.server.mcpserver.utilities.logging import configure_logging

        self._clear_root_handlers()
        configure_logging()
        self.assertEqual(len(self.root.handlers), 1)
        self.assertIsInstance(self.root.handlers[0], RichHandler)

        stderr = io.StringIO()
        with mock.patch.object(sys, "stderr", stderr):
            setup_logging(_config(log_enabled=True, log_format="json", log_level="DEBUG"))

        handlers = self.root.handlers
        self.assertEqual(len(handlers), 1)
        self.assertIsInstance(handlers[0], logging.StreamHandler)
        self.assertNotIsInstance(handlers[0], RichHandler)
        self.assertIsInstance(handlers[0].formatter, JsonFormatter)
        self.assertEqual(self.root.level, logging.DEBUG)
        logging.getLogger(_LOGGER_NAME).info("effective json")
        parsed = json.loads(stderr.getvalue().strip())
        self.assertEqual(parsed["message"], "effective json")

    def test_enabled_rich_setup_replaces_the_sdk_default_configure_logging(self):
        from mcp.server.mcpserver.utilities.logging import configure_logging

        self._clear_root_handlers()
        configure_logging()

        setup_logging(_config(log_enabled=True, log_format="rich", log_level="WARNING"))

        handlers = self.root.handlers
        self.assertEqual(len(handlers), 1)
        self.assertIsInstance(handlers[0], SpecmgrRichHandler)
        self.assertEqual(self.root.level, logging.WARNING)

    def test_setup_on_a_bare_root_installs_exactly_the_intended_handlers(self):
        self._clear_root_handlers()

        setup_logging(_config(log_enabled=True, log_format="rich", log_level="WARNING"))

        handlers = self.root.handlers
        self.assertEqual(len(handlers), 1)
        self.assertIsInstance(handlers[0], SpecmgrRichHandler)
        self.assertEqual(self.root.level, logging.WARNING)

    def test_setup_on_a_bare_root_with_the_file_sink_installs_console_and_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._setup_with_file_sink_bare(tmp)

            self.assertEqual(len(self.root.handlers), 2)
            self.assertIsInstance(self.root.handlers[0], SpecmgrRichHandler)
            file_handler = self.root.handlers[1]
            self.assertIsInstance(file_handler, logging.FileHandler)
            self.assertIsInstance(file_handler.formatter, JsonFormatter)
            self.assertEqual(file_handler.baseFilename, os.path.abspath(path))

    def _setup_with_file_sink_bare(self, tmp: str) -> str:
        path = os.path.join(tmp, "sink.jsonl")
        self._clear_root_handlers()
        setup_logging(_config(log_enabled=True, log_format="rich", log_file_enabled=True, log_file_path=path))
        return path

    def test_setup_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sink.jsonl")
            config = _config(log_enabled=True, log_format="json", log_file_enabled=True, log_file_path=path)
            self._clear_root_handlers()

            setup_logging(config)
            first = [(type(handler), handler.level) for handler in self.root.handlers]
            setup_logging(config)
            second = [(type(handler), handler.level) for handler in self.root.handlers]

            self.assertEqual(first, second)
            self.assertEqual(len(self.root.handlers), 2)

    def test_configured_level_filters_records(self):
        self._clear_root_handlers()
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch.object(sys, "stdout", stdout),
            mock.patch.object(sys, "stderr", stderr),
        ):
            setup_logging(_config(log_enabled=True, log_format="json", log_level="ERROR"))
            logger = logging.getLogger(_LOGGER_NAME)
            logger.info("below the level")
            logger.error("at the level")

        self.assertEqual(stdout.getvalue(), "")
        lines = [line for line in stderr.getvalue().splitlines() if line.strip()]
        self.assertEqual(len(lines), 1)
        self.assertEqual(json.loads(lines[0])["message"], "at the level")


class TestServerModuleScopeWiring(_RootLoggerTestCase):
    """Task 2.5: ``server.py``'s module scope calls the setup unconditionally, so the
    env vars take effect the moment ``specmgr mcp`` imports ``server``."""

    def _fresh_import_server(self, env: dict[str, str]) -> None:
        clean = {name: value for name, value in os.environ.items() if name not in _ALL_TELEMETRY_ENV_VARS}
        clean.update(env)
        saved = sys.modules.pop("biz.dfch.specmgr.server", None)
        try:
            with mock.patch.dict(os.environ, clean, clear=True):
                importlib.import_module("biz.dfch.specmgr.server")
        finally:
            if saved is not None:
                sys.modules["biz.dfch.specmgr.server"] = saved

    def test_fresh_server_import_with_enabled_logging_installs_the_selected_handlers(self):
        self._clear_root_handlers()

        self._fresh_import_server({ENV_LOG_ENABLED: "true", ENV_LOG_FORMAT: "json"})

        handlers = self.root.handlers
        self.assertEqual(len(handlers), 1)
        self.assertIsInstance(handlers[0], logging.StreamHandler)
        self.assertNotIsInstance(handlers[0], RichHandler)
        self.assertIsInstance(handlers[0].formatter, JsonFormatter)
        self.assertEqual(self.root.level, logging.INFO)

    def test_fresh_server_import_with_the_default_config_keeps_the_sdk_default_handlers(self):
        self._clear_root_handlers()

        self._fresh_import_server({})

        handlers = self.root.handlers
        self.assertEqual(len(handlers), 1)
        self.assertIsInstance(handlers[0], RichHandler)
        self.assertNotIsInstance(handlers[0], SpecmgrRichHandler)
        self.assertEqual(self.root.level, logging.INFO)


if __name__ == "__main__":
    unittest.main()
