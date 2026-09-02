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

"""Tests for the ``parse_sysrs`` ``@mcp.tool()`` wrapper (Task 3.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.sysrs.models.v1 import SysrsDocument
from biz.dfch.specmgr.sysrs.tools.parse_sysrs import parse_sysrs

_GOL_ID = "0e15c5de-4ac9-4279-aa75-53249a3e43e4"
_REQ_ID = "a3f8c2d1-7b4e-4d9a-b6c0-91e5f2a8d734"

_VALID_DOC = textwrap.dedent(
    f"""\
    ---
    id: sysrs-001
    type: sysrs
    status: draft
    ---

    # System Requirements Specification: Sample Document

    ## System Purpose

    Provision partner accounts.

    ## System Scope

    Onboarding only.

    ## Business Context and Goals

    ### Goals

    - GOL {_GOL_ID}: A goal

    ## System Overview

    ### System Context

    Context.

    ### System Functions

    Functions.

    ## Requirements

    ### Functional Suitability

    - REQ {_REQ_ID}: A requirement

    ## More Information

    Covers the MVP only.
    """
)


class TestParseSysrsTool(unittest.TestCase):
    """Tests for the parse_sysrs tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_sysrs must return the parsed, validated SysrsDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_sysrs(str(path))

            self.assertIsInstance(result, SysrsDocument)
            self.assertEqual(result.frontmatter.id, "sysrs-001")
            self.assertEqual(result.body.text, "System Requirements Specification: Sample Document")

    def test_model_dump_surfaces_leaf_section_body_content(self) -> None:
        """Regression test: `model_dump()` must surface the full body prose for `MoreInformation`,
        the bare leaf `MarkdownSection2` in `sysrs.models.v1.body` that declares no field of its own.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_sysrs(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["more_information"]["text"],
                "## More Information\n\nCovers the MVP only.\n",
            )

    def test_raises_for_invalid_frontmatter(self) -> None:
        """parse_sysrs must let a frontmatter validation failure propagate (`accepted` is not a sysrs status)."""
        text = _VALID_DOC.replace("status: draft", "status: accepted")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(ValidationError):
                parse_sysrs(str(path))

    def test_raises_for_malformed_structure(self) -> None:
        """parse_sysrs must let a structural parse failure propagate."""
        text = "# Title\n\nJust a paragraph, no recognized System Requirements Specification sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(AssertionError):
                parse_sysrs(str(path))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_sysrs must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_sysrs("/nonexistent/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
