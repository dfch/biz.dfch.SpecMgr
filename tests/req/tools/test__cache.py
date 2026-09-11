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

"""Tests for ``req.tools._cache`` (feat-107-doc-cache Phase 3).

Mirrors ``tests/req/tools/test__lock.py``'s shape (a small, focused test
module for a small, focused singleton-holding module) rather than
``tests/general/tools/test__doc_cache.py``'s exhaustive ``DocCache``
coverage -- the generic ``DocCache`` class itself is already fully tested
there; this module only needs to confirm the ``req``-specific wiring
(``read_req``/``invalidate_req_cache``/``reconcile_req_cache``/
``reset_req_cache``) actually routes through one shared, module-level
cache instance.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.req.models.v1 import ReqDocument
from biz.dfch.specmgr.req.tools._cache import (
    invalidate_req_cache,
    read_req,
    reconcile_req_cache,
    reset_req_cache,
)

_DOC_TEMPLATE = textwrap.dedent(
    """\
    ---
    id: {id}
    type: req
    version: 1.0.0
    status: draft
    created: '2026-08-05 00:00:00.000Z'
    updated: '2026-08-05 00:00:00.000Z'
    ---

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


def _req_text(id_: str) -> str:
    """Render a minimal, valid requirement document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


class TestReqCache(unittest.TestCase):
    """Tests for the req-specific cache wiring in ``req.tools._cache``."""

    def setUp(self) -> None:
        reset_req_cache()
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def tearDown(self) -> None:
        reset_req_cache()

    def _write(self, name: str, id_: str) -> Path:
        path = self.tmp_path / name
        path.write_text(_req_text(id_), encoding="utf-8")
        return path

    def test_read_req_returns_a_req_document(self) -> None:
        path = self._write("a.md", "id-1")

        document = read_req(path)

        self.assertIsInstance(document, ReqDocument)
        self.assertEqual(document.frontmatter.id, "id-1")

    def test_second_read_of_unchanged_file_does_not_reinvoke_parse_req(self) -> None:
        path = self._write("a.md", "id-1")
        real_parse_req = self._real_parse_req()
        with mock.patch("biz.dfch.specmgr.req.tools._cache.parse_req", wraps=real_parse_req) as spy:
            read_req(path)
            read_req(path)
            self.assertEqual(spy.call_count, 1)

    def test_read_after_content_change_reinvokes_parse_req(self) -> None:
        path = self._write("a.md", "id-1")
        real_parse_req = self._real_parse_req()
        with mock.patch("biz.dfch.specmgr.req.tools._cache.parse_req", wraps=real_parse_req) as spy:
            read_req(path)
            path.write_text(_req_text("id-2"), encoding="utf-8")
            document = read_req(path)
            self.assertEqual(spy.call_count, 2)
            self.assertEqual(document.frontmatter.id, "id-2")

    def test_invalidate_req_cache_forces_a_reread(self) -> None:
        path = self._write("a.md", "id-1")
        real_parse_req = self._real_parse_req()
        with mock.patch("biz.dfch.specmgr.req.tools._cache.parse_req", wraps=real_parse_req) as spy:
            read_req(path)
            invalidate_req_cache(path)
            read_req(path)
            self.assertEqual(spy.call_count, 2)

    def test_reconcile_req_cache_drops_entries_not_in_live_paths(self) -> None:
        kept = self._write("kept.md", "id-1")
        dropped = self._write("dropped.md", "id-2")
        real_parse_req = self._real_parse_req()
        with mock.patch("biz.dfch.specmgr.req.tools._cache.parse_req", wraps=real_parse_req) as spy:
            read_req(kept)
            read_req(dropped)
            self.assertEqual(spy.call_count, 2)

            reconcile_req_cache([kept])

            read_req(dropped)  # dropped's entry was reconciled away -- a fresh parse
            self.assertEqual(spy.call_count, 3)
            read_req(kept)  # kept's entry survived reconcile -- still a cache hit
            self.assertEqual(spy.call_count, 3)

    def test_reset_req_cache_clears_every_entry(self) -> None:
        path = self._write("a.md", "id-1")
        real_parse_req = self._real_parse_req()
        with mock.patch("biz.dfch.specmgr.req.tools._cache.parse_req", wraps=real_parse_req) as spy:
            read_req(path)
            reset_req_cache()
            read_req(path)
            self.assertEqual(spy.call_count, 2)

    @staticmethod
    def _real_parse_req():
        """Return the genuine, unpatched ``parse_req`` to wrap with a counting mock."""
        from biz.dfch.specmgr.req.models.v1 import parse_req  # noqa: PLC0415

        return parse_req


if __name__ == "__main__":
    unittest.main()
