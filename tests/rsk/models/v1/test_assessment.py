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

"""Tests for the `Probability`/`Impact`/`Assessment` 5x5 models.

Malformed headings (out-of-range or missing value digit, misspelled heading
word, wrong H3 order) fail at parse time via the `match_alias` assertion in
`MarkdownSection.from_text` -- i.e. with `AssertionError` (the engine's
structural error channel), not with `pydantic.ValidationError`.
"""

import unittest

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.rsk.models.v1.assessment import (
    LEVEL_HIGH,
    LEVEL_LOW,
    LEVEL_MEDIUM,
    LEVEL_VERY_HIGH,
    Assessment,
    Impact,
    InitialAssessment,
    Probability,
    ResidualAssessment,
    level_from_product,
)

_INITIAL_ASSESSMENT_TEXT = format_text(
    """\
## Initial Assessment

### Probability 4

### Impact 3
"""
)

_RESIDUAL_ASSESSMENT_TEXT = format_text(
    """\
## Residual Assessment

### Probability 2

### Impact 3
"""
)


class TestProbabilityLeaf(unittest.TestCase):
    """A `### Probability {1..5}` leaf parses, exposes its computed `value`, and round-trips."""

    def test_parses_all_five_values(self) -> None:
        for value in range(1, 6):
            with self.subTest(value=value):
                text = format_text(f"### Probability {value}\n")

                sut = Probability.from_text(text)

                self.assertEqual(sut.value, value)
                self.assertEqual(sut.text, f"### Probability {value}\n")
                self.assertEqual(str(sut), text)

    def test_retains_body_text_below_the_heading(self) -> None:
        text = format_text(
            """\
### Probability 4

Almost certain in the current exposure window.
"""
        )

        sut = Probability.from_text(text)

        self.assertEqual(sut.value, 4)
        self.assertEqual(str(sut), text)


class TestProbabilityHeadingRejection(unittest.TestCase):
    """`Probability`'s regex `@alias` rejects out-of-range/missing value digits at parse time."""

    def test_rejects_value_below_range(self) -> None:
        with self.assertRaises(AssertionError):
            Probability.from_text(format_text("### Probability 0\n"))

    def test_rejects_value_above_range(self) -> None:
        with self.assertRaises(AssertionError):
            Probability.from_text(format_text("### Probability 6\n"))

    def test_rejects_two_digit_value(self) -> None:
        with self.assertRaises(AssertionError):
            Probability.from_text(format_text("### Probability 12\n"))

    def test_rejects_missing_value(self) -> None:
        with self.assertRaises(AssertionError):
            Probability.from_text(format_text("### Probability\n"))


class TestImpactLeaf(unittest.TestCase):
    """A `### Impact {1..5}` leaf parses, exposes its computed `value`, and round-trips."""

    def test_parses_all_five_values(self) -> None:
        for value in range(1, 6):
            with self.subTest(value=value):
                text = format_text(f"### Impact {value}\n")

                sut = Impact.from_text(text)

                self.assertEqual(sut.value, value)
                self.assertEqual(sut.text, f"### Impact {value}\n")
                self.assertEqual(str(sut), text)

    def test_rejects_out_of_range_and_missing_value(self) -> None:
        for text in ("### Impact 0\n", "### Impact 6\n", "### Impact 12\n", "### Impact\n"):
            with self.subTest(text=text):
                with self.assertRaises(AssertionError):
                    Impact.from_text(format_text(text))


class TestLevelFromProduct(unittest.TestCase):
    """`level_from_product` maps the probability x impact product to the 5x5 zones.

    Covers all four zone boundaries (4/5, 9/10, 14/15) plus the range ends;
    the same thresholds are documented in the packaged domain-knowledge
    resource `specmgr://rsk/risk-matrix` (a Phase 3 test guards the two
    against drift).
    """

    def test_maps_each_zone(self) -> None:
        cases = (
            (1, LEVEL_LOW),
            (2, LEVEL_LOW),
            (3, LEVEL_LOW),
            (4, LEVEL_LOW),
            (5, LEVEL_MEDIUM),
            (9, LEVEL_MEDIUM),
            (10, LEVEL_HIGH),
            (14, LEVEL_HIGH),
            (15, LEVEL_VERY_HIGH),
            (20, LEVEL_VERY_HIGH),
            (25, LEVEL_VERY_HIGH),
        )
        for product, expected in cases:
            with self.subTest(product=product):
                sut = level_from_product(product)

                self.assertEqual(sut, expected)

    def test_rejects_product_outside_one_to_twenty_five(self) -> None:
        for product in (0, 26):
            with self.subTest(product=product):
                with self.assertRaises(AssertionError):
                    level_from_product(product)


class TestAssessmentParse(unittest.TestCase):
    """An `## Initial/Residual Assessment` section parses its two H3 leaves and derives `level`."""

    def test_parses_initial_assessment_and_derives_level(self) -> None:
        sut = InitialAssessment.from_text(_INITIAL_ASSESSMENT_TEXT)

        self.assertEqual(sut.probability.value, 4)
        self.assertEqual(sut.impact.value, 3)
        self.assertEqual(sut.level, LEVEL_HIGH)
        self.assertEqual(str(sut), _INITIAL_ASSESSMENT_TEXT)

    def test_parses_residual_assessment_and_derives_level(self) -> None:
        sut = ResidualAssessment.from_text(_RESIDUAL_ASSESSMENT_TEXT)

        self.assertEqual(sut.probability.value, 2)
        self.assertEqual(sut.impact.value, 3)
        self.assertEqual(sut.level, LEVEL_MEDIUM)
        self.assertEqual(str(sut), _RESIDUAL_ASSESSMENT_TEXT)

    def test_derives_level_for_every_zone(self) -> None:
        cases = (
            (1, 1, LEVEL_LOW),
            (2, 2, LEVEL_LOW),
            (1, 5, LEVEL_MEDIUM),
            (3, 3, LEVEL_MEDIUM),
            (2, 5, LEVEL_HIGH),
            (3, 4, LEVEL_HIGH),
            (3, 5, LEVEL_VERY_HIGH),
            (5, 5, LEVEL_VERY_HIGH),
        )
        for probability, impact, expected in cases:
            with self.subTest(probability=probability, impact=impact):
                text = format_text(f"## Initial Assessment\n\n### Probability {probability}\n\n### Impact {impact}\n")

                sut = InitialAssessment.from_text(text)

                self.assertEqual(sut.level, expected)

    def test_accepts_direct_construction_from_parsed_leaves(self) -> None:
        text = format_text(
            """\
## Initial Assessment

### Probability 3

### Impact 5
"""
        )
        parsed = Assessment.from_text(text)
        direct = Assessment(probability=parsed.probability, impact=parsed.impact)

        self.assertEqual(direct.level, LEVEL_VERY_HIGH)


class TestAssessmentH3OrderEnforced(unittest.TestCase):
    """`### Probability` must precede `### Impact`; the reverse fails the parse."""

    def test_rejects_impact_before_probability(self) -> None:
        text = format_text(
            """\
## Initial Assessment

### Impact 3

### Probability 4
"""
        )

        with self.assertRaises(AssertionError):
            InitialAssessment.from_text(text)


class TestAssessmentH2HeadingPinned(unittest.TestCase):
    """`InitialAssessment`/`ResidualAssessment` pin their H2 heading (LITERAL `@alias`).

    This is what enforces the initial-before-residual order on `Risk`: a
    document carrying the two sections swapped fails `match_alias` instead
    of being silently parsed with the contents transposed.
    """

    def test_initial_rejects_residual_heading(self) -> None:
        with self.assertRaises(AssertionError):
            InitialAssessment.from_text(_RESIDUAL_ASSESSMENT_TEXT)

    def test_residual_rejects_initial_heading(self) -> None:
        with self.assertRaises(AssertionError):
            ResidualAssessment.from_text(_INITIAL_ASSESSMENT_TEXT)

    def test_base_accepts_either_heading(self) -> None:
        self.assertEqual(Assessment.from_text(_INITIAL_ASSESSMENT_TEXT).level, LEVEL_HIGH)
        self.assertEqual(Assessment.from_text(_RESIDUAL_ASSESSMENT_TEXT).level, LEVEL_MEDIUM)


if __name__ == "__main__":
    unittest.main()
