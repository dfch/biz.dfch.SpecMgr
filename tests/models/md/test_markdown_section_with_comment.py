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

"""Unit tests for `MarkdownSection{1..6}WithComment`, across all six heading levels.

Mirrors `test_markdown_section_levels.py`'s "one combined file for all six
levels" structure, and `test_markdown_comment.py::_InvalidCommentWithField`'s
"fixture subclass to prove a guard" pattern.
"""

import unittest

import mdformat

from biz.dfch.specmgr.models.md import (
    MarkdownParagraph,
    MarkdownSection1WithComment,
    MarkdownSection2WithComment,
    MarkdownSection3WithComment,
    MarkdownSection4WithComment,
    MarkdownSection5WithComment,
    MarkdownSection6WithComment,
)


class OkLevel1(MarkdownSection1WithComment):
    """Well-formed: `comment` paired with a `value` field that absorbs the body."""

    value: MarkdownParagraph


class OkLevel2(MarkdownSection2WithComment):
    value: MarkdownParagraph


class OkLevel3(MarkdownSection3WithComment):
    value: MarkdownParagraph


class OkLevel4(MarkdownSection4WithComment):
    value: MarkdownParagraph


class OkLevel5(MarkdownSection5WithComment):
    value: MarkdownParagraph


class OkLevel6(MarkdownSection6WithComment):
    value: MarkdownParagraph


class BadLevel1(MarkdownSection1WithComment):
    """Malformed: declares no field besides the inherited `comment` -- must raise."""


class BadLevel2(MarkdownSection2WithComment): ...


class BadLevel3(MarkdownSection3WithComment): ...


class BadLevel4(MarkdownSection4WithComment): ...


class BadLevel5(MarkdownSection5WithComment): ...


class BadLevel6(MarkdownSection6WithComment): ...


_OK_CLASSES = {
    1: OkLevel1,
    2: OkLevel2,
    3: OkLevel3,
    4: OkLevel4,
    5: OkLevel5,
    6: OkLevel6,
}

_BAD_CLASSES = {
    1: BadLevel1,
    2: BadLevel2,
    3: BadLevel3,
    4: BadLevel4,
    5: BadLevel5,
    6: BadLevel6,
}


def _heading(level: int, title: str) -> str:
    return f"{'#' * level} {title}"


class TestMarkdownSectionWithCommentWellFormed(unittest.TestCase):
    """A well-formed `...WithComment` subclass (comment + one content field)."""

    def test_parses_without_a_leading_comment(self) -> None:
        for level, cls in _OK_CLASSES.items():
            with self.subTest(level=level):
                text = mdformat.text(f"{_heading(level, 'Ok Level ' + str(level))}\n\nBody text.\n")
                instance = cls.from_text(text)
                self.assertIsNone(instance.comment)
                self.assertEqual(instance.value.text, "Body text.")
                self.assertEqual(str(instance), text)

    def test_parses_with_a_leading_comment(self) -> None:
        for level, cls in _OK_CLASSES.items():
            with self.subTest(level=level):
                text = mdformat.text(f"{_heading(level, 'Ok Level ' + str(level))}\n\n<!-- a note -->\n\nBody text.\n")
                instance = cls.from_text(text)
                self.assertIsNotNone(instance.comment)
                self.assertEqual(instance.comment.text, "<!-- a note -->\n")
                self.assertEqual(instance.value.text, "Body text.")
                self.assertEqual(str(instance), text)


class TestMarkdownSectionWithCommentGuard(unittest.TestCase):
    """A malformed `...WithComment` subclass declaring no other field must raise."""

    def test_get_extent_rejects_a_comment_only_subclass(self) -> None:
        for level, cls in _BAD_CLASSES.items():
            with self.subTest(level=level):
                text = mdformat.text(f"{_heading(level, 'Bad Level ' + str(level))}\n\nBody text.\n")
                with self.assertRaises(AssertionError):
                    cls.get_extent(text)

    def test_from_text_rejects_a_comment_only_subclass(self) -> None:
        for level, cls in _BAD_CLASSES.items():
            with self.subTest(level=level):
                text = mdformat.text(f"{_heading(level, 'Bad Level ' + str(level))}\n\nBody text.\n")
                with self.assertRaises(AssertionError):
                    cls.from_text(text)


if __name__ == "__main__":
    unittest.main()
