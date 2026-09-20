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

"""Unit tests for the pure-Python cosine ranking (feat-134, Phase 2, Task 2.4).

Covers ACC-012 (the ranking half: the renormalized-mean pool is what makes
``dot_product`` == cosine) and ACC-015 (``top_k``/``min_score`` bounds rejected
with ``ValueError`` before any scoring). No file I/O, no provider, no ``numpy``
-- the vectors are hand-chosen so every expected score is hand-computable.
"""

from __future__ import annotations

import math
import unittest

from biz.dfch.specmgr.general.tools._similarity_ranking import (
    MAX_TOP_K,
    MIN_TOP_K,
    dot_product,
    rank_candidates,
    validate_ranking_bounds,
)


class TestDotProduct(unittest.TestCase):
    """ACC-012: the dot product on L2-normalized inputs is the cosine."""

    def test_normalized_inputs_give_cosine(self) -> None:
        a = [1.0, 0.0]
        b = [1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0)]

        result = dot_product(a, b)

        self.assertAlmostEqual(result, 1.0 / math.sqrt(2.0), places=9)

    def test_orthogonal_inputs_give_zero(self) -> None:
        result = dot_product([1.0, 0.0], [0.0, 1.0])

        self.assertAlmostEqual(result, 0.0, places=9)

    def test_opposite_inputs_give_minus_one(self) -> None:
        result = dot_product([1.0, 0.0], [-1.0, 0.0])

        self.assertAlmostEqual(result, -1.0, places=9)

    def test_accepts_tuple_vectors(self) -> None:
        result = dot_product((1.0, 2.0), (1.0, 2.0))

        self.assertAlmostEqual(result, 5.0, places=9)

    def test_dimension_mismatch_raises_assertion(self) -> None:
        with self.assertRaises(AssertionError):
            dot_product([1.0, 0.0], [1.0, 0.0, 0.0])

    def test_string_input_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            dot_product("ab", [1.0, 2.0])


class TestValidateRankingBounds(unittest.TestCase):
    """ACC-015: ``top_k``/``min_score`` out of bounds are a ``ValueError``."""

    def test_top_k_bounds_are_inclusive(self) -> None:
        validate_ranking_bounds(MIN_TOP_K, None)
        validate_ranking_bounds(10, None)
        validate_ranking_bounds(MAX_TOP_K, None)

    def test_top_k_zero_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_ranking_bounds(0, None)

    def test_top_k_above_max_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_ranking_bounds(MAX_TOP_K + 1, None)

    def test_top_k_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_ranking_bounds(-1, None)

    def test_min_score_bounds_are_inclusive(self) -> None:
        validate_ranking_bounds(10, -1.0)
        validate_ranking_bounds(10, 0.0)
        validate_ranking_bounds(10, 1.0)

    def test_min_score_none_is_valid(self) -> None:
        validate_ranking_bounds(10, None)

    def test_min_score_below_negative_one_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_ranking_bounds(10, -1.0001)

    def test_min_score_above_one_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_ranking_bounds(10, 1.0001)


class TestRankCandidates(unittest.TestCase):
    """ACC-012/ACC-015: descending cosine ranking with ``top_k``/``min_score`` and stable ties."""

    def test_sorted_descending_with_top_k(self) -> None:
        query = [1.0, 0.0, 0.0]
        candidates = [
            ("a", [0.0, 1.0, 0.0]),  # 0.0
            ("b", [1.0, 0.0, 0.0]),  # 1.0
            ("c", [0.6, 0.8, 0.0]),  # 0.6
            ("d", [0.0, 0.0, 1.0]),  # 0.0
        ]

        result = rank_candidates(query, candidates, top_k=2)

        self.assertEqual([key for key, _ in result], ["b", "c"])
        self.assertAlmostEqual(result[0][1], 1.0, places=9)
        self.assertAlmostEqual(result[1][1], 0.6, places=9)

    def test_min_score_is_inclusive(self) -> None:
        query = [1.0, 0.0, 0.0]
        candidates = [
            ("a", [0.0, 1.0, 0.0]),  # 0.0
            ("b", [1.0, 0.0, 0.0]),  # 1.0
            ("c", [0.6, 0.8, 0.0]),  # 0.6
        ]

        kept = rank_candidates(query, candidates, top_k=10, min_score=0.6)

        self.assertEqual([key for key, _ in kept], ["b", "c"])  # c is exactly at the threshold and kept
        dropped = rank_candidates(query, candidates, top_k=10, min_score=0.61)
        self.assertEqual([key for key, _ in dropped], ["b"])

    def test_equal_scores_keep_input_order(self) -> None:
        query = [1.0, 0.0, 0.0]
        candidates = [
            ("a", [0.0, 1.0, 0.0]),  # 0.0
            ("b", [0.0, 0.0, 1.0]),  # 0.0
            ("c", [1.0, 0.0, 0.0]),  # 1.0
        ]

        result = rank_candidates(query, candidates, top_k=10)

        self.assertEqual([key for key, _ in result], ["c", "a", "b"])  # a before b: stable tie-break

    def test_min_score_none_returns_up_to_top_k_regardless_of_score(self) -> None:
        query = [1.0, 0.0, 0.0]
        candidates = [
            ("a", [0.0, 1.0, 0.0]),  # 0.0
            ("b", [-1.0, 0.0, 0.0]),  # -1.0
        ]

        result = rank_candidates(query, candidates, top_k=10)

        self.assertEqual([key for key, _ in result], ["a", "b"])  # even the negative score is returned

    def test_bad_top_k_rejected_before_scoring(self) -> None:
        query = [1.0, 0.0]
        candidates = [("a", [1.0, 0.0])]

        for bad_top_k in (0, MAX_TOP_K + 1, -5):
            with self.subTest(top_k=bad_top_k):
                with self.assertRaises(ValueError):
                    rank_candidates(query, candidates, top_k=bad_top_k)

    def test_bad_min_score_rejected_before_scoring(self) -> None:
        query = [1.0, 0.0]
        candidates = [("a", [1.0, 0.0])]

        for bad_min_score in (-1.5, 1.5):
            with self.subTest(min_score=bad_min_score):
                with self.assertRaises(ValueError):
                    rank_candidates(query, candidates, top_k=10, min_score=bad_min_score)


if __name__ == "__main__":
    unittest.main()
