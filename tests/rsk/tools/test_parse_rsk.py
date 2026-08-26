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

"""Tests for the ``parse_rsk`` ``@mcp.tool()`` wrapper (Task 3.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.rsk.models.v1 import RskDocument
from biz.dfch.specmgr.rsk.tools.parse_rsk import parse_rsk

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: rsk-001
    type: rsk
    status: open
    ---

    # Sample Risk

    ## Cause

    A root condition.

    ## Trigger

    An event that sets the risk in motion.

    ## Consequence

    A bounded consequence.

    ## Scope

    - Sample subsystem

    ## Initial Assessment

    ### Probability 4

    ### Impact 3

    ## Strategy

    reduce

    ## Mitigation

    Sample treatment measures.

    ## Residual Assessment

    ### Probability 2

    ### Impact 3
    """
)


class TestParseRskTool(unittest.TestCase):
    """Tests for the parse_rsk tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_rsk must return the parsed, validated RskDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_rsk(str(path))

            self.assertIsInstance(result, RskDocument)
            self.assertEqual(result.frontmatter.id, "rsk-001")
            self.assertEqual(result.body.text, "Sample Risk")

    def test_model_dump_surfaces_assessments_and_strategy(self) -> None:
        """Regression-style check: `model_dump()` must surface the assessments' computed
        `level` and the strategy's own value -- exactly the path an MCP server uses to
        transmit a tool's return value over the wire.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_rsk(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(body["initial_assessment"]["probability"]["value"], 4)
            self.assertEqual(body["initial_assessment"]["impact"]["value"], 3)
            self.assertEqual(body["initial_assessment"]["level"], "high")
            self.assertEqual(body["residual_assessment"]["probability"]["value"], 2)
            self.assertEqual(body["residual_assessment"]["impact"]["value"], 3)
            self.assertEqual(body["residual_assessment"]["level"], "medium")
            self.assertEqual(body["strategy"]["value"]["text"], "reduce")

    def test_raises_for_invalid_frontmatter(self) -> None:
        """parse_rsk must let a frontmatter validation failure propagate."""
        text = _VALID_DOC.replace("status: open", "status: not-a-real-status")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(ValidationError):
                parse_rsk(str(path))

    def test_raises_for_malformed_structure(self) -> None:
        """parse_rsk must let a structural parse failure propagate."""
        text = "# Title\n\nJust a paragraph, no recognized risk sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(AssertionError):
                parse_rsk(str(path))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_rsk must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_rsk("/nonexistent/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
