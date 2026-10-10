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

"""Tests for the ``parse_sop`` ``@mcp.tool()`` wrapper (Task 2.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import ValidateResult
from biz.dfch.specmgr.general.tools.validate import _MAX_VALIDATE_ERROR_CHARS
from biz.dfch.specmgr.sop.models.v1 import SopDocument
from biz.dfch.specmgr.sop.tools.parse_sop import parse_sop

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: sop-001
    type: sop
    status: draft
    ---

    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for new hires.

    ## Scope

    All new hires in the engineering organization.

    ## Procedure

    ### Step 1: Submit request

    HR submits the request.

    ### Step 2: Provision account

    IT creates the account.
    """
)


class TestParseSopTool(unittest.TestCase):
    """Tests for the parse_sop tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_sop must return the parsed, validated SopDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_sop(str(path))

            self.assertIsInstance(result, SopDocument)
            self.assertEqual(result.frontmatter.id, "sop-001")
            self.assertEqual(result.body.text, "New Employee IT Account Provisioning")
            self.assertEqual(len(result.body.procedure.steps), 2)

    def test_model_dump_surfaces_leaf_section_body_content(self) -> None:
        """Regression test: `model_dump()` must surface the full body prose -- not just the heading --
        for `Purpose`/`Scope`, the bare leaf `MarkdownSection2`s in `sop.models.v1.body` that declare
        no field of their own to hold their content.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_sop(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["purpose"]["text"],
                "## Purpose\n\nProvision accounts for new hires.\n",
            )
            self.assertEqual(
                body["scope"]["text"],
                "## Scope\n\nAll new hires in the engineering organization.\n",
            )

    def test_invalid_frontmatter_returns_validate_result(self) -> None:
        """parse_sop must return the non-raising ``ValidateResult(valid=False, ...)`` for a
        frontmatter validation failure (`implemented` is GOL's, not SOP's;
        feat-204-create-error, Phase 120)."""
        text = _VALID_DOC.replace("status: draft", "status: implemented")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            result = parse_sop(str(path))

            self.assertIsInstance(result, ValidateResult)
            self.assertFalse(result.valid)
            self.assertEqual(len(result.errors), 1)
            message = result.errors[0].message
            self.assertTrue(message)
            self.assertIn("sop parse_sop: ", message)
            self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))

    def test_malformed_structure_returns_validate_result(self) -> None:
        """parse_sop must return the non-raising ``ValidateResult(valid=False, ...)`` for a
        structural parse failure (feat-204-create-error, Phase 120)."""
        text = "# Title\n\nJust a paragraph, no recognized SOP sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            result = parse_sop(str(path))

            self.assertIsInstance(result, ValidateResult)
            self.assertFalse(result.valid)
            self.assertEqual(len(result.errors), 1)
            message = result.errors[0].message
            self.assertTrue(message)
            self.assertIn("sop parse_sop: ", message)
            self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_sop must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_sop("/nonexistent/path/to/file.md")

    def test_unreadable_file_raises_permission_error(self) -> None:
        """parse_sop must raise PermissionError for an unreadable path -- ``Path.read_text()``
        sits outside the tool's own catch, so the unreadable half of the "truly-absent or
        unreadable path" file-access contract (feat-204-create-error REQ-002/ACC-002) is never
        intercepted by the non-raising ``ValidateResult`` branch (Phase 150)."""
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("permission denied")):
            with self.assertRaises(PermissionError):
                parse_sop("/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
