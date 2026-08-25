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

"""Tests for :func:`parse_prb`: the `PrbDocument`-level `from_text` entry point."""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.prb.models.v1 import PrbDocument
from biz.dfch.specmgr.prb.models.v1.parser import parse_prb

_REFERENCE_PATH = (
    Path(__file__).resolve().parents[4] / ".specmgr" / "feat" / "feat-16-problem-statement" / "prb_reference.md"
)

_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: prb-001
    type: prb
    version: 1.0.0
    status: draft
    created: 2026-08-25
    updated: 2026-08-25
    ---

    # Simple Problem Statement

    ## Current State

    ### Summary

    A short placeholder summary.

    ## Gap

    Some gap text.

    ## Future State

    Some future state text.
    """
)


class TestParsePrb(unittest.TestCase):
    """Tests for `parse_prb`."""

    def test_parses_minimal_document(self) -> None:
        """A minimal, valid document parses into a PrbDocument with the expected shape."""
        document = parse_prb(_MINIMAL_DOC)

        self.assertIsInstance(document, PrbDocument)
        self.assertEqual(document.frontmatter.id, "prb-001")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.body.text, "Simple Problem Statement")
        self.assertIsNone(document.body.comment)
        self.assertIn("A short placeholder summary.", document.body.current_state.summary.text)
        self.assertIsNone(document.body.current_state.question_1)
        self.assertIn("Some gap text.", document.body.gap.text)
        self.assertIsNone(document.body.impact)
        self.assertIn("Some future state text.", document.body.future_state.text)
        self.assertIsNone(document.body.references)
        self.assertIsNone(document.body.more_information)

    def test_parses_full_reference_document(self) -> None:
        """The feature's own reference document round-trips through parse_prb."""
        text = _REFERENCE_PATH.read_text(encoding="utf-8")

        document = parse_prb(text)

        self.assertEqual(document.frontmatter.id, "deaddead-cafe-cafe-cafe-deaddeadcafe")
        self.assertEqual(document.frontmatter.status, "active")
        self.assertEqual(document.body.text, "Widget Registry Migration Rollback Failures")
        self.assertIsNotNone(document.body.comment)
        cs = document.body.current_state
        self.assertIsNotNone(cs.summary)
        self.assertIsNotNone(cs.question_1)
        self.assertIsNotNone(cs.question_2)
        self.assertIsNotNone(cs.question_3)
        self.assertIsNotNone(cs.question_4)
        self.assertIsNotNone(cs.question_5)
        self.assertIsNotNone(cs.question_6)
        self.assertIsNotNone(cs.question_7)
        self.assertIn("The migration tool currently completes a partial migration", document.body.gap.text)
        self.assertIsNotNone(document.body.impact)
        self.assertIn("Each incident costs the on-call engineer", document.body.impact.text)
        self.assertIn("The migration tool automatically rolls back a widget", document.body.future_state.text)
        self.assertIsNotNone(document.body.references)
        self.assertIn("Migrate Widgets to the New Registry", document.body.references.text)
        self.assertIsNotNone(document.body.more_information)
        self.assertIn("This problem statement was drafted", document.body.more_information.text)

    def test_defaults_frontmatter_when_absent(self) -> None:
        """Omitting the frontmatter block entirely still parses, applying PrbFrontmatter's defaults."""
        text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

        document = parse_prb(text)

        self.assertIsNone(document.frontmatter.id)
        self.assertEqual(document.frontmatter.type, "prb")
        self.assertEqual(document.frontmatter.status, "draft")

    def test_invalid_status_raises_validation_error(self) -> None:
        """A frontmatter `status` outside PrbFrontmatter's closed set fails validation."""
        text = _MINIMAL_DOC.replace("status: draft", "status: not-a-real-status")

        with self.assertRaises(ValidationError):
            parse_prb(text)

    def test_missing_gap_section_raises_assertion_error(self) -> None:
        """A missing mandatory `## Gap` section is a structural failure."""
        text = textwrap.dedent(
            """\
            # Simple Problem Statement

            ## Current State

            ### Summary

            A short placeholder summary.

            ## Future State

            Some future state text.
            """
        )

        with self.assertRaises(AssertionError):
            parse_prb(text)

    def test_missing_future_state_section_raises_assertion_error(self) -> None:
        """A missing mandatory `## Future State` section is a structural failure."""
        text = textwrap.dedent(
            """\
            # Simple Problem Statement

            ## Current State

            ### Summary

            A short placeholder summary.

            ## Gap

            Some gap text.
            """
        )

        with self.assertRaises(AssertionError):
            parse_prb(text)

    def test_missing_current_state_section_raises_assertion_error(self) -> None:
        """A missing mandatory `## Current State` section is a structural failure."""
        text = textwrap.dedent(
            """\
            # Simple Problem Statement

            ## Gap

            Some gap text.

            ## Future State

            Some future state text.
            """
        )

        with self.assertRaises(AssertionError):
            parse_prb(text)

    def test_missing_summary_raises_assertion_error(self) -> None:
        """A `## Current State` section present but missing the mandatory `### Summary` is a structural failure."""
        text = textwrap.dedent(
            """\
            # Simple Problem Statement

            ## Current State

            ### What Is the Problem?

            Some answer.

            ## Gap

            Some gap text.

            ## Future State

            Some future state text.
            """
        )

        with self.assertRaises(AssertionError):
            parse_prb(text)

    def test_invalid_field_raises_validation_error_not_assertion_error(self) -> None:
        """A structurally-sound document with an invalid frontmatter field raises `ValidationError`, not `AssertionError`."""
        text = _MINIMAL_DOC.replace("type: prb", "type: not-prb")

        with self.assertRaises(ValidationError):
            parse_prb(text)


if __name__ == "__main__":
    unittest.main()
