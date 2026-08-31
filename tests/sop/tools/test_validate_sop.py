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

"""Tests for the ``validate_sop`` ``@mcp.tool()`` wrapper (Task 2.2)."""

from __future__ import annotations

import textwrap
import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.sop.tools.validate_sop import validate_sop

_MINIMAL_BODY = textwrap.dedent(
    """\
    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for new hires.

    ## Procedure

    ### Step 1: Submit request

    HR submits the request.
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized SOP sections.\n"

# Structurally valid, but a field/cross-field failure: two `### Step 1:`
# headings are duplicate step numbers (the `Sop` after-validator's
# `ValidationError` channel).
_BAD_STEP_BODY = textwrap.dedent(
    """\
    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for new hires.

    ## Procedure

    ### Step 1: Submit request

    HR submits the request.

    ### Step 1: Duplicate step

    HR submits the request again.
    """
)

_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: sop-001
    type: sop
    version: 1.0.0
    status: draft
    created: 2026-08-30
    updated: 2026-08-30
    ---

    """
    )
    + _MINIMAL_BODY
)


class TestValidateSop(unittest.TestCase):
    """Tests for the validate_sop tool."""

    def test_returns_true_for_valid_body_only_content(self) -> None:
        """validate_sop(full=False) must return True for valid body-only content."""
        self.assertIs(validate_sop(_MINIMAL_BODY), True)

    def test_returns_true_for_valid_full_document(self) -> None:
        """validate_sop(full=True) must return True for a valid, complete document."""
        self.assertIs(validate_sop(_FULL_DOCUMENT, full=True), True)

    def test_raises_assertion_error_for_malformed_body(self) -> None:
        """A structurally invalid body-only content must raise AssertionError."""
        with self.assertRaises(AssertionError):
            validate_sop(_MALFORMED_BODY)

    def test_raises_validation_error_for_bad_field_value(self) -> None:
        """A field-level validation failure (duplicate `### Step 1` number) must raise pydantic.ValidationError."""
        with self.assertRaises(ValidationError):
            validate_sop(_BAD_STEP_BODY)

    def test_raises_value_error_when_frontmatter_present_but_full_false(self) -> None:
        """full=False (default) must reject content carrying a frontmatter block."""
        with self.assertRaises(ValueError):
            validate_sop(_FULL_DOCUMENT)

    def test_raises_value_error_when_frontmatter_absent_but_full_true(self) -> None:
        """full=True must reject content with no frontmatter block."""
        with self.assertRaises(ValueError):
            validate_sop(_MINIMAL_BODY, full=True)

    def test_raises_validation_error_for_invalid_frontmatter_when_full(self) -> None:
        """full=True must let a frontmatter validation failure propagate (`implemented` is GOL's, not SOP's)."""
        text = _FULL_DOCUMENT.replace("status: draft", "status: implemented")
        with self.assertRaises(ValidationError):
            validate_sop(text, full=True)


if __name__ == "__main__":
    unittest.main()
