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

"""Tests for the language-variant parse of ``txt`` (feat-229-txt Phase 180, review findings E1/G1/G3).

The opaque free-form body is accepted verbatim in every language (REQ-002): a language
variant's heading-mapping table is applied to the one fixed-text schema heading
(``## Updates``) only, never to the body's free headings.
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.models import compare_skeletons, heading_skeleton, load_heading_table
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.txt.models.v1.parser import parse_txt_body

_ENTRY = "<!-- Newest entry first -- prepend new entries directly below this comment. -->\n\n"
_ENTRY += "### 2026-08-26 00:00:00.000Z - Angelegt\n\nText.\n"


def _variant(body: str, updates_heading: str = "Aktualisierungen") -> str:
    return f"# T\n\n{body}\n\n## {updates_heading}\n\n{_ENTRY}"


class TestParseTxtBodyLanguage(unittest.TestCase):
    """E1: free body headings stay byte-identical; only the ``Updates`` boundary heading is mapped."""

    def test_free_headings_matching_table_keys_are_left_verbatim(self) -> None:
        sut = parse_txt_body(
            _variant("## Zusammenfassung\n\nfoo\n\n## Quelle\n\nbar\n\n### Ursache\n\nbaz"), language="de"
        )

        self.assertEqual(
            sut.body.text, format_text("## Zusammenfassung\n\nfoo\n\n## Quelle\n\nbar\n\n### Ursache\n\nbaz")
        )
        self.assertNotIn("## Summary", sut.body.text)
        self.assertNotIn("## Source", sut.body.text)

    def test_translated_updates_heading_is_the_boundary(self) -> None:
        sut = parse_txt_body(_variant("prose"), language="de")

        self.assertEqual(sut.body.text, "prose\n")
        self.assertEqual(len(sut.updates.updates), 1)

    def test_canonical_updates_heading_is_accepted_in_a_variant(self) -> None:
        sut = parse_txt_body(_variant("prose", "Updates"), language="de")

        self.assertEqual(sut.body.text, "prose\n")

    def test_first_top_level_updates_heading_wins_by_design(self) -> None:
        """A body H2 spelled like the language's ``Updates`` heading IS the boundary (as ``## Updates`` is in EN)."""
        text = "# T\n\nprose\n\n## Aktualisierungen\n\n" + _ENTRY + "\n## Aktualisierungen\n\nleft over\n"

        with self.assertRaises(AssertionError):
            parse_txt_body(text, language="de")

    def test_fenced_translated_updates_heading_stays_in_body(self) -> None:
        sut = parse_txt_body(_variant("```\n## Aktualisierungen\n```\n\nprose"), language="de")

        self.assertIn("```\n## Aktualisierungen\n```", sut.body.text)

    def test_update_entry_content_headings_are_left_verbatim(self) -> None:
        text = _variant("prose") + "\n#### Zusammenfassung\n\nmore\n"

        sut = parse_txt_body(text, language="de")

        self.assertIn("#### Zusammenfassung", str(sut))
        self.assertNotIn("#### Summary", str(sut))

    def test_english_path_is_unchanged(self) -> None:
        sut = parse_txt_body(_variant("## Summary\n\nfoo", "Updates"))

        self.assertEqual(sut.body.text, format_text("## Summary\n\nfoo"))

    def test_missing_updates_heading_is_rejected_by_the_engine(self) -> None:
        with self.assertRaises(AssertionError):
            parse_txt_body("# T\n\n## Zusammenfassung\n\nfoo\n", language="de")


class TestTxtFreeHeadingDrift(unittest.TestCase):
    """G1: the drift check compares free headings as-is -- an untranslated free heading is quiet, a renamed one is drift."""

    def _skeleton(self, body: str, language: str | None) -> list:
        table = None if language is None else load_heading_table(language)
        return heading_skeleton(format_text(body), table)

    def test_identical_free_headings_report_no_drift(self) -> None:
        source = self._skeleton("# T\n\n## Findings\n\nx\n\n## Updates\n\ny\n", None)
        variant = self._skeleton("# T\n\n## Findings\n\nx\n\n## Aktualisierungen\n\ny\n", "de")

        self.assertEqual(compare_skeletons(source, variant), [])

    def test_renamed_free_heading_reports_drift(self) -> None:
        source = self._skeleton("# T\n\n## Findings\n\nx\n\n## Updates\n\ny\n", None)
        variant = self._skeleton("# T\n\n## Befunde\n\nx\n\n## Aktualisierungen\n\ny\n", "de")

        kinds = {finding.kind for finding in compare_skeletons(source, variant)}

        self.assertEqual(kinds, {"missing", "extra"})


if __name__ == "__main__":
    unittest.main()
