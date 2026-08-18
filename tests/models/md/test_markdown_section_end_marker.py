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

"""Unit tests for `MarkdownSection.get_extent`'s depth-aware `end_marker` stop
condition (feat-12-qa-artifact Task 1.3).

Uses a small fixture H4 section declaring `@markdown(end_marker=MarkdownBlockQuote)`
(the same mechanism `qa`'s `Requirement` field will use) to verify:

1. A depth-0 block quote following the section's own content stops the scan,
   the same way a sibling/ancestor heading already does.
2. A nested list *and* a nested block quote, both legitimately part of the
   section's own body, do not stop the scan -- only a depth-0 occurrence does.
3. With no end marker at all following, the extent still reaches the end of
   the text (unaffected by the new stop condition).
"""

import unittest

import mdformat

from biz.dfch.specmgr.models.md.alias import alias, AliasType
from biz.dfch.specmgr.models.md.markdown import markdown
from biz.dfch.specmgr.models.md.markdown_block_quote import MarkdownBlockQuote
from biz.dfch.specmgr.models.md.markdown_section4 import MarkdownSection4


@markdown(end_marker=MarkdownBlockQuote)
@alias(value=".+", type=AliasType.REGEX)
class _RequirementLikeSection(MarkdownSection4):
    """A leaf H4 section standing in for `qa`'s own `Requirement` class."""


class TestGetExtentStopsAtDepthZeroEndMarker(unittest.TestCase):
    """A depth-0 block quote following the section stops `get_extent`."""

    def test_declared_end_marker_is_recorded_in_metadata(self) -> None:
        self.assertIs(_RequirementLikeSection._metadata.get("end_marker"), MarkdownBlockQuote)
        self.assertEqual(_RequirementLikeSection._metadata.get("type"), "heading_open")
        self.assertEqual(_RequirementLikeSection._metadata.get("tag"), "h4")

    def test_extent_stops_before_the_first_depth_zero_block_quote(self) -> None:
        text = mdformat.text(
            "#### Some Requirement\n"
            "\n"
            "Some intro paragraph.\n"
            "\n"
            "> Actual next block quote (end marker)\n"
            "\n"
            "more after end marker\n"
        )
        lines = text.splitlines()
        stop_line = next(i for i, line in enumerate(lines) if line.startswith("> Actual"))

        result = _RequirementLikeSection.get_extent(text)

        self.assertEqual(result, stop_line)

    def test_from_text_does_not_absorb_the_end_marker_block_quote(self) -> None:
        text = mdformat.text(
            "#### Some Requirement\n"
            "\n"
            "Some intro paragraph.\n"
            "\n"
            "> Actual next block quote (end marker)\n"
            "\n"
            "more after end marker\n"
        )

        extent = _RequirementLikeSection.get_extent(text)
        own_text = mdformat.text("\n".join(text.splitlines()[:extent]))
        instance = _RequirementLikeSection.from_text(own_text)

        self.assertNotIn("Actual next block quote", str(instance))

    def test_extent_reaches_end_of_text_when_no_end_marker_follows(self) -> None:
        text = mdformat.text(
            "#### Some Requirement\n\nSome intro paragraph.\n\nSome more prose, no block quote anywhere.\n"
        )

        result = _RequirementLikeSection.get_extent(text)

        self.assertEqual(result, len(text.splitlines()))


class TestGetExtentIgnoresNestedEndMarkerOccurrences(unittest.TestCase):
    """A nested list *and* a nested block quote, both inside the section's own
    valid content, must not truncate the extent early (feat-12-qa-artifact
    Task 1.3's specific "not just one or the other" edge case)."""

    def test_nested_list_and_nested_block_quote_do_not_truncate(self) -> None:
        text = mdformat.text(
            "#### Some Requirement\n"
            "\n"
            "Some intro paragraph.\n"
            "\n"
            "- item one\n"
            "\n"
            "  > nested quote inside a list item\n"
            "\n"
            "- item two\n"
            "\n"
            "Some trailing text.\n"
            "\n"
            "> Actual next block quote (end marker)\n"
            "\n"
            "more after end marker\n"
        )
        lines = text.splitlines()
        stop_line = next(i for i, line in enumerate(lines) if line.startswith("> Actual"))

        result = _RequirementLikeSection.get_extent(text)

        self.assertEqual(result, stop_line)
        # The nested list and nested block quote are both still inside the
        # reported extent, not truncated away.
        consumed = "\n".join(lines[:result])
        self.assertIn("item one", consumed)
        self.assertIn("item two", consumed)
        self.assertIn("nested quote inside a list item", consumed)

    def test_from_text_retains_the_nested_list_and_quote_but_not_the_end_marker(self) -> None:
        full_text = mdformat.text(
            "#### Some Requirement\n"
            "\n"
            "Some intro paragraph.\n"
            "\n"
            "- item one\n"
            "\n"
            "  > nested quote inside a list item\n"
            "\n"
            "- item two\n"
            "\n"
            "Some trailing text.\n"
            "\n"
            "> Actual next block quote (end marker)\n"
            "\n"
            "more after end marker\n"
        )
        extent = _RequirementLikeSection.get_extent(full_text)
        own_text = mdformat.text("\n".join(full_text.splitlines()[:extent]))

        instance = _RequirementLikeSection.from_text(own_text)
        rendered = str(instance)

        self.assertIn("item one", rendered)
        self.assertIn("item two", rendered)
        self.assertIn("nested quote inside a list item", rendered)
        self.assertNotIn("Actual next block quote", rendered)


if __name__ == "__main__":
    unittest.main()
