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

"""Tests for :func:`parse_uc` (Task 1.8): the `UcDocument`-level `from_text` entry point."""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models.v2 import UcDocument
from biz.dfch.specmgr.uc.models.v2.parser import parse_uc

_REFERENCE_PATH = (
    Path(__file__).resolve().parents[4] / ".specmgr" / "feat" / "feat-4-use-cases" / "v2" / "uc_reference.md"
)

_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: uc-001
    type: uc
    version: 1.0.0
    status: draft
    created: '2026-08-05 00:00:00.000Z'
    updated: '2026-08-05 00:00:00.000Z'
    ---

    # Buy Goods

    ## Characteristic Information

    ### Goal in Context

    Buyer issues request.

    ### Scope

    Company.

    ### Level

    Summary

    ### Preconditions

    - We know Buyer

    ### Success End Condition

    - Buyer has goods

    ### Primary Actor

    Buyer.

    ### Trigger

    Purchase request comes in.

    ## Main Success Scenario

    1. Buyer calls in with a purchase request.
    2. Company creates order in system.
    """
)


class TestParseUc(unittest.TestCase):
    """Tests for `parse_uc`."""

    def test_parses_minimal_document(self) -> None:
        """A minimal, valid document parses into a UcDocument with the expected shape."""
        document = parse_uc(_MINIMAL_DOC)

        self.assertIsInstance(document, UcDocument)
        self.assertEqual(document.frontmatter.id, "uc-001")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.body.text, "Buy Goods")
        self.assertEqual(len(document.body.main_success_scenario.steps), 2)

    def test_parses_full_reference_document(self) -> None:
        """The feature's own reference document round-trips through parse_uc."""
        text = _REFERENCE_PATH.read_text(encoding="utf-8")

        document = parse_uc(text)

        self.assertEqual(document.frontmatter.id, "uc-001")
        self.assertEqual(document.body.text, "Buy Goods")
        self.assertEqual(len(document.body.main_success_scenario.steps), 11)
        self.assertIsNotNone(document.body.extensions)
        self.assertEqual(len(document.body.extensions.extensions), 8)
        self.assertIsNotNone(document.body.sub_variations)
        self.assertEqual(len(document.body.sub_variations.sub_variations), 4)

    def test_defaults_frontmatter_when_absent(self) -> None:
        """Omitting the frontmatter block entirely still parses, applying UcFrontmatter's defaults."""
        text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

        document = parse_uc(text)

        self.assertIsNone(document.frontmatter.id)
        self.assertEqual(document.frontmatter.type, "uc")
        self.assertEqual(document.frontmatter.status, "draft")

    def test_invalid_status_raises_validation_error(self) -> None:
        """A frontmatter `status` outside UcFrontmatter's closed set fails validation."""
        text = _MINIMAL_DOC.replace("status: draft", "status: not-a-real-status")

        with self.assertRaises(ValidationError):
            parse_uc(text)

    def test_unresolvable_extension_reference_raises_validation_error(self) -> None:
        """A structurally well-formed document with an invalid cross-reference still fails."""
        text = _MINIMAL_DOC + textwrap.dedent(
            """
            ## Extensions

            ### Extension 5a. Step 5 does not exist

            1. Company cancels the order.
            """
        )

        with self.assertRaises(ValidationError):
            parse_uc(text)

    def test_malformed_structure_raises_assertion_error(self) -> None:
        """A missing mandatory section (no Main Success Scenario) is a structural failure."""
        text = textwrap.dedent(
            """\
            # Buy Goods

            ## Characteristic Information

            ### Goal in Context

            Buyer issues request.

            ### Scope

            Company.

            ### Level

            Summary

            ### Preconditions

            - We know Buyer

            ### Success End Condition

            - Buyer has goods

            ### Primary Actor

            Buyer.

            ### Trigger

            Purchase request comes in.
            """
        )

        with self.assertRaises(AssertionError):
            parse_uc(text)


if __name__ == "__main__":
    unittest.main()
