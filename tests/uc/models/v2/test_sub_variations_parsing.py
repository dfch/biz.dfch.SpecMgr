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

"""Verify the generic markdown engine can parse Sub-Variations with dynamic h3 headings.

Same shape as `Extensions`/`Extension` (see `test_extensions_parsing.py`): an h2
(`SubVariations`) containing a variable number of dynamically-named h3 sub-headings
(`SubVariation`, matching "Step N: ...") that differ per document, each with a plain
bullet-list body (unlike `Extension`'s ordered list, `SubVariation`'s items have no
`short`/`notes` split -- just a flat `list[MarkdownListItem]`).
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.uc.models.v2.use_case import SubVariations, SubVariation


class TestSubVariationsParsing(unittest.TestCase):
    """Test parsing of Sub-Variations section with dynamic h3 sub-headings."""

    def test_sub_variation_regex_matches_step_headings(self) -> None:
        """The SubVariation @alias regex matches "Step 1:", "Step 10:", etc. headings."""
        markdown_text = format_text("""## Sub-Variations

### Step 1: Buyer may use

- Phone call
- Fax

### Step 10: Buyer may pay via

- Cash or money order
- Check
""")
        sub_variations = SubVariations.from_text(markdown_text)

        self.assertIsNotNone(sub_variations.sub_variations)
        self.assertEqual(len(sub_variations.sub_variations), 2)
        for sv in sub_variations.sub_variations:
            self.assertIsInstance(sv, SubVariation)

    def test_sub_variation_items_parsed_from_bullet_list(self) -> None:
        """SubVariation items are parsed from the bullet list under each h3."""
        markdown_text = format_text("""### Step 1: Buyer may use

- Phone call
- Fax
- Web order form
- Electronic data interchange (EDI)
""")
        sub_variation = SubVariation.from_text(markdown_text)

        self.assertEqual(len(sub_variation.items), 4)
        self.assertEqual(sub_variation.items[0].text, "Phone call")
        self.assertEqual(sub_variation.items[1].text, "Fax")
        self.assertEqual(sub_variation.items[2].text, "Web order form")
        self.assertEqual(sub_variation.items[3].text, "Electronic data interchange (EDI)")

    def test_sub_variations_contains_list_of_sub_variation_objects(self) -> None:
        """SubVariations.sub_variations is a list of SubVariation objects, not raw text."""
        markdown_text = format_text("""## Sub-Variations

### Step 1: Buyer may use

- Phone call
- Fax
- Web order form
- Electronic data interchange (EDI)

### Step 2: Company may capture information via

- Manual entry by customer service representative
- Automated web form
- EDI system

### Step 7: Company may ship via

- Standard ground shipping
- Expedited shipping
- Overnight shipping
- Local pickup

### Step 10: Buyer may pay via

- Cash or money order
- Check
- Credit card
- Debit card
- Bank transfer
- Digital wallet
""")
        sub_variations = SubVariations.from_text(markdown_text)

        self.assertIsNotNone(sub_variations.sub_variations)
        self.assertIsInstance(sub_variations.sub_variations, list)
        self.assertEqual(len(sub_variations.sub_variations), 4)

        expected_counts = [4, 3, 4, 6]
        for sv, expected_count in zip(sub_variations.sub_variations, expected_counts):
            self.assertIsInstance(sv, SubVariation)
            self.assertEqual(len(sv.items), expected_count)

    def test_sub_variations_absent_when_no_step_headings(self) -> None:
        """`sub_variations` is left `None` when the h2 section has no h3 sub-headings."""
        markdown_text = format_text("## Sub-Variations\n")
        sub_variations = SubVariations.from_text(markdown_text)

        self.assertIsNone(sub_variations.sub_variations)

    def test_sub_variation_with_loose_bullet_list_round_trips_byte_exact(self) -> None:
        """A loose bullet list (blank line between every item) round-trips exactly."""
        markdown_text = format_text("""### Step 1: Buyer may use

- Phone call

- Fax

- Web order form

- Electronic data interchange (EDI)
""")
        sub_variation = SubVariation.from_text(markdown_text)

        self.assertEqual(str(sub_variation), markdown_text)

    def test_sub_variation_with_tight_bullet_list_round_trips_to_loose_equivalent(self) -> None:
        """A tight bullet list (no blank lines) round-trips to an equivalent loose
        list -- same documented `MarkdownListItem` exception as `Extension`'s own
        ordered-list items (see `test_extensions_parsing.py`)."""
        tight = format_text("""### Step 1: Buyer may use

- Phone call
- Fax
- Web order form
- Electronic data interchange (EDI)
""")
        loose_equivalent = format_text("""### Step 1: Buyer may use

- Phone call

- Fax

- Web order form

- Electronic data interchange (EDI)
""")
        sub_variation = SubVariation.from_text(tight)

        self.assertNotEqual(str(sub_variation), tight)
        self.assertEqual(str(sub_variation), loose_equivalent)


if __name__ == "__main__":
    unittest.main()
