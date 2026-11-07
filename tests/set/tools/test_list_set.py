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

"""Tests for the ``list_set`` ``@mcp.tool()`` wrapper (feat-229-set Phase 110).

Paged from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13) -- there is no
former ``specmgr://set/list`` resource these tests could have migrated from,
so the paging assertions below are written directly against the tool's own
contract (default page size 25, cap 100, out-of-range values clamped not
errored).
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
from biz.dfch.specmgr.set.models.v1 import SetSummary
from biz.dfch.specmgr.set.tools._paths import ensure_set_base_dir
from biz.dfch.specmgr.set.tools.create_set import create_set
from biz.dfch.specmgr.set.tools.list_set import list_set

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Sample Review Set

    ## Description

    Some prose about what the set bundles and why the items belong together.

    ## Items

    - REQ 00000000-0000-4000-8000-000000000001: Sample Requirement
    """
)

_OTHER_BODY = _MINIMAL_BODY.replace("Sample Review Set", "Second Review Set")


def _body_with_title(title: str) -> str:
    return _MINIMAL_BODY.replace("Sample Review Set", title)


class TestListSet(unittest.TestCase):
    """Tests for the list_set tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_summaries_and_reports_malformed_file_as_a_failed_entry(self) -> None:
        first = create_set(_MINIMAL_BODY)
        second = create_set(_OTHER_BODY)

        base_dir = ensure_set_base_dir()
        broken_path = base_dir / "broken.md"
        broken_path.write_text("not a valid set document, no headings at all", encoding="utf-8")

        sut = list_set()

        self.assertIsInstance(sut, PagedResult)
        self.assertEqual(sut.total, 3)
        self.assertEqual(sut.error_count, 1)
        for summary in sut.results:
            self.assertIsInstance(summary, SetSummary)
        ids = {summary.id for summary in sut.results}
        self.assertEqual(ids, {first.id, second.id, None})
        titles = {summary.title for summary in sut.results}
        self.assertEqual(titles, {"Sample Review Set", "Second Review Set", "<failed to parse>"})
        statuses = {summary.status for summary in sut.results}
        self.assertEqual(statuses, {"draft", "<failed to parse>"})
        for summary in sut.results:
            self.assertNotIn(".md", summary.ref)
            self.assertTrue(summary.ref)
            self.assertTrue(Path(summary.path).is_absolute())

        failed = next(summary for summary in sut.results if summary.ref == "broken")
        self.assertIsNone(failed.id)
        self.assertEqual(failed.title, "<failed to parse>")
        self.assertEqual(failed.status, "<failed to parse>")
        self.assertEqual(Path(failed.path), broken_path.resolve())
        self.assertIsNotNone(failed.error)

    def test_empty_result_for_missing_directory(self) -> None:
        self.assertFalse((self.docs_root / "set").exists())

        sut = list_set()

        self.assertEqual(sut.total, 0)
        self.assertEqual(sut.results, [])
        self.assertFalse(sut.truncated)

    def test_default_page_size_with_more_than_25_documents(self) -> None:
        for i in range(26):
            create_set(_body_with_title(f"Review Notes Number {i:02d}"))

        sut = list_set()

        self.assertEqual(sut.total, 26)
        self.assertEqual(sut.offset, 0)
        self.assertEqual(sut.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(len(sut.results), 25)
        self.assertTrue(sut.truncated)

    def test_max_results_limits_page_and_marks_truncated(self) -> None:
        for i in range(3):
            create_set(_body_with_title(f"Review Notes Number {i:02d}"))

        sut = list_set(max_results=2)

        self.assertEqual(sut.total, 3)
        self.assertEqual(len(sut.results), 2)
        self.assertTrue(sut.truncated)

    def test_offset_selects_the_next_page(self) -> None:
        for i in range(3):
            create_set(_body_with_title(f"Review Notes Number {i:02d}"))

        first_page = list_set(max_results=2)
        second_page = list_set(max_results=2, offset=2)

        self.assertEqual(len(second_page.results), 1)
        self.assertFalse(second_page.truncated)
        first_ids = {summary.id for summary in first_page.results}
        second_ids = {summary.id for summary in second_page.results}
        self.assertEqual(len(first_ids | second_ids), 3)
        self.assertEqual(first_ids & second_ids, set())

    def test_max_results_is_clamped_to_the_cap(self) -> None:
        create_set(_MINIMAL_BODY)

        sut = list_set(max_results=500)

        self.assertEqual(sut.max_results, MAX_MAX_RESULTS)

    def test_negative_offset_is_floored_to_zero(self) -> None:
        create_set(_MINIMAL_BODY)

        sut = list_set(offset=-5)

        self.assertEqual(sut.offset, 0)

    def test_truncated_boundary_false_when_page_covers_all_items(self) -> None:
        for i in range(2):
            create_set(_body_with_title(f"Review Notes Number {i:02d}"))

        sut = list_set(max_results=2)

        self.assertFalse(sut.truncated)

    def test_truncated_boundary_true_when_one_item_remains(self) -> None:
        for i in range(3):
            create_set(_body_with_title(f"Review Notes Number {i:02d}"))

        sut = list_set(max_results=2)

        self.assertTrue(sut.truncated)

    def test_truncated_false_when_offset_exactly_at_the_end(self) -> None:
        for i in range(26):
            create_set(_body_with_title(f"Review Notes Number {i:02d}"))

        last_page = list_set(max_results=25, offset=25)
        past_end = list_set(max_results=25, offset=26)

        self.assertEqual(len(last_page.results), 1)
        self.assertFalse(last_page.truncated)
        self.assertEqual(past_end.results, [])
        self.assertFalse(past_end.truncated)

    def test_total_and_error_count_reflect_the_full_directory_regardless_of_paging(self) -> None:
        for i in range(5):
            create_set(_body_with_title(f"Review Notes Number {i:02d}"))
        base_dir = ensure_set_base_dir()
        (base_dir / "broken.md").write_text("not a valid set document, no headings at all", encoding="utf-8")

        sut = list_set(max_results=1, offset=1)

        self.assertEqual(sut.total, 6)
        self.assertEqual(sut.error_count, 1)


if __name__ == "__main__":
    unittest.main()
