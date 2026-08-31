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

"""Unit tests for MarkdownSection.get_extent, __str__, and @alias enforcement."""

import unittest

import mdformat

from biz.dfch.specmgr.models.md.alias import alias, AliasType
from biz.dfch.specmgr.models.md.markdown_section3 import MarkdownSection3

from .various_models import MainDocument


@alias(value="Correct Heading", type=AliasType.LITERAL)
class _AliasedLeafSection(MarkdownSection3): ...


@alias(value=".+", type=AliasType.REGEX)
class _AnyHeadingLeafSection(MarkdownSection3): ...


class TestMarkdownSectionGetExtent(unittest.TestCase):
    """Tests for MarkdownSection.get_extent (heading-level-aware extent).

    Uses `_AnyHeadingLeafSection` (a permissive `.+` regex `@alias`), not the
    bare `MarkdownSection3` -- `get_extent` also enforces the effective
    `@alias` now (same check `from_text` already made), so a class relying on
    the no-@alias `SPACE_SEPARATED` default (which derives
    `"MarkdownSection3"` -> `"Markdown Section 3"`) would reject every one of
    these fixtures' arbitrary heading text (`"Sec3"`, `"Sibling"`, ...); a
    `.+` regex alias is what actually isolates "heading *level*" from
    "heading *text*" for these level-only tests.
    """

    def test_no_extent_when_first_token_is_not_own_heading(self) -> None:
        """A text not starting with this class's own heading tag has no extent."""
        text = mdformat.text("## Not h3\ncontent\n")
        result = _AnyHeadingLeafSection.get_extent(text)
        self.assertEqual(result, 0)

    def test_extends_to_end_of_input_when_no_stopping_heading(self) -> None:
        """With no sibling/ancestor heading following, the extent reaches the end."""
        text = mdformat.text("### Sec3 only\ncontent\nmore content\n")
        result = _AnyHeadingLeafSection.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_nested_deeper_heading_is_included(self) -> None:
        """A deeper heading (h4) is nested content and does not stop the extent."""
        text = mdformat.text("### Sec3\ncontent\n\n#### Sec4 nested\nnested content\n")
        result = _AnyHeadingLeafSection.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_sibling_heading_stops_extent(self) -> None:
        """A sibling heading (same level, h3) stops the extent."""
        text = mdformat.text("### Sec3\ncontent\n\n### Sibling\nmore\n")
        lines = text.splitlines()
        stop_line = next(i for i, line in enumerate(lines) if line.startswith("### Sibling"))
        result = _AnyHeadingLeafSection.get_extent(text)
        self.assertEqual(result, stop_line)

    def test_ancestor_heading_stops_extent(self) -> None:
        """An ancestor heading (shallower level, h1 or h2) stops the extent."""
        text = mdformat.text("### Sec3\ncontent\n\n#### Sec4 nested\nnested content\n\n## Sec2 stops here\nmore\n")
        lines = text.splitlines()
        stop_line = next(i for i, line in enumerate(lines) if line.startswith("## Sec2"))
        result = _AnyHeadingLeafSection.get_extent(text)
        self.assertEqual(result, stop_line)

    def test_h1_and_h2_and_h3_stop_the_extent(self) -> None:
        """Any next heading of level 1, 2, or 3 (own level or shallower) stops the extent."""
        for level, marker in ((1, "#"), (2, "##"), (3, "###")):
            with self.subTest(level=level):
                text = mdformat.text(f"### Sec3\ncontent\n\n{marker} Next\nmore\n")
                lines = text.splitlines()
                stop_line = next(i for i, line in enumerate(lines) if line.startswith(f"{marker} Next"))
                result = _AnyHeadingLeafSection.get_extent(text)
                self.assertEqual(result, stop_line)

    def test_h4_and_h5_and_h6_do_not_stop_the_extent(self) -> None:
        """Any next heading of level 4, 5, or 6 (deeper than own level) is nested content."""
        for level, marker in ((4, "####"), (5, "#####"), (6, "######")):
            with self.subTest(level=level):
                text = mdformat.text(f"### Sec3\ncontent\n\n{marker} Nested\nmore\n")
                result = _AnyHeadingLeafSection.get_extent(text)
                self.assertEqual(result, len(text.splitlines()))

    def test_no_extent_when_heading_text_does_not_match_declared_alias(self) -> None:
        """A same-level heading that does NOT satisfy the class's own @alias has
        no extent -- this is what lets `process_field`'s optional-field handling
        correctly treat an absent optional section (followed by a *different*,
        sibling h3) as absent, rather than mis-matching the wrong heading."""
        text = mdformat.text("### Wrong Heading\ncontent\n")
        result = _AliasedLeafSection.get_extent(text)
        self.assertEqual(result, 0)


class TestMarkdownSectionStr(unittest.TestCase):
    """Tests for MarkdownSection.__str__ (heading re-emission)."""

    def test_leaf_section_reemits_its_complete_extent_verbatim(self) -> None:
        """A leaf section (no nested fields) round-trips its whole extent, heading and body."""
        text = mdformat.text("### Sec3\ncontent\n")
        instance = _AnyHeadingLeafSection.from_text(text)
        self.assertEqual(str(instance), text)

    def test_leaf_section_preserves_inline_formatting_in_heading(self) -> None:
        """Inline markdown markup inside a heading round-trips through __str__ verbatim."""
        text = mdformat.text("### *Emphasized* Sec3\ncontent\n")
        instance = _AnyHeadingLeafSection.from_text(text)
        self.assertEqual(str(instance), text)

    def test_composite_document_reemits_every_heading_and_body(self) -> None:
        """A composite MarkdownSection's __str__ is a full, byte-exact round-trip:
        its own heading plus every descendant section's heading *and* body text --
        not just the headings `MarkdownSection`'s own `_value` directly holds."""
        text = mdformat.text(
            "# Main Title\n"
            "\n"
            "## Characteristic Information\n"
            "\n"
            "### *Goal* In Context\n"
            "\n"
            "Some goal text.\n"
            "\n"
            "### Scope\n"
            "\n"
            "Some scope text.\n"
            "\n"
            "## Related Information\n"
            "\n"
            "### Notes\n"
            "\n"
            "Some notes text.\n"
            "\n"
            "### Assumptions\n"
            "\n"
            "Some assumptions text.\n"
        )

        doc = MainDocument.from_text(text)
        rendered = str(doc)

        self.assertEqual(rendered, text)


class TestMarkdownSectionAliasEnforcement(unittest.TestCase):
    """Tests for MarkdownSection.from_text honouring a declared @alias (match_alias)."""

    def test_accepts_heading_matching_declared_alias(self) -> None:
        """A heading matching an explicit @alias parses normally."""
        text = mdformat.text("### Correct Heading\ncontent\n")
        instance = _AliasedLeafSection.from_text(text)
        self.assertEqual(instance._value, text)

    def test_rejects_heading_not_matching_declared_alias(self) -> None:
        """A heading that does not match an explicit @alias fails loudly."""
        text = mdformat.text("### Wrong Heading\ncontent\n")
        with self.assertRaises(AssertionError):
            _AliasedLeafSection.from_text(text)

    def test_class_with_no_alias_defaults_to_space_separated_class_name_match(self) -> None:
        """A class with no @alias at all (e.g. MarkdownSection3 itself) defaults to
        `AliasType.SPACE_SEPARATED`'s derivation of its own class name (ADR
        832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.4.0), not "accept any heading
        text", and not a literal match against the raw class name."""
        text = mdformat.text("### Markdown Section 3\ncontent\n")
        instance = MarkdownSection3.from_text(text)
        self.assertEqual(instance._value, text)

    def test_class_with_no_alias_rejects_a_different_heading(self) -> None:
        """The space-separated-class-name default is not a wildcard: other text
        is rejected."""
        text = mdformat.text("### Anything Goes\ncontent\n")
        with self.assertRaises(AssertionError):
            MarkdownSection3.from_text(text)

    def test_regex_alias_accepts_any_non_empty_heading_text(self) -> None:
        """A class opting into a permissive regex alias (`.+`) accepts arbitrary
        heading text, per ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.3.1."""
        text = mdformat.text("### Anything Goes\ncontent\n")
        instance = _AnyHeadingLeafSection.from_text(text)
        self.assertEqual(instance._value, text)

    def test_fixture_document_rejects_a_mismatched_nested_heading(self) -> None:
        """End-to-end: MainDocument.from_text fails when a nested section's heading
        doesn't match that section's declared @alias (here, CharacteristicInformation
        expects "Characteristic Information", not "Not The Right Heading")."""
        text = mdformat.text(
            "# Main Title\n"
            "\n"
            "## Not The Right Heading\n"
            "\n"
            "### *Goal* In Context\n"
            "\n"
            "Some goal text.\n"
            "\n"
            "### Scope\n"
            "\n"
            "Some scope text.\n"
            "\n"
            "## Related Information\n"
            "\n"
            "### Notes\n"
            "\n"
            "Some notes text.\n"
            "\n"
            "### Assumptions\n"
            "\n"
            "Some assumptions text.\n"
        )
        with self.assertRaises(AssertionError):
            MainDocument.from_text(text)


class TestMarkdownSectionText(unittest.TestCase):
    """Tests for `MarkdownSection.text` (computed_field), leaf vs. composite."""

    def test_leaf_section_text_returns_the_complete_extent(self) -> None:
        """A leaf section's `.text` returns everything -- its own heading and
        body -- not just the heading, since it has no declared field of its
        own to hold the body and `_value` is otherwise invisible to
        `model_dump()`."""
        text = mdformat.text("### Sec3\n\ncontent\n\nmore content\n")
        instance = _AnyHeadingLeafSection.from_text(text)
        self.assertEqual(instance.text, text)

    def test_composite_section_text_returns_only_the_heading(self) -> None:
        """A composite section's `.text` returns just its own heading text --
        the body is already reachable through its declared nested fields."""
        text = mdformat.text(
            "# Main Title\n"
            "\n"
            "## Characteristic Information\n"
            "\n"
            "### *Goal* In Context\n"
            "\n"
            "Some goal text.\n"
            "\n"
            "### Scope\n"
            "\n"
            "Some scope text.\n"
            "\n"
            "## Related Information\n"
            "\n"
            "### Notes\n"
            "\n"
            "Some notes text.\n"
            "\n"
            "### Assumptions\n"
            "\n"
            "Some assumptions text.\n"
        )

        doc = MainDocument.from_text(text)

        self.assertEqual(doc.text, "Main Title")
        self.assertEqual(doc.characteristic_information.text, "Characteristic Information")

    def test_leaf_child_of_a_composite_section_text_returns_its_own_complete_extent(self) -> None:
        """A leaf section nested inside a composite parent still returns its
        own full heading-and-body extent from `.text`, independently of its
        parent's heading-only `.text`."""
        text = mdformat.text(
            "# Main Title\n"
            "\n"
            "## Characteristic Information\n"
            "\n"
            "### *Goal* In Context\n"
            "\n"
            "Some goal text.\n"
            "\n"
            "### Scope\n"
            "\n"
            "Some scope text.\n"
            "\n"
            "## Related Information\n"
            "\n"
            "### Notes\n"
            "\n"
            "Some notes text.\n"
            "\n"
            "### Assumptions\n"
            "\n"
            "Some assumptions text.\n"
        )

        doc = MainDocument.from_text(text)

        self.assertEqual(
            doc.characteristic_information.goal_in_context.text,
            mdformat.text("### *Goal* In Context\n\nSome goal text.\n"),
        )
        self.assertEqual(
            doc.related_information.notes.text,
            mdformat.text("### Notes\n\nSome notes text.\n"),
        )


class TestMarkdownSectionNestedHeadingContent(unittest.TestCase):
    """Tests for how a leaf MarkdownSection's body handles an embedded heading."""

    def test_leaf_section_silently_retains_a_deeper_nested_heading(self) -> None:
        """A heading deeper than the leaf's own level does not stop `get_extent`
        (see MarkdownSection.get_extent), so it ends up inside `_value` verbatim,
        with no validation of its presence."""
        text = mdformat.text("### Leaf H3\n\nSome real content.\n\n#### A nested heading\n\nMore text after it.\n")
        instance = _AnyHeadingLeafSection.from_text(text)
        self.assertEqual(instance._value, text)
        self.assertIn("#### A nested heading", instance._value)

    def test_directly_assigning_a_nested_heading_to_value_raises_nothing(self) -> None:
        """`validate_headings` (MarkdownSection1..6) is currently a no-op: its body
        is fully commented out, so nothing re-validates `_value`'s content shape
        after construction."""
        instance = MarkdownSection3()
        instance._value = "### Leaf H3\n\n#### nested heading\n"
        self.assertIn("#### nested heading", instance._value)


if __name__ == "__main__":
    unittest.main()
