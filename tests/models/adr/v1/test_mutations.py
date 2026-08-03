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

"""Tests for the structured edit operations in :mod:`mutations` (plan §4, §5, §8)."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.adr.v1 import (
    Adr,
    AdrBody,
    AdrFrontmatter,
    AdrOption,
    AdrOptionNotFoundError,
    AdrSectionError,
    option_create,
    option_delete,
    option_list,
    option_read,
    option_update,
    set_status,
    update_section,
)


def _adr(**body_overrides: object) -> Adr:
    body_fields = {
        "title": "A title",
        "context_and_problem_statement": "Context.",
        "considered_options": "Options.",
        "decision_outcome": "Outcome.",
    }
    body_fields.update(body_overrides)
    return Adr(frontmatter=AdrFrontmatter(), body=AdrBody(**body_fields))


class TestUpdateSection(unittest.TestCase):
    """Tests for update_section."""

    def test_replaces_optional_section(self):
        """A normal value replaces an optional field, leaving the input untouched."""
        adr = _adr()
        updated = update_section(adr, "decision_drivers", "* Driver 1")
        self.assertEqual(updated.body.decision_drivers, "* Driver 1")
        self.assertIsNone(adr.body.decision_drivers)

    def test_replaces_mandatory_section_with_non_sentinel_value(self):
        """A normal, non-blank value replaces a mandatory field too."""
        adr = _adr()
        updated = update_section(adr, "title", "A new title")
        self.assertEqual(updated.body.title, "A new title")

    def test_blank_sentinel_clears_optional_section(self):
        """A blank/whitespace-only value clears an optional field to None."""
        adr = _adr(decision_drivers="* Driver 1")
        updated = update_section(adr, "decision_drivers", "   ")
        self.assertIsNone(updated.body.decision_drivers)

    def test_remove_sentinel_clears_optional_section(self):
        """The literal 'REMOVE' (case-insensitive) also clears an optional field."""
        adr = _adr(decision_drivers="* Driver 1")
        updated = update_section(adr, "decision_drivers", "ReMoVe")
        self.assertIsNone(updated.body.decision_drivers)

    def test_blank_sentinel_on_mandatory_section_raises_and_does_not_write(self):
        """A deletion sentinel targeting a mandatory field is rejected outright."""
        adr = _adr()
        with self.assertRaises(AdrSectionError):
            update_section(adr, "title", "")
        self.assertEqual(adr.body.title, "A title")

    def test_remove_sentinel_on_mandatory_section_raises(self):
        """'REMOVE' targeting a mandatory field is rejected too."""
        adr = _adr()
        with self.assertRaises(AdrSectionError):
            update_section(adr, "considered_options", "REMOVE")

    def test_unknown_key_raises(self):
        """A key that is not an AdrBody field is rejected."""
        adr = _adr()
        with self.assertRaises(AdrSectionError):
            update_section(adr, "not_a_real_field", "value")

    def test_options_key_is_rejected(self):
        """'options' is not reachable through update_section -- use option_* instead."""
        adr = _adr()
        with self.assertRaises(AdrSectionError):
            update_section(adr, "options", "value")


class TestSetStatus(unittest.TestCase):
    """Tests for set_status."""

    def test_sets_plain_status(self):
        """A plain status value replaces frontmatter.status."""
        adr = _adr()
        updated = set_status(adr, "accepted")
        self.assertEqual(updated.frontmatter.status, "accepted")
        self.assertEqual(adr.frontmatter.status, "draft")

    def test_superseded_by_composes_status_string(self):
        """superseded_by composes the 'superseded by ...' status form."""
        adr = _adr()
        updated = set_status(adr, "accepted", superseded_by="0007-some-other-decision")
        self.assertEqual(updated.frontmatter.status, "superseded by 0007-some-other-decision")

    def test_invalid_status_still_raises(self):
        """An unrecognized status still fails AdrFrontmatter's own validator."""
        adr = _adr()
        with self.assertRaises(ValidationError):
            set_status(adr, "not-a-real-status")


class TestOptionCrud(unittest.TestCase):
    """Tests for option_list/option_create/option_read/option_update/option_delete."""

    def test_option_list_empty_by_default(self):
        """A fresh Adr has zero options."""
        self.assertEqual(option_list(_adr()), [])

    def test_option_create_assigns_number_one_first(self):
        """The first created option is numbered 1."""
        adr = _adr()
        updated, full_title = option_create(adr, "First", "Some content.")
        self.assertEqual(full_title, "Option 1: First")
        self.assertEqual(option_list(updated), ["Option 1: First"])
        self.assertEqual(option_list(adr), [])

    def test_option_create_increments_from_current_max(self):
        """A second option gets number = max(existing) + 1, not len() + 1."""
        adr = _adr(options=[AdrOption(number=5, partial_title="Existing", content="")])
        _, full_title = option_create(adr, "New", "content")
        self.assertEqual(full_title, "Option 6: New")

    def test_option_create_does_not_fill_numbering_gaps(self):
        """After deleting number 2, the next created option is 4, not 2."""
        adr = _adr(
            options=[
                AdrOption(number=1, partial_title="First", content=""),
                AdrOption(number=3, partial_title="Third", content=""),
            ]
        )
        _, full_title = option_create(adr, "Fourth", "content")
        self.assertEqual(full_title, "Option 4: Fourth")

    def test_option_read_returns_current_content(self):
        """option_read returns the matched option's content."""
        adr = _adr(options=[AdrOption(number=1, partial_title="First", content="Some content.")])
        self.assertEqual(option_read(adr, "Option 1: First"), "Some content.")

    def test_option_read_missing_raises(self):
        """option_read raises AdrOptionNotFoundError for an unknown title."""
        with self.assertRaises(AdrOptionNotFoundError):
            option_read(_adr(), "Option 1: Does not exist")

    def test_option_update_replaces_content(self):
        """option_update replaces content and returns the new value."""
        adr = _adr(options=[AdrOption(number=1, partial_title="First", content="Old.")])
        updated, new_content = option_update(adr, "Option 1: First", "New.")
        self.assertEqual(new_content, "New.")
        self.assertEqual(option_read(updated, "Option 1: First"), "New.")
        self.assertEqual(option_read(adr, "Option 1: First"), "Old.")

    def test_option_update_missing_raises_and_does_not_write(self):
        """option_update raises for an unknown title and leaves adr untouched."""
        adr = _adr(options=[AdrOption(number=1, partial_title="First", content="Old.")])
        with self.assertRaises(AdrOptionNotFoundError):
            option_update(adr, "Option 9: Missing", "New.")
        self.assertEqual(option_read(adr, "Option 1: First"), "Old.")

    def test_option_delete_removes_option_and_returns_remaining_titles(self):
        """option_delete removes the match and returns the remaining full titles."""
        adr = _adr(
            options=[
                AdrOption(number=1, partial_title="First", content=""),
                AdrOption(number=2, partial_title="Second", content=""),
            ]
        )
        updated, remaining = option_delete(adr, "Option 1: First")
        self.assertEqual(remaining, ["Option 2: Second"])
        self.assertEqual(option_list(updated), ["Option 2: Second"])
        self.assertEqual(option_list(adr), ["Option 1: First", "Option 2: Second"])

    def test_option_delete_leaves_numbering_gap(self):
        """Deleting option 1 out of {1, 3} leaves option 3 as-is, not renumbered."""
        adr = _adr(
            options=[
                AdrOption(number=1, partial_title="First", content=""),
                AdrOption(number=3, partial_title="Third", content=""),
            ]
        )
        _, remaining = option_delete(adr, "Option 1: First")
        self.assertEqual(remaining, ["Option 3: Third"])

    def test_option_delete_missing_raises(self):
        """option_delete raises AdrOptionNotFoundError for an unknown title."""
        with self.assertRaises(AdrOptionNotFoundError):
            option_delete(_adr(), "Option 1: Does not exist")


if __name__ == "__main__":
    unittest.main()
