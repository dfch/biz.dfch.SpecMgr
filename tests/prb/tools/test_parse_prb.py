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

"""Tests for the ``parse_prb`` ``@mcp.tool()`` wrapper (Task 3.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.prb.models.v1 import PrbDocument
from biz.dfch.specmgr.prb.tools.parse_prb import parse_prb

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: prb-001
    type: prb
    status: draft
    ---

    # Simple Problem Statement

    ## Current State

    ### Summary

    Something is wrong.

    ### What Is the Problem?

    Widgets are missing.

    ## Gap

    There is a gap.

    ## Future State

    It will be fixed.
    """
)


class TestParsePrbTool(unittest.TestCase):
    """Tests for the parse_prb tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_prb must return the parsed, validated PrbDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_prb(str(path))

            self.assertIsInstance(result, PrbDocument)
            self.assertEqual(result.frontmatter.id, "prb-001")
            self.assertEqual(result.body.text, "Simple Problem Statement")

    def test_model_dump_surfaces_current_state_and_gap(self) -> None:
        """Regression-style check: `model_dump()` must surface real content for
        `current_state`/`gap`/`future_state`, not an empty object -- exactly the
        path an MCP server uses to transmit a tool's return value over the wire.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_prb(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertIn("Something is wrong.", body["current_state"]["summary"]["text"])
            self.assertIsNotNone(body["current_state"]["question_1"])
            self.assertIn("There is a gap.", body["gap"]["text"])
            self.assertIn("It will be fixed.", body["future_state"]["text"])

    def test_raises_for_invalid_frontmatter(self) -> None:
        """parse_prb must let a frontmatter validation failure propagate."""
        text = _VALID_DOC.replace("status: draft", "status: not-a-real-status")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(ValidationError):
                parse_prb(str(path))

    def test_raises_for_malformed_structure(self) -> None:
        """parse_prb must let a structural parse failure propagate."""
        text = "# Title\n\nJust a paragraph, no recognized problem statement sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(AssertionError):
                parse_prb(str(path))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_prb must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_prb("/nonexistent/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
