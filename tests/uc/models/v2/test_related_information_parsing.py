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

"""Verify RelatedInformation parses its two fixed, individually-optional h3
sub-sections (`Notes`/`Assumptions`), each a plain bullet list.

Unlike `Extensions`/`Sub-Variations`, these h3 headings are NOT dynamically
named per document -- `Notes`/`Assumptions` are fixed schema labels, so no
regex `@alias` is needed (default `AliasType.SPACE_SEPARATED` matches them).
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.uc.models.v2.use_case import RelatedInformation, Notes, Assumptions


class TestRelatedInformationParsing(unittest.TestCase):
    """Test parsing of the Related Information section."""

    def test_notes_and_assumptions_both_present(self) -> None:
        """Both Notes and Assumptions populate when both h3s are present."""
        markdown_text = format_text("""## Related Information

### Notes

- This is a high-level summary use case.
- The main success scenario represents the happy path.

### Assumptions

- Buyer has already been authenticated and verified.
- System has access to real-time inventory data.
""")
        related_information = RelatedInformation.from_text(markdown_text)

        self.assertIsInstance(related_information.notes, Notes)
        self.assertEqual(len(related_information.notes.items), 2)
        self.assertEqual(related_information.notes.items[0].text, "This is a high-level summary use case.")

        self.assertIsInstance(related_information.assumptions, Assumptions)
        self.assertEqual(len(related_information.assumptions.items), 2)
        self.assertEqual(
            related_information.assumptions.items[0].text, "Buyer has already been authenticated and verified."
        )

    def test_notes_absent_when_only_assumptions_present(self) -> None:
        """`notes` is left `None` when only Assumptions is present."""
        markdown_text = format_text("""## Related Information

### Assumptions

- Buyer has already been authenticated and verified.
""")
        related_information = RelatedInformation.from_text(markdown_text)

        self.assertIsNone(related_information.notes)
        self.assertIsInstance(related_information.assumptions, Assumptions)

    def test_assumptions_absent_when_only_notes_present(self) -> None:
        """`assumptions` is left `None` when only Notes is present."""
        markdown_text = format_text("""## Related Information

### Notes

- This is a high-level summary use case.
""")
        related_information = RelatedInformation.from_text(markdown_text)

        self.assertIsInstance(related_information.notes, Notes)
        self.assertIsNone(related_information.assumptions)

    def test_both_absent_when_neither_present(self) -> None:
        """Both fields are left `None` when the h2 has neither h3 sub-section."""
        markdown_text = format_text("## Related Information\n")
        related_information = RelatedInformation.from_text(markdown_text)

        self.assertIsNone(related_information.notes)
        self.assertIsNone(related_information.assumptions)

    def test_loose_bullet_lists_round_trip_byte_exact(self) -> None:
        """Loose bullet lists (blank line between every item) round-trip exactly."""
        markdown_text = format_text("""## Related Information

### Notes

- This is a high-level summary use case.

- The main success scenario represents the happy path.

### Assumptions

- Buyer has already been authenticated and verified.

- System has access to real-time inventory data.
""")
        related_information = RelatedInformation.from_text(markdown_text)

        self.assertEqual(str(related_information), markdown_text)

    def test_tight_bullet_lists_round_trip_to_loose_equivalent(self) -> None:
        """Tight bullet lists round-trip to an equivalent loose list -- same
        documented `MarkdownListItem` exception used throughout this model."""
        tight = format_text("""## Related Information

### Notes

- This is a high-level summary use case.
- The main success scenario represents the happy path.

### Assumptions

- Buyer has already been authenticated and verified.
- System has access to real-time inventory data.
""")
        loose_equivalent = format_text("""## Related Information

### Notes

- This is a high-level summary use case.

- The main success scenario represents the happy path.

### Assumptions

- Buyer has already been authenticated and verified.

- System has access to real-time inventory data.
""")
        related_information = RelatedInformation.from_text(tight)

        self.assertNotEqual(str(related_information), tight)
        self.assertEqual(str(related_information), loose_equivalent)


if __name__ == "__main__":
    unittest.main()
