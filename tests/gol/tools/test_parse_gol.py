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

"""Tests for the ``parse_gol`` ``@mcp.tool()`` wrapper (Task 3.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.gol.models.v1 import GolDocument
from biz.dfch.specmgr.gol.tools.parse_gol import parse_gol

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: gol-001
    type: gol
    status: draft
    ---

    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output and fuel consumption.

    ## Description

    Buyers compare engine power output and fuel consumption across competing manufacturers.

    ## Priority

    10

    ## Source

    The vehicle program's 2027 market analysis

    ## More Information

    This optional section can contain additional information.

    ## Notes

    This optional section can contain additional notes.
    """
)


class TestParseGolTool(unittest.TestCase):
    """Tests for the parse_gol tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_gol must return the parsed, validated GolDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_gol(str(path))

            self.assertIsInstance(result, GolDocument)
            self.assertEqual(result.frontmatter.id, "gol-001")
            self.assertEqual(result.body.text, "Competitive Engines in Consumer Vehicles")

    def test_model_dump_surfaces_markdownparagraph_backed_fields(self) -> None:
        """Regression test: `model_dump()` must surface real content for every
        `MarkdownParagraph`-backed field (`statement`, `priority.value`), not an
        empty object.

        Before `MarkdownParagraph` gained its `text` computed_field, these
        fields serialized to `{}` because `_value` (where the parsed content
        actually lives) is a Pydantic private attribute, invisible to
        `model_dump()`/`model_dump_json()` -- exactly the path an MCP server
        uses to transmit a tool's return value over the wire.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_gol(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["statement"]["text"],
                "THE company shall provide engines that are competitive in power output and fuel consumption.",
            )
            self.assertEqual(body["priority"]["value"]["text"], "10")

    def test_model_dump_surfaces_leaf_section_body_content(self) -> None:
        """Regression test: `model_dump()` must surface the full body prose --
        not just the heading -- for `Description`/`MoreInformation`/`Notes`,
        the bare leaf `MarkdownSection2`s in `gol.models.v1.body` that declare
        no field of their own to hold their content.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_gol(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["description"]["text"],
                "## Description\n\nBuyers compare engine power output and fuel consumption across competing manufacturers.\n",
            )
            self.assertEqual(
                body["more_information"]["text"],
                "## More Information\n\nThis optional section can contain additional information.\n",
            )
            self.assertEqual(
                body["notes"]["text"],
                "## Notes\n\nThis optional section can contain additional notes.\n",
            )

    def test_raises_for_invalid_frontmatter(self) -> None:
        """parse_gol must let a frontmatter validation failure propagate."""
        text = _VALID_DOC.replace("status: draft", "status: not-a-real-status")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(ValidationError):
                parse_gol(str(path))

    def test_raises_for_malformed_structure(self) -> None:
        """parse_gol must let a structural parse failure propagate."""
        text = "# Title\n\nJust a paragraph, no recognized goal sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(AssertionError):
                parse_gol(str(path))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_gol must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_gol("/nonexistent/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
