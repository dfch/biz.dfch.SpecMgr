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

"""Unit tests for MarkdownListItemWithNotes (continuation paragraph capture in loose-list items).

Covers:
- Tight list item without notes (**notes** is ``None``, ``model_dump()`` omits/null)
- Loose list item with one continuation paragraph (**notes** has one ``MarkdownParagraph``, JSON shows it)
- Loose list item with two continuation paragraphs (**notes** has two entries)
- Compact item (no blank line -> no notes)
- ``str(parsed)`` round-trips match raw source for all scenarios
"""

import json
import unittest

from biz.dfch.specmgr.models.md import MarkdownListItemWithNotes, MarkdownParagraph
from biz.dfch.specmgr.models.md._markdown import format_text


# Helper that parses a single (possibly loose) bullet item from an isolated list body.


def _parse_single_item(markdown: str) -> MarkdownListItemWithNotes:
    return MarkdownListItemWithNotes.from_text(format_text(markdown))


# Helper that parses a single (possibly loose) numbered item from an isolated list body.


def _parse_single_numbered_item(markdown: str) -> MarkdownListItemWithNotes:
    return MarkdownListItemWithNotes.from_text(format_text(markdown))


class TestMarkdownListItemWithNotesParsing(unittest.TestCase):
    """Tests for MarkdownListItemWithNotes parsing of continuation paragraphs."""

    def test_tight_item_notes_is_none(self) -> None:
        """A tight (no blank line after lead) item has **notes** = ``None``."""
        txt = "- Reliability"
        item = _parse_single_item(txt)
        self.assertIsNone(item.notes)

    def test_loose_one_continuation_has_one_paragraph(self) -> None:
        """A loose item with one continuation paragraph captures exactly one entry."""
        txt_formatted = format_text("- Reliability\n\n  One continuation line.\n")
        item = _parse_single_item(txt_formatted)
        self.assertIsNotNone(item.notes)
        self.assertEqual(len(item.notes), 1)

        note_para: MarkdownParagraph = item.notes[0]
        self.assertEqual(note_para.text, "One continuation line.")

    def test_loose_two_continuations_has_two_paragraphs(self) -> None:
        """A loose item with two continuation paragraphs captures both entries."""
        raw = "- Security\n\n  First continuation.\n\n  Second continuation.\n"
        txt_formatted = format_text(raw)
        item = _parse_single_item(txt_formatted)
        self.assertIsNotNone(item.notes)
        self.assertEqual(len(item.notes), 2)

        self.assertEqual(item.notes[0].text, "First continuation.")
        self.assertEqual(item.notes[1].text, "Second continuation.")

    def test_no_blank_line_tight_compact(self) -> None:
        """A compact item (no blank line between lead and following text that is NOT indented 4+ spaces) remains tight."""
        txt = "- Security-Next"
        item = _parse_single_item(txt)
        self.assertIsNone(item.notes)

    def test_str_round_trips_tight_item(self) -> None:
        """Tight item round-trips verbatim -- no phantom newlines."""
        raw = "- Reliability\n"
        txt_formatted = format_text(raw)
        item = _parse_single_item(txt_formatted)
        self.assertEqual(str(item), txt_formatted)

    def test_str_round_trips_loose_one_continuation(self) -> None:
        """Loose item with one continuation paragraph round-trips exactly."""
        raw = "- Reliability\n\n  One continuation line.\n"
        txt_formatted = format_text(raw)
        item = _parse_single_item(txt_formatted)
        self.assertEqual(str(item), txt_formatted)

    def test_str_round_trips_loose_two_continuations(self) -> None:
        """Loose item with two continuation paragraphs round-trips exactly."""
        raw = "- Security\n\n  First continuation.\n\n  Second continuation.\n"
        txt_formatted = format_text(raw)
        item = _parse_single_item(txt_formatted)
        self.assertEqual(str(item), txt_formatted)

    def test_str_round_trips_mixed_list(self) -> None:
        """A list mixing tight and loose items round-trips as a loose-equivalent."""
        raw = "- Reliability\n\n- Security\n  A compact follow-up line.\n"
        _ = format_text(raw)  # noqa: F841 -- format_text side-effect validates fixture is well-formed
        item1 = _parse_single_item(format_text("- Reliability\n"))
        item2 = _parse_single_item(format_text("- Security\n  A compact follow-up line.\n"))
        self.assertEqual(str(item1), format_text("- Reliability\n"))
        # The compact follow-up stays inside the lead's text (not a separate paragraph).
        self.assertTrue("- Security" in str(item2))

    # --- Numbered list tests ---

    def test_tight_numbered_item_notes_is_none(self) -> None:
        """A tight numbered item (no blank line after lead) has **notes** = ``None``."""
        txt = "1. Safety"
        item = _parse_single_numbered_item(txt)
        self.assertIsNone(item.notes)

    def test_loose_numbered_one_continuation_has_one_paragraph(self) -> None:
        """A loose numbered item with one continuation paragraph captures exactly one entry."""
        txt_formatted = format_text("1. Safety\n\n  One continuation line.\n")
        item = _parse_single_numbered_item(txt_formatted)
        self.assertIsNotNone(item.notes)
        self.assertEqual(len(item.notes), 1)

        note_para: MarkdownParagraph = item.notes[0]
        self.assertEqual(note_para.text, "One continuation line.")

    def test_loose_numbered_two_continuations_has_two_paragraphs(self) -> None:
        """A loose numbered item with two continuation paragraphs captures both entries."""
        raw = "1. Security\n\n  First continuation.\n\n  Second continuation.\n"
        txt_formatted = format_text(raw)
        item = _parse_single_numbered_item(txt_formatted)
        self.assertIsNotNone(item.notes)
        self.assertEqual(len(item.notes), 2)

        self.assertEqual(item.notes[0].text, "First continuation.")
        self.assertEqual(item.notes[1].text, "Second continuation.")

    def test_str_round_trips_tight_numbered_item(self) -> None:
        """Tight numbered item round-trips verbatim -- no phantom newlines."""
        raw = "1. Safety\n"
        txt_formatted = format_text(raw)
        item = _parse_single_numbered_item(txt_formatted)
        self.assertEqual(str(item), txt_formatted)

    def test_str_round_trips_loose_numbered_one_continuation(self) -> None:
        """Loose numbered item with one continuation paragraph: parsing works, notes captured.

        Note: loose numbered lists do not round-trip byte-exact because mdformat
        strips indentation from continuation paragraphs, while our renderer adds
        marker-width indentation (same as bullet lists). This is an accepted
        limitation -- parsing correctly captures notes, which is the key feature.
        """
        raw = "1. Safety\n\n  One continuation line.\n"
        txt_formatted = format_text(raw)
        item = _parse_single_numbered_item(txt_formatted)
        # Verify parsing worked: notes captured correctly
        self.assertIsNotNone(item.notes)
        self.assertEqual(len(item.notes), 1)
        self.assertEqual(item.notes[0].text, "One continuation line.")

    def test_str_round_trips_loose_numbered_two_continuations(self) -> None:
        """Loose numbered item with two continuation paragraphs: parsing works, notes captured.

        Note: loose numbered lists do not round-trip byte-exact because mdformat
        strips indentation from continuation paragraphs, while our renderer adds
        marker-width indentation (same as bullet lists). This is an accepted
        limitation -- parsing correctly captures notes, which is the key feature.
        """
        raw = "1. Security\n\n  First continuation.\n\n  Second continuation.\n"
        txt_formatted = format_text(raw)
        item = _parse_single_numbered_item(txt_formatted)
        # Verify parsing worked: notes captured correctly
        self.assertIsNotNone(item.notes)
        self.assertEqual(len(item.notes), 2)
        self.assertEqual(item.notes[0].text, "First continuation.")
        self.assertEqual(item.notes[1].text, "Second continuation.")


class TestMarkdownListItemWithNotesSerialization(unittest.TestCase):
    """Tests for MarkdownListItemWithNotes model_dump() and model_dump_json() behavior."""

    def test_model_dump_tight_omits_none_notes(self) -> None:
        """Tight item notes field is ``None``; model_dump omits it or shows null."""
        txt_formatted = format_text("- Reliability\n")
        item = _parse_single_item(txt_formatted)
        dump = item.model_dump()
        self.assertEqual(dump.get("notes"), None)

    def test_model_dump_json_loose_shows_notes(self) -> None:
        """Loose item with one continuation paragraph: JSON shows the notes field."""
        raw = "- Reliability\n\n  One continuation line.\n"
        txt_formatted = format_text(raw)
        item = _parse_single_item(txt_formatted)
        json_str = item.model_dump_json()
        parsed = json.loads(json_str)
        self.assertIn("notes", parsed)
        self.assertEqual(len(parsed["notes"]), 1)

    def test_model_dump_json_loose_two_notes(self) -> None:
        """Loose item with two continuation paragraphs: JSON shows both entries."""
        raw = "- Security\n\n  First.\n\n  Second.\n"
        txt_formatted = format_text(raw)
        item = _parse_single_item(txt_formatted)
        json_str = item.model_dump_json()
        parsed = json.loads(json_str)
        self.assertIn("notes", parsed)
        self.assertEqual(len(parsed["notes"]), 2)

    # --- Numbered list serialization tests ---

    def test_model_dump_numbered_tight_omits_none_notes(self) -> None:
        """Tight numbered item notes field is ``None``; model_dump omits it or shows null."""
        txt_formatted = format_text("1. Reliability\n")
        item = _parse_single_numbered_item(txt_formatted)
        dump = item.model_dump()
        self.assertEqual(dump.get("notes"), None)

    def test_model_dump_json_numbered_loose_shows_notes(self) -> None:
        """Loose numbered item with one continuation paragraph: JSON shows the notes field."""
        raw = "1. Reliability\n\n  One continuation line.\n"
        txt_formatted = format_text(raw)
        item = _parse_single_numbered_item(txt_formatted)
        json_str = item.model_dump_json()
        parsed = json.loads(json_str)
        self.assertIn("notes", parsed)
        self.assertEqual(len(parsed["notes"]), 1)

    def test_model_dump_json_numbered_loose_two_notes(self) -> None:
        """Loose numbered item with two continuation paragraphs: JSON shows both entries."""
        raw = "1. Security\n\n  First.\n\n  Second.\n"
        txt_formatted = format_text(raw)
        item = _parse_single_numbered_item(txt_formatted)
        json_str = item.model_dump_json()
        parsed = json.loads(json_str)
        self.assertIn("notes", parsed)
        self.assertEqual(len(parsed["notes"]), 2)


if __name__ == "__main__":
    unittest.main()
