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

"""Acceptance-criteria-level tests for the req domain's cache wiring (feat-107-doc-cache Phase 3, Task 3.6).

Covers ACC-001 through ACC-006 (``.specmgr/feat/feat-107-doc-cache/README.md``)
specifically for ``req``, the pilot domain. See ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d for the cache design these tests
validate.

**Critical mocking detail**: to count real ``parse_req`` invocations, every
test here patches ``biz.dfch.specmgr.req.tools._cache.parse_req`` (the name
``req.tools._cache`` bound into its own module namespace via
``from ..models.v1 import parse_req``), not
``biz.dfch.specmgr.req.models.v1.parse_req`` -- patching the latter has no
effect on the already-bound local reference inside ``_cache.py``. Every
patch uses ``wraps=`` the real function so correctness is preserved (the
real parser still actually runs) while ``.call_count`` is recorded.

**Critical test-isolation requirement**: ``req.tools._cache``'s ``_cache``
is a module-level singleton -- every test here calls ``reset_req_cache()``
in both ``setUp`` and ``tearDown`` so no test observes another test's
cached entries (this project's suite runs under ``pytest-xdist``/``-n
auto``: each worker is its own process, so the real risk is cross-test
contamination *within* one worker process, not cross-worker).
"""

from __future__ import annotations

import tempfile
import textwrap
import threading
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools.delete import delete
from biz.dfch.specmgr.req.models.v1 import parse_req
from biz.dfch.specmgr.req.tools._cache import _cache, read_req, reset_req_cache
from biz.dfch.specmgr.req.tools._paths import ensure_req_base_dir, find_req_path
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.req.tools.get_req import get_req
from biz.dfch.specmgr.req.tools.list_req import list_req

#: Deliberately malformed YAML (an unterminated flow sequence) inside an otherwise well-formed
#: frontmatter block -- triggers a genuine, unwrapped `yaml.YAMLError` from `parse_req` (via
#: `models.md._frontmatter_parse.parse_frontmatter`), not a `pydantic.ValidationError`.
_MALFORMED_YAML_FRONTMATTER_DOC = (
    "---\n"
    "id: [this is not valid yaml because the flow sequence is never closed\n"
    "type: req\n"
    "version: 1.0.0\n"
    "status: draft\n"
    "created: '2026-08-05 00:00:00.000Z'\n"
    "updated: '2026-08-05 00:00:00.000Z'\n"
    "---\n"
    "\n"
    "# Malformed Frontmatter Fixture\n"
)

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.

    ## Description

    If the engine becomes too hot, the lifetime of the system decreases.

    ## Characteristics

    1. Safety
    1. Reliability

    ## Level

    MUST

    ## Source

    The International Safety Board Association (TISBA)
    """
)

_OTHER_BODY = _MINIMAL_BODY.replace("Maximum Engine Temperature", "Minimum Oil Pressure")


def _patch_parse_req() -> mock._patch:
    """A ``mock.patch`` targeting ``req.tools._cache``'s own bound ``parse_req`` name, wrapping the real function."""
    return mock.patch("biz.dfch.specmgr.req.tools._cache.parse_req", wraps=parse_req)


class TestAcc001SingleGetReqParsesOnce(unittest.TestCase):
    """ACC-001: a single get_req call must invoke parse_req exactly once, not twice.

    Regression test for the pre-existing matched-file double-parse bug:
    ``get_req``'s ``load_by_id`` -> ``find_req_path``'s scan (via
    ``find_doc_path_by_id``'s ``read_fn``) parses and caches the matching
    file; ``load_by_id``'s own subsequent ``read_req(path)`` call is then a
    guaranteed cache hit.
    """

    def setUp(self) -> None:
        reset_req_cache()
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def tearDown(self) -> None:
        reset_req_cache()

    def test_get_req_invokes_parse_req_exactly_once(self) -> None:
        # create_req itself warms the cache (Task 3.3) with its own read_req call, so a
        # get_req call immediately afterward would be a guaranteed cache hit (0 parses) --
        # not the scenario ACC-001 targets. reset_req_cache() here discards that warming so
        # the id is genuinely cold for the get_req call under test, exactly like a freshly
        # started server process reading a pre-existing on-disk document for the first time.
        created = create_req(_MINIMAL_BODY)
        reset_req_cache()

        with _patch_parse_req() as spy:
            result = get_req(created.id)

        self.assertEqual(result.frontmatter.id, created.id)
        # Exactly once, not twice: get_req's load_by_id -> find_req_path's scan (via
        # find_doc_path_by_id's read_fn) parses-and-caches the matching file; load_by_id's
        # own subsequent read_req(path) call is then a guaranteed cache hit.
        self.assertEqual(spy.call_count, 1)


class TestAcc002RepeatedGetReqParsesOnceTotal(unittest.TestCase):
    """ACC-002: N sequential get_req calls against an unchanged file invoke parse_req once total."""

    def setUp(self) -> None:
        reset_req_cache()
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def tearDown(self) -> None:
        reset_req_cache()

    def test_n_total_calls_including_the_first_produce_exactly_one_parse(self) -> None:
        """Framing: N calls total (including the first, cache-warming one) => parse_req.call_count == 1.

        (Equivalent framing to "N-1 additional calls after a warm-up call add zero
        parses" -- this test asserts the whole N-call sequence directly.) The cache is
        reset right after create_req so the very first of the N get_req calls below is
        the one that actually warms the cache (mirroring ACC-001's cold-start framing),
        rather than being a guaranteed hit from create_req's own write-path warming.
        """
        created = create_req(_MINIMAL_BODY)
        reset_req_cache()

        with _patch_parse_req() as spy:
            for _ in range(5):
                result = get_req(created.id)
                self.assertEqual(result.frontmatter.id, created.id)

        self.assertEqual(spy.call_count, 1)


class TestAcc003ContentChangeIsDetected(unittest.TestCase):
    """ACC-003: modifying a cached file's content on disk (bypassing every specmgr tool) is detected."""

    def setUp(self) -> None:
        reset_req_cache()
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def tearDown(self) -> None:
        reset_req_cache()

    def _sole_doc_path(self) -> Path:
        matches = list((self.docs_root / "req").glob("*.md"))
        self.assertEqual(len(matches), 1)
        return matches[0]

    def test_get_req_reparses_and_returns_new_content_after_direct_edit(self) -> None:
        created = create_req(_MINIMAL_BODY)
        path = self._sole_doc_path()

        with _patch_parse_req() as spy:
            get_req(created.id)  # warm/confirm cache state (should be a hit from create_req's own warming)
            self.assertEqual(spy.call_count, 0)

            new_text = path.read_text(encoding="utf-8").replace(
                "Maximum Engine Temperature", "Changed Title Direct Edit"
            )
            path.write_text(new_text, encoding="utf-8")

            result = get_req(created.id)

            self.assertEqual(spy.call_count, 1)
            self.assertEqual(result.body.text, "Changed Title Direct Edit")

    def test_list_req_reparses_and_returns_new_content_after_direct_edit(self) -> None:
        created = create_req(_MINIMAL_BODY)
        path = self._sole_doc_path()
        list_req()  # warm via a scan too

        new_text = path.read_text(encoding="utf-8").replace("Maximum Engine Temperature", "Changed Via List")
        path.write_text(new_text, encoding="utf-8")

        sut = list_req()

        summary = next(s for s in sut.results if s.id == created.id)
        self.assertEqual(summary.title, "Changed Via List")


class TestAcc004OrphanReconciledOnScan(unittest.TestCase):
    """ACC-004: deleting a file directly on disk drops its cache entry on the next scanning call."""

    def setUp(self) -> None:
        reset_req_cache()
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def tearDown(self) -> None:
        reset_req_cache()

    def test_list_req_reconcile_drops_entry_for_a_file_deleted_outside_specmgr(self) -> None:
        first = create_req(_MINIMAL_BODY)
        second = create_req(_OTHER_BODY)
        base_dir = ensure_req_base_dir()
        first_path = next(p for p in base_dir.glob("*.md") if first.id in p.name)

        # Warm the cache for both documents via one list_req() scan.
        sut = list_req()
        self.assertEqual(sut.total, 2)
        self.assertIn(first_path, _cache._entries)  # pylint: disable=protected-access

        # Bypass every specmgr tool: delete one file directly on disk.
        first_path.unlink()

        # The next scanning call must reconcile the cache against the live listing.
        sut = list_req()
        self.assertEqual(sut.total, 1)
        self.assertNotIn(first_path, _cache._entries)  # pylint: disable=protected-access
        remaining_ids = {summary.id for summary in sut.results}
        self.assertEqual(remaining_ids, {second.id})


class TestAcc005DeleteInvalidatesImmediately(unittest.TestCase):
    """ACC-005: calling the generic delete tool immediately invalidates that id's cache entry.

    Distinct from ACC-004: `delete` invalidates *eagerly*, at delete time,
    with no further "next scan" trigger call needed at all.
    """

    def setUp(self) -> None:
        reset_req_cache()
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def tearDown(self) -> None:
        reset_req_cache()

    def test_delete_immediately_drops_the_cache_entry_with_no_further_trigger_call(self) -> None:
        created = create_req(_MINIMAL_BODY)
        base_dir = ensure_req_base_dir()
        path = next(p for p in base_dir.glob("*.md") if created.id in p.name)

        # create_req's own write-path warming already populated the cache entry.
        self.assertIn(path, _cache._entries)  # pylint: disable=protected-access

        delete(id=created.id, type="req")

        self.assertNotIn(path, _cache._entries)  # pylint: disable=protected-access


class TestAcc006ConcurrentReadsOfAnAlreadyWarmIdParseOnce(unittest.TestCase):
    """ACC-006: N threads calling get_req/read_req on the same *already-warm* id parse exactly once total.

    "already-warm" (per the acceptance criterion's own wording) means the
    id is warmed with a single call BEFORE any concurrent contention
    starts; a genuinely warm (unchanged-hash) entry is servable as a pure
    cache hit with no race window, so this asserts an exact, deterministic
    parse count of 1 (the single warming call), not a bounded-slack count.
    """

    def setUp(self) -> None:
        reset_req_cache()
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def tearDown(self) -> None:
        reset_req_cache()

    def test_20_concurrent_get_req_calls_against_an_already_warm_id_parse_exactly_once_total(self) -> None:
        created = create_req(_MINIMAL_BODY)
        # Warm the cache with one, single call before any concurrency starts.
        get_req(created.id)

        thread_count = 20
        barrier = threading.Barrier(thread_count)
        errors: list[BaseException] = []

        def worker() -> None:
            try:
                barrier.wait()
                get_req(created.id)
            except BaseException as exc:  # noqa: BLE001 - record for the main thread to fail loudly on
                errors.append(exc)

        with _patch_parse_req() as spy:
            threads = [threading.Thread(target=worker) for _ in range(thread_count)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        self.assertEqual(errors, [])
        self.assertEqual(spy.call_count, 0)  # the warm-up call above already happened outside the patch


class TestAcc012FindReqPathSkipsMalformedYamlFrontmatter(unittest.TestCase):
    """ACC-012 (feat-107-doc-cache Phase 6, REQ-010): a malformed-YAML-frontmatter file must not
    crash the id-lookup scan for a *different*, valid file's id.

    Regression test for ``general.tools._doc_paths.find_doc_path_by_id``'s
    skip-on-parse-failure clause not previously catching ``yaml.YAMLError``
    (not a ``ValueError`` subclass) -- before this fix, a domain directory
    with one file whose frontmatter YAML was malformed crashed the scan
    with an uncaught ``yaml.YAMLError`` for *any* id in that domain, not
    just the malformed file's own id.
    """

    def setUp(self) -> None:
        reset_req_cache()
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def tearDown(self) -> None:
        reset_req_cache()

    def test_valid_files_id_still_resolves_alongside_a_malformed_yaml_sibling(self) -> None:
        created = create_req(_MINIMAL_BODY)
        base_dir = ensure_req_base_dir()

        malformed_path = base_dir / "malformed-yaml-frontmatter.md"
        malformed_path.write_text(_MALFORMED_YAML_FRONTMATTER_DOC, encoding="utf-8")

        good_path = next(p for p in base_dir.glob("*.md") if created.id in p.name)
        self.assertEqual(find_req_path(base_dir, created.id), good_path)


class TestAcc006ColdConcurrentReadsStayBounded(unittest.TestCase):
    """Supplementary to ACC-006: a genuinely cold (never-yet-read) path under concurrent contention.

    Unlike the "already-warm" variant above, a first-ever read of a path
    has a real race window (no entry exists yet for any thread to hit), so
    ``DocCache`` does not attempt to de-duplicate in-flight parses (see its
    own docstring). This asserts only a sane upper bound (``<= N``), not an
    exact count, and is kept separate from the primary, deterministic
    "already-warm" test so a flaky empirical slack number never taints the
    ACC-006 acceptance test itself.
    """

    def setUp(self) -> None:
        reset_req_cache()
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def tearDown(self) -> None:
        reset_req_cache()

    def test_20_concurrent_reads_of_a_cold_path_never_exceed_thread_count_parses(self) -> None:
        created = create_req(_MINIMAL_BODY)
        base_dir = ensure_req_base_dir()
        path = next(p for p in base_dir.glob("*.md") if created.id in p.name)
        reset_req_cache()  # discard create_req's own warming so the path is genuinely cold again

        thread_count = 20
        barrier = threading.Barrier(thread_count)
        errors: list[BaseException] = []

        def worker() -> None:
            try:
                barrier.wait()
                read_req(path)
            except BaseException as exc:  # noqa: BLE001 - record for the main thread to fail loudly on
                errors.append(exc)

        with _patch_parse_req() as spy:
            threads = [threading.Thread(target=worker) for _ in range(thread_count)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        self.assertEqual(errors, [])
        self.assertGreaterEqual(spy.call_count, 1)
        self.assertLessEqual(spy.call_count, thread_count)


if __name__ == "__main__":
    unittest.main()
