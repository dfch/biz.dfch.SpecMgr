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

"""Tests for the ``list_adr`` ``@mcp.tool()`` wrapper (feat-13-list-paging Task 2.1).

Migrated from ``tests/adr/resources/test_adr.py``'s former
``TestAdrListResource`` (the ``adr_list`` resource it exercised was
converted into this tool), plus new paging assertions.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR
from biz.dfch.specmgr.adr.tools.list_adr import list_adr
from biz.dfch.specmgr.general.models import PagedResult
from biz.dfch.specmgr.general.tools._paging import DEFAULT_MAX_RESULTS, MAX_MAX_RESULTS
from biz.dfch.specmgr.models.adr import Adr, AdrBody, AdrFrontmatter, AdrSummary, render_adr


def _body(title: str) -> AdrBody:
    return AdrBody(
        title=title,
        context_and_problem_statement="Context.",
        considered_options="Options.",
        decision_outcome="Outcome.",
    )


def _write_adr(base: Path, filename: str, id_: str, title: str, status: str = "accepted") -> None:
    adr = Adr(frontmatter=AdrFrontmatter(id=id_, status=status), body=_body(title))
    (base / filename).write_text(render_adr(adr), encoding="utf-8")


class TestListAdr(unittest.TestCase):
    """Tests for the list_adr tool."""

    def setUp(self) -> None:
        self.base = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {ADR_DIR_ENV_VAR: str(self.base)}))

    def test_returns_summaries_and_skips_malformed_file(self) -> None:
        _write_adr(self.base, "1.md", "id-1", "First title")
        _write_adr(self.base, "2.md", "id-2", "Second title", status="proposed")
        (self.base / "3-broken.md").write_text("not a valid ADR, no headings at all", encoding="utf-8")

        sut = list_adr()

        self.assertIsInstance(sut, PagedResult)
        self.assertEqual(sut.total, 2)
        for summary in sut.results:
            self.assertIsInstance(summary, AdrSummary)
        titles = {summary.title for summary in sut.results}
        self.assertEqual(titles, {"First title", "Second title"})
        refs = {summary.ref for summary in sut.results}
        self.assertEqual(refs, {"1", "2"})
        for ref in refs:
            self.assertNotIn(".md", ref)

    def test_empty_result_for_missing_directory(self) -> None:
        missing = self.base / "does-not-exist"
        with mock.patch.dict("os.environ", {ADR_DIR_ENV_VAR: str(missing)}):
            sut = list_adr()

        self.assertEqual(sut.total, 0)
        self.assertEqual(sut.results, [])
        self.assertFalse(sut.truncated)

    def test_default_page_size_and_shape(self) -> None:
        for i in range(3):
            _write_adr(self.base, f"{i}.md", f"id-{i}", f"Title {i}")

        sut = list_adr()

        self.assertEqual(sut.total, 3)
        self.assertEqual(sut.offset, 0)
        self.assertEqual(sut.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(len(sut.results), 3)
        self.assertFalse(sut.truncated)

    def test_max_results_limits_page_and_marks_truncated(self) -> None:
        for i in range(3):
            _write_adr(self.base, f"{i}.md", f"id-{i}", f"Title {i}")

        sut = list_adr(max_results=2)

        self.assertEqual(sut.total, 3)
        self.assertEqual(len(sut.results), 2)
        self.assertTrue(sut.truncated)

    def test_offset_selects_the_next_page(self) -> None:
        for i in range(3):
            _write_adr(self.base, f"{i}.md", f"id-{i}", f"Title {i}")

        first_page = list_adr(max_results=2)
        second_page = list_adr(max_results=2, offset=2)

        self.assertEqual(len(second_page.results), 1)
        self.assertFalse(second_page.truncated)
        self.assertNotEqual(first_page.results[0].id, second_page.results[0].id)

    def test_max_results_is_clamped_to_the_cap(self) -> None:
        _write_adr(self.base, "0.md", "id-0", "Title 0")

        sut = list_adr(max_results=500)

        self.assertEqual(sut.max_results, MAX_MAX_RESULTS)

    def test_negative_offset_is_floored_to_zero(self) -> None:
        _write_adr(self.base, "0.md", "id-0", "Title 0")

        sut = list_adr(offset=-5)

        self.assertEqual(sut.offset, 0)

    def test_truncated_boundary_false_when_page_covers_all_items(self) -> None:
        for i in range(2):
            _write_adr(self.base, f"{i}.md", f"id-{i}", f"Title {i}")

        sut = list_adr(max_results=2)

        self.assertFalse(sut.truncated)

    def test_truncated_boundary_true_when_one_item_remains(self) -> None:
        for i in range(3):
            _write_adr(self.base, f"{i}.md", f"id-{i}", f"Title {i}")

        sut = list_adr(max_results=2)

        self.assertTrue(sut.truncated)

    def test_total_reflects_full_parseable_count_regardless_of_paging(self) -> None:
        for i in range(5):
            _write_adr(self.base, f"{i}.md", f"id-{i}", f"Title {i}")
        (self.base / "broken.md").write_text("not a valid ADR, no headings at all", encoding="utf-8")

        sut = list_adr(max_results=1, offset=1)

        self.assertEqual(sut.total, 5)


if __name__ == "__main__":
    unittest.main()
