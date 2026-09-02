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

"""Tests for `TaskItem`'s `- [ ]`/`- [x]` checkbox-marker parsing."""

import unittest

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.tsk.models.v1.task_item import TaskItem


class TestTaskItemUnchecked(unittest.TestCase):
    """An unchecked `- [ ] ...` item parses to `checked=False`."""

    def test_parses_unchecked_marker(self) -> None:
        text = format_text("- [ ] Do the thing\n")

        sut = TaskItem.from_text(text)

        self.assertFalse(sut.checked)
        self.assertEqual(sut.description, "Do the thing")


class TestTaskItemChecked(unittest.TestCase):
    """A checked `- [x] ...` item parses to `checked=True`."""

    def test_parses_checked_lowercase_marker(self) -> None:
        text = format_text("- [x] Do the thing\n")

        sut = TaskItem.from_text(text)

        self.assertTrue(sut.checked)
        self.assertEqual(sut.description, "Do the thing")

    def test_parses_checked_uppercase_marker_case_insensitively(self) -> None:
        text = format_text("- [X] Do the thing\n")

        sut = TaskItem.from_text(text)

        self.assertTrue(sut.checked)
        self.assertEqual(sut.description, "Do the thing")


class TestTaskItemMalformed(unittest.TestCase):
    """An item with no checkbox marker at all is a structural failure."""

    def test_missing_marker_raises_on_checked(self) -> None:
        text = format_text("- Do the thing without a marker\n")
        sut = TaskItem.from_text(text)

        with self.assertRaises(AssertionError):
            _ = sut.checked

    def test_missing_marker_raises_on_description(self) -> None:
        text = format_text("- Do the thing without a marker\n")
        sut = TaskItem.from_text(text)

        with self.assertRaises(AssertionError):
            _ = sut.description

    def test_missing_marker_message_names_path_and_line_feat_27(self) -> None:
        """feat-27 Phase 1 (Task 1.7): the message now names this item's own document-
        relative path and 1-based line (`self._path`/`self._line`, threaded in by
        `models.md.MarkdownListItem.from_text`), not just a bare `"TaskItem: ..."` prefix."""
        text = format_text("- ok\n\n- Do the thing without a marker\n")
        _remaining, items = TaskItem.process_list_field("items", TaskItem, text, optional=False)
        assert items is not None, type(items)
        sut = items[1]

        with self.assertRaises(AssertionError) as ctx:
            _ = sut.checked

        self.assertEqual(
            str(ctx.exception),
            "TaskItem (line 3): expected a '- [ ]'/'- [x]' checkbox marker, got 'Do the thing without a marker'",
        )


if __name__ == "__main__":
    unittest.main()
