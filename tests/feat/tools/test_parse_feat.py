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

"""Tests for the ``parse_feat`` ``@mcp.tool()`` wrapper (Task 2.3)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.feat.models.v1 import FeatDocument
from biz.dfch.specmgr.feat.tools.parse_feat import parse_feat

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: feat-1-example-widget
    type: feat
    status: planning
    ---

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


class TestParseFeatTool(unittest.TestCase):
    """Tests for the parse_feat tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_feat must return the parsed, validated FeatDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "README.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_feat(str(path))

            self.assertIsInstance(result, FeatDocument)
            self.assertEqual(result.frontmatter.id, "feat-1-example-widget")
            self.assertEqual(result.body.text, "Feature: Example Widget")

    def test_does_not_check_folder_name_against_frontmatter_id(self) -> None:
        """Unlike load_by_id/find_feat_path_by_id, parse_feat never checks id against the containing folder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "some-other-folder-name" / "README.md"
            path.parent.mkdir()
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_feat(str(path))

            self.assertEqual(result.frontmatter.id, "feat-1-example-widget")

    def test_raises_for_invalid_frontmatter(self) -> None:
        """parse_feat must let a frontmatter validation failure propagate."""
        text = _VALID_DOC.replace("status: planning", "status: in-progress")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "README.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(ValidationError):
                parse_feat(str(path))

    def test_raises_for_malformed_structure(self) -> None:
        """parse_feat must let a structural parse failure propagate."""
        text = "# Title\n\nJust a paragraph, no recognized feature sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "README.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(AssertionError):
                parse_feat(str(path))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_feat must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_feat("/nonexistent/path/to/README.md")


if __name__ == "__main__":
    unittest.main()
