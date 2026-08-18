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

"""Tests for :func:`parse_qa`: the `QaDocument`-level `from_text` entry point."""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.qa.models.v1 import QaDocument
from biz.dfch.specmgr.qa.models.v1.parser import parse_qa

_REFERENCE_PATH = Path(__file__).resolve().parents[4] / ".specmgr" / "feat" / "feat-12-qa-artifact" / "qa_reference.md"

_MINIMAL_CATEGORIES = "\n\n".join(
    f"## {heading}"
    for heading in (
        "Functional Suitability",
        "Performance Efficiency",
        "Compatibility",
        "Interaction Capability",
        "Reliability",
        "Security",
        "Maintainability",
        "Flexibility",
        "Safety",
    )
)

_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: qa-001
    type: qa
    version: 1.0.0
    status: draft
    created: 2026-08-18
    updated: 2026-08-18
    ---

    # Simple Q&A Document

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    {categories}
    """
).format(categories=_MINIMAL_CATEGORIES)


class TestParseQa(unittest.TestCase):
    """Tests for `parse_qa`."""

    def test_parses_minimal_document(self) -> None:
        """A minimal, valid document parses into a QaDocument with the expected shape (ACC-004)."""
        document = parse_qa(_MINIMAL_DOC)

        self.assertIsInstance(document, QaDocument)
        self.assertEqual(document.frontmatter.id, "qa-001")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.body.text, "Simple Q&A Document")
        self.assertEqual(document.body.general.introduction.body[0].text, "Some intro text.")
        self.assertIn("Some raw requirements text.", document.body.general.raw_requirements.text)
        self.assertIsNone(document.body.functional_suitability.items)
        self.assertIsNone(document.body.safety.items)
        self.assertIsNone(document.body.more_information)

    def test_parses_full_reference_document(self) -> None:
        """The feature's own reference document round-trips through parse_qa (ACC-002/ACC-004)."""
        text = _REFERENCE_PATH.read_text(encoding="utf-8")

        document = parse_qa(text)

        self.assertEqual(document.frontmatter.id, "deaddead-feed-feed-feed-deaddeadfeed")
        self.assertEqual(document.frontmatter.status, "active")
        self.assertEqual(document.frontmatter.type, "qa")
        self.assertEqual(document.body.text, "Widget Registry Migration — Requirements Interview")

        # `Compatibility` was deliberately left empty (Phase 2's own choice) --
        # confirms the "category's items may be empty/absent" case end to end.
        self.assertIsNone(document.body.compatibility.items)

        # Every other category has at least one Q&A pair.
        self.assertEqual(len(document.body.functional_suitability.items), 2)
        self.assertEqual(len(document.body.performance_efficiency.items), 1)
        self.assertEqual(len(document.body.interaction_capability.items), 1)
        self.assertEqual(len(document.body.reliability.items), 1)
        self.assertEqual(len(document.body.security.items), 1)
        self.assertEqual(len(document.body.maintainability.items), 1)
        self.assertEqual(len(document.body.flexibility.items), 1)
        self.assertEqual(len(document.body.safety.items), 1)

        # The first `Functional Suitability` Q&A pair exercises all four
        # `QaSection` fields at once, including the `end_marker` scenario:
        # `requirement` must not swallow the immediately-following `question`
        # block quote (the concrete, end-to-end proof Phase 1's mechanism
        # actually works for `qa`).
        first = document.body.functional_suitability.items[0]
        self.assertIsNotNone(first.comment)
        self.assertIn("stakeholder workshop", first.comment.text)
        self.assertIsNotNone(first.requirement)
        self.assertIn("roll back a partially migrated widget", first.requirement.text)
        self.assertNotIn("Should the rollback also restore", first.requirement.text)
        self.assertIsNotNone(first.question)
        self.assertIn("Should the rollback also restore", first.question.text)
        self.assertIsNotNone(first.answer)
        self.assertIn("Losing listeners on failure is acceptable", first.answer.text)

        # The second `Functional Suitability` Q&A pair has no `comment`/`requirement`.
        second = document.body.functional_suitability.items[1]
        self.assertIsNone(second.comment)
        self.assertIsNone(second.requirement)
        self.assertIsNotNone(second.question)
        self.assertIsNotNone(second.answer)

        self.assertIsNotNone(document.body.more_information)

    def test_defaults_frontmatter_when_absent(self) -> None:
        """Omitting the frontmatter block entirely still parses, applying QaFrontmatter's defaults."""
        text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

        document = parse_qa(text)

        self.assertIsNone(document.frontmatter.id)
        self.assertEqual(document.frontmatter.type, "qa")
        self.assertEqual(document.frontmatter.status, "draft")

    def test_invalid_status_raises_validation_error(self) -> None:
        """A frontmatter `status` outside QaFrontmatter's closed set fails validation (ACC-004)."""
        text = _MINIMAL_DOC.replace("status: draft", "status: not-a-real-status")

        with self.assertRaises(ValidationError):
            parse_qa(text)

    def test_missing_general_section_raises_assertion_error(self) -> None:
        """A missing mandatory `## General` section is a structural failure (ACC-004)."""
        text = "# Simple Q&A Document\n\n" + _MINIMAL_CATEGORIES + "\n"

        with self.assertRaises(AssertionError):
            parse_qa(text)

    def test_missing_iso_characteristic_section_raises_assertion_error(self) -> None:
        """A missing mandatory ISO-characteristic H2 (e.g. `## Safety`) is a structural failure (ACC-004)."""
        categories_without_safety = "\n\n".join(
            f"## {heading}"
            for heading in (
                "Functional Suitability",
                "Performance Efficiency",
                "Compatibility",
                "Interaction Capability",
                "Reliability",
                "Security",
                "Maintainability",
                "Flexibility",
            )
        )
        text = textwrap.dedent(
            """\
            # Simple Q&A Document

            ## General

            ### Introduction

            Some intro text.

            ### Raw Requirements

            Some raw requirements text.

            {categories}
            """
        ).format(categories=categories_without_safety)

        with self.assertRaises(AssertionError):
            parse_qa(text)


if __name__ == "__main__":
    unittest.main()
