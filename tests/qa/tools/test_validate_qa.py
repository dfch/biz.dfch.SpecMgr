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

"""Tests for the ``validate_qa`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import textwrap
import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.qa.tools.validate_qa import validate_qa

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Some QA Title

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    ## Elicitation Context

    ## Functional Suitability

    ## Performance Efficiency

    ## Compatibility

    ## Interaction Capability

    ## Reliability

    ## Security

    ## Maintainability

    ## Flexibility

    ## Safety
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized QA sections.\n"

_V1_SHAPED_BODY = textwrap.dedent(
    """\
    # Some QA Title

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    ## Functional Suitability

    ### What must happen?

    > Is this acceptable?

    Yes, it is acceptable.

    ## Performance Efficiency

    ## Compatibility

    ## Interaction Capability

    ## Reliability

    ## Security

    ## Maintainability

    ## Flexibility

    ## Safety
    """
)

_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: qa-001
    type: qa
    version: 1.0.0
    status: draft
    created: '2026-08-18 00:00:00.000Z'
    updated: '2026-08-18 00:00:00.000Z'
    ---

    """
    )
    + _MINIMAL_BODY
)


class TestValidateQa(unittest.TestCase):
    """Tests for the validate_qa tool."""

    def test_returns_true_for_valid_body_only_content(self) -> None:
        """validate_qa(full=False) must return True for valid body-only content."""
        self.assertIs(validate_qa(_MINIMAL_BODY), True)

    def test_returns_true_for_valid_full_document(self) -> None:
        """validate_qa(full=True) must return True for a valid, complete document."""
        self.assertIs(validate_qa(_FULL_DOCUMENT, full=True), True)

    def test_raises_assertion_error_for_malformed_body(self) -> None:
        """A structurally invalid body-only content must raise AssertionError."""
        with self.assertRaises(AssertionError):
            validate_qa(_MALFORMED_BODY)

    def test_raises_value_error_when_frontmatter_present_but_full_false(self) -> None:
        """full=False (default) must reject content carrying a frontmatter block."""
        with self.assertRaises(ValueError):
            validate_qa(_FULL_DOCUMENT)

    def test_raises_value_error_when_frontmatter_absent_but_full_true(self) -> None:
        """full=True must reject content with no frontmatter block."""
        with self.assertRaises(ValueError):
            validate_qa(_MINIMAL_BODY, full=True)

    def test_raises_validation_error_for_invalid_frontmatter_when_full(self) -> None:
        """full=True must let a frontmatter validation failure propagate."""
        text = _FULL_DOCUMENT.replace("status: draft", "status: not-a-real-status")
        with self.assertRaises(ValidationError):
            validate_qa(text, full=True)

    def test_raises_structural_error_for_v1_shaped_body_only_content(self) -> None:
        """A v1-shaped body (per-question `### {heading}` sub-sections, no
        `## Elicitation Context`) must fail with the same structural
        `AssertionError` that `Qa.from_text` raises on its own -- no version
        gate, no silent fallback to v1 parsing (ACC-005, REQ-004 revised
        2026-08-23).
        """
        with self.assertRaises(AssertionError):
            validate_qa(_V1_SHAPED_BODY)

    def test_raises_structural_error_for_v1_shaped_full_document(self) -> None:
        """Same as above, but for a complete v1-shaped document (frontmatter +
        body) via `full=True`, exercising `qa.models.v2.parser.parse_qa`.
        """
        full_v1_document = (
            textwrap.dedent(
                """\
            ---
            id: qa-001
            type: qa
            version: 1.0.0
            status: draft
            created: '2026-08-18 00:00:00.000Z'
            updated: '2026-08-18 00:00:00.000Z'
            ---

            """
            )
            + _V1_SHAPED_BODY
        )
        with self.assertRaises(AssertionError):
            validate_qa(full_v1_document, full=True)


if __name__ == "__main__":
    unittest.main()
