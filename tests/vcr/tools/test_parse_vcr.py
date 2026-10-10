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

"""Tests for the ``parse_vcr`` ``@mcp.tool()`` wrapper (Task 2.1)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import ValidateResult
from biz.dfch.specmgr.general.tools.validate import _MAX_VALIDATE_ERROR_CHARS
from biz.dfch.specmgr.vcr.models.v1 import VcrDocument
from biz.dfch.specmgr.vcr.tools.parse_vcr import parse_vcr

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: vcr-001
    type: vcr
    status: draft
    ---

    # Sample Verification Case

    ## Verifies

    REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Sample requirement title

    Confirms that the sample requirement is met.

    ## Coverage

    partial

    ## Acceptance Criteria

    ### AC-001 (Test): The sample criterion passes

    ## More Information

    Verified against the staging environment.
    """
)


class TestParseVcrTool(unittest.TestCase):
    """Tests for the parse_vcr tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_vcr must return the parsed, validated VcrDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_vcr(str(path))

            self.assertIsInstance(result, VcrDocument)
            self.assertEqual(result.frontmatter.id, "vcr-001")
            self.assertEqual(result.body.text, "Sample Verification Case")

    def test_model_dump_surfaces_markdownparagraph_backed_fields(self) -> None:
        """Regression test: `model_dump()` must surface real content for the
        `MarkdownParagraph`-backed field (`verifies.notes`), not an empty object.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_vcr(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["verifies"]["notes"]["text"],
                "Confirms that the sample requirement is met.",
            )

    def test_model_dump_surfaces_leaf_section_body_content(self) -> None:
        """Regression test: `model_dump()` must surface the full body prose for `MoreInformation`,
        the bare leaf `MarkdownSection2` in `vcr.models.v1.body` that declares no field of its own.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_vcr(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["more_information"]["text"],
                "## More Information\n\nVerified against the staging environment.\n",
            )

    def test_invalid_frontmatter_returns_validate_result(self) -> None:
        """parse_vcr must return the non-raising ``ValidateResult(valid=False, ...)`` for a
        frontmatter validation failure (`accepted` is DEC's, not VCR's;
        feat-204-create-error, Phase 120)."""
        text = _VALID_DOC.replace("status: draft", "status: accepted")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            result = parse_vcr(str(path))

            self.assertIsInstance(result, ValidateResult)
            self.assertFalse(result.valid)
            self.assertEqual(len(result.errors), 1)
            message = result.errors[0].message
            self.assertTrue(message)
            self.assertIn("vcr parse_vcr: ", message)
            self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))

    def test_malformed_structure_returns_validate_result(self) -> None:
        """parse_vcr must return the non-raising ``ValidateResult(valid=False, ...)`` for a
        structural parse failure (feat-204-create-error, Phase 120)."""
        text = "# Title\n\nJust a paragraph, no recognized verification case record sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            result = parse_vcr(str(path))

            self.assertIsInstance(result, ValidateResult)
            self.assertFalse(result.valid)
            self.assertEqual(len(result.errors), 1)
            message = result.errors[0].message
            self.assertTrue(message)
            self.assertIn("vcr parse_vcr: ", message)
            self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_vcr must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_vcr("/nonexistent/path/to/file.md")

    def test_unreadable_file_raises_permission_error(self) -> None:
        """parse_vcr must raise PermissionError for an unreadable path -- ``Path.read_text()``
        sits outside the tool's own catch, so the unreadable half of the "truly-absent or
        unreadable path" file-access contract (feat-204-create-error REQ-002/ACC-002) is never
        intercepted by the non-raising ``ValidateResult`` branch (Phase 150)."""
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("permission denied")):
            with self.assertRaises(PermissionError):
                parse_vcr("/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
