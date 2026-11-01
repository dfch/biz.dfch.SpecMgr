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

"""Tests for the ``list_req`` ``@mcp.tool()`` wrapper (feat-13-list-paging Task 2.2).

Migrated from ``tests/req/resources/test_req_list.py`` (the ``req_list``
resource it exercised was converted into this tool), plus new paging
assertions.

feat-81-83-validation Phase 3 (REQ-006/REQ-007, Task 3.3): a malformed file
no longer silently disappears from the listing -- it appears inline in
``results`` as a failed entry and contributes to both ``total`` and the new
``error_count``, and every successful entry now carries a resolved ``path``.
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
from biz.dfch.specmgr.req.models.v1 import ReqSummary
from biz.dfch.specmgr.req.tools._paths import ensure_req_base_dir
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.req.tools.list_req import list_req

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


def _body_with_title(title: str) -> str:
    return _MINIMAL_BODY.replace("Maximum Engine Temperature", title)


class TestListReq(unittest.TestCase):
    """Tests for the list_req tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_summaries_and_reports_malformed_file_as_a_failed_entry(self) -> None:
        first = create_req(_MINIMAL_BODY)
        second = create_req(_OTHER_BODY)

        base_dir = ensure_req_base_dir()
        broken_path = base_dir / "broken.md"
        broken_path.write_text("not a valid requirement, no headings at all", encoding="utf-8")

        sut = list_req()

        self.assertIsInstance(sut, PagedResult)
        self.assertEqual(sut.total, 3)
        self.assertEqual(sut.error_count, 1)
        for summary in sut.results:
            self.assertIsInstance(summary, ReqSummary)
        ids = {summary.id for summary in sut.results}
        self.assertEqual(ids, {first.id, second.id, None})
        titles = {summary.title for summary in sut.results}
        self.assertEqual(titles, {"Maximum Engine Temperature", "Minimum Oil Pressure", "<failed to parse>"})
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

        for summary in sut.results:
            if summary.ref != "broken":
                self.assertIsNone(summary.error)

    def test_malformed_yaml_frontmatter_is_reported_as_a_failed_entry(self) -> None:
        """A malformed YAML frontmatter block raises `yaml.YAMLError`, not `AssertionError`/`ValidationError`.

        Exercises the `yaml.YAMLError` arm of `build_summaries`'s default
        `error_types` (feat-81-83-validation Phase 3, Design Notes) --
        distinct from a structural/field-validation failure.
        """
        create_req(_MINIMAL_BODY)
        base_dir = ensure_req_base_dir()
        malformed = f"---\nid: req-1\nstatus: [unterminated\n---\n{_MINIMAL_BODY}"
        (base_dir / "malformed-yaml.md").write_text(malformed, encoding="utf-8")

        sut = list_req()

        self.assertEqual(sut.total, 2)
        self.assertEqual(sut.error_count, 1)
        failed = next(summary for summary in sut.results if summary.ref == "malformed-yaml")
        self.assertIsNone(failed.id)
        self.assertEqual(failed.title, "<failed to parse>")
        self.assertEqual(failed.status, "<failed to parse>")
        self.assertIsNotNone(failed.error)

    def test_empty_result_for_missing_directory(self) -> None:
        self.assertFalse((self.docs_root / "req").exists())

        sut = list_req()

        self.assertEqual(sut.total, 0)
        self.assertEqual(sut.results, [])
        self.assertFalse(sut.truncated)

    def test_default_page_size_and_shape(self) -> None:
        for i in range(3):
            create_req(_body_with_title(f"Title {i}"))

        sut = list_req()

        self.assertEqual(sut.total, 3)
        self.assertEqual(sut.offset, 0)
        self.assertEqual(sut.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(len(sut.results), 3)
        self.assertFalse(sut.truncated)

    def test_max_results_limits_page_and_marks_truncated(self) -> None:
        for i in range(3):
            create_req(_body_with_title(f"Title {i}"))

        sut = list_req(max_results=2)

        self.assertEqual(sut.total, 3)
        self.assertEqual(len(sut.results), 2)
        self.assertTrue(sut.truncated)

    def test_offset_selects_the_next_page(self) -> None:
        for i in range(3):
            create_req(_body_with_title(f"Title {i}"))

        first_page = list_req(max_results=2)
        second_page = list_req(max_results=2, offset=2)

        self.assertEqual(len(second_page.results), 1)
        self.assertFalse(second_page.truncated)
        self.assertNotEqual(first_page.results[0].id, second_page.results[0].id)

    def test_max_results_is_clamped_to_the_cap(self) -> None:
        create_req(_MINIMAL_BODY)

        sut = list_req(max_results=500)

        self.assertEqual(sut.max_results, MAX_MAX_RESULTS)

    def test_negative_offset_is_floored_to_zero(self) -> None:
        create_req(_MINIMAL_BODY)

        sut = list_req(offset=-5)

        self.assertEqual(sut.offset, 0)

    def test_truncated_boundary_false_when_page_covers_all_items(self) -> None:
        for i in range(2):
            create_req(_body_with_title(f"Title {i}"))

        sut = list_req(max_results=2)

        self.assertFalse(sut.truncated)

    def test_truncated_boundary_true_when_one_item_remains(self) -> None:
        for i in range(3):
            create_req(_body_with_title(f"Title {i}"))

        sut = list_req(max_results=2)

        self.assertTrue(sut.truncated)

    def test_total_and_error_count_reflect_the_full_directory_regardless_of_paging(self) -> None:
        for i in range(5):
            create_req(_body_with_title(f"Title {i}"))
        base_dir = ensure_req_base_dir()
        (base_dir / "broken.md").write_text("not a valid requirement, no headings at all", encoding="utf-8")

        sut = list_req(max_results=1, offset=1)

        self.assertEqual(sut.total, 6)
        self.assertEqual(sut.error_count, 1)


if __name__ == "__main__":
    unittest.main()
