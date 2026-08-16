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

"""Tests for the ``validate_tsk`` ``@mcp.tool()`` wrapper (Task 3.7)."""

from __future__ import annotations

import textwrap
import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.tsk.tools.validate_tsk import validate_tsk

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [ ] Do the first thing

    ## Recent Updates

    ### Kickoff

    Started the task list.
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized task list sections.\n"

_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: tsk-001
    type: tsk
    version: 1.0.0
    status: draft
    created: 2026-08-16
    updated: 2026-08-16
    ---

    """
    )
    + _MINIMAL_BODY
)


class TestValidateTsk(unittest.TestCase):
    """Tests for the validate_tsk tool."""

    def test_returns_true_for_valid_body_only_content(self) -> None:
        """validate_tsk(full=False) must return True for valid body-only content."""
        self.assertIs(validate_tsk(_MINIMAL_BODY), True)

    def test_returns_true_for_valid_full_document(self) -> None:
        """validate_tsk(full=True) must return True for a valid, complete document."""
        self.assertIs(validate_tsk(_FULL_DOCUMENT, full=True), True)

    def test_raises_assertion_error_for_malformed_body(self) -> None:
        """A structurally invalid body-only content must raise AssertionError."""
        with self.assertRaises(AssertionError):
            validate_tsk(_MALFORMED_BODY)

    def test_raises_value_error_when_frontmatter_present_but_full_false(self) -> None:
        """full=False (default) must reject content carrying a frontmatter block."""
        with self.assertRaises(ValueError):
            validate_tsk(_FULL_DOCUMENT)

    def test_raises_value_error_when_frontmatter_absent_but_full_true(self) -> None:
        """full=True must reject content with no frontmatter block."""
        with self.assertRaises(ValueError):
            validate_tsk(_MINIMAL_BODY, full=True)

    def test_raises_validation_error_for_invalid_frontmatter_when_full(self) -> None:
        """full=True must let a frontmatter validation failure propagate."""
        text = _FULL_DOCUMENT.replace("status: draft", "status: not-a-real-status")
        with self.assertRaises(ValidationError):
            validate_tsk(text, full=True)

    def test_raises_assertion_error_for_zero_recent_updates_entries(self) -> None:
        """A body with no `## Recent Updates` section at all must raise AssertionError."""
        text = "# Simple Task List\n\n- [ ] Do the first thing\n"
        with self.assertRaises(AssertionError):
            validate_tsk(text)


if __name__ == "__main__":
    unittest.main()
