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

"""Tests for the ``validate_feat`` ``@mcp.tool()`` wrapper (Task 2.3)."""

from __future__ import annotations

import textwrap
import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.feat.tools.validate_feat import validate_feat

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Feature: Example Widget

    ## Plan

    ### Overview

    Short description.

    ### Requirements

    - REQ-001: The widget must render within 200ms.

    ### Acceptance Criteria

    - [ ] ACC-001: Render time stays below 200ms.

    ### Scope

    #### Included

    - The widget component itself.

    #### Explicitly Out Of Scope

    - Mobile touch gestures.

    ### Task List

    #### Phase 0: Scaffolding

    - [x] Task 0.1: Create branch and package skeleton

    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z - Paused for review

    Free-form prose describing what happened in this update.
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized feature sections.\n"

# Structurally valid, but a field/cross-field failure (malformed ACC item).
_BAD_ACC_BODY = _MINIMAL_BODY.replace(
    "- [ ] ACC-001: Render time stays below 200ms.",
    "- [ ] Not a valid ACC item at all.",
)

_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: feat-1-example-widget
    type: feat
    version: 1.0.0
    status: planning
    created: 2026-08-30
    updated: 2026-08-30
    ---

    """
    )
    + _MINIMAL_BODY
)


class TestValidateFeat(unittest.TestCase):
    """Tests for the validate_feat tool."""

    def test_returns_true_for_valid_body_only_content(self) -> None:
        """validate_feat(full=False) must return True for valid body-only content."""
        self.assertIs(validate_feat(_MINIMAL_BODY), True)

    def test_returns_true_for_valid_full_document(self) -> None:
        """validate_feat(full=True) must return True for a valid, complete document."""
        self.assertIs(validate_feat(_FULL_DOCUMENT, full=True), True)

    def test_raises_assertion_error_for_malformed_body(self) -> None:
        """A structurally invalid body-only content must raise AssertionError."""
        with self.assertRaises(AssertionError):
            validate_feat(_MALFORMED_BODY)

    def test_raises_validation_error_for_bad_field_value(self) -> None:
        """A field-level validation failure (malformed ACC item) must raise pydantic.ValidationError."""
        with self.assertRaises(ValidationError):
            validate_feat(_BAD_ACC_BODY)

    def test_raises_value_error_when_frontmatter_present_but_full_false(self) -> None:
        """full=False (default) must reject content carrying a frontmatter block."""
        with self.assertRaises(ValueError):
            validate_feat(_FULL_DOCUMENT)

    def test_raises_value_error_when_frontmatter_absent_but_full_true(self) -> None:
        """full=True must reject content with no frontmatter block."""
        with self.assertRaises(ValueError):
            validate_feat(_MINIMAL_BODY, full=True)

    def test_raises_validation_error_for_invalid_frontmatter_when_full(self) -> None:
        """full=True must let a frontmatter validation failure propagate."""
        text = _FULL_DOCUMENT.replace("status: planning", "status: in-progress")
        with self.assertRaises(ValidationError):
            validate_feat(text, full=True)


if __name__ == "__main__":
    unittest.main()
