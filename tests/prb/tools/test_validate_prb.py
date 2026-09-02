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

"""Tests for the ``validate_prb`` ``@mcp.tool()`` wrapper (Task 3.7)."""

from __future__ import annotations

import textwrap
import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.prb.tools.validate_prb import validate_prb

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Simple Problem Statement

    ## Current State

    ### Summary

    Something is wrong.

    ## Gap

    There is a gap.

    ## Future State

    It will be fixed.
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized problem statement sections.\n"

_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: prb-001
    type: prb
    version: 1.0.0
    status: draft
    created: '2026-08-25 00:00:00.000Z'
    updated: '2026-08-25 00:00:00.000Z'
    ---

    """
    )
    + _MINIMAL_BODY
)


class TestValidatePrb(unittest.TestCase):
    """Tests for the validate_prb tool."""

    def test_returns_true_for_valid_body_only_content(self) -> None:
        """validate_prb(full=False) must return True for valid body-only content."""
        self.assertIs(validate_prb(_MINIMAL_BODY), True)

    def test_returns_true_for_valid_full_document(self) -> None:
        """validate_prb(full=True) must return True for a valid, complete document."""
        self.assertIs(validate_prb(_FULL_DOCUMENT, full=True), True)

    def test_raises_assertion_error_for_malformed_body(self) -> None:
        """A structurally invalid body-only content must raise AssertionError."""
        with self.assertRaises(AssertionError):
            validate_prb(_MALFORMED_BODY)

    def test_raises_value_error_when_frontmatter_present_but_full_false(self) -> None:
        """full=False (default) must reject content carrying a frontmatter block."""
        with self.assertRaises(ValueError):
            validate_prb(_FULL_DOCUMENT)

    def test_raises_value_error_when_frontmatter_absent_but_full_true(self) -> None:
        """full=True must reject content with no frontmatter block."""
        with self.assertRaises(ValueError):
            validate_prb(_MINIMAL_BODY, full=True)

    def test_raises_validation_error_for_invalid_frontmatter_when_full(self) -> None:
        """full=True must let a frontmatter validation failure propagate."""
        text = _FULL_DOCUMENT.replace("status: draft", "status: not-a-real-status")
        with self.assertRaises(ValidationError):
            validate_prb(text, full=True)

    def test_raises_assertion_error_for_missing_mandatory_section(self) -> None:
        """A body missing the mandatory `## Future State` section must raise AssertionError."""
        text = (
            "# Simple Problem Statement\n\n## Current State\n\n### Summary\n\nSomething is wrong.\n\n## Gap\n\nA gap.\n"
        )
        with self.assertRaises(AssertionError):
            validate_prb(text)


if __name__ == "__main__":
    unittest.main()
