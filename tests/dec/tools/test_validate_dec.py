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

"""Tests for the ``validate_dec`` ``@mcp.tool()`` wrapper (Task 2.2)."""

from __future__ import annotations

import textwrap
import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.dec.tools.validate_dec import validate_dec

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Outcome

    We chose the document store.
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized decision sections.\n"

# Structurally valid, but a field/cross-field failure: two `### Option 1:`
# headings are duplicate option numbers (the `Decision` after-validator's
# `ValidationError` channel).
_BAD_OPTION_BODY = textwrap.dedent(
    """\
    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Outcome

    We chose the document store.

    ## Pros and Cons

    ### Option 1: Document Store

    Meets the latency budget.

    ### Option 1: Key-Value Store

    Even faster reads.
    """
)

_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: dec-001
    type: dec
    version: 1.0.0
    status: draft
    created: 2026-08-26
    updated: 2026-08-26
    ---

    """
    )
    + _MINIMAL_BODY
)


class TestValidateDec(unittest.TestCase):
    """Tests for the validate_dec tool."""

    def test_returns_true_for_valid_body_only_content(self) -> None:
        """validate_dec(full=False) must return True for valid body-only content."""
        self.assertIs(validate_dec(_MINIMAL_BODY), True)

    def test_returns_true_for_valid_full_document(self) -> None:
        """validate_dec(full=True) must return True for a valid, complete document."""
        self.assertIs(validate_dec(_FULL_DOCUMENT, full=True), True)

    def test_raises_assertion_error_for_malformed_body(self) -> None:
        """A structurally invalid body-only content must raise AssertionError."""
        with self.assertRaises(AssertionError):
            validate_dec(_MALFORMED_BODY)

    def test_raises_validation_error_for_bad_field_value(self) -> None:
        """A field-level validation failure (duplicate `### Option 1:` number) must raise pydantic.ValidationError."""
        with self.assertRaises(ValidationError):
            validate_dec(_BAD_OPTION_BODY)

    def test_raises_value_error_when_frontmatter_present_but_full_false(self) -> None:
        """full=False (default) must reject content carrying a frontmatter block."""
        with self.assertRaises(ValueError):
            validate_dec(_FULL_DOCUMENT)

    def test_raises_value_error_when_frontmatter_absent_but_full_true(self) -> None:
        """full=True must reject content with no frontmatter block."""
        with self.assertRaises(ValueError):
            validate_dec(_MINIMAL_BODY, full=True)

    def test_raises_validation_error_for_invalid_frontmatter_when_full(self) -> None:
        """full=True must let a frontmatter validation failure propagate (`implemented` is GOL's, not DEC's)."""
        text = _FULL_DOCUMENT.replace("status: draft", "status: implemented")
        with self.assertRaises(ValidationError):
            validate_dec(text, full=True)


if __name__ == "__main__":
    unittest.main()
