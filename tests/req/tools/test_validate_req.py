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

"""Tests for the ``validate_req`` ``@mcp.tool()`` wrapper (Task 3.16)."""

from __future__ import annotations

import textwrap
import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.req.tools.validate_req import validate_req

_MINIMAL_BODY = textwrap.dedent(
    """\
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

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized requirement sections.\n"

_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: req-001
    type: req
    version: 1.0.0
    status: draft
    created: 2026-08-05
    updated: 2026-08-05
    ---

    """
    )
    + _MINIMAL_BODY
)


class TestValidateReq(unittest.TestCase):
    """Tests for the validate_req tool."""

    def test_returns_true_for_valid_body_only_content(self) -> None:
        """validate_req(full=False) must return True for valid body-only content."""
        self.assertIs(validate_req(_MINIMAL_BODY), True)

    def test_returns_true_for_valid_full_document(self) -> None:
        """validate_req(full=True) must return True for a valid, complete document."""
        self.assertIs(validate_req(_FULL_DOCUMENT, full=True), True)

    def test_raises_assertion_error_for_malformed_body(self) -> None:
        """A structurally invalid body-only content must raise AssertionError."""
        with self.assertRaises(AssertionError):
            validate_req(_MALFORMED_BODY)

    def test_raises_validation_error_for_bad_field_value(self) -> None:
        """A field-level validation failure must raise pydantic.ValidationError."""
        text = _MINIMAL_BODY.replace("MUST", "NOT-A-VALID-LEVEL")
        with self.assertRaises(ValidationError):
            validate_req(text)

    def test_raises_value_error_when_frontmatter_present_but_full_false(self) -> None:
        """full=False (default) must reject content carrying a frontmatter block."""
        with self.assertRaises(ValueError):
            validate_req(_FULL_DOCUMENT)

    def test_raises_value_error_when_frontmatter_absent_but_full_true(self) -> None:
        """full=True must reject content with no frontmatter block."""
        with self.assertRaises(ValueError):
            validate_req(_MINIMAL_BODY, full=True)

    def test_raises_validation_error_for_invalid_frontmatter_when_full(self) -> None:
        """full=True must let a frontmatter validation failure propagate."""
        text = _FULL_DOCUMENT.replace("status: draft", "status: not-a-real-status")
        with self.assertRaises(ValidationError):
            validate_req(text, full=True)


if __name__ == "__main__":
    unittest.main()
