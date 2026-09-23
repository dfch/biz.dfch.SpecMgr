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

"""Tests for the Phase 5 metric instruments (feat-139-logging-telemetry, Tasks 5.2/5.3/5.4/5.5/5.6).

The middleware's own ``mcp.tool.duration``/``mcp.tool.call.count``/
``mcp.tool.error.count`` instruments (lazily created on first observation
from the ``telemetry/metrics.py`` meter slot, with the pinned
``mcp.tool.name``/``mcp.item.type``/``mcp.domain`` attributes -- the
domain attribute omitted, never empty, when the Task 5.1 mapping yields
no domain), the bootstrap-created ``mcp.lock.wait_time`` histogram and
``mcp.cache.hit``/``mcp.cache.miss`` observable counters (the
``telemetry/metrics.py`` callbacks reading the
``general/tools/_doc_cache.py`` registry at collection time), the shared
``record_lock_wait`` helper (import-safe no-op while the slot is unset,
fail-open on a recording failure), and the production bootstrap's
pinned explicit-bucket Views (verified against the installed SDK 1.44.0
with an ``InMemoryMetricReader`` in place of the
``PeriodicExportingMetricReader`` -- the Phase 4 tests'
global-state-reset pattern from ``tests/telemetry/test_otel.py``).

Covers VCR ``54fd355f-0978-4dd0-9e1d-da89432e5321``'s acceptance criteria
AC-005 (the MCP-specific metric naming scheme), AC-006 (always-on
sampling -- the config surface carries no sample-rate variable), and
AC-008 (the metrics recorded with correct values/attributes).

Requires the ``mcp`` extra (the SDK's context models + the OTel SDK),
same as ``telemetry/middleware.py``/``telemetry/otel.py`` themselves.
"""

from __future__ import annotations

import importlib
import inspect
import logging
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from mcp.shared.exceptions import MCPError
from mcp_types import INTERNAL_ERROR
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from pydantic import BaseModel, ValidationError

from biz.dfch.specmgr.general.tools._doc_cache import DOC_CACHE_REGISTRY, DocCache, reset_doc_cache_registry
from biz.dfch.specmgr.telemetry import metrics
from biz.dfch.specmgr.telemetry import otel
from biz.dfch.specmgr.telemetry.middleware import SpecmgrTelemetryMiddleware

from tests.telemetry.test_otel import _config, _isolated_otel_globals
from tests.telemetry.test_middleware import _invoke, _make_ctx, _raises, _returns

#: The feature's own logger (the fail-open warnings' destination).
_FEATURE_LOGGER_NAME = "biz.dfch.specmgr.telemetry"


class _Capture(logging.Handler):
    """A ``logging.Handler`` that keeps every record it receives."""

    def __init__(self) -> None:
        """Initialize the capture with an empty record list."""
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Keep the record."""
        self.records.append(record)


class _FakeHistogram:
    """A recording stand-in for the ``mcp.lock.wait_time`` histogram slot."""

    def __init__(self) -> None:
        """Initialize with no recorded values."""
        self.records: list[tuple[float, dict[str, str]]] = []

    def record(self, value: float, attributes: dict[str, str] | None = None) -> None:
        """Keep the recorded value/attributes."""
        self.records.append((value, dict(attributes) if attributes else {}))


def _collected(reader: InMemoryMetricReader) -> dict[str, Any]:
    """Collect the reader's cumulative metrics data, keyed by metric name.

    Args:
        reader: The ``InMemoryMetricReader`` to collect from.

    Returns:
        ``{metric_name: {"unit": <unit>, "data_points": [<data point>, ...]}}``
        across every scope (the single-scope readers used in these tests
        make the name key unique).
    """
    # ``get_metrics_data()`` returns ``None`` (not an empty
    # ``MetricsData``) when no instrument has recorded any data yet.
    data = reader.get_metrics_data()
    if data is None:
        result: dict[str, Any] = {}
        return result
    result = {}
    for resource_metrics in data.resource_metrics:
        for scope_metrics in resource_metrics.scope_metrics:
            for metric in scope_metrics.metrics:
                entry = result.setdefault(metric.name, {"unit": metric.unit, "data_points": []})
                entry["data_points"].extend(metric.data.data_points)
    return result


def _identity_parse(text: str) -> str:
    """A ``parse_fn`` that returns its text unchanged."""
    result = text
    return result


class TestRecordLockWait(unittest.TestCase):
    """Task 5.5's shared ``record_lock_wait`` helper: no-op while unset, fail-open when set."""

    def setUp(self) -> None:
        self._logger = logging.getLogger(_FEATURE_LOGGER_NAME)
        self._saved_handlers = list(self._logger.handlers)
        self._capture = _Capture()
        self._logger.addHandler(self._capture)
        metrics.clear_instrument_slots()

    def tearDown(self) -> None:
        metrics.clear_instrument_slots()
        self._logger.removeHandler(self._capture)
        self._logger.handlers = self._saved_handlers

    def test_is_a_noop_while_the_slot_is_unset(self):
        metrics.record_lock_wait("req", 12.5)  # must not raise
        self.assertIsNone(metrics.meter_slot())

    def test_records_the_wait_to_the_bootstrapped_histogram_with_the_domain_attribute(self):
        fake = _FakeHistogram()
        metrics.set_lock_wait_histogram(fake)

        metrics.record_lock_wait("req", 12.5)

        self.assertEqual(fake.records, [(12.5, {metrics.ATTR_DOMAIN: "req"})])

    def test_never_propagates_a_histogram_failure_and_warns_once(self):
        class _BrokenHistogram(_FakeHistogram):
            def record(self, value: float, attributes: dict[str, str] | None = None) -> None:
                raise RuntimeError("the histogram is broken")

        metrics.set_lock_wait_histogram(_BrokenHistogram())

        metrics.record_lock_wait("req", 1.0)  # first failure: one warning, no propagation
        metrics.record_lock_wait("req", 2.0)  # second failure: silent
        metrics.record_lock_wait("uc", 3.0)

        warnings = [record for record in self._capture.records if record.levelno == logging.WARNING]
        self.assertEqual(len(warnings), 1)

    def test_rejects_an_empty_domain_and_a_negative_duration(self):
        with self.assertRaises(AssertionError):
            metrics.record_lock_wait("", 1.0)
        with self.assertRaises(AssertionError):
            metrics.record_lock_wait("req", -0.1)

    def test_clear_instrument_slots_resets_both_slots(self):
        fake = _FakeHistogram()
        metrics.set_meter(object())
        metrics.set_lock_wait_histogram(fake)

        metrics.clear_instrument_slots()

        self.assertIsNone(metrics.meter_slot())
        self.assertEqual(fake.records, [])


class TestCacheObservationCallbacks(unittest.TestCase):
    """Task 5.4's observable-counter callbacks: every live registry entry, defensive iteration."""

    def setUp(self) -> None:
        reset_doc_cache_registry()

    def tearDown(self) -> None:
        reset_doc_cache_registry()

    def test_an_empty_registry_yields_no_observations(self):
        self.assertEqual(metrics.cache_hit_callback(None), [])
        self.assertEqual(metrics.cache_miss_callback(None), [])

    def test_one_observation_per_registered_domain_with_the_domain_attribute(self):
        DocCache("req")
        DocCache("uc")

        hits = metrics.cache_hit_callback(None)
        misses = metrics.cache_miss_callback(None)

        self.assertEqual(sorted(obs.attributes[metrics.ATTR_DOMAIN] for obs in hits), ["req", "uc"])
        self.assertTrue(all(obs.value == 0 for obs in hits))
        self.assertEqual(sorted(obs.attributes[metrics.ATTR_DOMAIN] for obs in misses), ["req", "uc"])
        self.assertTrue(all(obs.value == 0 for obs in misses))

    def test_the_observations_reflect_the_caches_at_collection_time(self):
        cache = DocCache("req")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text("hello", encoding="utf-8")
            cache.read(path, _identity_parse)  # a miss
            cache.read(path, _identity_parse)  # a hit (hash match, no re-parse)

        hits = {obs.attributes[metrics.ATTR_DOMAIN]: obs.value for obs in metrics.cache_hit_callback(None)}
        misses = {obs.attributes[metrics.ATTR_DOMAIN]: obs.value for obs in metrics.cache_miss_callback(None)}

        self.assertEqual(hits, {"req": 1})
        self.assertEqual(misses, {"req": 1})

    def test_a_raising_registry_entry_is_skipped_not_fatal(self):
        DocCache("req")

        class _BrokenCache:
            def stats(self) -> dict[str, int]:
                raise RuntimeError("stats() is broken")

        DOC_CACHE_REGISTRY["broken"] = _BrokenCache()  # a deliberately malformed registry entry

        hits = metrics.cache_hit_callback(None)

        self.assertEqual([obs.attributes[metrics.ATTR_DOMAIN] for obs in hits], ["req"])

    def test_an_unimportable_general_module_yields_no_observations_instead_of_raising(self):
        # The callback's lazy import lives in its own try: with the general
        # package unavailable it must degrade to an empty collection, not
        # raise (a raising callback drops the instrument's entire cycle).
        with mock.patch.dict("sys.modules", {"biz.dfch.specmgr.general": None}):
            result = metrics.cache_hit_callback(None)
        self.assertEqual(result, [])


class _MiddlewareMetricsCase(unittest.TestCase):
    """Drive the middleware's lazily created instruments against a live, in-memory ``Meter``."""

    def setUp(self) -> None:
        self._reader = InMemoryMetricReader()
        self._provider = MeterProvider(metric_readers=[self._reader])
        metrics.set_meter(self._provider.get_meter("specmgr"))
        self._sut = SpecmgrTelemetryMiddleware(_config(otel_enabled=True))

    def tearDown(self) -> None:
        metrics.clear_instrument_slots()
        self._provider.shutdown()

    def _data_points(self, name: str) -> list[Any]:
        collected = _collected(self._reader)
        if name not in collected:
            return []
        return collected[name]["data_points"]

    def _unit(self, name: str) -> str:
        return _collected(self._reader)[name]["unit"]


class TestMiddlewareCallCount(_MiddlewareMetricsCase):
    """``mcp.tool.call.count``: exactly one increment per observed invocation (Task 5.2, the pin's semantics)."""

    def test_a_success_is_counted_once_with_the_pinned_attributes(self):
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})

        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        points = self._data_points(metrics.MCP_TOOL_CALL_COUNT)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0].value, 1)
        self.assertEqual(
            points[0].attributes,
            {metrics.ATTR_TOOL_NAME: "get_req", metrics.ATTR_ITEM_TYPE: "tool", metrics.ATTR_DOMAIN: "req"},
        )

    def test_every_observed_invocation_is_counted_whatever_its_outcome(self):
        success_ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})
        error_ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "bad"}})
        _invoke(self._sut, success_ctx, _returns({"resultType": "complete"}))
        _invoke(
            self._sut,
            error_ctx,
            _returns({"content": [{"type": "text", "text": "boom"}], "isError": True}),
        )

        points = self._data_points(metrics.MCP_TOOL_CALL_COUNT)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0].value, 2)

    def test_an_unobserved_method_is_never_counted(self):
        ctx = _make_ctx("tools/list", {})

        _invoke(self._sut, ctx, _returns({"tools": []}))

        self.assertEqual(self._data_points(metrics.MCP_TOOL_CALL_COUNT), [])

    def test_the_instruments_are_created_once_and_reused(self):
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})

        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))
        first = self._sut._metric_instruments
        self.assertIsNotNone(first)
        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        self.assertIs(self._sut._metric_instruments, first)

    def test_a_disabled_meter_slot_allocates_nothing_per_call(self):
        metrics.clear_instrument_slots()
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})

        result = _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        self.assertEqual(result, {"resultType": "complete"})
        self.assertIsNone(self._sut._metric_instruments)


class TestMiddlewareItemTypesAndDomains(_MiddlewareMetricsCase):
    """``mcp.item.type``/``mcp.tool.name``/``mcp.domain`` population across every item kind (Tasks 5.1/5.2)."""

    def _attributes_of(self, name: str) -> dict[str, str]:
        points = self._data_points(metrics.MCP_TOOL_CALL_COUNT)
        self.assertEqual(len(points), 1, name)
        result = points[0].attributes
        return result

    def test_a_domain_tool_call_carries_all_three_attributes(self):
        ctx = _make_ctx("tools/call", {"name": "create_rsk", "arguments": {"id": "x"}})

        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        self.assertEqual(
            self._attributes_of("tool"),
            {metrics.ATTR_TOOL_NAME: "create_rsk", metrics.ATTR_ITEM_TYPE: "tool", metrics.ATTR_DOMAIN: "rsk"},
        )

    def test_a_resource_read_carries_the_uri_as_the_identity_key(self):
        ctx = _make_ctx("resources/read", {"uri": "specmgr://rsk/tara"})

        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        self.assertEqual(
            self._attributes_of("resource"),
            {
                metrics.ATTR_TOOL_NAME: "specmgr://rsk/tara",
                metrics.ATTR_ITEM_TYPE: "resource",
                metrics.ATTR_DOMAIN: "rsk",
            },
        )

    def test_a_prompt_call_carries_the_prompt_attributes(self):
        ctx = _make_ctx("prompts/get", {"name": "implement_task"})

        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        self.assertEqual(
            self._attributes_of("prompt"),
            {metrics.ATTR_TOOL_NAME: "implement_task", metrics.ATTR_ITEM_TYPE: "prompt", metrics.ATTR_DOMAIN: "tsk"},
        )

    def test_the_no_domain_case_omits_the_domain_attribute_for_a_tool(self):
        ctx = _make_ctx("tools/call", {"name": "mdformat"})

        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        attributes = self._attributes_of("no-domain tool")
        self.assertNotIn(metrics.ATTR_DOMAIN, attributes)
        self.assertEqual(attributes[metrics.ATTR_ITEM_TYPE], "tool")
        self.assertEqual(attributes[metrics.ATTR_TOOL_NAME], "mdformat")

    def test_the_no_domain_case_omits_the_domain_attribute_for_a_resource(self):
        ctx = _make_ctx("resources/read", {"uri": "specmgr://version"})

        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        attributes = self._attributes_of("no-domain resource")
        self.assertNotIn(metrics.ATTR_DOMAIN, attributes)
        self.assertEqual(attributes[metrics.ATTR_ITEM_TYPE], "resource")
        self.assertEqual(attributes[metrics.ATTR_TOOL_NAME], "specmgr://version")

    def test_the_no_domain_case_omits_the_domain_attribute_for_a_prompt(self):
        ctx = _make_ctx("prompts/get", {"name": "compact_history"})

        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        attributes = self._attributes_of("no-domain prompt")
        self.assertNotIn(metrics.ATTR_DOMAIN, attributes)
        self.assertEqual(attributes[metrics.ATTR_ITEM_TYPE], "prompt")
        self.assertEqual(attributes[metrics.ATTR_TOOL_NAME], "compact_history")

    def test_a_generic_dispatch_tool_carries_its_type_argument_as_the_domain(self):
        ctx = _make_ctx(
            "tools/call",
            {"name": "set_status", "arguments": {"id": "x", "type": "vcr", "status": "accepted"}},
        )

        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        attributes = self._attributes_of("dispatch-tool")
        self.assertEqual(attributes[metrics.ATTR_DOMAIN], "vcr")
        self.assertEqual(attributes[metrics.ATTR_TOOL_NAME], "set_status")

    def test_a_generic_dispatch_tool_without_a_type_argument_carries_no_domain(self):
        ctx = _make_ctx("tools/call", {"name": "delete", "arguments": {"id": "x"}})

        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        attributes = self._attributes_of("dispatch-tool")
        self.assertNotIn(metrics.ATTR_DOMAIN, attributes)


class TestMiddlewareDurationHistogram(_MiddlewareMetricsCase):
    """``mcp.tool.duration``: unit ``ms`` and one observation per invocation (Task 5.2)."""

    def test_a_success_records_a_non_negative_duration_with_the_pinned_attributes(self):
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})

        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        points = self._data_points(metrics.MCP_TOOL_DURATION)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0].count, 1)
        self.assertGreaterEqual(points[0].sum, 0.0)
        self.assertEqual(
            points[0].attributes,
            {metrics.ATTR_TOOL_NAME: "get_req", metrics.ATTR_ITEM_TYPE: "tool", metrics.ATTR_DOMAIN: "req"},
        )
        self.assertEqual(self._unit(metrics.MCP_TOOL_DURATION), metrics.UNIT_MS)

    def test_a_failed_invocation_records_its_duration_too(self):
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "bad"}})

        _invoke(self._sut, ctx, _returns({"content": [{"type": "text", "text": "boom"}], "isError": True}))

        points = self._data_points(metrics.MCP_TOOL_DURATION)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0].count, 1)


class TestMiddlewareErrorCount(_MiddlewareMetricsCase):
    """``mcp.tool.error.count``: the per-channel ``error.type`` signal (Task 5.3)."""

    def test_a_tool_error_result_is_attributed_the_sdk_value(self):
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "bad"}})

        _invoke(self._sut, ctx, _returns({"content": [{"type": "text", "text": "boom"}], "isError": True}))

        points = self._data_points(metrics.MCP_TOOL_ERROR_COUNT)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0].value, 1)
        self.assertEqual(points[0].attributes[metrics.ATTR_ERROR_TYPE], "tool_error")
        self.assertEqual(points[0].attributes[metrics.ATTR_DOMAIN], "req")

    def test_a_raised_mcp_error_is_attributed_its_json_rpc_code_as_a_string(self):
        ctx = _make_ctx("resources/read", {"uri": "specmgr://req/schema"})

        with self.assertRaises(MCPError):
            _invoke(self._sut, ctx, _raises(MCPError(code=INTERNAL_ERROR, message="nope")))

        points = self._data_points(metrics.MCP_TOOL_ERROR_COUNT)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0].attributes[metrics.ATTR_ERROR_TYPE], str(INTERNAL_ERROR))

    def test_a_raised_raw_exception_is_attributed_its_qualname(self):
        ctx = _make_ctx("resources/read", {"uri": "specmgr://req/schema"})

        with self.assertRaises(MCPError):
            _invoke(self._sut, ctx, _raises(RuntimeError("boom")))

        points = self._data_points(metrics.MCP_TOOL_ERROR_COUNT)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0].attributes[metrics.ATTR_ERROR_TYPE], "RuntimeError")

    def test_a_raised_validation_error_is_attributed_its_qualname(self):
        class _Params(BaseModel):
            name: str

        with self.assertRaises(ValidationError) as validation_cm:
            _Params.model_validate({"name": 3})
        ctx = _make_ctx("prompts/get", {"name": "create_req"})

        with self.assertRaises(MCPError):
            _invoke(self._sut, ctx, _raises(validation_cm.exception))

        points = self._data_points(metrics.MCP_TOOL_ERROR_COUNT)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0].attributes[metrics.ATTR_ERROR_TYPE], "ValidationError")

    def test_a_success_increments_no_error_count(self):
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})

        _invoke(self._sut, ctx, _returns({"resultType": "complete"}))

        self.assertEqual(self._data_points(metrics.MCP_TOOL_ERROR_COUNT), [])


class TestMiddlewareMetricsFailOpen(_MiddlewareMetricsCase):
    """A first metrics-recording failure disables recording for the process (one warning, never a broken call)."""

    def setUp(self) -> None:
        super().setUp()
        self._logger = logging.getLogger(_FEATURE_LOGGER_NAME)
        self._saved_handlers = list(self._logger.handlers)
        self._capture = _Capture()
        self._logger.addHandler(self._capture)
        self._logger.setLevel(logging.DEBUG)

    def tearDown(self) -> None:
        self._logger.removeHandler(self._capture)
        self._logger.handlers = self._saved_handlers
        super().tearDown()

    def test_a_broken_meter_fails_open_once_and_the_call_completes(self):
        class _BrokenMeter:
            def create_histogram(self, *args: object, **kwargs: object) -> object:
                raise RuntimeError("the meter is broken")

        metrics.clear_instrument_slots()
        metrics.set_meter(_BrokenMeter())
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})
        sentinel = {"resultType": "complete"}

        first = _invoke(self._sut, ctx, _returns(sentinel))
        second = _invoke(self._sut, ctx, _returns(sentinel))

        self.assertIs(first, sentinel)
        self.assertIs(second, sentinel)
        self.assertTrue(self._sut._metrics_failed)
        warnings = [record for record in self._capture.records if record.levelno == logging.WARNING]
        self.assertEqual(len(warnings), 1)


class TestBootstrapInstruments(unittest.TestCase):
    """The production bootstrap's Phase 5 half: pinned Views, the bootstrap-created instruments, the slot hand-off."""

    def setUp(self) -> None:
        self._isolation = _isolated_otel_globals()
        self._isolation.__enter__()
        self._reader = InMemoryMetricReader()
        self._reader_patcher = mock.patch.object(otel, "PeriodicExportingMetricReader", lambda exporter: self._reader)
        self._reader_patcher.start()
        reset_doc_cache_registry()
        self._req_cache: DocCache[Any] = DocCache("req")
        self._uc_cache: DocCache[Any] = DocCache("uc")

    def tearDown(self) -> None:
        otel.shutdown_telemetry()
        self._reader_patcher.stop()
        self._isolation.__exit__(None, None, None)
        reset_doc_cache_registry()

    def _bootstrap_enabled(self) -> None:
        otel.bootstrap_telemetry(_config(otel_enabled=True))

    def test_the_bootstrap_stores_the_meter_in_the_shared_slot(self):
        self._bootstrap_enabled()

        self.assertIs(metrics.meter_slot(), otel._meter)

    def test_lock_wait_records_land_in_the_bootstrap_histogram_with_the_pinned_buckets(self):
        self._bootstrap_enabled()

        metrics.record_lock_wait("req", 42.0)

        collected = _collected(self._reader)
        points = collected[metrics.MCP_LOCK_WAIT]["data_points"]
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0].count, 1)
        self.assertEqual(points[0].sum, 42.0)
        self.assertEqual(tuple(points[0].explicit_bounds), metrics.LOCK_WAIT_BUCKET_BOUNDS)
        self.assertEqual(points[0].attributes, {metrics.ATTR_DOMAIN: "req"})
        self.assertEqual(collected[metrics.MCP_LOCK_WAIT]["unit"], metrics.UNIT_MS)

    def test_the_cache_observables_carry_one_series_per_registered_domain(self):
        self._bootstrap_enabled()
        with tempfile.TemporaryDirectory() as tmp:
            req_path = Path(tmp) / "req.md"
            req_path.write_text("req", encoding="utf-8")
            uc_path = Path(tmp) / "uc.md"
            uc_path.write_text("uc", encoding="utf-8")
            self._req_cache.read(req_path, _identity_parse)  # req: a miss
            self._req_cache.read(req_path, _identity_parse)  # req: a hit
            self._uc_cache.read(uc_path, _identity_parse)  # uc: a miss

        collected = _collected(self._reader)
        hits = {
            point.attributes[metrics.ATTR_DOMAIN]: point.value
            for point in collected[metrics.MCP_CACHE_HIT]["data_points"]
        }
        misses = {
            point.attributes[metrics.ATTR_DOMAIN]: point.value
            for point in collected[metrics.MCP_CACHE_MISS]["data_points"]
        }

        self.assertEqual(hits, {"req": 1, "uc": 0})
        self.assertEqual(misses, {"req": 1, "uc": 1})

    def test_the_middleware_duration_picks_up_the_bootstrap_view(self):
        # The View is registered before the middleware's own mcp.tool.duration
        # histogram is created (on first observation), so the lazy instrument
        # must carry the pinned explicit buckets.
        self._bootstrap_enabled()
        sut = SpecmgrTelemetryMiddleware(_config(otel_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        collected = _collected(self._reader)
        points = collected[metrics.MCP_TOOL_DURATION]["data_points"]
        self.assertEqual(len(points), 1)
        self.assertEqual(tuple(points[0].explicit_bounds), metrics.TOOL_DURATION_BUCKET_BOUNDS)
        self.assertEqual(collected[metrics.MCP_TOOL_DURATION]["unit"], metrics.UNIT_MS)
        self.assertEqual(points[0].count, 1)
        self.assertGreaterEqual(points[0].sum, 0.0)

    def test_a_disabled_bootstrap_creates_no_instruments_and_leaves_the_slots_unset(self):
        otel.bootstrap_telemetry(_config())

        self.assertIsNone(metrics.meter_slot())
        metrics.record_lock_wait("req", 1.0)  # still a no-op
        self.assertEqual(_collected(self._reader), {})

    def test_shutdown_clears_the_shared_slots(self):
        self._bootstrap_enabled()

        otel.shutdown_telemetry()

        self.assertIsNone(metrics.meter_slot())


class TestBootstrapSampler(unittest.TestCase):
    """AC-006's analysis: the config surface carries no sample-rate variable, and the bootstrap installs no sampler."""

    def test_the_config_module_defines_exactly_the_pinned_eight_env_vars(self):
        config_module = importlib.import_module("biz.dfch.specmgr.telemetry.config")

        env_vars = {
            name
            for name in dir(config_module)
            if name.startswith("ENV_") and isinstance(getattr(config_module, name), str)
        }

        self.assertEqual(
            env_vars,
            {
                "ENV_LOG_ENABLED",
                "ENV_LOG_LEVEL",
                "ENV_LOG_FORMAT",
                "ENV_LOG_FILE_ENABLED",
                "ENV_LOG_FILE_PATH",
                "ENV_OTEL_ENABLED",
                "ENV_OTEL_EXPORTER",
                "ENV_OTEL_ENDPOINT",
            },
        )

    def test_the_bootstrap_passes_no_sampler_to_the_tracer_provider(self):
        # Always-on (100%) sampling: the bootstrap constructs the
        # TracerProvider without a sampler= argument (the SDK default),
        # confirmed by source inspection of the bootstrap's own call.
        source = inspect.getsource(otel.bootstrap_telemetry)
        self.assertNotIn("sampler", source)


if __name__ == "__main__":
    unittest.main()
