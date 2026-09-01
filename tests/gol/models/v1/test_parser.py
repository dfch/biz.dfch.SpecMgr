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

"""Tests for :func:`parse_gol`: the `GolDocument`-level `from_text` entry point."""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.gol.models.v1 import GolDocument
from biz.dfch.specmgr.gol.models.v1.parser import parse_gol
from biz.dfch.specmgr.models.md._markdown import format_text

_REFERENCE_PATH = Path(__file__).resolve().parents[4] / ".specmgr" / "feat" / "feat-18-goal" / "gol_reference.md"

# Zero optional sections: the H1, the mandatory `statement` lead paragraph,
# and the mandatory `## Source` -- nothing else. This is the shape a freshly
# created `gol` document may legitimately have (ACC-002: every optional
# section defaults to `None` end to end through the full parser).
_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: gol-001
    type: gol
    version: 1.0.0
    status: draft
    created: '2026-08-25 00:00:00.000Z'
    updated: '2026-08-25 00:00:00.000Z'
    ---

    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output and fuel consumption in the consumer vehicle segment.

    ## Source

    The vehicle program's 2027 market analysis
    """
)


class TestParseGol(unittest.TestCase):
    """Tests for `parse_gol`."""

    def test_parses_minimal_document(self) -> None:
        """A minimal, valid document (zero optional sections) parses into a GolDocument with the expected shape."""
        document = parse_gol(_MINIMAL_DOC)

        self.assertIsInstance(document, GolDocument)
        self.assertEqual(document.frontmatter.id, "gol-001")
        self.assertEqual(document.frontmatter.type, "gol")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.body.text, "Competitive Engines in Consumer Vehicles")
        self.assertEqual(
            document.body.statement.text,
            "THE company shall provide engines that are competitive in power output and fuel consumption in the consumer vehicle segment.",
        )
        self.assertEqual(document.body.source.value.text, "The vehicle program's 2027 market analysis")
        self.assertIsNone(document.body.description)
        self.assertIsNone(document.body.priority)
        self.assertIsNone(document.body.tags)
        self.assertIsNone(document.body.related_artifacts)
        self.assertIsNone(document.body.more_information)
        self.assertIsNone(document.body.notes)

    def test_parses_full_reference_document(self) -> None:
        """The feature's own reference document parses, and its body round-trips byte-exact through parse_gol."""
        text = _REFERENCE_PATH.read_text(encoding="utf-8")

        document = parse_gol(text)

        self.assertEqual(document.frontmatter.id, "deaddead-goal-goal-goal-deaddeadgoal")
        self.assertEqual(document.frontmatter.status, "accepted")
        self.assertEqual(document.body.text, "Competitive Engines in Consumer Vehicles")
        self.assertIsNotNone(document.body.priority)
        self.assertEqual(document.body.priority.value.text, "10")
        self.assertIsNotNone(document.body.tags)
        self.assertEqual(
            [item.text for item in document.body.tags.items],
            ["Business Goals", "Combustion Engines", "Vehicles"],
        )
        self.assertEqual(
            document.body.source.value.text,
            "The vehicle program's 2027 market analysis and the sales organization's consumer vehicle segment study",
        )

        related_artifacts = document.body.related_artifacts
        self.assertIsNotNone(related_artifacts)
        self.assertEqual(
            [item.text for item in related_artifacts.requirements.items],
            ["REQ-9687: Maximum temperatures of running engines in civil vehicles"],
        )
        self.assertEqual(
            [item.text for item in related_artifacts.decisions.items],
            ["DEC-2703: Usage of metal conductors in moving engine parts"],
        )
        self.assertEqual(
            [item.text for item in related_artifacts.goals.items],
            [
                "GOL-0003: Affordable and Efficient Powertrains for the Consumer Segment",
                "GOL-0007: Competitive Engines in Consumer Vehicles",
            ],
        )
        self.assertEqual(
            [item.text for item in related_artifacts.acceptance_criteria.items],
            ["ACC-1234: Temperature Measurements on running combustion engines"],
        )
        self.assertIsNotNone(document.body.more_information)
        self.assertIsNotNone(document.body.notes)

        self.assertEqual(str(document.body), format_text(frontmatter.loads(text).content))

    def test_defaults_frontmatter_when_absent(self) -> None:
        """Omitting the frontmatter block entirely still parses, applying GolFrontmatter's defaults."""
        text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

        document = parse_gol(text)

        self.assertIsNone(document.frontmatter.id)
        self.assertEqual(document.frontmatter.type, "gol")
        self.assertEqual(document.frontmatter.status, "draft")

    def test_invalid_status_raises_validation_error(self) -> None:
        """A frontmatter `status` outside GolFrontmatter's closed set fails validation."""
        text = _MINIMAL_DOC.replace("status: draft", "status: pending")

        with self.assertRaises(ValidationError):
            parse_gol(text)

    def test_invalid_type_raises_validation_error(self) -> None:
        """A frontmatter `type` other than `gol` fails validation."""
        text = _MINIMAL_DOC.replace("type: gol", "type: req")

        with self.assertRaises(ValidationError):
            parse_gol(text)

    def test_priority_out_of_range_raises_validation_error(self) -> None:
        """A `## Priority` value outside 0-99, or with leading zeros, fails validation."""
        for value in ("100", "-1", "007"):
            with self.subTest(value=value):
                text = _MINIMAL_DOC.replace("## Source", f"## Priority\n\n{value}\n\n## Source")

                with self.assertRaises(ValidationError):
                    parse_gol(text)

    def test_priority_upper_bound_is_accepted(self) -> None:
        """`## Priority` value 99 (the documented upper bound) is accepted."""
        text = _MINIMAL_DOC.replace("## Source", "## Priority\n\n99\n\n## Source")

        document = parse_gol(text)

        self.assertEqual(document.body.priority.value.text, "99")

    def test_missing_statement_raises_assertion_error(self) -> None:
        """An H1 with no `statement` lead paragraph (H2 immediately after) is a structural failure."""
        text = textwrap.dedent(
            """\
            # Competitive Engines in Consumer Vehicles

            ## Source

            The vehicle program's 2027 market analysis
            """
        )

        with self.assertRaises(AssertionError):
            parse_gol(text)

    def test_missing_source_raises_assertion_error(self) -> None:
        """A missing mandatory `## Source` section is a structural failure."""
        text = textwrap.dedent(
            """\
            # Competitive Engines in Consumer Vehicles

            THE company shall provide engines that are competitive.
            """
        )

        with self.assertRaises(AssertionError):
            parse_gol(text)

    def test_out_of_order_sections_raise_assertion_error(self) -> None:
        """H2 sections not in declaration order (`## Source` before `## Tags`) leave text over: structural failure."""
        text = textwrap.dedent(
            """\
            # Competitive Engines in Consumer Vehicles

            THE company shall provide engines that are competitive.

            ## Source

            The vehicle program's 2027 market analysis

            ## Tags

            - Vehicles
            """
        )

        with self.assertRaises(AssertionError):
            parse_gol(text)


if __name__ == "__main__":
    unittest.main()
