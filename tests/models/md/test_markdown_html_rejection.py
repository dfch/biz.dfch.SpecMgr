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

"""Unit tests for REQ-005: raw HTML rejection via `_markdown.parse`."""

import unittest

import mdformat

from biz.dfch.specmgr.models.md import MarkdownStr
from biz.dfch.specmgr.models.md.alias import alias, AliasType
from biz.dfch.specmgr.models.md.markdown_section2 import MarkdownSection2
from biz.dfch.specmgr.models.md._markdown import format_text, parse


@alias(value=".+", type=AliasType.REGEX)
class _AnyHeadingLeafSection(MarkdownSection2): ...


class TestParseRejectsRawHtml(unittest.TestCase):
    """Tests for `_markdown.parse` (the shared, guarded tokenizer)."""

    def test_html_block_raises(self) -> None:
        """A top-level `html_block` token causes `parse` to raise."""
        text = format_text("<div>raw html</div>\n")
        with self.assertRaises(AssertionError):
            parse(text)

    def test_html_inline_raises(self) -> None:
        """An `html_inline` token nested inside a paragraph's `inline` children causes `parse` to raise."""
        text = format_text("Some <b>bold</b> text.\n")
        with self.assertRaises(AssertionError):
            parse(text)

    def test_html_inline_inside_a_heading_raises(self) -> None:
        """An `html_inline` token inside a heading's own `inline` children also causes `parse` to raise."""
        text = format_text("# A <span>span</span> heading\n")
        with self.assertRaises(AssertionError):
            parse(text)

    def test_plain_emphasis_and_strong_are_unaffected(self) -> None:
        """Ordinary Markdown inline formatting (not raw HTML) parses without raising."""
        text = format_text("Some *emphasis* and **strong** text.\n")
        tokens = parse(text)
        self.assertTrue(tokens)

    def test_fenced_code_block_content_looking_like_html_is_unaffected(self) -> None:
        """HTML-looking text inside a fenced code block is opaque code, not raw HTML, and is not rejected."""
        text = format_text("```\n<div>not actually raw html here</div>\n```\n")
        tokens = parse(text)
        self.assertTrue(tokens)

    def test_plain_text_is_unaffected(self) -> None:
        """Plain prose with no HTML at all parses without raising."""
        text = format_text("Just a plain paragraph.\n")
        tokens = parse(text)
        self.assertTrue(tokens)


class TestFromTextRejectsRawHtml(unittest.TestCase):
    """End-to-end coverage of REQ-005 through `MarkdownStr.from_text`/`MarkdownSection.from_text`."""

    def test_markdown_str_from_text_raises_on_html_block(self) -> None:
        """A leaf `MarkdownStr.from_text` call rejects a raw HTML block in its own text."""
        text = mdformat.text("<div>raw html</div>\n")
        with self.assertRaises(AssertionError):
            MarkdownStr.from_text(text)

    def test_markdown_str_from_text_raises_on_html_inline(self) -> None:
        """A leaf `MarkdownStr.from_text` call rejects inline raw HTML in its own text."""
        text = mdformat.text("Some <b>bold</b> text.\n")
        with self.assertRaises(AssertionError):
            MarkdownStr.from_text(text)

    def test_markdown_str_from_text_accepts_plain_formatting(self) -> None:
        """A leaf `MarkdownStr.from_text` call is unaffected by ordinary Markdown formatting."""
        text = mdformat.text("Some *emphasis* and **strong** text.\n")
        instance = MarkdownStr.from_text(text)
        self.assertEqual(instance._value, text)

    def test_markdown_section_from_text_raises_on_html_block_in_body(self) -> None:
        """A leaf `MarkdownSection.from_text` call rejects a raw HTML block in its body."""
        text = mdformat.text("## A Heading\n\n<div>raw html</div>\n")
        with self.assertRaises(AssertionError):
            _AnyHeadingLeafSection.from_text(text)

    def test_markdown_section_from_text_raises_on_html_inline_in_heading(self) -> None:
        """A leaf `MarkdownSection.from_text` call rejects inline raw HTML in its own heading text."""
        text = mdformat.text("## A <span>span</span> heading\n\ncontent\n")
        with self.assertRaises(AssertionError):
            _AnyHeadingLeafSection.from_text(text)

    def test_markdown_section_from_text_accepts_plain_formatting(self) -> None:
        """A leaf `MarkdownSection.from_text` call is unaffected by ordinary Markdown formatting."""
        text = mdformat.text("## *A* Heading\n\nSome **strong** content.\n")
        instance = _AnyHeadingLeafSection.from_text(text)
        self.assertEqual(str(instance), text)


if __name__ == "__main__":
    unittest.main()
