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
from unittest import mock

from biz.dfch.specmgr.general.models import ValidateResult
from biz.dfch.specmgr.general.tools.validate import _MAX_VALIDATE_ERROR_CHARS
from biz.dfch.specmgr.rsk.models.v1 import RskDocument
from biz.dfch.specmgr.rsk.tools.parse_rsk import parse_rsk

from ._helpers import MANDATORY_SOURCE

_VALID_DOC = (
    textwrap.dedent(
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
    + MANDATORY_SOURCE
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

    def test_invalid_frontmatter_returns_validate_result(self) -> None:
        """parse_rsk must return the non-raising ``ValidateResult(valid=False, ...)`` for a
        frontmatter validation failure (feat-204-create-error, Phase 120)."""
        text = _VALID_DOC.replace("status: open", "status: not-a-real-status")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            result = parse_rsk(str(path))

            self.assertIsInstance(result, ValidateResult)
            self.assertFalse(result.valid)
            self.assertEqual(len(result.errors), 1)
            message = result.errors[0].message
            self.assertTrue(message)
            self.assertIn("rsk parse_rsk: ", message)
            self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))
            self.assertTrue(message.endswith("... (truncated)"), message)

    def test_malformed_structure_returns_validate_result(self) -> None:
        """parse_rsk must return the non-raising ``ValidateResult(valid=False, ...)`` for a
        structural parse failure (feat-204-create-error, Phase 120)."""
        text = "# Title\n\nJust a paragraph, no recognized risk sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            result = parse_rsk(str(path))

            self.assertIsInstance(result, ValidateResult)
            self.assertFalse(result.valid)
            self.assertEqual(len(result.errors), 1)
            message = result.errors[0].message
            self.assertTrue(message)
            self.assertIn("rsk parse_rsk: ", message)
            self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_rsk must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_rsk("/nonexistent/path/to/file.md")

    def test_unreadable_file_raises_permission_error(self) -> None:
        """parse_rsk must raise PermissionError for an unreadable path -- ``Path.read_text()``
        sits outside the tool's own catch, so the unreadable half of the "truly-absent or
        unreadable path" file-access contract (feat-204-create-error REQ-002/ACC-002) is never
        intercepted by the non-raising ``ValidateResult`` branch (Phase 150)."""
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("permission denied")):
            with self.assertRaises(PermissionError):
                parse_rsk("/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
