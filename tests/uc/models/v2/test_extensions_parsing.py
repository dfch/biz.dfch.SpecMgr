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

"""Verify the generic markdown engine can parse Extensions with dynamic h3 headings.

Confirms that the regex `@alias` on `Extension` (h3) matches compound-numbered
headings like "Extension 3a. Company is out of one of the ordered items" and that
the generic engine decomposes the `Extensions` (h2) section into a `list[Extension]`
-- no custom `parsed_items()`/second parsing pass needed.

Also confirms `ExtensionItem`'s field semantics: `MarkdownListItem.from_text` stores
an item's own *leading* paragraph in `_value`/exposes it via the inherited `.text`
property -- it is never assigned to a declared field. Only content *after* that
leading paragraph is available to populate declared fields, hence `ExtensionItem`
declares only `notes: list[MarkdownParagraph] | None` (optional continuation
paragraphs), not a `short`/leading-text field.
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.uc.models.v2.use_case import Extensions, Extension, ExtensionItem


class TestExtensionsParsing(unittest.TestCase):
    """Test parsing of Extensions section with dynamic h3 sub-headings."""

    def test_extension_regex_matches_compound_numbered_headings(self) -> None:
        """The Extension @alias regex matches "Extension 3a.", "Extension 4a.", etc. headings."""
        markdown_text = format_text("""## Extensions

### Extension 3a. Company is out of one of the ordered items

1. Company informs buyer of out-of-stock items.
2. Buyer chooses to: (a) wait for restock, (b) substitute with similar item, or (c) remove item from order.
3. Return to step 4.

### Extension 4a. Buyer requests expedited shipping

1. Company calculates expedited shipping cost.
2. Company provides expedited shipping quote to buyer.
3. Buyer accepts or declines expedited shipping.
4. Return to step 5.
""")
        extensions = Extensions.from_text(markdown_text)

        self.assertIsNotNone(extensions.extensions)
        self.assertEqual(len(extensions.extensions), 2)
        for ext in extensions.extensions:
            self.assertIsInstance(ext, Extension)

    def test_extension_items_parsed_from_ordered_list(self) -> None:
        """Extension items are parsed from the ordered list under each h3."""
        markdown_text = format_text("""### Extension 3a. Company is out of one of the ordered items

1. Company informs buyer of out-of-stock items.
2. Buyer chooses to: (a) wait for restock, (b) substitute with similar item, or (c) remove item from order.
3. Return to step 4.
""")
        extension = Extension.from_text(markdown_text)

        self.assertEqual(len(extension.items), 3)
        for item in extension.items:
            self.assertIsInstance(item, ExtensionItem)

    def test_extensions_contains_list_of_extension_objects(self) -> None:
        """Extensions.extensions is a list of Extension objects, not raw text."""
        markdown_text = format_text("""## Extensions

### Extension 3a. Company is out of one of the ordered items

1. Company informs buyer of out-of-stock items.
2. Buyer chooses to: (a) wait for restock, (b) substitute with similar item, or (c) remove item from order.
3. Return to step 4.

### Extension 4a. Buyer requests expedited shipping

1. Company calculates expedited shipping cost.
2. Company provides expedited shipping quote to buyer.
3. Buyer accepts or declines expedited shipping.
4. Return to step 5.
""")
        extensions = Extensions.from_text(markdown_text)

        self.assertIsNotNone(extensions.extensions)
        self.assertIsInstance(extensions.extensions, list)
        self.assertEqual(len(extensions.extensions), 2)
        for ext in extensions.extensions:
            self.assertIsInstance(ext, Extension)

    def test_extension_item_text_is_its_own_leading_paragraph(self) -> None:
        """An item's `.text` (inherited) is its own leading paragraph, marker-free."""
        markdown_text = format_text("""### Extension 3a. Company is out of one of the ordered items

1. Company informs buyer of out-of-stock items.
2. Buyer chooses to: (a) wait for restock, (b) substitute with similar item, or (c) remove item from order.
3. Return to step 4.
""")
        extension = Extension.from_text(markdown_text)

        self.assertEqual(extension.items[0].text, "Company informs buyer of out-of-stock items.")
        self.assertEqual(
            extension.items[1].text,
            "Buyer chooses to: (a) wait for restock, (b) substitute with similar item, or (c) remove item from order.",
        )
        self.assertEqual(extension.items[2].text, "Return to step 4.")

    def test_extension_item_notes_absent_without_continuation_paragraph(self) -> None:
        """An item with no continuation paragraph leaves `notes` unset (None)."""
        markdown_text = format_text("""### Extension 3a. Company is out of one of the ordered items

1. Company informs buyer of out-of-stock items.
2. Buyer chooses to: (a) wait for restock, (b) substitute with similar item, or (c) remove item from order.
3. Return to step 4.
""")
        extension = Extension.from_text(markdown_text)

        for item in extension.items:
            self.assertIsNone(item.notes)

    def test_extension_item_notes_populated_from_continuation_paragraph(self) -> None:
        """An item's continuation paragraph(s) populate `notes` (a loose list required)."""
        markdown_text = format_text("""### Extension 3a. Company is out of one of the ordered items

1. Company informs buyer of out-of-stock items.

   This should rarely happen. Still we have to address this.

2. Buyer chooses to: (a) wait for restock, (b) substitute with similar item, or (c) remove item from order.
3. Return to step 4.
""")
        extension = Extension.from_text(markdown_text)

        self.assertEqual(extension.items[0].text, "Company informs buyer of out-of-stock items.")
        self.assertIsNotNone(extension.items[0].notes)
        self.assertEqual(len(extension.items[0].notes), 1)
        self.assertEqual(
            str(extension.items[0].notes[0]).strip(),
            "This should rarely happen. Still we have to address this.",
        )

        # No continuation paragraph on the other two items.
        self.assertIsNone(extension.items[1].notes)
        self.assertIsNone(extension.items[2].notes)

    def test_extension_with_notes_round_trips_byte_exact(self) -> None:
        """`str(Extension.from_text(text))` reproduces the exact source text."""
        markdown_text = format_text("""### Extension 3a. Company is out of one of the ordered items

1. Company informs buyer of out-of-stock items.

   This should rarely happen. Still we have to address this.

2. Buyer chooses to: (a) wait for restock, (b) substitute with similar item, or (c) remove item from order.

3. Return to step 4.
""")
        extension = Extension.from_text(markdown_text)

        self.assertEqual(str(extension), markdown_text)

    def test_extensions_with_multiple_extensions_round_trips_byte_exact(self) -> None:
        """The full Extensions (h2) section, with nested Extension h3s, round-trips.

        Both nested extensions use a *loose* list (blank line between every
        item) so this is byte-exact -- see
        `test_extensions_with_tight_list_round_trips_to_loose_equivalent`
        below for the documented tight->loose exception.
        """
        markdown_text = format_text("""## Extensions

### Extension 3a. Company is out of one of the ordered items

1. Company informs buyer of out-of-stock items.

   This should rarely happen. Still we have to address this.

2. Buyer chooses to: (a) wait for restock, (b) substitute with similar item, or (c) remove item from order.

3. Return to step 4.

### Extension 4a. Buyer requests expedited shipping

1. Company calculates expedited shipping cost.

2. Company provides expedited shipping quote to buyer.

3. Buyer accepts or declines expedited shipping.

4. Return to step 5.
""")
        extensions = Extensions.from_text(markdown_text)

        self.assertEqual(str(extensions), markdown_text)

    def test_extensions_with_tight_list_round_trips_to_loose_equivalent(self) -> None:
        """A tight list (no blank line between items) round-trips to an equivalent
        loose list -- `MarkdownListItem`'s documented, accepted exception to
        otherwise byte-exact round-tripping (each item is independently
        re-`mdformat`-normalized before rejoining)."""
        tight = format_text("""## Extensions

### Extension 4a. Buyer requests expedited shipping

1. Company calculates expedited shipping cost.
2. Company provides expedited shipping quote to buyer.
3. Buyer accepts or declines expedited shipping.
4. Return to step 5.
""")
        loose_equivalent = format_text("""## Extensions

### Extension 4a. Buyer requests expedited shipping

1. Company calculates expedited shipping cost.

2. Company provides expedited shipping quote to buyer.

3. Buyer accepts or declines expedited shipping.

4. Return to step 5.
""")
        extensions = Extensions.from_text(tight)

        self.assertNotEqual(str(extensions), tight)
        self.assertEqual(str(extensions), loose_equivalent)


if __name__ == "__main__":
    unittest.main()
