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

"""Unit tests for `MarkdownSection4`/`5`/`6` through the full recursive engine.

Builds a six-level fixture (`TopLevel` h1 down to `SixthLevel` h6, one nested
field per level) to exercise the entire h1-h6 spectrum end-to-end, matching
the depth already covered for h1-h3 by `various_models.py`/`test_uc_example.py`.
"""

import unittest

import mdformat

from biz.dfch.specmgr.models.md.markdown_section1 import MarkdownSection1
from biz.dfch.specmgr.models.md.markdown_section2 import MarkdownSection2
from biz.dfch.specmgr.models.md.markdown_section3 import MarkdownSection3
from biz.dfch.specmgr.models.md.markdown_section4 import MarkdownSection4
from biz.dfch.specmgr.models.md.markdown_section5 import MarkdownSection5
from biz.dfch.specmgr.models.md.markdown_section6 import MarkdownSection6

# None of these six classes declares an @alias: each class name's
# `AliasType.SPACE_SEPARATED` derivation (e.g. "TopLevel" -> "Top Level")
# already equals its fixture heading text verbatim, which is exactly what
# the no-@alias default now produces (ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae
# v1.4.0) -- an explicit `@alias(type=AliasType.SPACE_SEPARATED)` here would
# only restate that default, so it is omitted.


class SixthLevel(MarkdownSection6): ...


class FifthLevel(MarkdownSection5):
    sixth_level: SixthLevel


class FourthLevel(MarkdownSection4):
    fifth_level: FifthLevel


class ThirdLevel(MarkdownSection3):
    fourth_level: FourthLevel


class SecondLevel(MarkdownSection2):
    third_level: ThirdLevel


class TopLevel(MarkdownSection1):
    second_level: SecondLevel


_TEXT = mdformat.text(
    "# Top Level\n"
    "\n"
    "## Second Level\n"
    "\n"
    "### Third Level\n"
    "\n"
    "#### Fourth Level\n"
    "\n"
    "##### Fifth Level\n"
    "\n"
    "###### Sixth Level\n"
    "\n"
    "Deepest paragraph content.\n"
)


class TestDeepHeadingNesting(unittest.TestCase):
    """`TopLevel.from_text` down through `SixthLevel`, all six heading levels."""

    def test_populates_every_level_down_to_h6(self) -> None:
        instance = TopLevel.from_text(_TEXT)

        self.assertIsInstance(instance.second_level, SecondLevel)
        self.assertIsInstance(instance.second_level.third_level, ThirdLevel)
        self.assertIsInstance(instance.second_level.third_level.fourth_level, FourthLevel)
        self.assertIsInstance(instance.second_level.third_level.fourth_level.fifth_level, FifthLevel)
        self.assertIsInstance(
            instance.second_level.third_level.fourth_level.fifth_level.sixth_level,
            SixthLevel,
        )

    def test_h6_leaf_retains_its_full_extent(self) -> None:
        instance = TopLevel.from_text(_TEXT)
        sixth = instance.second_level.third_level.fourth_level.fifth_level.sixth_level

        self.assertEqual(sixth._value, "###### Sixth Level\n\nDeepest paragraph content.\n")

    def test_round_trip_reproduces_the_source_text(self) -> None:
        instance = TopLevel.from_text(_TEXT)

        self.assertEqual(str(instance), _TEXT)

    def test_get_extent_agrees_across_all_six_levels(self) -> None:
        self.assertEqual(FourthLevel.get_extent(mdformat.text("#### Fourth Level\ncontent\n")), 3)
        self.assertEqual(FifthLevel.get_extent(mdformat.text("##### Fifth Level\ncontent\n")), 3)
        self.assertEqual(SixthLevel.get_extent(mdformat.text("###### Sixth Level\ncontent\n")), 3)


if __name__ == "__main__":
    unittest.main()
