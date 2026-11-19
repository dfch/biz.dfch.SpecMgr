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

"""Statistics tests: Wilson intervals, pass^k and the margin machinery."""

import unittest

from c4_skills import pins, stats


class TestWilsonInterval(unittest.TestCase):
    def test_perfect_k5_is_wide(self) -> None:
        expected_lower = 0.5655
        expected_upper = 1.0

        sut = stats.wilson_interval

        lower, upper = sut(5, 5)

        self.assertAlmostEqual(lower, expected_lower, places=3)
        self.assertAlmostEqual(upper, expected_upper, places=3)

    def test_half_k5(self) -> None:
        expected_lower = 0.1176
        expected_upper = 0.7693

        sut = stats.wilson_interval

        lower, upper = sut(2, 5)

        self.assertAlmostEqual(lower, expected_lower, places=3)
        self.assertAlmostEqual(upper, expected_upper, places=3)

    def test_zero_k5(self) -> None:
        expected_upper = 0.4345

        sut = stats.wilson_interval

        lower, upper = sut(0, 5)

        self.assertAlmostEqual(lower, 0.0, places=3)
        self.assertAlmostEqual(upper, expected_upper, places=3)

    def test_bounds_are_clamped_to_unit_interval(self) -> None:
        sut = stats.wilson_interval

        lower, upper = sut(0, 1)

        self.assertGreaterEqual(lower, 0.0)
        self.assertLessEqual(upper, 1.0)
        self.assertLess(lower, upper)

    def test_invalid_inputs_raise(self) -> None:
        sut = stats.wilson_interval

        with self.assertRaises(ValueError):
            sut(1, 0)
        with self.assertRaises(ValueError):
            sut(6, 5)
        with self.assertRaises(ValueError):
            sut(-1, 5)


class TestPassPowerK(unittest.TestCase):
    def test_rate_one_is_one(self) -> None:
        sut = stats.pass_power_k

        result = sut(1.0, 5)

        self.assertEqual(result, 1.0)

    def test_rate_two_fifths_to_the_fifth(self) -> None:
        expected = (2 / 5) ** 5

        sut = stats.pass_power_k

        result = sut(2 / 5, 5)

        self.assertAlmostEqual(result, expected, places=12)

    def test_invalid_inputs_raise(self) -> None:
        sut = stats.pass_power_k

        with self.assertRaises(ValueError):
            sut(0.5, 0)
        with self.assertRaises(AssertionError):
            sut(1.5, 5)


class TestConditionStats(unittest.TestCase):
    def test_aggregation_over_cases(self) -> None:
        outcomes = {"case-a": [True, True, False, True, True], "case-b": [False, False, False, False, False]}

        sut = stats.stats_for_condition

        result = sut("skill", outcomes)

        self.assertEqual(result.passes, 4)
        self.assertEqual(result.trials, 10)
        self.assertAlmostEqual(result.pass_rate, 0.4)
        self.assertEqual(result.per_case["case-a"], (4, 5))
        self.assertEqual(result.per_case["case-b"], (0, 5))

    def test_empty_outcomes_have_zero_rate_and_no_wilson(self) -> None:
        sut = stats.stats_for_condition

        result = sut("skill", {})

        self.assertEqual(result.pass_rate, 0.0)
        self.assertIsNone(result.wilson())


class TestMarginChecks(unittest.TestCase):
    def _stats(self, condition: str, per_case: dict[str, int]) -> stats.ConditionStats:
        outcomes = {case: [True] * passes + [False] * (5 - passes) for case, passes in per_case.items()}
        return stats.stats_for_condition(condition, outcomes)

    def test_within_margin_and_not_worse_than_none_passes(self) -> None:
        # skill 8/10 = 80%, comparison 9/10 = 90% -> exactly the 10 pp limit
        skill = self._stats(pins.CONDITION_SKILL, {"case-a": 4, "case-b": 4})
        comparison = self._stats(pins.CONDITION_UPSTREAM, {"case-a": 4, "case-b": 5})
        none = self._stats(pins.CONDITION_NONE, {"case-a": 3, "case-b": 4})

        sut = stats.check_margins

        result = sut(skill, comparison, none)

        self.assertTrue(result.ok)
        self.assertAlmostEqual(result.rate_margin_pp, 10.0, places=2)
        self.assertEqual(result.clearly_worse_cases, [])
        self.assertIs(result.better_than_none, True)

    def test_rate_margin_beyond_ten_points_fails(self) -> None:
        # skill 6/10 = 60%, comparison 10/10 = 100% -> 40 pp over the limit
        skill = self._stats(pins.CONDITION_SKILL, {"case-a": 3, "case-b": 3})
        comparison = self._stats(pins.CONDITION_UPSTREAM, {"case-a": 5, "case-b": 5})
        none = self._stats(pins.CONDITION_NONE, {"case-a": 3, "case-b": 3})

        sut = stats.check_margins

        result = sut(skill, comparison, none)

        self.assertFalse(result.ok)
        self.assertAlmostEqual(result.rate_margin_pp, 40.0, places=2)
        self.assertFalse(result.within_rate_margin)

    def test_one_case_clearly_worse_fails(self) -> None:
        skill = self._stats(pins.CONDITION_SKILL, {"case-a": 4, "case-b": 2})
        comparison = self._stats(pins.CONDITION_UPSTREAM, {"case-a": 4, "case-b": 4})
        none = self._stats(pins.CONDITION_NONE, {"case-a": 3, "case-b": 3})

        sut = stats.check_margins

        result = sut(skill, comparison, none)

        self.assertFalse(result.ok)
        self.assertEqual(result.clearly_worse_cases, ["case-b"])

    def test_worse_than_none_fails_acc012(self) -> None:
        skill = self._stats(pins.CONDITION_SKILL, {"case-a": 2})
        comparison = self._stats(pins.CONDITION_UPSTREAM, {"case-a": 2})
        none = self._stats(pins.CONDITION_NONE, {"case-a": 3})

        sut = stats.check_margins

        result = sut(skill, comparison, none)

        self.assertFalse(result.ok)
        self.assertIs(result.better_than_none, False)

    def test_missing_reference_is_not_ok(self) -> None:
        skill = self._stats(pins.CONDITION_SKILL, {"case-a": 4})

        sut = stats.check_margins

        result = sut(skill, None, None)

        self.assertFalse(result.ok)
        self.assertIs(result.better_than_none, None)


if __name__ == "__main__":
    unittest.main()
