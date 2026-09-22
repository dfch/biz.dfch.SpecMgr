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

"""Tests for ``telemetry/otel.py``'s ``OtlpExporterWrapper`` (feat-139-logging-telemetry, Phase 4, Task 4.6).

Unit tests for the Task 4.5 graceful OTLP-unreachable degradation: the
wrapper's episode state machine (an episode runs from the first
``FAILURE`` return until the first ``SUCCESS`` or ``shutdown``), the
at-most-one-stderr-message-per-episode de-duplication (via the feature's
own ``biz.dfch.specmgr.telemetry`` logger), the state-gated suppression of
the two OTLP exporters' own per-attempt failure noise (Task 1a.4's
confirmed 4-lines-per-cycle behavior -- logged *during* the ``export()``
call, so the suppression filter must be armed from the attempt's start,
not on the first ``FAILURE`` return), the pass-through of ``export()``'s
result and the ``force_flush()``/``shutdown()`` signatures, and the
independence of the two wrapper instances (span + metric).

Covers VCR ``54fd355f-0978-4dd0-9e1d-da89432e5321``'s acceptance criterion
AC-003 (an unreachable OTLP endpoint degrades gracefully: tool calls keep
succeeding, exactly one stderr message per episode, never repeating while
the condition persists).

Requires the ``mcp`` extra (the OTel SDK's export-result enums), same as
``telemetry/otel.py`` itself.
"""

import contextlib
import logging
import unittest
from collections.abc import Iterator

from opentelemetry.sdk.metrics.export import MetricExportResult
from opentelemetry.sdk.trace.export import SpanExportResult, SpanExporter

from biz.dfch.specmgr.telemetry.otel import (
    OTLP_METRIC_EXPORTER_LOGGER_NAME,
    OTLP_TRACE_EXPORTER_LOGGER_NAME,
    OtlpExporterWrapper,
    _OTLP_EXPORTER_LOGGER_NAMES,
    _SPAN_EXPORT_FAILURE_MESSAGE,
)

#: A sentinel export payload the fake exporter records (spans or metrics data stand-in).
_PAYLOAD = object()


class _Capture(logging.Handler):
    """A ``logging.Handler`` that keeps every record it receives."""

    def __init__(self) -> None:
        """Initialize the capture with an empty record list."""
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Keep the record."""
        self.records.append(record)


class _FakeExporter(SpanExporter):
    """A fake OTLP exporter: scripted ``export`` results, recorded calls.

    Subclasses ``SpanExporter`` (the union member the wrapper's input
    assertion accepts) and records every call so the pass-through behavior
    (``export()``'s result, ``force_flush()``/``shutdown()``'s arguments)
    is directly assertable. With ``log_during_export=True`` it mimics the
    real SDK's OTLP HTTP exporter, which logs its per-attempt failure
    lines (3x WARNING + 1x ERROR, Task 1a.4) on the exporter's own module
    logger *during* the ``export()`` call -- before the ``FAILURE`` result
    is returned -- the timing the Phase 4 re-evaluation fix pins.
    """

    def __init__(self, results: list[object], *, log_during_export: bool = False) -> None:
        """Initialize with the scripted sequence of ``export`` results.

        Args:
            results: The scripted ``export`` return values, in order.
            log_during_export: Whether each attempt first emits the real
                SDK's per-attempt failure lines on the span exporter's own
                logger (like the installed OTLP exporter does).
        """
        self.results = list(results)
        self.log_during_export = log_during_export
        self.export_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.force_flush_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.shutdown_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def export(self, *args: object, **kwargs: object) -> object:
        """Record the call, optionally log the per-attempt lines, and return the next scripted result."""
        self.export_calls.append((args, kwargs))
        if self.log_during_export:
            exporter_logger = logging.getLogger(OTLP_TRACE_EXPORTER_LOGGER_NAME)
            for _ in range(3):
                exporter_logger.warning("Transient error encountered while exporting span batch, retrying in 1.00s.")
            exporter_logger.error("Failed to export span batch due to timeout, max retries or shutdown.")
        return self.results.pop(0)

    def force_flush(self, *args: object, **kwargs: object) -> bool:
        """Record the call and pass the return value through."""
        self.force_flush_calls.append((args, kwargs))
        return True

    def shutdown(self, *args: object, **kwargs: object) -> None:
        """Record the call."""
        self.shutdown_calls.append((args, kwargs))


@contextlib.contextmanager
def _capture_raw_exporter_logs() -> Iterator[dict[str, _Capture]]:
    """Capture every record the two OTLP exporter loggers emit (propagation off).

    The wrapper's own filter is a *logger* filter, so it suppresses before
    any handler runs: whatever these captures receive is raw leakage.
    Propagation is disabled for the duration so a leak cannot also reach
    the root handlers (and be lost among unrelated records).

    Yields:
        A mapping of exporter logger name to its capture handler.
    """
    captures = {name: _Capture() for name in _OTLP_EXPORTER_LOGGER_NAMES}
    saved = {
        name: (list(logging.getLogger(name).handlers), logging.getLogger(name).propagate)
        for name in _OTLP_EXPORTER_LOGGER_NAMES
    }
    for name, capture in captures.items():
        exporter_logger = logging.getLogger(name)
        exporter_logger.addHandler(capture)
        exporter_logger.propagate = False
    try:
        yield captures
    finally:
        for name, (handlers, propagate) in saved.items():
            exporter_logger = logging.getLogger(name)
            for handler in list(exporter_logger.handlers):
                if handler not in handlers:
                    exporter_logger.removeHandler(handler)
            exporter_logger.handlers = handlers
            exporter_logger.propagate = propagate


class _WrapperTestCase(unittest.TestCase):
    """Capture the feature logger and save/restore the exporter loggers' filters."""

    def setUp(self) -> None:
        self._logger = logging.getLogger("biz.dfch.specmgr.telemetry")
        self._capture = _Capture()
        self._saved_logger_level = self._logger.level
        self._saved_logger_propagate = self._logger.propagate
        self._saved_logger_handlers = list(self._logger.handlers)
        self._logger.addHandler(self._capture)
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False
        # Whatever filters the two exporter loggers carry before the test
        # (the wrapper attaches/detaches its own during episodes);
        # tearDown restores the saved sets exactly.
        self._saved_exporter_filters = {
            name: list(logging.getLogger(name).filters) for name in _OTLP_EXPORTER_LOGGER_NAMES
        }

    def tearDown(self) -> None:
        for name, saved in self._saved_exporter_filters.items():
            logging.getLogger(name).filters[:] = saved
        for handler in list(self._logger.handlers):
            if handler not in self._saved_logger_handlers:
                self._logger.removeHandler(handler)
        self._logger.handlers = self._saved_logger_handlers
        self._logger.setLevel(self._saved_logger_level)
        self._logger.propagate = self._saved_logger_propagate

    @property
    def warnings(self) -> list[logging.LogRecord]:
        """The WARNING records the feature logger emitted during the test."""
        result = [record for record in self._capture.records if record.levelno == logging.WARNING]
        return result

    def _exporter_filter_attached(self, sut: OtlpExporterWrapper, name: str) -> bool:
        """Whether the wrapper's state-gated filter is on the named exporter logger."""
        result = any(isinstance(f, type(sut._filter)) and f is sut._filter for f in logging.getLogger(name).filters)
        return result

    def _emit_exporter_log(self, name: str) -> int:
        """Emit one WARNING on the named exporter logger; return how many records reached a handler."""
        capture = _Capture()
        logger = logging.getLogger(name)
        logger.addHandler(capture)
        try:
            logger.warning("Transient error encountered while exporting span batch, retrying in 1.00s.")
        finally:
            logger.removeHandler(capture)
        return len(capture.records)


class TestEpisodeStateMachine(_WrapperTestCase):
    """The at-most-one-message-per-episode de-duplication (Task 4.5/4.6, ACC-010)."""

    def test_a_first_failure_emits_exactly_one_warning_and_attaches_the_suppression(self):
        exporter = _FakeExporter([SpanExportResult.FAILURE])
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        sut.export(_PAYLOAD)

        self.assertEqual(len(self.warnings), 1)
        self.assertEqual(self.warnings[0].getMessage(), _SPAN_EXPORT_FAILURE_MESSAGE)
        self.assertTrue(sut.failing)
        for name in _OTLP_EXPORTER_LOGGER_NAMES:
            self.assertTrue(self._exporter_filter_attached(sut, name), name)

    def test_repeated_failures_emit_no_further_warnings(self):
        exporter = _FakeExporter([SpanExportResult.FAILURE] * 5)
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        for _ in range(5):
            sut.export(_PAYLOAD)

        self.assertEqual(len(self.warnings), 1)
        self.assertTrue(sut.failing)

    def test_recovery_ends_the_episode_without_a_message(self):
        exporter = _FakeExporter([SpanExportResult.FAILURE, SpanExportResult.SUCCESS])
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        sut.export(_PAYLOAD)
        sut.export(_PAYLOAD)

        self.assertEqual(len(self.warnings), 1)
        self.assertFalse(sut.failing)
        for name in _OTLP_EXPORTER_LOGGER_NAMES:
            self.assertFalse(self._exporter_filter_attached(sut, name), name)

    def test_a_subsequent_episode_emits_one_further_warning(self):
        exporter = _FakeExporter(
            [
                SpanExportResult.FAILURE,
                SpanExportResult.FAILURE,
                SpanExportResult.SUCCESS,
                SpanExportResult.SUCCESS,
                SpanExportResult.FAILURE,
            ]
        )
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        for _ in range(5):
            sut.export(_PAYLOAD)

        self.assertEqual(len(self.warnings), 2)
        for record in self.warnings:
            self.assertEqual(record.getMessage(), _SPAN_EXPORT_FAILURE_MESSAGE)
        self.assertTrue(sut.failing)

    def test_an_all_healthy_exporter_never_warns_nor_attaches_the_suppression(self):
        exporter = _FakeExporter([MetricExportResult.SUCCESS] * 3)
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        for _ in range(3):
            sut.export(_PAYLOAD)

        self.assertEqual(self.warnings, [])
        self.assertFalse(sut.failing)
        for name in _OTLP_EXPORTER_LOGGER_NAMES:
            self.assertFalse(self._exporter_filter_attached(sut, name), name)

    def test_shutdown_ends_an_active_episode_and_prevents_a_new_one(self):
        exporter = _FakeExporter([SpanExportResult.FAILURE, SpanExportResult.FAILURE])
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        sut.export(_PAYLOAD)
        self.assertEqual(len(self.warnings), 1)
        sut.shutdown(timeout_millis=1)
        self.assertFalse(sut.failing)
        for name in _OTLP_EXPORTER_LOGGER_NAMES:
            self.assertFalse(self._exporter_filter_attached(sut, name), name)
        sut.export(_PAYLOAD)

        self.assertEqual(len(self.warnings), 1)
        self.assertFalse(sut.failing)
        self.assertEqual(len(exporter.shutdown_calls), 1)
        self.assertEqual(exporter.shutdown_calls[0], ((), {"timeout_millis": 1}))


class TestFirstCycleAttemptSuppression(_WrapperTestCase):
    """The SDK logs DURING the attempt, before the first ``FAILURE`` return: the filter must be armed from the attempt's start.

    The Phase 4 re-evaluation fix: arming only on the first ``FAILURE``
    return leaked the first cycle's raw SDK lines (the reproduced ACC-010
    violation). These scenarios drive a fake exporter that emits the real
    per-attempt lines (3x WARNING + 1x ERROR) on the exporter's own logger
    *inside* ``export()``, and assert zero raw leakage across a whole
    episode plus exactly one wrapper message.
    """

    def test_in_attempt_logging_on_the_first_cycle_is_suppressed_with_exactly_one_message(self):
        exporter = _FakeExporter([SpanExportResult.FAILURE] * 3, log_during_export=True)
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        with _capture_raw_exporter_logs() as raw:
            for _ in range(3):
                sut.export(_PAYLOAD)

        self.assertEqual(raw[OTLP_TRACE_EXPORTER_LOGGER_NAME].records, [])
        self.assertEqual(raw[OTLP_METRIC_EXPORTER_LOGGER_NAME].records, [])
        self.assertEqual(len(self.warnings), 1)
        self.assertEqual(self.warnings[0].getMessage(), _SPAN_EXPORT_FAILURE_MESSAGE)
        self.assertTrue(sut.failing)
        self.assertTrue(sut.armed)

    def test_in_attempt_logging_is_suppressed_across_recovery_and_a_second_episode(self):
        exporter = _FakeExporter(
            [
                SpanExportResult.FAILURE,
                SpanExportResult.FAILURE,
                SpanExportResult.SUCCESS,
                SpanExportResult.FAILURE,
                SpanExportResult.SUCCESS,
            ],
            log_during_export=True,
        )
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        with _capture_raw_exporter_logs() as raw:
            for _ in range(5):
                sut.export(_PAYLOAD)

        self.assertEqual(raw[OTLP_TRACE_EXPORTER_LOGGER_NAME].records, [])
        self.assertEqual(len(self.warnings), 2)
        for record in self.warnings:
            self.assertEqual(record.getMessage(), _SPAN_EXPORT_FAILURE_MESSAGE)
        self.assertFalse(sut.failing)
        self.assertFalse(sut.armed)

    def test_a_healthy_attempt_arms_and_disarms_around_the_export_call(self):
        exporter = _FakeExporter([MetricExportResult.SUCCESS], log_during_export=True)
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        with _capture_raw_exporter_logs() as raw:
            sut.export(_PAYLOAD)

        self.assertEqual(raw[OTLP_TRACE_EXPORTER_LOGGER_NAME].records, [])
        self.assertEqual(self.warnings, [])
        self.assertFalse(sut.failing)
        self.assertFalse(sut.armed)
        for name in _OTLP_EXPORTER_LOGGER_NAMES:
            self.assertFalse(self._exporter_filter_attached(sut, name), name)


class TestExporterLogSuppression(_WrapperTestCase):
    """The state-gated filter drops the exporters' own noise while the wrapper is armed (an attempt in progress or an episode active)."""

    def test_the_exporters_own_logs_are_suppressed_while_the_episode_is_active(self):
        exporter = _FakeExporter([SpanExportResult.FAILURE])
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        sut.export(_PAYLOAD)

        self.assertEqual(self._emit_exporter_log(OTLP_TRACE_EXPORTER_LOGGER_NAME), 0)
        self.assertEqual(self._emit_exporter_log(OTLP_METRIC_EXPORTER_LOGGER_NAME), 0)

    def test_the_exporters_own_logs_flow_again_after_recovery(self):
        exporter = _FakeExporter([SpanExportResult.FAILURE, SpanExportResult.SUCCESS])
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        sut.export(_PAYLOAD)
        sut.export(_PAYLOAD)

        self.assertEqual(self._emit_exporter_log(OTLP_TRACE_EXPORTER_LOGGER_NAME), 1)
        self.assertEqual(self._emit_exporter_log(OTLP_METRIC_EXPORTER_LOGGER_NAME), 1)

    def test_an_unrelated_logger_is_never_suppressed(self):
        exporter = _FakeExporter([SpanExportResult.FAILURE])
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)
        capture = _Capture()
        other = logging.getLogger("some.unrelated.logger")
        other.addHandler(capture)
        try:
            sut.export(_PAYLOAD)
            other.warning("unaffected")
        finally:
            other.removeHandler(capture)

        self.assertEqual(len(capture.records), 1)


class TestPassThrough(_WrapperTestCase):
    """``export()``'s result and the ``force_flush()``/``shutdown()`` signatures pass through unchanged."""

    def test_export_returns_the_wrapped_exporters_result_object_unchanged(self):
        exporter = _FakeExporter([SpanExportResult.FAILURE, SpanExportResult.SUCCESS])
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        first = sut.export(_PAYLOAD, timeout_millis=1234)
        second = sut.export(_PAYLOAD)

        self.assertIs(first, SpanExportResult.FAILURE)
        self.assertIs(second, SpanExportResult.SUCCESS)
        self.assertEqual(exporter.export_calls, [((_PAYLOAD,), {"timeout_millis": 1234}), ((_PAYLOAD,), {})])

    def test_force_flush_passes_arguments_and_return_value_through(self):
        exporter = _FakeExporter([])
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        result = sut.force_flush(4321)

        self.assertTrue(result)
        self.assertEqual(exporter.force_flush_calls, [((4321,), {})])

    def test_shutdown_passes_arguments_through(self):
        exporter = _FakeExporter([])
        sut = OtlpExporterWrapper(exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)

        sut.shutdown(1, extra="kwarg")

        self.assertEqual(exporter.shutdown_calls, [((1,), {"extra": "kwarg"})])


class TestTwoWrapperInstances(_WrapperTestCase):
    """The bootstrap applies the one shared class twice (span + metric): independent episodes."""

    def test_each_instance_tracks_its_own_episode_and_message(self):
        span_exporter = _FakeExporter([SpanExportResult.FAILURE, SpanExportResult.SUCCESS])
        metric_exporter = _FakeExporter([MetricExportResult.SUCCESS])
        sut_span = OtlpExporterWrapper(span_exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)
        sut_metric = OtlpExporterWrapper(metric_exporter, episode_message="OTLP metric export is failing")

        sut_span.export(_PAYLOAD)
        sut_metric.export(_PAYLOAD)

        self.assertTrue(sut_span.failing)
        self.assertFalse(sut_metric.failing)
        self.assertEqual(len(self.warnings), 1)
        self.assertEqual(self.warnings[0].getMessage(), _SPAN_EXPORT_FAILURE_MESSAGE)

        sut_span.export(_PAYLOAD)
        self.assertEqual(len(self.warnings), 1)
        self.assertFalse(sut_span.failing)

    def test_a_failing_instances_filter_is_attached_to_exactly_the_two_exporter_loggers(self):
        span_exporter = _FakeExporter([SpanExportResult.FAILURE])
        metric_exporter = _FakeExporter([MetricExportResult.SUCCESS])
        sut_span = OtlpExporterWrapper(span_exporter, episode_message=_SPAN_EXPORT_FAILURE_MESSAGE)
        sut_metric = OtlpExporterWrapper(metric_exporter, episode_message="OTLP metric export is failing")

        sut_span.export(_PAYLOAD)
        sut_metric.export(_PAYLOAD)

        for name in _OTLP_EXPORTER_LOGGER_NAMES:
            filters = logging.getLogger(name).filters
            self.assertIn(sut_span._filter, filters, name)
            self.assertNotIn(sut_metric._filter, filters, name)
            # While the span episode is active, the state-gated filter
            # suppresses both exporters' own loggers (the SDK never logs a
            # successful export, so nothing healthy is lost).
            self.assertEqual(self._emit_exporter_log(name), 0, name)
