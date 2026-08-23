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

"""Tests for the ``list_qa`` ``@mcp.tool()`` wrapper (feat-13-list-paging Task 2.5).

Migrated from ``tests/qa/resources/test_qa_list.py`` (the ``qa_list``
resource it exercised was converted into this tool), plus new paging
assertions.
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
from biz.dfch.specmgr.qa.models.v2 import QaSummary
from biz.dfch.specmgr.qa.tools._paths import ensure_qa_base_dir
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.qa.tools.list_qa import list_qa

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Some QA Title

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    ## Elicitation Context

    ## Functional Suitability

    ## Performance Efficiency

    ## Compatibility

    ## Interaction Capability

    ## Reliability

    ## Security

    ## Maintainability

    ## Flexibility

    ## Safety
    """
)

_OTHER_BODY = _MINIMAL_BODY.replace("Some QA Title", "Another QA Title")


def _body_with_title(title: str) -> str:
    return _MINIMAL_BODY.replace("Some QA Title", title)


class TestListQa(unittest.TestCase):
    """Tests for the list_qa tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_summaries_and_skips_malformed_file(self) -> None:
        first = create_qa(_MINIMAL_BODY)
        second = create_qa(_OTHER_BODY)

        base_dir = ensure_qa_base_dir()
        (base_dir / "broken.md").write_text("not a valid QA document, no headings at all", encoding="utf-8")

        sut = list_qa()

        self.assertIsInstance(sut, PagedResult)
        self.assertEqual(sut.total, 2)
        for summary in sut.results:
            self.assertIsInstance(summary, QaSummary)
        ids = {summary.id for summary in sut.results}
        self.assertEqual(ids, {first.frontmatter.id, second.frontmatter.id})
        titles = {summary.title for summary in sut.results}
        self.assertEqual(titles, {"Some QA Title", "Another QA Title"})
        statuses = {summary.status for summary in sut.results}
        self.assertEqual(statuses, {"draft"})
        for summary in sut.results:
            self.assertNotIn(".md", summary.ref)
            self.assertTrue(summary.ref)

    def test_empty_result_for_missing_directory(self) -> None:
        self.assertFalse((self.docs_root / "qa").exists())

        sut = list_qa()

        self.assertEqual(sut.total, 0)
        self.assertEqual(sut.results, [])
        self.assertFalse(sut.truncated)

    def test_default_page_size_and_shape(self) -> None:
        for i in range(3):
            create_qa(_body_with_title(f"Title {i}"))

        sut = list_qa()

        self.assertEqual(sut.total, 3)
        self.assertEqual(sut.offset, 0)
        self.assertEqual(sut.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(len(sut.results), 3)
        self.assertFalse(sut.truncated)

    def test_max_results_limits_page_and_marks_truncated(self) -> None:
        for i in range(3):
            create_qa(_body_with_title(f"Title {i}"))

        sut = list_qa(max_results=2)

        self.assertEqual(sut.total, 3)
        self.assertEqual(len(sut.results), 2)
        self.assertTrue(sut.truncated)

    def test_offset_selects_the_next_page(self) -> None:
        for i in range(3):
            create_qa(_body_with_title(f"Title {i}"))

        first_page = list_qa(max_results=2)
        second_page = list_qa(max_results=2, offset=2)

        self.assertEqual(len(second_page.results), 1)
        self.assertFalse(second_page.truncated)
        self.assertNotEqual(first_page.results[0].id, second_page.results[0].id)

    def test_max_results_is_clamped_to_the_cap(self) -> None:
        create_qa(_MINIMAL_BODY)

        sut = list_qa(max_results=500)

        self.assertEqual(sut.max_results, MAX_MAX_RESULTS)

    def test_negative_offset_is_floored_to_zero(self) -> None:
        create_qa(_MINIMAL_BODY)

        sut = list_qa(offset=-5)

        self.assertEqual(sut.offset, 0)

    def test_truncated_boundary_false_when_page_covers_all_items(self) -> None:
        for i in range(2):
            create_qa(_body_with_title(f"Title {i}"))

        sut = list_qa(max_results=2)

        self.assertFalse(sut.truncated)

    def test_truncated_boundary_true_when_one_item_remains(self) -> None:
        for i in range(3):
            create_qa(_body_with_title(f"Title {i}"))

        sut = list_qa(max_results=2)

        self.assertTrue(sut.truncated)

    def test_total_reflects_full_parseable_count_regardless_of_paging(self) -> None:
        for i in range(5):
            create_qa(_body_with_title(f"Title {i}"))
        base_dir = ensure_qa_base_dir()
        (base_dir / "broken.md").write_text("not a valid QA document, no headings at all", encoding="utf-8")

        sut = list_qa(max_results=1, offset=1)

        self.assertEqual(sut.total, 5)


if __name__ == "__main__":
    unittest.main()
