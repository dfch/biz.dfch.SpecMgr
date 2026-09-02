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

"""Tests for the ``list_feat`` ``@mcp.tool()`` wrapper (Task 2.3, ACC-003)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.models.v1 import FeatSummary
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, README_FILENAME, ensure_feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.feat.tools.list_feat import list_feat
from biz.dfch.specmgr.general.models import PagedResult
from biz.dfch.specmgr.general.tools._paging import DEFAULT_MAX_RESULTS, MAX_MAX_RESULTS

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Feature: Example Widget

    ## Plan

    ### Overview

    Short description.

    ### Requirements

    - REQ-001: The widget must render within 200ms.

    ### Acceptance Criteria

    - [ ] ACC-001: Render time stays below 200ms.

    ### Scope

    #### Included

    - The widget component itself.

    #### Explicitly Out Of Scope

    - Mobile touch gestures.

    ### Task List

    #### Phase 0: Scaffolding

    - [x] Task 0.1: Create branch and package skeleton

    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z - Paused for review

    Free-form prose describing what happened in this update.
    """
)

_OTHER_BODY = _MINIMAL_BODY.replace("Example Widget", "Nightly Order Export")


def _body_with_title(title: str) -> str:
    return _MINIMAL_BODY.replace("Example Widget", title)


class TestListFeat(unittest.TestCase):
    """Tests for the list_feat tool."""

    def setUp(self) -> None:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_root = tmp / "feat"
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))

    def test_returns_summaries_and_skips_malformed_folder(self) -> None:
        first = create_feat(_MINIMAL_BODY)
        second = create_feat(_OTHER_BODY)

        base_dir = ensure_feat_base_dir()
        broken = base_dir / "feat-99-broken"
        broken.mkdir()
        (broken / README_FILENAME).write_text("not a valid feature, no headings at all", encoding="utf-8")

        sut = list_feat()

        self.assertIsInstance(sut, PagedResult)
        self.assertEqual(sut.total, 2)
        for summary in sut.results:
            self.assertIsInstance(summary, FeatSummary)
        ids = {summary.id for summary in sut.results}
        self.assertEqual(ids, {first.frontmatter.id, second.frontmatter.id})
        titles = {summary.title for summary in sut.results}
        self.assertEqual(titles, {"Example Widget", "Nightly Order Export"})
        statuses = {summary.status for summary in sut.results}
        self.assertEqual(statuses, {"planning"})
        for summary in sut.results:
            self.assertTrue(summary.ref)
            self.assertEqual(summary.ref, summary.id)
            self.assertTrue(summary.path.endswith(f"{summary.id}/{README_FILENAME}"))
            self.assertTrue(Path(summary.path).exists())

    def test_empty_result_for_missing_directory(self) -> None:
        self.assertFalse(self.feat_root.exists())

        sut = list_feat()

        self.assertEqual(sut.total, 0)
        self.assertEqual(sut.results, [])
        self.assertFalse(sut.truncated)

    def test_default_page_size_with_more_than_25_documents(self) -> None:
        for i in range(26):
            create_feat(_body_with_title(f"Widget Number {i:02d}"))

        sut = list_feat()

        self.assertEqual(sut.total, 26)
        self.assertEqual(sut.offset, 0)
        self.assertEqual(sut.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(len(sut.results), 25)
        self.assertTrue(sut.truncated)

    def test_max_results_limits_page_and_marks_truncated(self) -> None:
        for i in range(3):
            create_feat(_body_with_title(f"Widget Number {i:02d}"))

        sut = list_feat(max_results=2)

        self.assertEqual(sut.total, 3)
        self.assertEqual(len(sut.results), 2)
        self.assertTrue(sut.truncated)

    def test_offset_selects_the_next_page(self) -> None:
        for i in range(3):
            create_feat(_body_with_title(f"Widget Number {i:02d}"))

        first_page = list_feat(max_results=2)
        second_page = list_feat(max_results=2, offset=2)

        self.assertEqual(len(second_page.results), 1)
        self.assertFalse(second_page.truncated)
        first_ids = {summary.id for summary in first_page.results}
        second_ids = {summary.id for summary in second_page.results}
        self.assertEqual(len(first_ids | second_ids), 3)
        self.assertEqual(first_ids & second_ids, set())

    def test_max_results_is_clamped_to_the_cap(self) -> None:
        create_feat(_MINIMAL_BODY)

        sut = list_feat(max_results=500)

        self.assertEqual(sut.max_results, MAX_MAX_RESULTS)

    def test_negative_offset_is_floored_to_zero(self) -> None:
        create_feat(_MINIMAL_BODY)

        sut = list_feat(offset=-5)

        self.assertEqual(sut.offset, 0)

    def test_total_reflects_full_parseable_count_regardless_of_paging(self) -> None:
        for i in range(5):
            create_feat(_body_with_title(f"Widget Number {i:02d}"))
        base_dir = ensure_feat_base_dir()
        broken = base_dir / "feat-99-broken"
        broken.mkdir()
        (broken / README_FILENAME).write_text("not a valid feature, no headings at all", encoding="utf-8")

        sut = list_feat(max_results=1, offset=1)

        self.assertEqual(sut.total, 5)


if __name__ == "__main__":
    unittest.main()
