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

"""Tests for the ``parse_txt`` ``@mcp.tool()`` wrapper (feat-229-txt Phase 110)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import ValidateResult
from biz.dfch.specmgr.general.tools.validate import _MAX_VALIDATE_ERROR_CHARS
from biz.dfch.specmgr.txt.models.v1 import TxtDocument
from biz.dfch.specmgr.txt.tools.parse_txt import parse_txt

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: txt-001
    type: txt
    status: draft
    ---

    # Ad-hoc review notes

    Some free-form prose about what was reviewed.

    ## Updates

    ### 2026-08-31 00:00:00.000Z - Created

    Initial draft of the review notes.
    """
)


class TestParseTxtTool(unittest.TestCase):
    """Tests for the parse_txt tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_txt must return the parsed, validated TxtDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_txt(str(path))

            self.assertIsInstance(result, TxtDocument)
            self.assertEqual(result.frontmatter.id, "txt-001")
            self.assertEqual(result.frontmatter.type, "txt")
            self.assertEqual(result.body.text, "Ad-hoc review notes")

    def test_model_dump_surfaces_opaque_body_text(self) -> None:
        """Regression test: `model_dump()` must surface the full opaque body text (REQ-006)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_txt(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["body"]["text"],
                "Some free-form prose about what was reviewed.\n",
            )
            self.assertEqual(
                body["updates"]["updates"][0]["content"]["text"],
                "Initial draft of the review notes.\n",
            )

    def test_invalid_frontmatter_returns_validate_result(self) -> None:
        """parse_txt must return the non-raising ``ValidateResult(valid=False, ...)`` for a
        frontmatter validation failure (`accepted` is VCR's, not TXT's;
        feat-204-create-error)."""
        text = _VALID_DOC.replace("status: draft", "status: accepted")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            result = parse_txt(str(path))

            self.assertIsInstance(result, ValidateResult)
            self.assertFalse(result.valid)
            self.assertEqual(len(result.errors), 1)
            message = result.errors[0].message
            self.assertTrue(message)
            self.assertIn("txt parse_txt: ", message)
            self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))

    def test_malformed_structure_returns_validate_result(self) -> None:
        """parse_txt must return the non-raising ``ValidateResult(valid=False, ...)`` for a
        structural parse failure (feat-204-create-error)."""
        text = "# Title\n\nJust a paragraph, no recognized sections and no Updates log.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            result = parse_txt(str(path))

            self.assertIsInstance(result, ValidateResult)
            self.assertFalse(result.valid)
            self.assertEqual(len(result.errors), 1)
            message = result.errors[0].message
            self.assertTrue(message)
            self.assertIn("txt parse_txt: ", message)
            self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_txt must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_txt("/nonexistent/path/to/file.md")

    def test_unreadable_file_raises_permission_error(self) -> None:
        """parse_txt must raise PermissionError for an unreadable path -- ``Path.read_text()``
        sits outside the tool's own catch, so the unreadable half of the "truly-absent or
        unreadable path" file-access contract (feat-204-create-error REQ-002) is never
        intercepted by the non-raising ``ValidateResult`` branch."""
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("permission denied")):
            with self.assertRaises(PermissionError):
                parse_txt("/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
