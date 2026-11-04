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

"""Body-model tests for ``set`` (feat-173-req-iso29148-level-set Phase 180).

Covers the opaque ``## Description`` (any markdown, verbatim round-trip), the
mandatory mixed-tag ``## Items`` list (the 12 reference tags in any mix,
per-bullet notes, the duplicate ``(tag, id)`` guard), the binding section
order (H1 -> Description -> Items, engine trailing-completeness for any
further H2), and the ``min_length=1`` items rule.
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.set.models.v1 import Set


def _doc(description: str = "Prose.", items: str = "- REQ 00000000-0000-4000-8000-000000000001: A") -> str:
    return format_text(f"# T\n\n## Description\n\n{description}\n\n## Items\n\n{items}\n")


class TestDescription(unittest.TestCase):
    """The opaque ``## Description`` section: any markdown, captured verbatim."""

    def test_plain_prose(self) -> None:
        sut = Set.from_text(_doc())

        self.assertEqual(sut.description.text, "## Description\n\nProse.\n")

    def test_nested_h3_to_h6_headings_round_trip(self) -> None:
        description = "### H3\n\nA.\n\n#### H4\n\nB.\n\n##### H5\n\nC.\n\n###### H6\n\nD.\n"
        sut = Set.from_text(_doc(description))

        rendered = str(sut.description)
        for heading in ("### H3", "#### H4", "##### H5", "###### H6"):
            self.assertIn(heading, rendered)

    def test_lists_quotes_and_code_round_trip(self) -> None:
        description = "- one\n- two\n\n> a quote\n\n```\n## Items\n## Description\n```\n\nprose after the fence\n"
        sut = Set.from_text(_doc(description))

        rendered = str(sut.description)
        self.assertIn("- one", rendered)
        self.assertIn("> a quote", rendered)
        # a fenced `## Items` line yields no heading token -- it stays in the opaque section
        self.assertIn("```\n## Items\n## Description\n```", rendered)
        self.assertIn("prose after the fence", rendered)

    def test_html_comment_round_trips(self) -> None:
        description = "<!-- an authoring hint -->\n\nProse.\n"
        sut = Set.from_text(_doc(description))

        self.assertIn("<!-- an authoring hint -->", str(sut.description))

    def test_empty_description_is_rejected(self) -> None:
        # an H1 followed directly by `## Items` leaves the mandatory description
        # with a zero extent -- the engine's own mandatory-field error
        with self.assertRaises(AssertionError):
            Set.from_text(format_text("# T\n\n## Items\n\n- REQ 00000000-0000-4000-8000-000000000001: A\n"))


class TestItems(unittest.TestCase):
    """The mandatory mixed-tag ``## Items`` bullet list."""

    def test_single_item(self) -> None:
        sut = Set.from_text(_doc())

        self.assertEqual(len(sut.items.items), 1)
        self.assertEqual(sut.items.items[0].text, "REQ 00000000-0000-4000-8000-000000000001: A")

    def test_mixed_tags_in_any_order(self) -> None:
        items = (
            "- GOL 00000000-0000-4000-8000-000000000001: G\n"
            "- PRB 00000000-0000-4000-8000-000000000002: P\n"
            "- QA 00000000-0000-4000-8000-000000000003: Q\n"
            "- UC 00000000-0000-4000-8000-000000000004: U\n"
            "- REQ 00000000-0000-4000-8000-000000000005: R\n"
            "- RSK 00000000-0000-4000-8000-000000000006: K\n"
            "- DEC 00000000-0000-4000-8000-000000000007: D\n"
            "- ADR 00000000-0000-4000-8000-000000000008: A\n"
            "- VCR 00000000-0000-4000-8000-000000000009: V\n"
            "- SYSRS 00000000-0000-4000-8000-000000000010: S\n"
            "- TXT 00000000-0000-4000-8000-000000000011: T\n"
            "- FEAT feat-42-thermal-management: F\n"
        )
        sut = Set.from_text(_doc(items=items))

        self.assertEqual(len(sut.items.items), 12)
        tags = [item.text.split()[0] for item in sut.items.items]
        self.assertEqual(tags, ["GOL", "PRB", "QA", "UC", "REQ", "RSK", "DEC", "ADR", "VCR", "SYSRS", "TXT", "FEAT"])

    def test_feat_bare_number_id(self) -> None:
        sut = Set.from_text(_doc(items="- FEAT feat-42: F"))

        self.assertEqual(sut.items.items[0].text, "FEAT feat-42: F")

    def test_per_bullet_notes_paragraph(self) -> None:
        items = (
            "- REQ 00000000-0000-4000-8000-000000000001: A\n"
            "\n"
            "  A notes paragraph.\n"
            "\n"
            "  A second notes paragraph.\n"
            "\n"
            "- UC 00000000-0000-4000-8000-000000000002: B\n"
        )
        sut = Set.from_text(_doc(items=items))

        self.assertEqual(len(sut.items.items[0].notes or []), 2)
        self.assertIn("A notes paragraph.", sut.items.items[0].notes[0].text)  # type: ignore[union-attr]
        self.assertIsNone(sut.items.items[1].notes)

    def test_unknown_tag_is_rejected(self) -> None:
        # SOP is a whole-body domain but not one of the 12 reference tags
        with self.assertRaises(ValidationError):
            Set.from_text(_doc(items="- SOP 00000000-0000-4000-8000-000000000001: S"))

    def test_set_tag_is_rejected(self) -> None:
        # SET is deliberately not a reference tag (forward references only)
        with self.assertRaises(ValidationError):
            Set.from_text(_doc(items="- SET 00000000-0000-4000-8000-000000000001: S"))

    def test_missing_title_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Set.from_text(_doc(items="- REQ 00000000-0000-4000-8000-000000000001:"))

    def test_malformed_uuid_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Set.from_text(_doc(items="- REQ not-a-uuid: A"))

    def test_malformed_feat_id_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Set.from_text(_doc(items="- FEAT feat-42: A\n\n- FEAT 42: B\n"))

    def test_empty_items_list_is_rejected(self) -> None:
        # a `## Items` heading with zero bullets: the min_length=1 field check
        with self.assertRaises(AssertionError):
            Set.from_text(format_text("# T\n\n## Description\n\nProse.\n\n## Items\n"))

    def test_missing_items_section_is_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            Set.from_text(format_text("# T\n\n## Description\n\nProse.\n"))

    def test_duplicate_tag_id_pair_is_rejected(self) -> None:
        items = (
            "- REQ 00000000-0000-4000-8000-000000000001: A\n"
            "\n"
            "- REQ 00000000-0000-4000-8000-000000000001: The same artifact again\n"
        )
        with self.assertRaises(ValidationError) as ctx:
            Set.from_text(_doc(items=items))
        self.assertIn("REQ 00000000-0000-4000-8000-000000000001", str(ctx.exception))

    def test_same_id_under_two_tags_is_allowed(self) -> None:
        # different tags are different pairs -- the uuid is a per-document id
        # namespace only by convention, not enforced across tags here
        items = "- REQ 00000000-0000-4000-8000-000000000001: A\n\n- UC 00000000-0000-4000-8000-000000000001: B\n"
        sut = Set.from_text(_doc(items=items))

        self.assertEqual(len(sut.items.items), 2)

    def test_feat_bare_and_full_spellings_are_distinct_pairs(self) -> None:
        # the schema compares the id exactly as spelled: the bare number and
        # the full slug are two different spellings, hence two different pairs
        items = "- FEAT feat-42: A\n\n- FEAT feat-42-thermal-management: B\n"
        sut = Set.from_text(_doc(items=items))

        self.assertEqual(len(sut.items.items), 2)


class TestSectionOrder(unittest.TestCase):
    """The binding H1 -> Description -> Items order (engine trailing-completeness)."""

    def test_items_before_description_is_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            Set.from_text(
                format_text(
                    "# T\n\n## Items\n\n- REQ 00000000-0000-4000-8000-000000000001: A\n\n## Description\n\nProse.\n"
                )
            )

    def test_extra_h2_after_items_is_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            Set.from_text(
                format_text(
                    "# T\n\n## Description\n\nProse.\n\n## Items\n\n"
                    "- REQ 00000000-0000-4000-8000-000000000001: A\n\n## Source\n\nLeft over.\n"
                )
            )

    def test_extra_h2_between_description_and_items_is_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            Set.from_text(
                format_text(
                    "# T\n\n## Description\n\nProse.\n\n## Tags\n\n- a tag\n\n"
                    "## Items\n\n- REQ 00000000-0000-4000-8000-000000000001: A\n"
                )
            )


class TestRoot(unittest.TestCase):
    """The H1 root section itself."""

    def test_h1_title_is_free_form(self) -> None:
        sut = Set.from_text(_doc().replace("# T\n", "# Any Title With Spaces & Symbols!\n", 1))

        self.assertEqual(sut.text, "Any Title With Spaces & Symbols!")

    def test_model_dump_surfaces_description_and_items(self) -> None:
        sut = Set.from_text(_doc())
        dump = sut.model_dump(mode="json")

        self.assertIn("## Description", dump["description"]["text"])
        self.assertEqual(dump["items"]["items"][0]["text"], "REQ 00000000-0000-4000-8000-000000000001: A")
        self.assertIsNone(dump["items"]["items"][0]["notes"])


if __name__ == "__main__":
    unittest.main()
