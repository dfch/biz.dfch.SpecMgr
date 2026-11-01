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

"""Committed ADR-outcome regression fixtures (feat-247-dec-outcome-blocks, ACC-007).

The three fixture documents under ``tests/fixtures/dec-outcome-blocks/`` each
carry the real ``## Decision Outcome`` section of one of the ADRs named in the
plan (``750842b2``, ``92cc4ce8``, ``356d8781`` -- the ADRs' own UUIDs are the
fixtures' ``id`` frontmatter, and each fixture's ``## Source`` names its
provenance) verbatim inside a minimal-but-valid ``dec`` body. Every one of
the three outcomes genuinely has more than one lead block (one lead paragraph
plus a bullet list of sub-decisions; two lead paragraphs twice over), so each
fixture exercises the new optional ``outcome.further_blocks`` field: before
feat-247 all three failed the parse with "text left over after processing all
fields".
"""

from __future__ import annotations

import unittest
from pathlib import Path

import frontmatter

from biz.dfch.specmgr.dec.models.v1 import DecDocument
from biz.dfch.specmgr.dec.models.v1.parser import parse_dec
from biz.dfch.specmgr.models.md._markdown import format_markdown_document, format_text

_FIXTURES = Path(__file__).resolve().parents[3] / "fixtures" / "dec-outcome-blocks"

#: ``(fixture file name, the ADR's own UUID carried as the fixture's ``id``,
#: a distinctive prefix of the first line of the fixture's ``further_blocks``)``
#: -- the prefix pins that the fixture's extra blocks really are the ADR
#: outcome's second lead block, not some other content.
_FIXTURES_AND_EXPECTATIONS = [
    (
        "adr-750842b2-outcome.md",
        "750842b2-aca4-4649-ba0c-855ec8e1f505",
        "- **Backend:** `fastembed` wrapping `BAAI/bge-small-en-v1.5`",
    ),
    (
        "adr-92cc4ce8-outcome.md",
        "92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c",
        "This decision covers the ADR/decision-record step only",
    ),
    (
        "adr-356d8781-outcome.md",
        "356d8781-e446-4c26-917a-eda85648ce9d",
        "Why Option 1 wins: the audience for every one of these resources",
    ),
]


class TestAdrOutcomeFixturesParse(unittest.TestCase):
    """ACC-007: each ADR-derived outcome fixture parses without "text left over" and with
    ``outcome.further_blocks`` populated."""

    def test_each_fixture_is_mdformat_stable(self) -> None:
        """The committed fixture files are ``mdformat``-stable (frontmatter key order included), so a
        re-format of any of them is a no-op."""
        for file_name, _adr_id, _first_line in _FIXTURES_AND_EXPECTATIONS:
            with self.subTest(fixture=file_name):
                text = (_FIXTURES / file_name).read_text(encoding="utf-8")
                changed, _formatted = format_markdown_document(text)
                self.assertFalse(changed)

    def test_each_fixture_parses_with_further_blocks_populated(self) -> None:
        """Each fixture parses via ``parse_dec`` (no "text left over" in ``DecisionOutcome``), with
        the ADR's own UUID as the document ``id``, a non-empty lead ``statement``, and a
        ``further_blocks`` leaf whose first line is the ADR outcome's real second lead block."""
        for file_name, adr_id, first_line in _FIXTURES_AND_EXPECTATIONS:
            with self.subTest(fixture=file_name):
                text = (_FIXTURES / file_name).read_text(encoding="utf-8")

                document = parse_dec(text)

                self.assertIsInstance(document, DecDocument)
                assert isinstance(document, DecDocument)
                self.assertEqual(document.frontmatter.id, adr_id)
                outcome = document.body.outcome
                self.assertTrue(outcome.statement.text)
                assert outcome.further_blocks is not None
                self.assertTrue(outcome.further_blocks.text)
                self.assertTrue(outcome.further_blocks.text.splitlines()[0].startswith(first_line))

    def test_each_fixture_round_trips_byte_exact(self) -> None:
        """Each fixture's body round-trips byte-exact through the full parser (REQ-003 at the
        document level)."""
        for file_name, _adr_id, _first_line in _FIXTURES_AND_EXPECTATIONS:
            with self.subTest(fixture=file_name):
                text = (_FIXTURES / file_name).read_text(encoding="utf-8")

                document = parse_dec(text)
                assert isinstance(document, DecDocument)

                body = frontmatter.loads(text).content
                self.assertEqual(str(document.body), format_text(body))


if __name__ == "__main__":
    unittest.main()
