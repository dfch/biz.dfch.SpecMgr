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

"""Tests for the ``validate_vcr`` ``@mcp.tool()`` wrapper (Task 2.1)."""

from __future__ import annotations

import textwrap
import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.vcr.tools.validate_vcr import validate_vcr

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Sample Verification Case

    ## Verifies

    REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Sample requirement title

    Confirms that the sample requirement is met.

    ## Coverage

    partial

    ## Acceptance Criteria

    ### AC-001 (Test): The sample criterion passes
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized verification case record sections.\n"

# Structurally valid, but a field/cross-field failure: two `### AC-001`
# headings are duplicate AC numbers (the `Vcr` after-validator's
# `ValidationError` channel).
_BAD_AC_BODY = textwrap.dedent(
    """\
    # Sample Verification Case

    ## Verifies

    REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Sample requirement title

    Confirms that the sample requirement is met.

    ## Coverage

    partial

    ## Acceptance Criteria

    ### AC-001 (Test): The sample criterion passes

    ### AC-001 (Analysis): Duplicate AC number
    """
)

_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: vcr-001
    type: vcr
    version: 1.0.0
    status: draft
    created: '2026-08-31 00:00:00.000Z'
    updated: '2026-08-31 00:00:00.000Z'
    ---

    """
    )
    + _MINIMAL_BODY
)


class TestValidateVcr(unittest.TestCase):
    """Tests for the validate_vcr tool."""

    def test_returns_true_for_valid_body_only_content(self) -> None:
        """validate_vcr(full=False) must return True for valid body-only content."""
        self.assertIs(validate_vcr(_MINIMAL_BODY), True)

    def test_returns_true_for_valid_full_document(self) -> None:
        """validate_vcr(full=True) must return True for a valid, complete document."""
        self.assertIs(validate_vcr(_FULL_DOCUMENT, full=True), True)

    def test_raises_assertion_error_for_malformed_body(self) -> None:
        """A structurally invalid body-only content must raise AssertionError."""
        with self.assertRaises(AssertionError):
            validate_vcr(_MALFORMED_BODY)

    def test_raises_validation_error_for_bad_field_value(self) -> None:
        """A field-level validation failure (duplicate `### AC-001` number) must raise pydantic.ValidationError."""
        with self.assertRaises(ValidationError):
            validate_vcr(_BAD_AC_BODY)

    def test_raises_value_error_when_frontmatter_present_but_full_false(self) -> None:
        """full=False (default) must reject content carrying a frontmatter block."""
        with self.assertRaises(ValueError):
            validate_vcr(_FULL_DOCUMENT)

    def test_raises_value_error_when_frontmatter_absent_but_full_true(self) -> None:
        """full=True must reject content with no frontmatter block."""
        with self.assertRaises(ValueError):
            validate_vcr(_MINIMAL_BODY, full=True)

    def test_raises_validation_error_for_invalid_frontmatter_when_full(self) -> None:
        """full=True must let a frontmatter validation failure propagate (`accepted` is DEC's, not VCR's)."""
        text = _FULL_DOCUMENT.replace("status: draft", "status: accepted")
        with self.assertRaises(ValidationError):
            validate_vcr(text, full=True)


if __name__ == "__main__":
    unittest.main()
