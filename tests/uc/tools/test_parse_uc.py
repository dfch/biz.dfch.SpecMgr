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

"""Tests for the ``parse_uc`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models.v2 import UcDocument
from biz.dfch.specmgr.uc.tools.parse_uc import parse_uc

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: uc-001
    type: uc
    status: draft
    ---

    # Buy Goods

    ## Characteristic Information

    ### Goal in Context

    Buyer issues request.

    ### Scope

    Company.

    ### Level

    Summary

    ### Preconditions

    - We know Buyer

    ### Success End Condition

    - Buyer has goods

    ### Primary Actor

    Buyer.

    ### Trigger

    Purchase request comes in.

    ## Main Success Scenario

    1. Buyer calls in with a purchase request.
    2. Company creates order in system.
    """
)


class TestParseUcTool(unittest.TestCase):
    """Tests for the parse_uc tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_uc must return the parsed, validated UcDocument for valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_uc(str(path))

            self.assertIsInstance(result, UcDocument)
            self.assertEqual(result.frontmatter.id, "uc-001")
            self.assertEqual(result.body.text, "Buy Goods")

    def test_model_dump_surfaces_markdownparagraph_backed_fields(self) -> None:
        """Regression test: `model_dump()` must surface real content for every
        `MarkdownParagraph`-backed field (`goal_in_context`, `scope`, `level`,
        `primary_actor`, `trigger`), not an empty object.

        Before `MarkdownParagraph` gained its `text` computed_field, these
        fields serialized to `{}` because `_value` (where the parsed content
        actually lives) is a Pydantic private attribute, invisible to
        `model_dump()`/`model_dump_json()` -- exactly the path an MCP server
        uses to transmit a tool's return value over the wire.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_uc(str(path))
            dump = result.model_dump(mode="json")

            ci = dump["body"]["characteristic_information"]
            self.assertEqual(ci["goal_in_context"]["body"][0]["text"], "Buyer issues request.")
            self.assertEqual(ci["scope"]["body"][0]["text"], "Company.")
            self.assertEqual(ci["level"]["body"][0]["text"], "Summary")
            self.assertEqual(ci["primary_actor"]["body"][0]["text"], "Buyer.")
            self.assertEqual(ci["trigger"]["body"][0]["text"], "Purchase request comes in.")

    def test_raises_for_invalid_frontmatter(self) -> None:
        """parse_uc must let a frontmatter validation failure propagate."""
        text = _VALID_DOC.replace("status: draft", "status: not-a-real-status")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(ValidationError):
                parse_uc(str(path))

    def test_raises_for_malformed_structure(self) -> None:
        """parse_uc must let a structural parse failure propagate."""
        text = "# Title\n\nJust a paragraph, no recognized use-case sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(AssertionError):
                parse_uc(str(path))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_uc must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_uc("/nonexistent/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
