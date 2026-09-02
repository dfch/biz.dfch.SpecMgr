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

"""Tests for the ``parse_tsk`` ``@mcp.tool()`` wrapper (Task 3.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.tsk.models.v1 import TskDocument
from biz.dfch.specmgr.tsk.tools.parse_tsk import parse_tsk

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: tsk-001
    type: tsk
    status: draft
    ---

    # Simple Task List

    - [ ] Do the first thing
    - [x] Do the second thing

    ## Recent Updates

    ### 2026-08-19 - Kickoff

    Started the task list.
    """
)


class TestParseTskTool(unittest.TestCase):
    """Tests for the parse_tsk tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_tsk must return the parsed, validated TskDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_tsk(str(path))

            self.assertIsInstance(result, TskDocument)
            self.assertEqual(result.frontmatter.id, "tsk-001")
            self.assertEqual(result.body.text, "Simple Task List")

    def test_model_dump_surfaces_items_and_recent_updates(self) -> None:
        """Regression-style check: `model_dump()` must surface real content for the
        checklist items and Recent Updates entries, not an empty object -- exactly the
        path an MCP server uses to transmit a tool's return value over the wire.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_tsk(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(len(body["items"]), 2)
            self.assertEqual(body["items"][0]["checked"], False)
            self.assertEqual(body["items"][0]["description"], "Do the first thing")
            self.assertEqual(body["items"][1]["checked"], True)
            self.assertEqual(len(body["recent_updates"]["updates"]), 1)
            self.assertEqual(body["recent_updates"]["updates"][0]["content"]["text"], "Started the task list.")

    def test_raises_for_invalid_frontmatter(self) -> None:
        """parse_tsk must let a frontmatter validation failure propagate."""
        text = _VALID_DOC.replace("status: draft", "status: not-a-real-status")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(ValidationError):
                parse_tsk(str(path))

    def test_raises_for_malformed_structure(self) -> None:
        """parse_tsk must let a structural parse failure propagate."""
        text = "# Title\n\nJust a paragraph, no recognized task list sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(AssertionError):
                parse_tsk(str(path))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_tsk must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_tsk("/nonexistent/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
