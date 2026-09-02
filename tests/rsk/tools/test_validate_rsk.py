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

"""Tests for the ``validate_rsk`` ``@mcp.tool()`` wrapper (Task 3.7)."""

from __future__ import annotations

import textwrap
import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.rsk.tools.validate_rsk import validate_rsk

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Sample Risk

    ## Cause

    A root condition.

    ## Trigger

    An event that sets the risk in motion.

    ## Consequence

    A bounded consequence.

    ## Scope

    - Sample subsystem

    ## Initial Assessment

    ### Probability 4

    ### Impact 3

    ## Strategy

    reduce

    ## Mitigation

    Sample treatment measures.

    ## Residual Assessment

    ### Probability 2

    ### Impact 3
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized risk sections.\n"

_ZERO_SCOPE_BODY = _MINIMAL_BODY.replace("- Sample subsystem\n", "")

_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: rsk-001
    type: rsk
    version: 1.0.0
    status: open
    created: '2026-08-24 00:00:00.000Z'
    updated: '2026-08-24 00:00:00.000Z'
    ---

    """
    )
    + _MINIMAL_BODY
)


class TestValidateRsk(unittest.TestCase):
    """Tests for the validate_rsk tool."""

    def test_returns_true_for_valid_body_only_content(self) -> None:
        """validate_rsk(full=False) must return True for valid body-only content."""
        self.assertIs(validate_rsk(_MINIMAL_BODY), True)

    def test_returns_true_for_valid_full_document(self) -> None:
        """validate_rsk(full=True) must return True for a valid, complete document."""
        self.assertIs(validate_rsk(_FULL_DOCUMENT, full=True), True)

    def test_raises_assertion_error_for_malformed_body(self) -> None:
        """A structurally invalid body-only content must raise AssertionError."""
        with self.assertRaises(AssertionError):
            validate_rsk(_MALFORMED_BODY)

    def test_raises_value_error_when_frontmatter_present_but_full_false(self) -> None:
        """full=False (default) must reject content carrying a frontmatter block."""
        with self.assertRaises(ValueError):
            validate_rsk(_FULL_DOCUMENT)

    def test_raises_value_error_when_frontmatter_absent_but_full_true(self) -> None:
        """full=True must reject content with no frontmatter block."""
        with self.assertRaises(ValueError):
            validate_rsk(_MINIMAL_BODY, full=True)

    def test_raises_validation_error_for_invalid_frontmatter_when_full(self) -> None:
        """full=True must let a frontmatter validation failure propagate."""
        text = _FULL_DOCUMENT.replace("status: open", "status: not-a-real-status")
        with self.assertRaises(ValidationError):
            validate_rsk(text, full=True)

    def test_raises_assertion_error_for_zero_scope_entries(self) -> None:
        """A body whose `## Scope` section has zero list entries must raise AssertionError."""
        with self.assertRaises(AssertionError):
            validate_rsk(_ZERO_SCOPE_BODY)


if __name__ == "__main__":
    unittest.main()
