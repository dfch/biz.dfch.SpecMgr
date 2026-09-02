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

"""Tests for the ``list_uc`` ``@mcp.tool()`` wrapper (feat-13-list-paging Task 2.3).

Migrated from ``tests/uc/resources/test_uc_list.py`` (the ``uc_list``
resource it exercised was converted into this tool), plus new paging
assertions. Also exercises
:class:`~biz.dfch.specmgr.uc.models.v2.UcSummary` -- no dedicated
``test_summary.py`` exists (mirroring REQ, which has none either).
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import PagedResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._paging import DEFAULT_MAX_RESULTS, MAX_MAX_RESULTS
from biz.dfch.specmgr.uc.models.v2 import UcSummary
from biz.dfch.specmgr.uc.tools._paths import ensure_uc_base_dir
from biz.dfch.specmgr.uc.tools.create_uc import create_uc
from biz.dfch.specmgr.uc.tools.list_uc import list_uc

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Buy Goods

    ## Characteristic Information

    ### Goal in Context

    Buyer issues request directly to our company.

    ### Scope

    Company (the system being designed as a black box)

    ### Level

    Summary

    ### Preconditions

    - We know Buyer

    ### Success End Condition

    - Buyer has goods

    ### Primary Actor

    Buyer.

    ### Trigger

    Purchase request comes in.

    ## Main Success Scenario

    1. Buyer calls in with a purchase request.
    2. Company creates order in system.
    """
)

_OTHER_BODY = _MINIMAL_BODY.replace("Buy Goods", "Return Goods")


def _body_with_title(title: str) -> str:
    return _MINIMAL_BODY.replace("Buy Goods", title)


class TestListUc(unittest.TestCase):
    """Tests for the list_uc tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_summaries_and_skips_malformed_file(self) -> None:
        first = create_uc(_MINIMAL_BODY)
        second = create_uc(_OTHER_BODY)

        base_dir = ensure_uc_base_dir()
        (base_dir / "broken.md").write_text("not a valid use case, no headings at all", encoding="utf-8")

        sut = list_uc()

        self.assertIsInstance(sut, PagedResult)
        self.assertEqual(sut.total, 2)
        for summary in sut.results:
            self.assertIsInstance(summary, UcSummary)
        ids = {summary.id for summary in sut.results}
        self.assertEqual(ids, {first.id, second.id})
        titles = {summary.title for summary in sut.results}
        self.assertEqual(titles, {"Buy Goods", "Return Goods"})
        statuses = {summary.status for summary in sut.results}
        self.assertEqual(statuses, {"draft"})
        for summary in sut.results:
            self.assertNotIn(".md", summary.ref)
            self.assertTrue(summary.ref)

    def test_empty_result_for_missing_directory(self) -> None:
        self.assertFalse((self.docs_root / "uc").exists())

        sut = list_uc()

        self.assertEqual(sut.total, 0)
        self.assertEqual(sut.results, [])
        self.assertFalse(sut.truncated)

    def test_default_page_size_and_shape(self) -> None:
        for i in range(3):
            create_uc(_body_with_title(f"Title {i}"))

        sut = list_uc()

        self.assertEqual(sut.total, 3)
        self.assertEqual(sut.offset, 0)
        self.assertEqual(sut.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(len(sut.results), 3)
        self.assertFalse(sut.truncated)

    def test_max_results_limits_page_and_marks_truncated(self) -> None:
        for i in range(3):
            create_uc(_body_with_title(f"Title {i}"))

        sut = list_uc(max_results=2)

        self.assertEqual(sut.total, 3)
        self.assertEqual(len(sut.results), 2)
        self.assertTrue(sut.truncated)

    def test_offset_selects_the_next_page(self) -> None:
        for i in range(3):
            create_uc(_body_with_title(f"Title {i}"))

        first_page = list_uc(max_results=2)
        second_page = list_uc(max_results=2, offset=2)

        self.assertEqual(len(second_page.results), 1)
        self.assertFalse(second_page.truncated)
        self.assertNotEqual(first_page.results[0].id, second_page.results[0].id)

    def test_max_results_is_clamped_to_the_cap(self) -> None:
        create_uc(_MINIMAL_BODY)

        sut = list_uc(max_results=500)

        self.assertEqual(sut.max_results, MAX_MAX_RESULTS)

    def test_negative_offset_is_floored_to_zero(self) -> None:
        create_uc(_MINIMAL_BODY)

        sut = list_uc(offset=-5)

        self.assertEqual(sut.offset, 0)

    def test_truncated_boundary_false_when_page_covers_all_items(self) -> None:
        for i in range(2):
            create_uc(_body_with_title(f"Title {i}"))

        sut = list_uc(max_results=2)

        self.assertFalse(sut.truncated)

    def test_truncated_boundary_true_when_one_item_remains(self) -> None:
        for i in range(3):
            create_uc(_body_with_title(f"Title {i}"))

        sut = list_uc(max_results=2)

        self.assertTrue(sut.truncated)

    def test_total_reflects_full_parseable_count_regardless_of_paging(self) -> None:
        for i in range(5):
            create_uc(_body_with_title(f"Title {i}"))
        base_dir = ensure_uc_base_dir()
        (base_dir / "broken.md").write_text("not a valid use case, no headings at all", encoding="utf-8")

        sut = list_uc(max_results=1, offset=1)

        self.assertEqual(sut.total, 5)


if __name__ == "__main__":
    unittest.main()
