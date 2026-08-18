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

"""Unit tests for the `@markdown` decorator: merge-into-inherited-`_metadata`
semantics (feat-12-qa-artifact Task 1.1) and the `end_marker` parameter
(Task 1.2).

The first test class is a regression check against all 11 existing
`@markdown(...)` call sites in `models/md/` -- every one of them must still
carry exactly the same `type`/`tag` values it did before this change, with
no unexpected `end_marker` key leaking in.
"""

import unittest

from biz.dfch.specmgr.models.md.markdown import markdown
from biz.dfch.specmgr.models.md.markdown_str import MarkdownStr
from biz.dfch.specmgr.models.md.markdown_block_quote import MarkdownBlockQuote
from biz.dfch.specmgr.models.md.markdown_code_block import MarkdownCodeBlock
from biz.dfch.specmgr.models.md.markdown_comment import MarkdownComment
from biz.dfch.specmgr.models.md.markdown_paragraph import MarkdownParagraph
from biz.dfch.specmgr.models.md.markdown_section import MarkdownSection
from biz.dfch.specmgr.models.md.markdown_section1 import MarkdownSection1
from biz.dfch.specmgr.models.md.markdown_section2 import MarkdownSection2
from biz.dfch.specmgr.models.md.markdown_section3 import MarkdownSection3
from biz.dfch.specmgr.models.md.markdown_section4 import MarkdownSection4
from biz.dfch.specmgr.models.md.markdown_section5 import MarkdownSection5
from biz.dfch.specmgr.models.md.markdown_section6 import MarkdownSection6


class TestMarkdownDecoratorBackwardCompatibility(unittest.TestCase):
    """Every one of the 11 existing `@markdown(...)` call sites is unaffected."""

    def test_markdown_section_metadata_unchanged(self) -> None:
        self.assertEqual(MarkdownSection._metadata.get("type"), "heading_open")
        self.assertIsNone(MarkdownSection._metadata.get("tag"))
        self.assertIsNone(MarkdownSection._metadata.get("end_marker"))

    def test_markdown_section_levels_metadata_unchanged(self) -> None:
        expectations = (
            (MarkdownSection1, "h1"),
            (MarkdownSection2, "h2"),
            (MarkdownSection3, "h3"),
            (MarkdownSection4, "h4"),
            (MarkdownSection5, "h5"),
            (MarkdownSection6, "h6"),
        )
        for cls, tag in expectations:
            with self.subTest(cls=cls.__name__):
                self.assertEqual(cls._metadata.get("type"), "heading_open")
                self.assertEqual(cls._metadata.get("tag"), tag)
                self.assertIsNone(cls._metadata.get("end_marker"))

    def test_markdown_block_quote_metadata_unchanged(self) -> None:
        self.assertEqual(MarkdownBlockQuote._metadata.get("type"), "blockquote_open")
        self.assertEqual(MarkdownBlockQuote._metadata.get("tag"), "blockquote")
        self.assertIsNone(MarkdownBlockQuote._metadata.get("end_marker"))

    def test_markdown_code_block_metadata_unchanged(self) -> None:
        self.assertEqual(MarkdownCodeBlock._metadata.get("type"), "fence")
        self.assertEqual(MarkdownCodeBlock._metadata.get("tag"), "code")
        self.assertIsNone(MarkdownCodeBlock._metadata.get("end_marker"))

    def test_markdown_comment_metadata_unchanged(self) -> None:
        self.assertEqual(MarkdownComment._metadata.get("type"), "html_block")
        self.assertEqual(MarkdownComment._metadata.get("tag"), "")
        self.assertIsNone(MarkdownComment._metadata.get("end_marker"))

    def test_markdown_paragraph_metadata_unchanged(self) -> None:
        self.assertEqual(MarkdownParagraph._metadata.get("type"), "paragraph_open")
        self.assertEqual(MarkdownParagraph._metadata.get("tag"), "p")
        self.assertIsNone(MarkdownParagraph._metadata.get("end_marker"))

    def test_with_comment_variants_inherit_rather_than_redeclare(self) -> None:
        """`*WithComment` classes never re-apply `@markdown`, so their `_metadata`
        is exactly their base class's `_metadata` object -- unaffected by this
        change, mirroring Task 1.1's "do not change that" instruction."""
        from biz.dfch.specmgr.models.md.markdown_section1_with_comment import (
            MarkdownSection1WithComment,
        )

        self.assertEqual(MarkdownSection1WithComment._metadata, MarkdownSection1._metadata)


class TestMarkdownDecoratorMergeSemantics(unittest.TestCase):
    """New behavior: `@markdown(...)` merges into inherited `_metadata`."""

    def test_reapplying_with_no_arguments_keeps_every_inherited_key(self) -> None:
        @markdown(type="heading_open", tag="h4")
        class _Base(MarkdownStr): ...

        @markdown()
        class _Sub(_Base): ...

        self.assertEqual(_Sub._metadata, {"type": "heading_open", "tag": "h4"})

    def test_reapplying_with_one_argument_only_overrides_that_key(self) -> None:
        @markdown(type="heading_open", tag="h4")
        class _Base(MarkdownStr): ...

        @markdown(tag="h5")
        class _Sub(_Base): ...

        self.assertEqual(_Sub._metadata, {"type": "heading_open", "tag": "h5"})

    def test_explicitly_passing_none_clears_an_inherited_value(self) -> None:
        @markdown(type="heading_open", tag="h4")
        class _Base(MarkdownStr): ...

        @markdown(tag=None)
        class _Sub(_Base): ...

        self.assertEqual(_Sub._metadata, {"type": "heading_open", "tag": None})

    def test_end_marker_is_merged_the_same_way(self) -> None:
        @markdown(type="heading_open", tag="h4", end_marker=MarkdownBlockQuote)
        class _Base(MarkdownStr): ...

        @markdown(tag="h5")
        class _Sub(_Base): ...

        self.assertIs(_Sub._metadata.get("end_marker"), MarkdownBlockQuote)
        self.assertEqual(_Sub._metadata.get("tag"), "h5")

    def test_end_marker_defaults_to_absent_when_never_declared(self) -> None:
        @markdown(type="heading_open", tag="h4")
        class _Base(MarkdownStr): ...

        self.assertIsNone(_Base._metadata.get("end_marker"))


if __name__ == "__main__":
    unittest.main()
