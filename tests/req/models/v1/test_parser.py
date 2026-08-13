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

"""Tests for :func:`parse_req`: the `ReqDocument`-level `from_text` entry point."""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.req.models.v1 import ReqDocument
from biz.dfch.specmgr.req.models.v1.parser import parse_req

_REFERENCE_PATH = (
    Path(__file__).resolve().parents[4] / ".specmgr" / "feat" / "feat-6-requirement-artifact" / "req_reference.md"
)

_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: req-001
    type: req
    version: 1.0.0
    status: draft
    created: 2026-08-05
    updated: 2026-08-05
    ---

    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.

    ## Description

    If the engine becomes too hot, the lifetime of the system decreases.

    ## Characteristics

    1. Safety
    1. Reliability

    ## Level

    MUST

    ## Source

    The International Safety Board Association (TISBA)
    """
)


class TestParseReq(unittest.TestCase):
    """Tests for `parse_req`."""

    def test_parses_minimal_document(self) -> None:
        """A minimal, valid document parses into a ReqDocument with the expected shape."""
        document = parse_req(_MINIMAL_DOC)

        self.assertIsInstance(document, ReqDocument)
        self.assertEqual(document.frontmatter.id, "req-001")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.body.text, "Maximum Engine Temperature")
        self.assertEqual(
            document.body.statement.text,
            "WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.",
        )
        self.assertEqual([item.text for item in document.body.characteristics.items], ["Safety", "Reliability"])
        self.assertIsNone(document.body.priority)
        self.assertIsNone(document.body.tags)
        self.assertIsNone(document.body.related_artifacts)
        self.assertIsNone(document.body.more_information)
        self.assertIsNone(document.body.notes)

    def test_parses_full_reference_document(self) -> None:
        """The feature's own reference document round-trips through parse_req."""
        text = _REFERENCE_PATH.read_text(encoding="utf-8")

        document = parse_req(text)

        self.assertEqual(document.frontmatter.id, "deaddead-dead-dead-dead-deaddeaddead")
        self.assertEqual(document.body.text, "Maximum Engine Temperature")
        self.assertEqual([item.text for item in document.body.characteristics.items], ["Safety", "Reliability"])
        self.assertEqual(document.body.level.value.text, "MUST")
        self.assertIsNotNone(document.body.priority)
        self.assertEqual(document.body.priority.value.text, "50")
        self.assertIsNotNone(document.body.tags)
        self.assertEqual([item.text for item in document.body.tags.items], ["Combustion Engines", "Vehicles"])
        self.assertEqual(document.body.source.value.text, "The International Safety Board Association (TISBA)")

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
            ["GOL-0007: Competitive Engines in Consumer Vehicles"],
        )
        self.assertEqual(
            [item.text for item in related_artifacts.acceptance_criteria.items],
            ["ACC-1234: Temperature Measurements on running combustion engines"],
        )
        self.assertIsNotNone(document.body.more_information)
        self.assertIsNotNone(document.body.notes)

    def test_defaults_frontmatter_when_absent(self) -> None:
        """Omitting the frontmatter block entirely still parses, applying ReqFrontmatter's defaults."""
        text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

        document = parse_req(text)

        self.assertIsNone(document.frontmatter.id)
        self.assertEqual(document.frontmatter.type, "req")
        self.assertEqual(document.frontmatter.status, "draft")

    def test_invalid_status_raises_validation_error(self) -> None:
        """A frontmatter `status` outside ReqFrontmatter's closed set fails validation."""
        text = _MINIMAL_DOC.replace("status: draft", "status: not-a-real-status")

        with self.assertRaises(ValidationError):
            parse_req(text)

    def test_malformed_structure_raises_assertion_error(self) -> None:
        """A missing mandatory section (no Description) is a structural failure."""
        text = textwrap.dedent(
            """\
            # Maximum Engine Temperature

            WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.

            ## Characteristics

            1. Safety
            """
        )

        with self.assertRaises(AssertionError):
            parse_req(text)


if __name__ == "__main__":
    unittest.main()
