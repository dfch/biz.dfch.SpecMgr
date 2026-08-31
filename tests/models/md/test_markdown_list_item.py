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

"""Unit tests for MarkdownListItem.get_extent, from_text, __str__, and `text`."""

import unittest

import mdformat

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md.alias import alias, AliasType
from biz.dfch.specmgr.models.md import (
    MarkdownListItem,
    MarkdownSection1,
    MarkdownSection3,
    MarkdownParagraph,
    MarkdownStr,
)


class _Note(MarkdownStr):
    """A leaf `MarkdownStr` field standing in for a composite item's own extra field."""


class _ItemWithNote(MarkdownListItem):
    """A composite item: its own leading paragraph, then a delegated `note` field."""

    note: _Note


class _ItemWithSubList(MarkdownListItem):
    """A composite item whose declared field is itself a nested list of items."""

    sub_items: list[MarkdownListItem]


class _ItemWithOptionalSubList(MarkdownListItem):
    """A composite item with an optional nested list of items."""

    sub_items: list[MarkdownListItem] | None = None


@alias(value=".+", type=AliasType.REGEX)
class _Assumptions(MarkdownSection3):
    """An h3 section exposing its bullet list body as structured items."""

    items: list[MarkdownListItem]


@alias(value=".+", type=AliasType.REGEX)
class _OptionalAssumptions(MarkdownSection3):
    """An h3 section with an optional structured list."""

    items: list[MarkdownListItem] | None = None


class TestMarkdownListItemGetExtent(unittest.TestCase):
    """Tests for MarkdownListItem.get_extent."""

    def test_no_extent_when_first_token_is_not_a_list(self) -> None:
        """A text not starting with a list has no extent."""
        text = format_text("Just a plain paragraph.\n")
        result = MarkdownListItem.get_extent(text)
        self.assertEqual(result, 0)

    def test_no_extent_when_first_token_is_a_heading(self) -> None:
        """Confirms `MarkdownListItem` cannot be used as a top-level/scalar field --
        it never matches anything other than a list wrapper's first item."""
        text = format_text("## A Heading\n\ncontent\n")
        result = MarkdownListItem.get_extent(text)
        self.assertEqual(result, 0)

    def test_leaf_bullet_item_extent_is_its_own_span_only(self) -> None:
        """Only the *first* item's extent is reported, even with siblings following."""
        text = format_text("- Item 1\n- Item 2\n- Item 3\n")
        result = MarkdownListItem.get_extent(text)
        self.assertEqual(result, 1)

    def test_leaf_ordered_item_extent_is_its_own_span_only(self) -> None:
        """Same as bullet, for an ordered list."""
        text = format_text("1. First\n2. Second\n3. Third\n")
        result = MarkdownListItem.get_extent(text)
        self.assertEqual(result, 1)

    def test_extent_includes_an_unmodelled_nested_sub_list(self) -> None:
        """`list_item_open`'s own map already spans nested content -- no extra
        scanning needed, unlike `MarkdownSection`/`MarkdownParagraph`."""
        text = format_text("- Item 1\n\n  - Sub A\n  - Sub B\n\n- Item 2\n")
        result = MarkdownListItem.get_extent(text)
        # Item 1 owns everything up to (excluding) "- Item 2".
        expected = text.splitlines().index("- Item 2")
        self.assertEqual(result, expected)


class TestMarkdownListItemFromTextAndStr(unittest.TestCase):
    """Tests for MarkdownListItem.from_text and __str__ (round-trip)."""

    def test_leaf_bullet_item_round_trips_verbatim(self) -> None:
        """A leaf item (no declared fields) stores and re-emits its extent verbatim,
        marker included."""
        text = format_text("- A single item.\n")
        instance = MarkdownListItem.from_text(text)
        self.assertEqual(instance._value, text)
        self.assertEqual(str(instance), text)

    def test_leaf_ordered_item_round_trips_verbatim(self) -> None:
        """Same as bullet, for an ordered item."""
        text = format_text("1. A single item.\n")
        instance = MarkdownListItem.from_text(text)
        self.assertEqual(str(instance), text)

    def test_leaf_item_preserves_inline_formatting(self) -> None:
        """Inline markdown markup inside an item round-trips verbatim."""
        text = format_text("- An item with *emphasis* and **strong** text.\n")
        instance = MarkdownListItem.from_text(text)
        self.assertEqual(str(instance), text)

    def test_leaf_item_with_unmodelled_nested_sub_list_stays_opaque_and_round_trips(self) -> None:
        """A nested sub-list inside a leaf item is not decomposed -- it just stays
        as part of the item's own verbatim `_value`, and still round-trips exactly."""
        text = format_text("- Item 1\n\n  - Sub A\n  - Sub B\n")
        instance = MarkdownListItem.from_text(text)
        self.assertEqual(str(instance), text)

    def test_from_text_rejects_text_not_starting_with_a_list_item(self) -> None:
        """from_text fails loudly when text doesn't start with a list wrapper."""
        text = format_text("Just a plain paragraph.\n")
        with self.assertRaises(AssertionError):
            MarkdownListItem.from_text(text)

    def test_composite_item_splits_lead_paragraph_and_delegates_rest_to_field(self) -> None:
        """A composite item's own `_value` holds only its own leading paragraph,
        marker included; everything after is delegated to the declared field."""
        text = format_text("- Lead sentence.\n\n  Note content.\n")
        instance = _ItemWithNote.from_text(text)
        self.assertEqual(instance._value, "- Lead sentence.")
        self.assertEqual(instance.note._value, "Note content.\n")

    def test_composite_item_round_trips_exactly(self) -> None:
        """str(instance) reproduces the exact source text, byte-exact."""
        text = format_text("- Lead sentence.\n\n  Note content.\n")
        instance = _ItemWithNote.from_text(text)
        self.assertEqual(str(instance), text)

    def test_composite_ordered_item_round_trips_exactly(self) -> None:
        """Same composite reconstruction, but for an ordered item's marker."""
        text = format_text("1. Lead sentence.\n\n   Note content.\n")
        instance = _ItemWithNote.from_text(text)
        self.assertEqual(str(instance), text)

    def test_composite_item_with_nested_sub_list_round_trips_to_an_equivalent_loose_list(self) -> None:
        """A list can contain other lists: a composite item's declared field can
        itself be `list[MarkdownListItem]`. The same tight->loose widening applies
        one level down too, since the nested list is rendered by the very same
        generic `list[MarkdownStr]` machinery."""
        text = format_text("- Parent item.\n\n  - Sub A\n  - Sub B\n")
        loose_equivalent = format_text("- Parent item.\n\n  - Sub A\n\n  - Sub B\n")
        instance = _ItemWithSubList.from_text(text)
        self.assertEqual(len(instance.sub_items), 2)
        self.assertEqual(str(instance), loose_equivalent)

    def test_composite_item_with_absent_optional_sub_list(self) -> None:
        """An optional nested list field is left unset when no nested list follows."""
        text = format_text("- Just a lead sentence, no sub-list.\n")
        instance = _ItemWithOptionalSubList.from_text(text)
        self.assertIsNone(instance.sub_items)
        self.assertEqual(str(instance), text)

    def test_tight_list_round_trips_to_an_equivalent_loose_list(self) -> None:
        """Accepted, documented exception to the engine's otherwise byte-exact
        round-trip: a genuinely tight source list becomes loose once every item is
        independently sliced/renormalized. Loose lists (see next test) are exact."""
        tight = format_text("- A\n- B\n- C\n")
        loose_equivalent = format_text("- A\n\n- B\n\n- C\n")
        instance = _Assumptions.from_text(format_text("### Assumptions\n\n- A\n- B\n- C\n"))
        self.assertEqual(len(instance.items), 3)
        rendered_body = "\n".join(str(item) for item in instance.items)
        self.assertNotEqual(format_text(rendered_body), tight)
        self.assertEqual(format_text(rendered_body), loose_equivalent)

    def test_loose_list_round_trips_byte_exact(self) -> None:
        """A source list that is already loose is unaffected by the tight->loose
        widening above, and round-trips byte-exact end to end."""
        text = format_text("### Assumptions\n\n- A\n\n- B\n\n- C\n")
        instance = _Assumptions.from_text(text)
        self.assertEqual(str(instance), text)

    def test_ordered_list_used_as_a_section_field_round_trips_with_real_numbering(self) -> None:
        """`list[MarkdownListItem]` correctly preserves/regenerates consecutive
        ordered-list numbering (not the `mdformat` default of collapsing every
        item to "1.") when used as a section's structured field."""

        @alias(value=".+", type=AliasType.REGEX)
        class _Steps(MarkdownSection3):
            items: list[MarkdownListItem]

        raw = "\n".join(f"{i}. Step {i}" for i in range(1, 12))
        text = format_text(f"### Steps\n\n{raw}\n")
        instance = _Steps.from_text(text)
        self.assertEqual(len(instance.items), 11)
        self.assertEqual(instance.items[9].text, "Step 10")

    def test_ordered_list_with_a_composite_item_preserves_correct_padding(self) -> None:
        """A composite item in the middle of a large ordered list does not disrupt
        the final consecutive-numbering/padding pass (`01.`..`11.`)."""

        class _StepWithNote(MarkdownListItem):
            note: _Note

        @alias(value=".+", type=AliasType.REGEX)
        class _Steps(MarkdownSection3):
            items: list[MarkdownListItem]

        body_lines = []
        for i in range(1, 12):
            if i == 10:
                body_lines.append(f"{i}. Step {i}\n\n    Sub note for step 10.")
            else:
                body_lines.append(f"{i}. Step {i}")
        text = format_text("### Steps\n\n" + "\n".join(body_lines) + "\n")

        instance = _Steps.from_text(text)
        self.assertEqual(len(instance.items), 11)
        self.assertEqual(str(instance), text)

    def test_optional_items_field_absent(self) -> None:
        """An optional `list[MarkdownListItem] | None` section field is left unset
        when the section has no list body at all."""
        text = format_text("### Assumptions\n")
        instance = _OptionalAssumptions.from_text(text)
        self.assertIsNone(instance.items)
        self.assertEqual(str(instance), text)


class TestMarkdownListItemText(unittest.TestCase):
    """Tests for the `text` computed field."""

    def test_text_strips_marker_from_a_leaf_bullet_item(self) -> None:
        text = format_text("- We know Buyer\n")
        instance = MarkdownListItem.from_text(text)
        self.assertEqual(instance.text, "We know Buyer")

    def test_text_strips_marker_from_a_leaf_ordered_item(self) -> None:
        text = format_text("1. First step\n")
        instance = MarkdownListItem.from_text(text)
        self.assertEqual(instance.text, "First step")

    def test_text_strips_marker_and_indent_from_a_composite_item(self) -> None:
        text = format_text("- Lead sentence.\n\n  Note content.\n")
        instance = _ItemWithNote.from_text(text)
        self.assertEqual(instance.text, "Lead sentence.")

    def test_text_ignores_an_unmodelled_nested_sub_list(self) -> None:
        """Only the leading paragraph's text is returned, even if the leaf item's
        `_value` also contains further, un-modelled nested content."""
        text = format_text("- Item 1\n\n  - Sub A\n  - Sub B\n")
        instance = MarkdownListItem.from_text(text)
        self.assertEqual(instance.text, "Item 1")


class TestMarkdownListItemComplex(unittest.TestCase):
    def test_nested_list(self) -> None:
        class Document(MarkdownSection1):
            class ComplexListItem(MarkdownListItem): ...

            intro: MarkdownParagraph
            items: list[ComplexListItem]
            outro: MarkdownParagraph

        text = mdformat.text(
            """# Document

This is the intro of the document.

1. This is a list item
2. This is another list item

This is the outro of the document.

""",
            options={"number": True},
        )

        sut = Document.from_text(text)

        assert isinstance(sut, Document), type(Document)

        item_text = mdformat.text("1. ~Another~ item", options={"number": True})
        item = Document.ComplexListItem.from_text(item_text)
        assert isinstance(item, Document.ComplexListItem), type(item)
        sut.items.append(item)


if __name__ == "__main__":
    unittest.main()
