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

"""Tests for the ``parse_qa`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.qa.models.v1 import QaDocument
from biz.dfch.specmgr.qa.tools.parse_qa import parse_qa

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: qa-001
    type: qa
    status: draft
    ---

    # Some QA Title

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    ## Functional Suitability

    ### What must happen?

    > Is this acceptable?

    Yes, it is acceptable.

    ## Performance Efficiency

    ## Compatibility

    ## Interaction Capability

    ## Reliability

    ## Security

    ## Maintainability

    ## Flexibility

    ## Safety

    ## More Information

    This optional section can contain additional information.
    """
)


class TestParseQaTool(unittest.TestCase):
    """Tests for the parse_qa tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_qa must return the parsed, validated QaDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_qa(str(path))

            self.assertIsInstance(result, QaDocument)
            self.assertEqual(result.frontmatter.id, "qa-001")
            self.assertEqual(result.body.text, "Some QA Title")

    def test_model_dump_surfaces_markdownparagraph_backed_fields(self) -> None:
        """Regression test: `model_dump()` must surface real content for
        `Introduction`'s `body` field, not an empty object -- exactly the path
        an MCP server uses to transmit a tool's return value over the wire.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_qa(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(body["general"]["introduction"]["body"][0]["text"], "Some intro text.")

    def test_model_dump_surfaces_leaf_section_body_content(self) -> None:
        """Regression test: `model_dump()` must surface the full body prose --
        not just the heading -- for `RawRequirements`/`MoreInformation`/
        `QaAnswer`, the bare leaf classes in `qa.models.v1.body` that declare
        no field of their own to hold their content.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_qa(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertIn("Some raw requirements text.", body["general"]["raw_requirements"]["text"])
            self.assertIn("additional information", body["more_information"]["text"])
            item = body["functional_suitability"]["items"][0]
            self.assertIn("Yes, it is acceptable.", item["answer"]["text"])
            self.assertIn("Is this acceptable?", item["question"]["text"])

    def test_raises_for_invalid_frontmatter(self) -> None:
        """parse_qa must let a frontmatter validation failure propagate."""
        text = _VALID_DOC.replace("status: draft", "status: not-a-real-status")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(ValidationError):
                parse_qa(str(path))

    def test_raises_for_malformed_structure(self) -> None:
        """parse_qa must let a structural parse failure propagate."""
        text = "# Title\n\nJust a paragraph, no recognized QA sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(AssertionError):
                parse_qa(str(path))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_qa must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_qa("/nonexistent/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
