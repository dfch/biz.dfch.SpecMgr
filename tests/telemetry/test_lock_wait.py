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

"""Tests for the thirteen refactored ``<domain>/tools/_lock.py`` context managers (feat-139-logging-telemetry, Phase 5, Tasks 5.5/5.6).

Includes the production-path regression test (``TestLockWaitProductionPath``):
a real ``create_req`` + real generic ``set_status`` write, through the real
import chain and the real per-domain lock, asserting the
``mcp.lock.wait_time`` series actually appears in a forced collection --
plus the negative half that pins *when* it does not appear (an invalid
status returns before any lock is taken).

The Task 5.5 refactor changed every domain lock's context manager from a
bare ``with lock: yield`` to the explicit acquire/record/release shape
(measuring the acquire WAIT only, and recording it to the
``mcp.lock.wait_time`` histogram via the shared
``telemetry.metrics.record_lock_wait`` helper). Because that changes the
acquire/release control flow of thirteen concurrency-critical context
managers, Task 5.6 requires a regression check -- independent of the new
timing metric itself -- that each refactored context manager still (1)
releases its lock on every exit path, including when the caller's
``yield``-wrapped body raises, and (2) still serializes concurrent
acquirers of the same id (mutual exclusion unchanged, per-id locks stay
per-id). The third test class additionally confirms the new behavior:
each lock's acquire wait is recorded to the shared helper's histogram
slot with the ``mcp.domain`` attribute.

Every test runs data-driven over all thirteen modules (the feat domain's
global ``feat_create_lock`` is covered too), so a future change that
diverges one file's shape trips this file in CI.
"""

from __future__ import annotations

import importlib
import os
import tempfile
import threading
import time
import unittest
import uuid
from pathlib import Path
from typing import Any
from unittest import mock

from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from biz.dfch.specmgr.general.models import InvalidStatusResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.telemetry import metrics
from biz.dfch.specmgr.telemetry import otel

from tests.telemetry.test_otel import _config, _isolated_otel_globals

#: The thirteen refactored per-domain lock modules: (domain, module path, per-id lock function).
_LOCK_MODULES = (
    ("adr", "biz.dfch.specmgr.adr.tools._lock", "adr_lock"),
    ("dec", "biz.dfch.specmgr.dec.tools._lock", "dec_lock"),
    ("feat", "biz.dfch.specmgr.feat.tools._lock", "feat_lock"),
    ("gol", "biz.dfch.specmgr.gol.tools._lock", "gol_lock"),
    ("prb", "biz.dfch.specmgr.prb.tools._lock", "prb_lock"),
    ("qa", "biz.dfch.specmgr.qa.tools._lock", "qa_lock"),
    ("req", "biz.dfch.specmgr.req.tools._lock", "req_lock"),
    ("rsk", "biz.dfch.specmgr.rsk.tools._lock", "rsk_lock"),
    ("sop", "biz.dfch.specmgr.sop.tools._lock", "sop_lock"),
    ("sysrs", "biz.dfch.specmgr.sysrs.tools._lock", "sysrs_lock"),
    ("tsk", "biz.dfch.specmgr.tsk.tools._lock", "tsk_lock"),
    ("uc", "biz.dfch.specmgr.uc.tools._lock", "uc_lock"),
    ("vcr", "biz.dfch.specmgr.vcr.tools._lock", "vcr_lock"),
)


def _fresh_id() -> str:
    """A per-test unique document id (so no cross-test lock state can interfere)."""
    result = f"lock-wait-test-{uuid.uuid4().hex}"
    return result


class TestLockReleaseOnException(unittest.TestCase):
    """Task 5.6's regression: every refactored context manager releases its lock on every exit path."""

    def test_the_per_id_lock_releases_when_the_wrapped_body_raises(self):
        for domain, module_path, lock_fn_name in _LOCK_MODULES:
            with self.subTest(domain=domain):
                module = importlib.import_module(module_path)
                lock_fn = getattr(module, lock_fn_name)
                doc_id = _fresh_id()
                lock = module._lock_for(doc_id)

                with self.assertRaises(RuntimeError):
                    with lock_fn(doc_id):
                        raise RuntimeError("the wrapped body failed")

                self.assertTrue(lock.acquire(blocking=False), f"{domain}: the lock is still held after a raising body")
                lock.release()

    def test_the_per_id_lock_is_held_inside_the_body_and_released_on_a_normal_exit(self):
        for domain, module_path, lock_fn_name in _LOCK_MODULES:
            with self.subTest(domain=domain):
                module = importlib.import_module(module_path)
                lock_fn = getattr(module, lock_fn_name)
                doc_id = _fresh_id()
                lock = module._lock_for(doc_id)

                with lock_fn(doc_id):
                    self.assertFalse(
                        lock.acquire(blocking=False), f"{domain}: the lock is not held inside its own body"
                    )

                self.assertTrue(lock.acquire(blocking=False), f"{domain}: the lock is still held after a normal exit")
                lock.release()

    def test_feat_create_lock_releases_when_the_wrapped_body_raises(self):
        module = importlib.import_module("biz.dfch.specmgr.feat.tools._lock")

        with self.assertRaises(RuntimeError):
            with module.feat_create_lock():
                raise RuntimeError("the wrapped body failed")

        self.assertTrue(
            module._create_lock.acquire(blocking=False), "feat's create lock is still held after a raising body"
        )
        module._create_lock.release()


class TestLockSerializationPreserved(unittest.TestCase):
    """The refactor kept the mutual-exclusion semantics: a held lock still blocks a concurrent acquirer."""

    def test_a_held_per_id_lock_blocks_a_concurrent_acquirer_until_released(self):
        for domain, module_path, lock_fn_name in _LOCK_MODULES:
            with self.subTest(domain=domain):
                module = importlib.import_module(module_path)
                lock_fn = getattr(module, lock_fn_name)
                doc_id = _fresh_id()
                lock = module._lock_for(doc_id)
                lock.acquire()
                entered = threading.Event()

                def worker() -> None:
                    with lock_fn(doc_id):
                        entered.set()

                thread = threading.Thread(target=worker)
                thread.start()
                self.assertFalse(entered.wait(0.3), f"{domain}: a concurrent acquirer entered while the lock was held")
                lock.release()
                thread.join(5)
                self.assertFalse(thread.is_alive(), f"{domain}: the waiter did not finish after the lock was released")

    def test_different_ids_still_run_concurrently(self):
        for domain, module_path, lock_fn_name in _LOCK_MODULES:
            with self.subTest(domain=domain):
                module = importlib.import_module(module_path)
                lock_fn = getattr(module, lock_fn_name)
                first_id = _fresh_id()
                second_id = _fresh_id()
                first_lock = module._lock_for(first_id)
                first_lock.acquire()
                entered = threading.Event()

                def worker() -> None:
                    with lock_fn(second_id):
                        entered.set()

                thread = threading.Thread(target=worker)
                thread.start()
                # The other id's lock is untouched by first_id's holder.
                self.assertTrue(entered.wait(0.3), f"{domain}: distinct ids no longer run concurrently")
                first_lock.release()
                thread.join(5)


class _FakeHistogram:
    """A recording stand-in for the ``mcp.lock.wait_time`` histogram slot."""

    def __init__(self) -> None:
        """Initialize with no recorded values."""
        self.records: list[tuple[float, dict[str, str]]] = []

    def record(self, value: float, attributes: dict[str, str] | None = None) -> None:
        """Keep the recorded value/attributes."""
        self.records.append((value, dict(attributes) if attributes else {}))


class TestLockWaitRecording(unittest.TestCase):
    """Task 5.5's new behavior: each lock records its acquire WAIT (not hold) to the shared helper."""

    def setUp(self) -> None:
        metrics.clear_instrument_slots()

    def tearDown(self) -> None:
        metrics.clear_instrument_slots()

    def test_each_per_id_lock_records_its_acquire_wait_with_the_domain_attribute(self):
        fake = _FakeHistogram()
        metrics.set_lock_wait_histogram(fake)
        for domain, module_path, lock_fn_name in _LOCK_MODULES:
            with self.subTest(domain=domain):
                fake.records.clear()
                module = importlib.import_module(module_path)
                lock_fn = getattr(module, lock_fn_name)
                doc_id = _fresh_id()
                lock = module._lock_for(doc_id)
                lock.acquire()

                def holder() -> None:
                    time.sleep(0.05)
                    lock.release()

                holder_thread = threading.Thread(target=holder)
                holder_thread.start()
                with lock_fn(doc_id):
                    pass
                holder_thread.join(5)

                self.assertEqual(len(fake.records), 1, f"{domain}: the wait was not recorded exactly once")
                value, attributes = fake.records[0]
                self.assertEqual(attributes, {metrics.ATTR_DOMAIN: domain})
                self.assertGreaterEqual(value, 0.0)

    def test_feat_create_lock_records_its_acquire_wait_with_the_domain_attribute(self):
        fake = _FakeHistogram()
        metrics.set_lock_wait_histogram(fake)
        module = importlib.import_module("biz.dfch.specmgr.feat.tools._lock")
        module._create_lock.acquire()

        def holder() -> None:
            time.sleep(0.05)
            module._create_lock.release()

        holder_thread = threading.Thread(target=holder)
        holder_thread.start()
        with module.feat_create_lock():
            pass
        holder_thread.join(5)

        self.assertEqual(len(fake.records), 1)
        value, attributes = fake.records[0]
        self.assertEqual(attributes, {metrics.ATTR_DOMAIN: "feat"})
        self.assertGreaterEqual(value, 0.0)

    def test_no_record_is_made_while_the_slot_is_unset(self):
        # With telemetry disabled (the default) the helper is a no-op and
        # the refactored control flow changes no observable lock behavior.
        module = importlib.import_module("biz.dfch.specmgr.req.tools._lock")
        doc_id = _fresh_id()

        with module.req_lock(doc_id):
            pass

        self.assertIsNone(metrics._lock_wait_histogram)


class TestLockWaitProductionPath(unittest.TestCase):
    """The production lock path records deterministically (Phase 5 verification regression).

    The orchestrator's Phase 5 verification reported ``mcp.lock.wait_time``
    missing (flakily) after a production ``set_status`` call. Root cause,
    pinned by this test: the generic ``set_status`` tool validates the
    requested status against the domain's own closed vocabulary **before**
    taking any domain lock (ADR b399f1ce-ed42-4929-b01c-7a57d18e8014's
    Decision Outcome point 3, ``_check_status_allowed``'s own docstring)
    and returns a structured, non-raising ``InvalidStatusResult`` on a
    miss -- a *successful* JSON-RPC result (no ``isError``) whose
    ``status`` field echoes the rejected request, so ``set_status(rid,
    "req", "review")`` looks like "a real write returning status review"
    while performing no write and taking no lock. An absent
    ``mcp.lock.wait_time`` series for such a session is correct, not a
    recording defect (the recording path itself was verified instance-
    clean: one ``_lock`` module instance in ``sys.modules``, identical
    ``req_lock.__wrapped__``/``__globals__``/``record_lock_wait`` bindings,
    one non-``None`` histogram slot shared by the production function and
    the bootstrap). This test pins both halves through the real
    production chain (real ``create_req`` tool function + real generic
    ``set_status`` dispatching to the ported ``_set_status_req`` adapter
    with its ``with req_lock(id_):``): a valid status is a real write and
    produces the series; an invalid status takes no lock and leaves the
    series count unchanged.
    """

    def setUp(self) -> None:
        self._tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self._docs_dir = self._tmp / "docs"
        (self._docs_dir / "req").mkdir(parents=True)
        # Strip every SPECMGR_* var (so server.py's own module-scope
        # bootstrap -- triggered by the production import chain below --
        # is a no-op) and point the domain base dir at the temp tree.
        self._env_patcher = mock.patch.dict(
            os.environ,
            {name: value for name, value in os.environ.items() if not name.startswith("SPECMGR_")}
            | {DOCS_DIR_ENV_VAR: str(self._docs_dir)},
        )
        self._env_patcher.start()

        self._isolation = _isolated_otel_globals()
        self._isolation.__enter__()
        self._reader = InMemoryMetricReader()
        self._reader_patcher = mock.patch.object(otel, "PeriodicExportingMetricReader", lambda exporter: self._reader)
        self._reader_patcher.start()

        from biz.dfch.specmgr.general.tools.set_status import set_status
        from biz.dfch.specmgr.req.tools.create_req import create_req

        self._set_status = set_status
        self._create_req = create_req
        otel.bootstrap_telemetry(_config(otel_enabled=True))

    def tearDown(self) -> None:
        otel.shutdown_telemetry()
        self._reader_patcher.stop()
        self._isolation.__exit__(None, None, None)
        self._env_patcher.stop()

    def _template_body(self) -> str:
        """The packaged REQ template as body-only markdown (create_req's input contract)."""
        req_package = importlib.import_module("biz.dfch.specmgr.req")
        raw = (Path(req_package.__file__).parent / "data" / "req_template.md").read_text(encoding="utf-8")
        result = raw.split("---", 2)[2] if raw.startswith("---") else raw
        return result

    def _req_lock_wait_counts(self) -> dict[str, int]:
        data = self._reader.get_metrics_data()
        result: dict[str, int] = {}
        if data is None:
            return result
        for resource_metrics in data.resource_metrics:
            for scope_metrics in resource_metrics.scope_metrics:
                for metric in scope_metrics.metrics:
                    if metric.name != metrics.MCP_LOCK_WAIT:
                        continue
                    for point in metric.data.data_points:
                        domain = point.attributes.get(metrics.ATTR_DOMAIN)
                        if domain is not None:
                            result[domain] = result.get(domain, 0) + point.count
        return result

    def test_a_real_write_through_the_generic_set_status_records_its_lock_wait(self):
        rid = self._create_req(self._template_body()).id
        assert rid is not None, "create_req always assigns a fresh id"

        result: Any = self._set_status(rid, "req", "proposed")

        self.assertNotIsInstance(result, InvalidStatusResult)  # a real write, not a rejected request
        self.assertEqual(result.status, "proposed")
        counts = self._req_lock_wait_counts()
        self.assertGreaterEqual(counts.get("req", 0), 1, "the production write's lock wait was not recorded")

    def test_an_invalid_status_takes_no_lock_and_records_no_wait(self):
        rid = self._create_req(self._template_body()).id
        assert rid is not None, "create_req always assigns a fresh id"
        before = self._req_lock_wait_counts()

        result = self._set_status(rid, "req", "review")  # not in REQ's closed vocabulary

        self.assertIsInstance(result, InvalidStatusResult)
        self.assertFalse(result.valid)
        self.assertEqual(result.status, "review")  # echoes the rejected request
        self.assertEqual(self._req_lock_wait_counts(), before)  # no lock taken, nothing recorded
        # and the document was not modified by the rejected call:
        self.assertEqual(self._set_status(rid, "req", "draft").status, "draft")


if __name__ == "__main__":
    unittest.main()
