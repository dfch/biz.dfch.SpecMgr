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

"""Tests for ``telemetry/otel.py`` (feat-139-logging-telemetry, Phase 4, Tasks 4.1/4.2/4.10/4.11).

Covers the OpenTelemetry SDK bootstrap (Task 4.1): off-by-default
(``SPECMGR_OTEL_ENABLED=false`` sets nothing -- ACC-001/ACC-003's baseline),
the console exporters' mandatory ``out=sys.stderr`` redirection (ACC-003's
"enabling telemetry never writes any byte to stdout"), the fixed
``service.name = "specmgr"`` resource on every exported span and metric
(Task 4.11), the OTLP/HTTP exporters' wrapper application and
endpoint/path construction, the bootstrap's idempotency and the
``shutdown_telemetry`` slot/provider cleanup, and the Task 4.9 wiring
(``server.py``'s module scope calls the bootstrap at the pinned import-time
location).

The span-ID branch of the Task 3.1 correlation-ID helper is confirmed end
to end with the real import order (Task 4.2): a real ``specmgr mcp`` stdio
subprocess session runs ``import server`` (config -> logging -> OTel
bootstrap -> ``MCPServer`` -> middleware append) in the child process, and
the parent asserts each invocation's exported SDK span carries the same
trace ID the middleware's log record carries as its correlation ID. The
stdout-safety test (Task 4.10) uses the same real stdio transport for
every supported ``SPECMGR_OTEL_EXPORTER`` value (the assertion is scoped
to stdio, where stdout is the JSON-RPC channel).

The in-process bootstrap tests reset the OTel API's set-once global
provider state around the test (:func:`_isolated_otel_globals`) and shut
the providers down afterwards, so the full suite stays free of OTel
global-state pollution (the other tests in this repo are OTel-unaware and
must not start seeing real spans).

Requires the ``mcp`` extra (the OTel SDK + the ``mcp`` import order),
same as ``telemetry/otel.py`` itself.
"""

import contextlib
import io
import json
import logging
import os
import selectors
import socket
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.metrics import get_meter_provider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.trace import get_tracer_provider
from opentelemetry.util._once import Once

from biz.dfch.specmgr.telemetry import otel
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
from biz.dfch.specmgr.telemetry.otel import (
    OTLP_METRIC_EXPORTER_LOGGER_NAME,
    OTLP_TRACE_EXPORTER_LOGGER_NAME,
    OtlpExporterWrapper,
    SERVICE_NAME,
    _SPAN_EXPORT_FAILURE_MESSAGE,
    _METRIC_EXPORT_FAILURE_MESSAGE,
)

#: The repo root (this file is ``tests/telemetry/test_otel.py``).
_REPO_ROOT = Path(__file__).resolve().parents[2]

#: All eight telemetry env vars, stripped from the child processes'
#: environment so the sessions pin exactly the environment they assert on.
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

#: The SDK's own exporter-timeout env var (shortened for the otlp
#: subprocess case so the child's shutdown flush is ~1 s, not the
#: 10 s production default).
_SDK_OTLP_TIMEOUT_ENV = "OTEL_EXPORTER_OTLP_TIMEOUT"


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


@contextlib.contextmanager
def _isolated_otel_globals():
    """Yield with the OTel API's global provider state reset to pristine, restoring it on exit.

    The public ``set_tracer_provider``/``set_meter_provider`` are set-once
    per process (the API's ``Once`` guards), and the bootstrap under test
    must use them (the production path) -- so the test installs pristine
    guards (and ``None`` providers) for the duration and restores the
    worker process's previous provider objects on exit. No other test in
    this xdist worker sees the providers this test creates, nor the set-once
    guard it consumes: a previously pristine guard comes back pristine
    (fresh, unused), a previously used guard comes back used.

    Yields:
        ``None`` (the reset state is in effect for the ``with`` body).
    """
    from opentelemetry.metrics import _internal as metrics_internal
    import opentelemetry.trace as trace_api

    saved_tp = trace_api._TRACER_PROVIDER
    saved_tp_guard = trace_api._TRACER_PROVIDER_SET_ONCE
    saved_mp = metrics_internal._METER_PROVIDER
    saved_mp_guard = metrics_internal._METER_PROVIDER_SET_ONCE
    saved_mp_proxy_real = metrics_internal._PROXY_METER_PROVIDER._real_meter_provider
    trace_api._TRACER_PROVIDER = None
    trace_api._TRACER_PROVIDER_SET_ONCE = Once()
    metrics_internal._METER_PROVIDER = None
    metrics_internal._METER_PROVIDER_SET_ONCE = Once()
    try:
        yield
    finally:
        trace_api._TRACER_PROVIDER = saved_tp
        metrics_internal._METER_PROVIDER = saved_mp
        metrics_internal._PROXY_METER_PROVIDER._real_meter_provider = saved_mp_proxy_real
        # A pristine (unused) guard before the test means the public setter
        # was still available after it too: the test consumed the fresh
        # guard installed above, so hand the process a fresh unused one. A
        # previously used guard is restored as-is.
        if not saved_tp_guard._done:
            trace_api._TRACER_PROVIDER_SET_ONCE = Once()
        else:
            trace_api._TRACER_PROVIDER_SET_ONCE = saved_tp_guard
        if not saved_mp_guard._done:
            metrics_internal._METER_PROVIDER_SET_ONCE = Once()
        else:
            metrics_internal._METER_PROVIDER_SET_ONCE = saved_mp_guard


def _parse_json_objects(text: str) -> list[dict[str, object]]:
    """Extract every JSON object from a mixed stderr stream.

    The stream mixes single-line JSON log records with the console
    exporters' multi-line JSON blobs (spans, ``resource_metrics``); a
    ``raw_decode`` scan over ``{`` boundaries recovers all of them.

    Args:
        text: The stream content.

    Returns:
        The decoded JSON objects, in stream order.
    """
    decoder = json.JSONDecoder()
    result: list[dict[str, object]] = []
    i = 0
    while i < len(text):
        if text[i] != "{":
            i += 1
            continue
        try:
            obj, end = decoder.raw_decode(text, i)
        except json.JSONDecodeError:
            i += 1
            continue
        if isinstance(obj, dict):
            result.append(obj)
        i = end
    return result


def _drain_stream(stream: io.TextIOBase, sink: list[str]) -> None:
    """Read ``stream`` to EOF (blocking), appending the text to ``sink``.

    Runs in its own worker thread, one per pipe: the child writes
    potentially large console/OTLP export output to stderr at shutdown,
    after its last stdout response, so stdout and stderr must drain
    concurrently -- a sequential drain (stdout to EOF, then stderr) can
    block the child on a full stderr pipe buffer and deadlock. See
    ``_StdioSessionTestCase._run_session`` for the full wiring.

    Args:
        stream: The pipe end to drain (``proc.stdout`` or
            ``proc.stderr``); read by exactly this thread (the
            incremental stdout read in the main thread has already
            finished by the time the drain threads start).
        sink: The list the drained text is appended to, owned by the
            caller (appended from exactly this one thread, so no
            locking is needed).
    """
    while True:
        chunk = stream.read(1 << 16)
        if not chunk:
            break
        sink.append(chunk)


class _StdioSessionTestCase(unittest.TestCase):
    """Run a real ``specmgr mcp`` stdio subprocess session (fresh child process).

    The child is a fresh Python process -- the real import order (config ->
    logging -> OTel bootstrap -> ``MCPServer`` -> middleware append) runs in
    the child's ``server.py`` module scope, and the child's OTel global
    state is pristine, so no worker-process isolation is needed here.
    """

    def _run_session(
        self, extra_env: dict[str, str], expected_ids: list[int], timeout: float = 120.0
    ) -> tuple[str, str]:
        """Spawn the server, send the pinned frames, and return (stdout, stderr) after the child exits.

        Args:
            extra_env: The telemetry env vars for the child (the eight
                ``SPECMGR_*`` vars are stripped first, plus the
                ``SPECMGR_MCP_*`` transport vars).
            expected_ids: The request ids to wait for a response to before
                closing stdin.
            timeout: The overall child deadline in seconds.

        Returns:
            The child's complete stdout and stderr text.
        """
        env = {k: v for k, v in os.environ.items() if not k.startswith("SPECMGR_")}
        env.update(extra_env)
        proc = subprocess.Popen(
            [sys.executable, "-m", "biz.dfch.specmgr", "mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=_REPO_ROOT,
            text=True,
        )
        assert proc.stdin is not None and proc.stdout is not None and proc.stderr is not None
        frames = [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "specmgr-otel-test", "version": "0"},
                },
            }
        ]
        stdout = ""
        drained_stdout: list[str] = []
        drained_stderr: list[str] = []
        try:
            for frame in frames:
                proc.stdin.write(json.dumps(frame) + "\n")
                proc.stdin.flush()
            proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
            proc.stdin.flush()
            for frame in self._request_frames():
                proc.stdin.write(json.dumps(frame) + "\n")
                proc.stdin.flush()
            # Read stdout until every expected response arrives (or the deadline).
            selector = selectors.DefaultSelector()
            selector.register(proc.stdout, selectors.EVENT_READ)
            received: dict[int, dict[str, object]] = {}
            end = time.monotonic() + timeout
            while len(received) < len(expected_ids) and time.monotonic() < end:
                events = selector.select(timeout=0.5)
                if not events:
                    continue
                line = proc.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict) and obj.get("id") in expected_ids:
                    received[obj["id"]] = obj
                stdout += line + "\n"
            selector.close()
        finally:
            # Drain the remaining stdout AND all of stderr concurrently, one
            # reader thread per pipe (NOT sequentially: the child writes
            # potentially large console/OTLP export output to stderr at
            # shutdown, after its last stdout response, so a
            # stdout-to-EOF-then-stderr drain can block the child on a full
            # stderr pipe buffer and deadlock). The threads must run before
            # stdin is closed, since the close is what triggers the child's
            # shutdown flush. (A ``communicate()`` here would not work: it
            # raises ``ValueError: I/O operation on closed file`` on
            # Python 3.11/3.12 once stdin is already closed.)
            stdout_thread = threading.Thread(
                target=_drain_stream,
                args=(proc.stdout, drained_stdout),
                name="specmgr-test-stdout-drain",
                daemon=True,
            )
            stderr_thread = threading.Thread(
                target=_drain_stream,
                args=(proc.stderr, drained_stderr),
                name="specmgr-test-stderr-drain",
                daemon=True,
            )
            stdout_thread.start()
            stderr_thread.start()
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
            deadline = time.monotonic() + timeout
            for thread in (stdout_thread, stderr_thread):
                thread.join(timeout=max(0.0, deadline - time.monotonic()))
            if stdout_thread.is_alive() or stderr_thread.is_alive():
                # The child did not flush its pipes within the deadline:
                # kill it and reap, so the test fails on the partial output
                # below instead of leaking the process.
                proc.kill()
                for thread in (stdout_thread, stderr_thread):
                    thread.join(timeout=10.0)
            proc.wait(timeout=timeout)
        # The drain threads captured only the bytes NOT read by the
        # incremental stdout read above; reassemble the full stdout.
        stdout_text = "".join(drained_stdout)
        stderr_text = "".join(drained_stderr)
        full_stdout = stdout + stdout_text
        self.assertEqual(proc.returncode, 0, f"child exited {proc.returncode}; stderr: {stderr_text[:2000]}")
        return full_stdout, stderr_text

    def _request_frames(self) -> list[dict[str, object]]:
        """The item-invocation frames for the child (overridden per test)."""
        return []


class TestBootstrapDisabled(unittest.TestCase):
    """``SPECMGR_OTEL_ENABLED=false`` (the default): the bootstrap sets nothing (Task 4.1, ACC-001)."""

    def test_disabled_config_installs_no_providers_and_leaves_the_meter_slot_none(self):
        with _isolated_otel_globals():
            provider_before = get_tracer_provider()
            meter_provider_before = get_meter_provider()

            otel.bootstrap_telemetry(_config())

            self.assertIsNone(otel._tracer_provider)
            self.assertIsNone(otel._meter_provider)
            self.assertIsNone(otel._meter)
            self.assertIs(get_tracer_provider(), provider_before)
            self.assertIs(get_meter_provider(), meter_provider_before)

    def test_shutdown_with_nothing_bootstrapped_is_a_no_op(self):
        with _isolated_otel_globals():
            otel.shutdown_telemetry()

            self.assertIsNone(otel._tracer_provider)
            self.assertIsNone(otel._meter_provider)
            self.assertIsNone(otel._meter)


class TestBootstrapConsole(unittest.TestCase):
    """The default ``console`` exporter: stderr redirection, the service.name resource (Tasks 4.1/4.11)."""

    def setUp(self) -> None:
        self._isolation = _isolated_otel_globals()
        self._isolation.__enter__()
        # The console exporters capture the sys.stdout/sys.stderr objects at
        # construction time; buffer both so the redirection is observable.
        self._stdout_buf = io.StringIO()
        self._stderr_buf = io.StringIO()
        self._stdout_patcher = mock.patch.object(sys, "stdout", self._stdout_buf)
        self._stderr_patcher = mock.patch.object(sys, "stderr", self._stderr_buf)
        self._stdout_patcher.start()
        self._stderr_patcher.start()
        self._feature_logger = logging.getLogger("biz.dfch.specmgr.telemetry")
        self._saved_logger_handlers = list(self._feature_logger.handlers)
        self._capture = _LoggingCapture()
        self._feature_logger.addHandler(self._capture)
        otel.bootstrap_telemetry(_config(otel_enabled=True, otel_exporter="console"))

    def tearDown(self) -> None:
        otel.shutdown_telemetry()
        self._stderr_patcher.stop()
        self._stdout_patcher.stop()
        self._feature_logger.removeHandler(self._capture)
        self._feature_logger.handlers = self._saved_logger_handlers
        self._isolation.__exit__(None, None, None)

    def _stderr_text(self) -> str:
        return self._stderr_buf.getvalue()

    def test_exported_span_carries_the_service_name_resource(self):
        from opentelemetry.trace import get_tracer

        tracer = get_tracer("test")
        with tracer.start_as_current_span("the-span"):
            pass
        assert otel._tracer_provider is not None
        otel._tracer_provider.force_flush()

        spans = [obj for obj in _parse_json_objects(self._stderr_text()) if obj.get("name") == "the-span"]
        self.assertEqual(len(spans), 1)
        resource_attributes = spans[0]["resource"]["attributes"]
        self.assertEqual(resource_attributes["service.name"], SERVICE_NAME)

    def test_exported_metric_carries_the_service_name_resource(self):
        assert otel._meter is not None
        counter = otel._meter.create_counter("test.counter")
        counter.add(5, {"k": "v"})
        # The final collection happens at MeterProvider.shutdown (the
        # reader's own last collect), i.e. in tearDown -- collect it here
        # via the provider's force_flush to assert on a live export.
        assert otel._meter_provider is not None
        otel._meter_provider.force_flush()

        blobs = [obj for obj in _parse_json_objects(self._stderr_text()) if "resource_metrics" in obj]
        self.assertEqual(len(blobs), 1)
        resource_metrics = blobs[0]["resource_metrics"]
        self.assertEqual(resource_metrics[0]["resource"]["attributes"]["service.name"], SERVICE_NAME)
        scope_metrics = resource_metrics[0]["scope_metrics"]
        self.assertEqual(scope_metrics[0]["scope"]["name"], "specmgr")
        self.assertEqual(scope_metrics[0]["metrics"][0]["name"], "test.counter")

    def test_console_exporter_output_never_reaches_stdout(self):
        from opentelemetry.trace import get_tracer

        tracer = get_tracer("test")
        with tracer.start_as_current_span("the-span"):
            pass
        assert otel._tracer_provider is not None
        otel._tracer_provider.force_flush()
        assert otel._meter is not None
        otel._meter.create_counter("test.counter").add(1)

        self.assertEqual(self._stdout_buf.getvalue(), "")
        self.assertIn("the-span", self._stderr_buf.getvalue())

    def test_the_meter_slot_holds_the_bootstraps_meter(self):
        self.assertIsNotNone(otel._meter)
        counter = otel._meter.create_counter("slot.counter")
        counter.add(1)


class TestBootstrapIdempotent(unittest.TestCase):
    """A repeated bootstrap in an already-bootstrapped process is a no-op (Task 4.1)."""

    def test_a_second_bootstrap_keeps_the_same_providers(self):
        with _isolated_otel_globals():
            otel.bootstrap_telemetry(_config(otel_enabled=True, otel_exporter="console"))
            tp = otel._tracer_provider
            mp = otel._meter_provider
            meter = otel._meter

            otel.bootstrap_telemetry(_config(otel_enabled=True, otel_exporter="console"))

            self.assertIs(otel._tracer_provider, tp)
            self.assertIs(otel._meter_provider, mp)
            self.assertIs(otel._meter, meter)
            otel.shutdown_telemetry()
            self.assertIsNone(otel._tracer_provider)
            self.assertIsNone(otel._meter_provider)
            self.assertIsNone(otel._meter)
            otel.shutdown_telemetry()  # idempotent


class TestOtlpExporterConstruction(unittest.TestCase):
    """The ``otlp`` exporter branch: wrapper application, endpoint paths, stderr redirection (Task 4.1)."""

    def test_console_span_exporter_targets_stderr_by_keyword_and_is_not_wrapped(self):
        sentinel = object()
        with mock.patch.object(sys, "stderr", sentinel):
            sut = otel._build_span_exporter(_config(otel_exporter="console"))

        self.assertIsInstance(sut, ConsoleSpanExporter)
        self.assertNotIsInstance(sut, OtlpExporterWrapper)
        self.assertIs(sut.out, sentinel)

    def test_console_metric_exporter_targets_stderr_by_keyword_and_is_not_wrapped(self):
        sentinel = object()
        with mock.patch.object(sys, "stderr", sentinel):
            sut = otel._build_metric_exporter(_config(otel_exporter="console"))

        self.assertIsInstance(sut, ConsoleMetricExporter)
        self.assertNotIsInstance(sut, OtlpExporterWrapper)
        self.assertIs(sut.out, sentinel)

    def test_otlp_span_exporter_is_wrapped_and_points_at_the_traces_path(self):
        sut = otel._build_span_exporter(_config(otel_exporter="otlp", otel_endpoint="http://127.0.0.1:4318"))

        self.assertIsInstance(sut, OtlpExporterWrapper)
        inner = sut.exporter
        self.assertIsInstance(inner, OTLPSpanExporter)
        self.assertEqual(inner._endpoint, "http://127.0.0.1:4318/v1/traces")
        self.assertEqual(_first_warning_message(sut), _SPAN_EXPORT_FAILURE_MESSAGE)

    def test_otlp_metric_exporter_is_wrapped_and_points_at_the_metrics_path(self):
        sut = otel._build_metric_exporter(_config(otel_exporter="otlp", otel_endpoint="http://127.0.0.1:4318"))

        self.assertIsInstance(sut, OtlpExporterWrapper)
        inner = sut.exporter
        self.assertIsInstance(inner, OTLPMetricExporter)
        self.assertEqual(inner._endpoint, "http://127.0.0.1:4318/v1/metrics")
        self.assertEqual(_first_warning_message(sut), _METRIC_EXPORT_FAILURE_MESSAGE)

    def test_an_otlp_endpoint_with_a_trailing_slash_is_not_doubled(self):
        sut = otel._build_span_exporter(_config(otel_exporter="otlp", otel_endpoint="http://127.0.0.1:4318/"))

        self.assertEqual(sut.exporter._endpoint, "http://127.0.0.1:4318/v1/traces")


def _first_warning_message(sut: OtlpExporterWrapper) -> str:
    """Trigger one export failure on a fresh wrapper and return its episode warning message.

    (The construction tests assert the episode message the bootstrap
    pinned per exporter kind; a ``FAILURE`` export on the real OTLP
    exporter would hit the network, so the message is read from the
    wrapper's own configuration instead.)
    """
    result = sut._episode_message
    return result


class _LoggingCapture(logging.Handler):
    """A ``logging.Handler`` that keeps every record it receives."""

    def __init__(self) -> None:
        """Initialize the capture with an empty record list."""
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Keep the record."""
        self.records.append(record)


class TestSpanCorrelationRealImportOrder(_StdioSessionTestCase):
    """Task 4.2: the span-ID branch of the correlation-ID helper engages end to end (ACC-002/ACC-003).

    The real import order runs in a fresh child process (``import server``
    -> the Task 4.1 bootstrap -> a real stdio session), not the Phase 1a
    spike's pre-import provider installation: the child's ``mcp`` import
    fetches the SDK's proxy tracer first, and the bootstrap (later in the
    same module scope) is what the proxy resolves against.
    """

    def _request_frames(self) -> list[dict[str, object]]:
        return [
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "get_feat_template", "arguments": {}},
            },
            {"jsonrpc": "2.0", "id": 3, "method": "resources/read", "params": {"uri": "specmgr://version"}},
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "prompts/get",
                "params": {"name": "compact_history", "arguments": {"feature_id": "feat-0-template"}},
            },
        ]

    def test_every_invocation_correlation_id_matches_the_sdk_span_trace_id(self):
        stdout, stderr = self._run_session(
            {
                ENV_OTEL_ENABLED: "true",
                ENV_LOG_ENABLED: "true",
                ENV_LOG_FORMAT: "json",
            },
            expected_ids=[1, 2, 3, 4],
        )

        # Every request got a JSON-RPC response (the server kept operating).
        frames = _parse_json_objects(stdout)
        self.assertEqual({obj.get("id") for obj in frames if isinstance(obj.get("id"), int)}, {1, 2, 3, 4})

        objects = _parse_json_objects(stderr)
        records = [obj for obj in objects if "correlation_id" in obj]
        spans = [obj for obj in objects if "context" in obj and "name" in obj and "resource" in obj]

        # (invocation, its exported SDK span name, its completed log record's message)
        for span_name, record_message, item in (
            ("tools/call get_feat_template", "tool get_feat_template completed", "tool"),
            ("resources/read", "resource specmgr://version completed", "resource"),
            ("prompts/get compact_history", "prompt compact_history completed", "prompt"),
        ):
            record = next(
                (obj for obj in records if obj.get("message") == record_message and obj.get("item_type") == item),
                None,
            )
            self.assertIsNotNone(record, f"no completion record for {record_message}")
            correlation_id = record["correlation_id"]
            self.assertRegex(correlation_id, r"^[0-9a-f]{32}$", record_message)
            self.assertNotEqual(correlation_id, "0" * 32, f"non-recording span context in {record_message}")
            span = next((obj for obj in spans if obj.get("name") == span_name), None)
            self.assertIsNotNone(span, f"no exported span named {span_name}")
            trace_id = span["context"]["trace_id"]
            self.assertTrue(trace_id.startswith("0x"), span_name)
            self.assertEqual(trace_id[2:], correlation_id, f"correlation mismatch for {span_name}")


class TestStdoutSafetySubprocess(_StdioSessionTestCase):
    """Task 4.10: enabling telemetry never writes any byte to stdout, on the stdio transport (ACC-001/ACC-003).

    Mirrors Task 2.2's logging stdout-safety test for the telemetry half:
    with ``SPECMGR_OTEL_ENABLED=true`` and every supported
    ``SPECMGR_OTEL_EXPORTER`` value (the default ``console`` and
    ``otlp``), a real stdio session's stdout carries exactly the JSON-RPC
    response frames -- and nothing else. The ``otlp`` case points at an
    unreachable endpoint (the SDK's own export timeout shortened via its
    ``OTEL_EXPORTER_OTLP_TIMEOUT`` env var) and additionally asserts the
    Task 4.5 wrapper's one-message-per-episode behavior end to end.
    """

    def _request_frames(self) -> list[dict[str, object]]:
        return [
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "get_feat_template", "arguments": {}},
            },
        ]

    def _assert_stdout_is_json_rpc_only(self, stdout: str, expected_ids: list[int]) -> list[str]:
        lines = [line for line in stdout.splitlines() if line.strip()]
        self.assertEqual(len(lines), len(expected_ids))
        seen_ids = set()
        for line in lines:
            obj = json.loads(line)
            self.assertEqual(obj.get("jsonrpc"), "2.0")
            self.assertIsInstance(obj.get("id"), int)
            seen_ids.add(obj["id"])
        self.assertEqual(seen_ids, set(expected_ids))
        return lines

    def test_default_exporter_console_writes_zero_bytes_beyond_json_rpc_to_stdout(self):
        stdout, _ = self._run_session(
            {
                ENV_OTEL_ENABLED: "true",
                ENV_LOG_ENABLED: "true",
                ENV_LOG_FORMAT: "json",
            },
            expected_ids=[1, 2],
        )

        self._assert_stdout_is_json_rpc_only(stdout, [1, 2])

    def test_explicit_console_exporter_writes_zero_bytes_beyond_json_rpc_to_stdout(self):
        stdout, _ = self._run_session(
            {
                ENV_OTEL_ENABLED: "true",
                ENV_OTEL_EXPORTER: "console",
                ENV_LOG_ENABLED: "true",
                ENV_LOG_FORMAT: "json",
            },
            expected_ids=[1, 2],
        )

        self._assert_stdout_is_json_rpc_only(stdout, [1, 2])

    def test_unreachable_otlp_endpoint_writes_zero_bytes_beyond_json_rpc_to_stdout(self):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        stdout, stderr = self._run_session(
            {
                ENV_OTEL_ENABLED: "true",
                ENV_OTEL_EXPORTER: "otlp",
                ENV_OTEL_ENDPOINT: f"http://127.0.0.1:{port}",
                _SDK_OTLP_TIMEOUT_ENV: "1",
                ENV_LOG_ENABLED: "true",
                ENV_LOG_FORMAT: "json",
            },
            expected_ids=[1, 2],
        )

        self._assert_stdout_is_json_rpc_only(stdout, [1, 2])
        # The Task 4.5 wrapper's end-to-end behavior: exactly one stderr
        # message per exporter's failure episode, never repeating
        # (ACC-010). The span episode occurs because the SDK's built-in
        # middleware creates a span for the request; the metric episode
        # occurs -- since Phase 5 -- because the bootstrap creates metric
        # instruments (the ``mcp.cache.*`` observables, plus the
        # middleware's lazily created ``mcp.tool.*`` instruments from the
        # observed tool call), so the ``MeterProvider``'s final collection
        # at shutdown is non-empty and the metric exporter calls
        # ``export()`` against the unreachable endpoint. Both wrappers'
        # episode de-duplication is also unit-covered by
        # ``test_otel_exporter_wrapper.py``.
        span_lines = [line for line in stderr.splitlines() if _SPAN_EXPORT_FAILURE_MESSAGE in line]
        self.assertEqual(len(span_lines), 1)
        metric_lines = [line for line in stderr.splitlines() if _METRIC_EXPORT_FAILURE_MESSAGE in line]
        self.assertEqual(len(metric_lines), 1)
        # The Phase 4 re-evaluation fix: the SDK logs its per-attempt
        # failure lines DURING the export attempt (before the first
        # FAILURE return), so the wrapper's suppression filter must be
        # armed from the attempt's start -- across the whole child
        # session, zero raw lines may reach stderr from either OTLP
        # exporter logger (the child's JSON log format renders every
        # record with a ``logger`` field, so a leak is directly visible).
        raw_exporter_loggers = (OTLP_TRACE_EXPORTER_LOGGER_NAME, OTLP_METRIC_EXPORTER_LOGGER_NAME)
        raw_lines = []
        for line in stderr.splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(entry, dict) and entry.get("logger") in raw_exporter_loggers:
                raw_lines.append(line)
        self.assertEqual(raw_lines, [])


if __name__ == "__main__":
    unittest.main()
