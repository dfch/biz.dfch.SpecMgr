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

"""Tests for the ``parse_dec`` ``@mcp.tool()`` wrapper (Task 2.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.dec.models.v1 import DecDocument
from biz.dfch.specmgr.dec.tools.parse_dec import parse_dec

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: dec-001
    type: dec
    status: draft
    ---

    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Drivers

    - Latency under 100 ms at p95.

    ## Decision Outcome

    We chose the document store.

    ### Consequences

    Reporting reads from the nightly export.

    ## More Information

    Harness config in the platform repository.
    """
)


class TestParseDecTool(unittest.TestCase):
    """Tests for the parse_dec tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_dec must return the parsed, validated DecDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_dec(str(path))

            self.assertIsInstance(result, DecDocument)
            self.assertEqual(result.frontmatter.id, "dec-001")
            self.assertEqual(result.body.text, "Choose a Document Store")

    def test_model_dump_surfaces_markdownparagraph_backed_fields(self) -> None:
        """Regression test: `model_dump()` must surface real content for the
        `MarkdownParagraph`-backed field (`outcome.statement`), not an empty
        object.

        Before `MarkdownParagraph` gained its `text` computed_field, this
        field serialized to `{}` because `_value` (where the parsed content
        actually lives) is a Pydantic private attribute, invisible to
        `model_dump()`/`model_dump_json()` -- exactly the path an MCP server
        uses to transmit a tool's return value over the wire.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_dec(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["outcome"]["statement"]["text"],
                "We chose the document store.",
            )

    def test_model_dump_surfaces_leaf_section_body_content(self) -> None:
        """Regression test: `model_dump()` must surface the full body prose --
        not just the heading -- for `Context`/`MoreInformation`, the bare leaf
        `MarkdownSection2`s in `dec.models.v1.body` that declare no field of
        their own to hold their content.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_dec(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["context"]["text"],
                "## Context and Problem Statement\n\nThe current store cannot serve the dashboard read path.\n",
            )
            self.assertEqual(
                body["more_information"]["text"],
                "## More Information\n\nHarness config in the platform repository.\n",
            )

    def test_raises_for_invalid_frontmatter(self) -> None:
        """parse_dec must let a frontmatter validation failure propagate (`implemented` is GOL's, not DEC's)."""
        text = _VALID_DOC.replace("status: draft", "status: implemented")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(ValidationError):
                parse_dec(str(path))

    def test_raises_for_malformed_structure(self) -> None:
        """parse_dec must let a structural parse failure propagate."""
        text = "# Title\n\nJust a paragraph, no recognized decision sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(AssertionError):
                parse_dec(str(path))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_dec must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_dec("/nonexistent/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
