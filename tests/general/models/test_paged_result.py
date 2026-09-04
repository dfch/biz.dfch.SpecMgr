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

"""Tests for `general.models.paged_result.PagedResult` (feat-13 Task 1.1/1.4).

feat-81-83-validation Phase 3 (REQ-006) added ``error_count: int = 0``.
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.models.paged_result import PagedResult
from biz.dfch.specmgr.general.models.summary import DocSummary


class TestPagedResult(unittest.TestCase):
    """Tests for PagedResult."""

    def test_holds_fields_in_the_documented_order(self):
        self.assertEqual(
            list(PagedResult.model_fields.keys()),
            ["total", "offset", "max_results", "truncated", "results", "error_count"],
        )

    def test_constructs_with_given_values(self):
        sut = PagedResult(total=10, offset=5, max_results=5, truncated=False, results=[1, 2, 3, 4, 5])

        self.assertEqual(sut.total, 10)
        self.assertEqual(sut.offset, 5)
        self.assertEqual(sut.max_results, 5)
        self.assertFalse(sut.truncated)
        self.assertEqual(sut.results, [1, 2, 3, 4, 5])

    def test_error_count_defaults_to_zero(self):
        sut = PagedResult(total=10, offset=5, max_results=5, truncated=False, results=[1, 2, 3, 4, 5])

        self.assertEqual(sut.error_count, 0)

    def test_error_count_accepts_a_given_value(self):
        sut = PagedResult(total=10, offset=5, max_results=5, truncated=False, results=[], error_count=3)

        self.assertEqual(sut.error_count, 3)

    def test_serializes_to_the_documented_shape(self):
        sut = PagedResult(total=1, offset=0, max_results=25, truncated=False, results=["only"])

        dumped = sut.model_dump()

        self.assertEqual(
            dumped,
            {"total": 1, "offset": 0, "max_results": 25, "truncated": False, "results": ["only"], "error_count": 0},
        )

    def test_accepts_an_empty_results_list(self):
        sut = PagedResult(total=0, offset=0, max_results=25, truncated=False, results=[])

        self.assertEqual(sut.results, [])

    def test_accepts_model_instances_as_results(self):
        items = [DocSummary(id="1", title="t", status="draft", ref="r", path="/tmp/r.md")]

        sut = PagedResult(total=1, offset=0, max_results=25, truncated=False, results=items)

        self.assertEqual(sut.results, items)


if __name__ == "__main__":
    unittest.main()
