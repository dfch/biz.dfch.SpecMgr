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

"""Tests for `general.tools._paging` (feat-13 Task 1.2/1.4)."""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.tools._paging import (
    DEFAULT_MAX_RESULTS,
    MAX_MAX_RESULTS,
    MIN_MAX_RESULTS,
    MIN_OFFSET,
    normalize_paging,
    paginate,
)


class TestNormalizePaging(unittest.TestCase):
    """Tests for normalize_paging."""

    def test_defaults_max_results_when_not_given(self):
        offset, max_results = normalize_paging(None, 0)

        self.assertEqual(max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(offset, 0)

    def test_defaults_offset_when_not_given(self):
        offset, max_results = normalize_paging(25, None)

        self.assertEqual(offset, MIN_OFFSET)
        self.assertEqual(max_results, 25)

    def test_defaults_both_when_neither_given(self):
        offset, max_results = normalize_paging(None, None)

        self.assertEqual(offset, MIN_OFFSET)
        self.assertEqual(max_results, DEFAULT_MAX_RESULTS)

    def test_clamps_max_results_above_the_cap(self):
        _, max_results = normalize_paging(500, 0)

        self.assertEqual(max_results, MAX_MAX_RESULTS)

    def test_clamps_max_results_below_the_minimum(self):
        _, max_results = normalize_paging(0, 0)

        self.assertEqual(max_results, MIN_MAX_RESULTS)

    def test_clamps_negative_max_results_to_the_minimum(self):
        _, max_results = normalize_paging(-10, 0)

        self.assertEqual(max_results, MIN_MAX_RESULTS)

    def test_passes_through_an_in_range_max_results(self):
        _, max_results = normalize_paging(50, 0)

        self.assertEqual(max_results, 50)

    def test_floors_a_negative_offset_to_zero(self):
        offset, _ = normalize_paging(25, -5)

        self.assertEqual(offset, MIN_OFFSET)

    def test_passes_through_a_non_negative_offset(self):
        offset, _ = normalize_paging(25, 40)

        self.assertEqual(offset, 40)

    def test_returns_offset_before_max_results(self):
        result = normalize_paging(25, 10)

        self.assertEqual(result, (10, 25))


class TestPaginate(unittest.TestCase):
    """Tests for paginate."""

    def test_empty_items_yields_empty_page(self):
        sut = paginate([], 0, 25)

        self.assertEqual(sut.total, 0)
        self.assertEqual(sut.results, [])
        self.assertFalse(sut.truncated)

    def test_exact_fit_is_not_truncated(self):
        items = list(range(25))

        sut = paginate(items, 0, 25)

        self.assertEqual(sut.total, 25)
        self.assertEqual(sut.results, items)
        self.assertFalse(sut.truncated)

    def test_partial_page_is_truncated(self):
        items = list(range(30))

        sut = paginate(items, 0, 25)

        self.assertEqual(sut.total, 30)
        self.assertEqual(sut.results, items[:25])
        self.assertTrue(sut.truncated)

    def test_offset_past_the_end_yields_empty_results_and_is_not_truncated(self):
        items = list(range(10))

        sut = paginate(items, 100, 25)

        self.assertEqual(sut.total, 10)
        self.assertEqual(sut.results, [])
        self.assertFalse(sut.truncated)

    def test_offset_at_exact_end_yields_empty_results_and_is_not_truncated(self):
        items = list(range(10))

        sut = paginate(items, 10, 25)

        self.assertEqual(sut.results, [])
        self.assertFalse(sut.truncated)

    def test_truncated_boundary_is_false_when_page_end_equals_total(self):
        items = list(range(20))

        sut = paginate(items, 0, 20)

        self.assertFalse(sut.truncated)

    def test_truncated_boundary_is_true_when_page_end_is_one_less_than_total(self):
        items = list(range(21))

        sut = paginate(items, 0, 20)

        self.assertTrue(sut.truncated)

    def test_second_page_reflects_offset(self):
        items = list(range(60))

        sut = paginate(items, 25, 25)

        self.assertEqual(sut.offset, 25)
        self.assertEqual(sut.results, items[25:50])
        self.assertTrue(sut.truncated)

    def test_echoes_back_the_applied_offset_and_max_results(self):
        sut = paginate(list(range(5)), 2, 10)

        self.assertEqual(sut.offset, 2)
        self.assertEqual(sut.max_results, 10)

    def test_total_reflects_full_item_count_not_page_size(self):
        items = list(range(1000))

        sut = paginate(items, 0, 25)

        self.assertEqual(sut.total, 1000)

    def test_error_count_defaults_to_zero(self):
        sut = paginate(list(range(5)), 0, 25)

        self.assertEqual(sut.error_count, 0)

    def test_error_count_is_passed_through_unchanged(self):
        sut = paginate(list(range(5)), 0, 25, error_count=3)

        self.assertEqual(sut.error_count, 3)

    def test_error_count_is_independent_of_paging(self):
        sut = paginate(list(range(100)), 50, 10, error_count=7)

        self.assertEqual(sut.error_count, 7)
        self.assertEqual(len(sut.results), 10)


class TestNormalizePagingThenPaginate(unittest.TestCase):
    """Integration-style tests combining normalize_paging and paginate."""

    def test_splat_unpacking_matches_paginate_argument_order(self):
        items = list(range(100))

        sut = paginate(items, *normalize_paging(None, None))

        self.assertEqual(sut.offset, 0)
        self.assertEqual(sut.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(len(sut.results), DEFAULT_MAX_RESULTS)
        self.assertTrue(sut.truncated)

    def test_out_of_range_inputs_are_clamped_not_errored(self):
        items = list(range(5))

        sut = paginate(items, *normalize_paging(9999, -50))

        self.assertEqual(sut.offset, 0)
        self.assertEqual(sut.max_results, MAX_MAX_RESULTS)
        self.assertEqual(sut.results, items)
        self.assertFalse(sut.truncated)


if __name__ == "__main__":
    unittest.main()
