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

"""Tests for the ``list_sop`` ``@mcp.tool()`` wrapper (Task 2.2, ACC-003).

Paged from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13) -- there is no
former ``specmgr://sop/list`` resource these tests could have migrated from,
so the paging assertions below are written directly against the tool's own
contract (default page size 25, cap 100, out-of-range values clamped not
errored -- ACC-003's ``list_sop`` paging-clamp clause).
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
from biz.dfch.specmgr.sop.models.v1 import SopSummary
from biz.dfch.specmgr.sop.tools._paths import ensure_sop_base_dir
from biz.dfch.specmgr.sop.tools.create_sop import create_sop
from biz.dfch.specmgr.sop.tools.list_sop import list_sop

_MINIMAL_BODY = textwrap.dedent(
    """\
    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for new hires.

    ## Procedure

    ### Step 1: Submit request

    HR submits the request.
    """
)

_OTHER_BODY = _MINIMAL_BODY.replace("New Employee IT Account Provisioning", "Nightly Backup Procedure")


def _body_with_title(title: str) -> str:
    return _MINIMAL_BODY.replace("New Employee IT Account Provisioning", title)


class TestListSop(unittest.TestCase):
    """Tests for the list_sop tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_summaries_and_skips_malformed_file(self) -> None:
        first = create_sop(_MINIMAL_BODY)
        second = create_sop(_OTHER_BODY)

        base_dir = ensure_sop_base_dir()
        (base_dir / "broken.md").write_text("not a valid SOP, no headings at all", encoding="utf-8")

        sut = list_sop()

        self.assertIsInstance(sut, PagedResult)
        self.assertEqual(sut.total, 2)
        for summary in sut.results:
            self.assertIsInstance(summary, SopSummary)
        ids = {summary.id for summary in sut.results}
        self.assertEqual(ids, {first.id, second.id})
        titles = {summary.title for summary in sut.results}
        self.assertEqual(titles, {"New Employee IT Account Provisioning", "Nightly Backup Procedure"})
        statuses = {summary.status for summary in sut.results}
        self.assertEqual(statuses, {"draft"})
        for summary in sut.results:
            self.assertNotIn(".md", summary.ref)
            self.assertTrue(summary.ref)

    def test_empty_result_for_missing_directory(self) -> None:
        self.assertFalse((self.docs_root / "sop").exists())

        sut = list_sop()

        self.assertEqual(sut.total, 0)
        self.assertEqual(sut.results, [])
        self.assertFalse(sut.truncated)

    def test_default_page_size_with_more_than_25_documents(self) -> None:
        for i in range(26):
            create_sop(_body_with_title(f"Procedure Number {i:02d}"))

        sut = list_sop()

        self.assertEqual(sut.total, 26)
        self.assertEqual(sut.offset, 0)
        self.assertEqual(sut.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(len(sut.results), 25)
        self.assertTrue(sut.truncated)

    def test_max_results_limits_page_and_marks_truncated(self) -> None:
        for i in range(3):
            create_sop(_body_with_title(f"Procedure Number {i:02d}"))

        sut = list_sop(max_results=2)

        self.assertEqual(sut.total, 3)
        self.assertEqual(len(sut.results), 2)
        self.assertTrue(sut.truncated)

    def test_offset_selects_the_next_page(self) -> None:
        for i in range(3):
            create_sop(_body_with_title(f"Procedure Number {i:02d}"))

        first_page = list_sop(max_results=2)
        second_page = list_sop(max_results=2, offset=2)

        self.assertEqual(len(second_page.results), 1)
        self.assertFalse(second_page.truncated)
        first_ids = {summary.id for summary in first_page.results}
        second_ids = {summary.id for summary in second_page.results}
        self.assertEqual(len(first_ids | second_ids), 3)
        self.assertEqual(first_ids & second_ids, set())

    def test_max_results_is_clamped_to_the_cap(self) -> None:
        create_sop(_MINIMAL_BODY)

        sut = list_sop(max_results=500)

        self.assertEqual(sut.max_results, MAX_MAX_RESULTS)

    def test_negative_offset_is_floored_to_zero(self) -> None:
        create_sop(_MINIMAL_BODY)

        sut = list_sop(offset=-5)

        self.assertEqual(sut.offset, 0)

    def test_truncated_boundary_false_when_page_covers_all_items(self) -> None:
        for i in range(2):
            create_sop(_body_with_title(f"Procedure Number {i:02d}"))

        sut = list_sop(max_results=2)

        self.assertFalse(sut.truncated)

    def test_truncated_boundary_true_when_one_item_remains(self) -> None:
        for i in range(3):
            create_sop(_body_with_title(f"Procedure Number {i:02d}"))

        sut = list_sop(max_results=2)

        self.assertTrue(sut.truncated)

    def test_truncated_false_when_offset_exactly_at_the_end(self) -> None:
        for i in range(26):
            create_sop(_body_with_title(f"Procedure Number {i:02d}"))

        last_page = list_sop(max_results=25, offset=25)
        past_end = list_sop(max_results=25, offset=26)

        self.assertEqual(len(last_page.results), 1)
        self.assertFalse(last_page.truncated)
        self.assertEqual(past_end.results, [])
        self.assertFalse(past_end.truncated)

    def test_total_reflects_full_parseable_count_regardless_of_paging(self) -> None:
        for i in range(5):
            create_sop(_body_with_title(f"Procedure Number {i:02d}"))
        base_dir = ensure_sop_base_dir()
        (base_dir / "broken.md").write_text("not a valid SOP, no headings at all", encoding="utf-8")

        sut = list_sop(max_results=1, offset=1)

        self.assertEqual(sut.total, 5)


if __name__ == "__main__":
    unittest.main()
