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

"""Tests for the language-variant parse of ``set`` (feat-173-req-iso29148-level-set Phase 180).

``set``'s body is fully structured (unlike ``txt``'s opaque catch-all body), so the
GENERIC fence-aware ``normalize_heading_lines`` pre-pass applies: the two fixed-text
schema headings (``## Description``/``## Items``) map through the language's table,
and free nested headings inside ``## Description`` are looked up like any other
levels 2-6 heading (a table hit is rewritten to canonical, a miss stays verbatim --
the ADR item 5 rule). The ``## Items`` bullets are never touched (their schema-
constant tokens stay canonical in the file, REQ-010).
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.models import compare_skeletons, heading_skeleton, load_heading_table
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.set.models.v1.parser import parse_set_body


def _variant(description: str, description_heading: str = "Beschreibung", items_heading: str = "Elemente") -> str:
    return (
        f"# T\n\n"
        f"## {description_heading}\n\n{description}\n\n"
        f"## {items_heading}\n\n"
        "- REQ 00000000-0000-4000-8000-000000000001: Sample Requirement\n"
    )


class TestParseSetBodyLanguage(unittest.TestCase):
    """The two table-mapped schema headings parse to canonical keys; free description
    headings follow the generic levels 2-6 lookup rule."""

    def test_translated_schema_headings_parse_to_canonical_keys(self) -> None:
        sut = parse_set_body(_variant("prose"), language="de")

        self.assertEqual(sut.text, "T")
        self.assertIn("## Description", str(sut.description))
        self.assertIn("## Items", str(sut.items))
        self.assertEqual(len(sut.items.items), 1)

    def test_canonical_schema_headings_are_accepted_in_a_variant(self) -> None:
        sut = parse_set_body(_variant("prose", "Description", "Items"), language="de")

        self.assertEqual(sut.description.text, "## Description\n\nprose\n")

    def test_free_headings_without_table_entries_stay_verbatim(self) -> None:
        sut = parse_set_body(_variant("### Hintergrund\n\nfoo"), language="de")

        self.assertIn("### Hintergrund", str(sut))

    def test_free_headings_with_table_entries_are_mapped_like_any_other_level(self) -> None:
        # the generic pre-pass (ADR 38efdb66 item 5) rewrites table hits at levels
        # 2-6 -- a `### Quelle` nested heading maps to its canonical `Source`
        sut = parse_set_body(_variant("### Quelle\n\nfoo"), language="de")

        self.assertIn("### Source", str(sut))
        self.assertNotIn("### Quelle", str(sut))

    def test_fenced_translated_heading_stays_in_description(self) -> None:
        sut = parse_set_body(_variant("```\n## Elemente\n```\n\nprose"), language="de")

        self.assertIn("```\n## Elemente\n```", str(sut.description))

    def test_english_path_is_unchanged(self) -> None:
        sut = parse_set_body(_variant("prose", "Description", "Items"))

        self.assertEqual(sut.description.text, format_text("## Description\n\nprose\n"))

    def test_missing_items_heading_is_rejected_by_the_engine(self) -> None:
        with self.assertRaises(AssertionError):
            parse_set_body("# T\n\n## Beschreibung\n\nfoo\n", language="de")


class TestSetFreeHeadingDrift(unittest.TestCase):
    """The drift check compares headings through the table -- an untranslated (or
    table-mapped) free description heading is quiet, a renamed one is drift."""

    def _skeleton(self, body: str, language: str | None) -> list:
        table = None if language is None else load_heading_table(language)
        return heading_skeleton(format_text(body), table)

    def test_identical_free_headings_report_no_drift(self) -> None:
        source = self._skeleton(_variant("### Hintergrund\n\nx", "Description", "Items"), None)
        variant = self._skeleton(_variant("### Hintergrund\n\nx"), "de")

        self.assertEqual(compare_skeletons(source, variant), [])

    def test_renamed_free_heading_reports_drift(self) -> None:
        source = self._skeleton(_variant("### Hintergrund\n\nx", "Description", "Items"), None)
        variant = self._skeleton(_variant("### Anderes\n\nx"), "de")

        kinds = {finding.kind for finding in compare_skeletons(source, variant)}

        self.assertEqual(kinds, {"missing", "extra"})


if __name__ == "__main__":
    unittest.main()
