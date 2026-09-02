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

"""Tests for the ``validate_sysrs`` ``@mcp.tool()`` wrapper (Task 3.2)."""

from __future__ import annotations

import textwrap
import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.sysrs.tools.validate_sysrs import validate_sysrs

_GOL_ID = "0e15c5de-4ac9-4279-aa75-53249a3e43e4"
_REQ_ID = "a3f8c2d1-7b4e-4d9a-b6c0-91e5f2a8d734"

_MINIMAL_BODY = textwrap.dedent(
    f"""\
    # System Requirements Specification: Sample Document

    ## System Purpose

    Provision partner accounts.

    ## System Scope

    Onboarding only.

    ## Business Context and Goals

    ### Goals

    - GOL {_GOL_ID}: A goal

    ## System Overview

    ### System Context

    Context.

    ### System Functions

    Functions.

    ## Requirements

    ### Functional Suitability

    - REQ {_REQ_ID}: A requirement
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized System Requirements Specification sections.\n"

# Structurally valid, but a field/cross-field failure: a cross-reference
# bullet with the wrong type tag (`PRB` under `### Goals`, which only
# accepts `GOL`) -- the `Goals` after-validator's `ValidationError` channel.
_BAD_CROSS_REF_BODY = _MINIMAL_BODY.replace(f"- GOL {_GOL_ID}", f"- PRB {_GOL_ID}")

_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: sysrs-001
    type: sysrs
    version: 1.0.0
    status: draft
    created: '2026-08-31 00:00:00.000Z'
    updated: '2026-08-31 00:00:00.000Z'
    ---

    """
    )
    + _MINIMAL_BODY
)


class TestValidateSysrs(unittest.TestCase):
    """Tests for the validate_sysrs tool."""

    def test_returns_true_for_valid_body_only_content(self) -> None:
        """validate_sysrs(full=False) must return True for valid body-only content."""
        self.assertIs(validate_sysrs(_MINIMAL_BODY), True)

    def test_returns_true_for_valid_full_document(self) -> None:
        """validate_sysrs(full=True) must return True for a valid, complete document."""
        self.assertIs(validate_sysrs(_FULL_DOCUMENT, full=True), True)

    def test_raises_assertion_error_for_malformed_body(self) -> None:
        """A structurally invalid body-only content must raise AssertionError."""
        with self.assertRaises(AssertionError):
            validate_sysrs(_MALFORMED_BODY)

    def test_raises_validation_error_for_bad_field_value(self) -> None:
        """A field-level validation failure (wrong cross-reference type tag) must raise pydantic.ValidationError."""
        with self.assertRaises(ValidationError):
            validate_sysrs(_BAD_CROSS_REF_BODY)

    def test_raises_value_error_when_frontmatter_present_but_full_false(self) -> None:
        """full=False (default) must reject content carrying a frontmatter block."""
        with self.assertRaises(ValueError):
            validate_sysrs(_FULL_DOCUMENT)

    def test_raises_value_error_when_frontmatter_absent_but_full_true(self) -> None:
        """full=True must reject content with no frontmatter block."""
        with self.assertRaises(ValueError):
            validate_sysrs(_MINIMAL_BODY, full=True)

    def test_raises_validation_error_for_invalid_frontmatter_when_full(self) -> None:
        """full=True must let a frontmatter validation failure propagate (`accepted` is not a sysrs status)."""
        text = _FULL_DOCUMENT.replace("status: draft", "status: accepted")
        with self.assertRaises(ValidationError):
            validate_sysrs(text, full=True)


if __name__ == "__main__":
    unittest.main()
